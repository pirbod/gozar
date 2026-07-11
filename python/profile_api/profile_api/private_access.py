from __future__ import annotations

import base64
import hashlib
import ipaddress
import json
import secrets
from datetime import UTC, timedelta
from typing import Any

from nacl.signing import SigningKey
from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import record_audit
from .config import Settings
from .crypto import (
    canonical_json_text,
    public_key_fingerprint,
    sha256_json,
    sha256_text,
    sign_envelope,
    verify_envelope_signature,
)
from .issuer_keys import get_or_create_active_issuer_key
from .models import Device, RevokedProfile, SessionProfile, utc_now
from .safety import get_safety_state
from .schemas import PrivateAccessEnrollmentRequest, PrivateAccessProfileRequest
from .storage import dumps_json, new_id

PRODUCT_PROFILE_TYPE = "wireguard_private_access"
PRODUCT_POLICY_VERSION = "private-access-v1"
PRODUCT_SAFETY_NOTES = ["approved_routes_only", "no_default_route", "private_access_only"]


class DeviceAuthenticationError(ValueError):
    pass


class PrivateAccessDenied(ValueError):
    pass


def enroll_device(
    session: Session,
    payload: PrivateAccessEnrollmentRequest,
    settings: Settings,
) -> tuple[Device, str]:
    _validate_curve25519_key(payload.device_public_key, "device_public_key")
    _validate_curve25519_key(payload.wireguard_public_key, "wireguard_public_key")
    public_key_hash = public_key_fingerprint(payload.device_public_key)
    device = session.scalar(select(Device).where(Device.device_public_key_hash == public_key_hash))
    if device is None:
        device = Device(
            device_id=new_id("dev"),
            display_name=payload.display_name,
            platform="android",
            app_version=payload.app_version,
            device_public_key=payload.device_public_key,
            device_public_key_hash=public_key_hash,
            capabilities_json=dumps_json(
                {
                    "private_access": True,
                    "wireguard": True,
                    "split_tunnel": True,
                }
            ),
            assigned_address=_next_client_address(session, settings.client_address_pool),
        )
        session.add(device)

    device.display_name = payload.display_name
    device.app_version = payload.app_version
    device.status = "active"
    device.wireguard_public_key = payload.wireguard_public_key
    device.assigned_address = device.assigned_address or _next_client_address(session, settings.client_address_pool)
    device.updated_at = utc_now()

    raw_token = secrets.token_urlsafe(32)
    device.auth_token_hash = hash_device_token(raw_token, settings.device_token_pepper)
    record_audit(
        session,
        "private_access.device_enrolled",
        actor_id=device.device_id,
        summary="Android device enrolled for approved private-service access.",
        metadata={
            "device_id": device.device_id,
            "device_public_key_hash": device.device_public_key_hash,
            "status": device.status,
        },
    )
    session.flush()
    return device, raw_token


def authenticate_device(session: Session, raw_token: str, settings: Settings) -> Device:
    if not raw_token:
        raise DeviceAuthenticationError("device bearer token is required")
    token_hash = hash_device_token(raw_token, settings.device_token_pepper)
    device = session.scalar(select(Device).where(Device.auth_token_hash == token_hash))
    if device is None or device.status != "active":
        raise DeviceAuthenticationError("device bearer token is invalid or inactive")
    device.last_seen_at = utc_now()
    return device


def issue_access_profile(
    session: Session,
    device: Device,
    request: PrivateAccessProfileRequest,
    settings: Settings,
) -> dict[str, Any]:
    if get_safety_state(session).pause_enabled:
        raise PrivateAccessDenied("private access is paused by an operator")
    if device.wireguard_public_key is None or device.assigned_address is None:
        raise PrivateAccessDenied("device enrollment is incomplete")

    ttl_seconds = request.ttl_seconds or settings.default_ttl_seconds
    ttl_seconds = min(max(ttl_seconds, 60), 3600)
    issued_at = utc_now()
    expires_at = issued_at + timedelta(seconds=ttl_seconds)
    profile_id = new_id("access")
    issuer_key_id, issuer_public_key, issuer_private_key = _signing_material(session, settings)
    envelope_without_signature = {
        "approved_routes": settings.approved_routes,
        "approved_services": settings.approved_services,
        "audience": device.device_public_key_hash,
        "client_address": device.assigned_address,
        "device_id": device.device_id,
        "dns_servers": settings.dns_servers,
        "expires_at": _timestamp(expires_at),
        "gateway_endpoint": settings.gateway_endpoint,
        "gateway_public_key": settings.gateway_public_key,
        "issued_at": _timestamp(issued_at),
        "issuer_key_id": issuer_key_id,
        "issuer_public_key": issuer_public_key,
        "persistent_keepalive_seconds": 25,
        "policy_version": PRODUCT_POLICY_VERSION,
        "profile_id": profile_id,
        "ttl_seconds": ttl_seconds,
    }
    signature = sign_envelope(envelope_without_signature, issuer_private_key)
    envelope = {**envelope_without_signature, "signature": signature}
    if not verify_envelope_signature(envelope, issuer_public_key):
        raise RuntimeError("private-access profile signature verification failed")

    session.add(
        SessionProfile(
            profile_id=profile_id,
            device_id_hash=device.device_public_key_hash,
            audience_hash=device.device_public_key_hash,
            profile_type=PRODUCT_PROFILE_TYPE,
            issued_at=issued_at,
            expires_at=expires_at,
            ttl_seconds=ttl_seconds,
            status="active",
            policy_version=PRODUCT_POLICY_VERSION,
            redacted_routing_mode="private_split_tunnel",
            safety_notes_json=dumps_json(PRODUCT_SAFETY_NOTES),
            signed_envelope_json=canonical_json_text(envelope_without_signature),
            signature=signature,
            issuer_key_id=issuer_key_id,
            issuer_public_key=issuer_public_key,
            envelope_hash=sha256_json(envelope_without_signature),
            encrypted_payload_hash=sha256_text(""),
            signature_hash=sha256_text(signature),
            signature_format_valid=True,
        )
    )
    record_audit(
        session,
        "private_access.profile_issued",
        actor_id=device.device_id,
        summary="Short-lived WireGuard profile issued for approved internal routes.",
        metadata={
            "profile_id": profile_id,
            "device_id": device.device_id,
            "policy_version": PRODUCT_POLICY_VERSION,
            "ttl_seconds": ttl_seconds,
        },
    )
    return envelope


def validate_access_profile(session: Session, profile_id: str, device: Device) -> dict[str, Any]:
    profile = session.get(SessionProfile, profile_id)
    checks = {
        "exists": "fail",
        "ownership": "fail",
        "signature": "fail",
        "envelope_hash": "fail",
        "ttl": "fail",
        "revocation": "fail",
        "route_policy": "fail",
    }
    if profile is None or profile.profile_type != PRODUCT_PROFILE_TYPE:
        return {"profile_id": profile_id, "valid": False, "status": "unknown", "checks": checks}

    checks["exists"] = "pass"
    ownership_ok = profile.device_id_hash == device.device_public_key_hash
    checks["ownership"] = "pass" if ownership_ok else "fail"

    try:
        signed_fields = json.loads(profile.signed_envelope_json)
    except json.JSONDecodeError:
        signed_fields = {}
    envelope_hash_ok = isinstance(signed_fields, dict) and sha256_json(signed_fields) == profile.envelope_hash
    checks["envelope_hash"] = "pass" if envelope_hash_ok else "fail"
    signature_ok = isinstance(signed_fields, dict) and verify_envelope_signature(
        {**signed_fields, "signature": profile.signature},
        profile.issuer_public_key,
    )
    checks["signature"] = "pass" if signature_ok else "fail"

    now = utc_now()
    expires_at = profile.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    ttl_ok = now < expires_at
    checks["ttl"] = "pass" if ttl_ok else "fail"
    revoked = session.get(RevokedProfile, profile_id) is not None or profile.status == "revoked"
    checks["revocation"] = "fail" if revoked else "pass"
    routes = signed_fields.get("approved_routes", []) if isinstance(signed_fields, dict) else []
    route_policy_ok = bool(routes) and all(_is_bounded_private_route(str(route)) for route in routes)
    checks["route_policy"] = "pass" if route_policy_ok else "fail"

    valid = all(value == "pass" for value in checks.values())
    status = "active" if valid else ("revoked" if revoked else "expired" if not ttl_ok else "invalid_signature")
    return {"profile_id": profile_id, "valid": valid, "status": status, "checks": checks}


def device_summary(device: Device, settings: Settings) -> dict[str, Any]:
    return {
        "device_id": device.device_id,
        "display_name": device.display_name,
        "status": device.status,
        "assigned_address": device.assigned_address,
        "approved_routes": settings.approved_routes,
        "last_seen_at": device.last_seen_at,
    }


def wireguard_peers(session: Session) -> list[dict[str, str]]:
    devices = session.scalars(
        select(Device).where(
            Device.status == "active",
            Device.wireguard_public_key.is_not(None),
            Device.assigned_address.is_not(None),
        )
    ).all()
    return [
        {
            "device_id": device.device_id,
            "public_key": str(device.wireguard_public_key),
            "allowed_ip": f"{device.assigned_address}/32",
        }
        for device in devices
    ]


def hash_device_token(raw_token: str, pepper: str) -> str:
    return "dth_" + hashlib.sha256(f"{pepper}:{raw_token}".encode()).hexdigest()


def _signing_material(session: Session, settings: Settings) -> tuple[str, str, str]:
    if settings.issuer_private_key:
        signing_key = SigningKey(base64.b64decode(settings.issuer_private_key))
        public_key = base64.b64encode(bytes(signing_key.verify_key)).decode()
        return settings.issuer_key_id, public_key, settings.issuer_private_key
    key = get_or_create_active_issuer_key(session, allow_demo_private_keys=settings.allow_demo_private_keys)
    return key.key_id, key.public_key, key.private_key_demo


def _next_client_address(session: Session, raw_pool: str) -> str:
    used = set(session.scalars(select(Device.assigned_address).where(Device.assigned_address.is_not(None))).all())
    hosts = ipaddress.ip_network(raw_pool, strict=True).hosts()
    next(hosts, None)  # Reserve the first usable address for the gateway.
    for address in hosts:
        value = str(address)
        if value not in used:
            return value
    raise PrivateAccessDenied("private-access address pool is exhausted")


def _validate_curve25519_key(value: str, field_name: str) -> None:
    try:
        decoded = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be base64") from exc
    if len(decoded) != 32:
        raise ValueError(f"{field_name} must decode to 32 bytes")


def _is_bounded_private_route(value: str) -> bool:
    try:
        network = ipaddress.ip_network(value, strict=True)
    except ValueError:
        return False
    return network.is_private and network.prefixlen > 0


def _timestamp(value: Any) -> str:
    return value.isoformat().replace("+00:00", "Z")
