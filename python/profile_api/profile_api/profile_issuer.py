from __future__ import annotations

import base64
import binascii
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import record_audit
from .crypto import (
    canonical_json_text,
    encrypt_for_android_local_demo,
    encrypt_for_device,
    sha256_json,
    sha256_text,
    sign_envelope,
    verify_envelope_signature,
)
from .issuer_keys import get_or_create_active_issuer_key
from .models import Device, SessionProfile, utc_now
from .policy_engine import select_profile_policy
from .profile_templates import build_profile_payload
from .safety import SAFETY_NOTES, get_safety_state
from .schemas import SessionProfileRequest
from .storage import dumps_json, loads_json, new_id


class ProfileIssueDenied(ValueError):
    def __init__(self, decision: dict[str, Any]) -> None:
        super().__init__(decision["reasons"][0])
        self.decision = decision


def issue_session_profile(
    *,
    session: Session,
    device: Device,
    request: SessionProfileRequest,
    default_ttl_seconds: int,
) -> dict[str, Any]:
    state = get_safety_state(session)
    capabilities = loads_json(device.capabilities_json)
    device_context = {
        "device_id_hash": device.device_public_key_hash,
        "platform": device.platform,
        "capabilities": capabilities,
    }
    record_audit(
        session,
        "profile.requested",
        actor_id=device.device_id,
        summary="Local-only adaptive session profile requested.",
        metadata={
            "device_id": device.device_id,
            "requested_mode": request.requested_mode,
            "risk_tolerance": request.risk_tolerance,
            "previous_failure_class": request.client_context.previous_failure_class,
        },
    )
    decision = select_profile_policy(
        device=device_context,
        requested_mode=request.requested_mode,
        risk_tolerance=request.risk_tolerance,
        client_context=request.client_context.model_dump(),
        safety_pause_enabled=state.pause_enabled,
    )
    record_audit(
        session,
        "policy.selected",
        actor_id=device.device_id,
        summary="Deterministic policy engine selected a local demo profile decision.",
        metadata={
            "device_id": device.device_id,
            "selected_profile_type": decision["selected_profile_type"],
            "decision": decision["decision"],
            "risk": decision["risk"],
            "confidence": decision["confidence"],
            "reasons": decision["reasons"],
        },
    )
    if decision["decision"] != "issue":
        raise ProfileIssueDenied(decision)

    ttl_seconds = request.ttl_seconds or default_ttl_seconds
    issuer_key = get_or_create_active_issuer_key(session)
    issued_at = utc_now()
    expires_at = issued_at + timedelta(seconds=ttl_seconds)
    issued_at_text = _timestamp(issued_at)
    expires_at_text = _timestamp(expires_at)
    profile_id = new_id("prof")
    profile_type = str(decision["selected_profile_type"])
    safety_notes = sorted(set(SAFETY_NOTES + list(decision["safety_notes"])))
    payload = build_profile_payload(
        profile_id=profile_id,
        profile_type=profile_type,
        routing_mode=str(decision["routing_mode"]),
        issued_at=issued_at_text,
        expires_at=expires_at_text,
        ttl_seconds=ttl_seconds,
        audience=device.device_public_key_hash,
        policy_version=str(decision["policy_version"]),
        policy_reasons=list(decision["reasons"]),
        safety_notes=safety_notes,
    )
    envelope_mode = request.envelope_mode
    if envelope_mode == "android_local_demo":
        encrypted_payload = encrypt_for_android_local_demo(payload, device.device_public_key)
    else:
        encrypted_payload = encrypt_for_device(payload, device.device_public_key)
    envelope_without_signature = {
        "profile_id": profile_id,
        "profile_type": profile_type,
        "envelope_mode": envelope_mode,
        "issued_at": issued_at_text,
        "expires_at": expires_at_text,
        "ttl_seconds": ttl_seconds,
        "audience": device.device_public_key_hash,
        "policy_version": decision["policy_version"],
        "encrypted_payload": encrypted_payload,
        "issuer_key_id": issuer_key.key_id,
        "issuer_public_key": issuer_key.public_key,
        "safety_notes": safety_notes,
    }
    signature = sign_envelope(envelope_without_signature, issuer_key.private_key_demo)
    envelope = {**envelope_without_signature, "signature": signature}
    if not verify_envelope_signature(envelope, issuer_key.public_key):
        raise ValueError("issued envelope signature failed verification")
    envelope_hash = sha256_json(envelope_without_signature)
    encrypted_payload_hash = sha256_text(encrypted_payload)
    signature_hash = _hash_base64(signature)

    session.add(
        SessionProfile(
            profile_id=profile_id,
            device_id_hash=device.device_public_key_hash,
            audience_hash=device.device_public_key_hash,
            profile_type=profile_type,
            issued_at=issued_at,
            expires_at=expires_at,
            ttl_seconds=ttl_seconds,
            status="active",
            policy_version=str(decision["policy_version"]),
            redacted_routing_mode=str(payload["config"]["routing"]["mode"]),
            safety_notes_json=dumps_json(safety_notes),
            signed_envelope_json=canonical_json_text(envelope_without_signature),
            signature=signature,
            issuer_key_id=issuer_key.key_id,
            issuer_public_key=issuer_key.public_key,
            envelope_hash=envelope_hash,
            encrypted_payload_hash=encrypted_payload_hash,
            signature_hash=signature_hash,
            signature_format_valid=_is_base64(signature),
        )
    )
    record_audit(
        session,
        "profile.issued",
        actor_id=device.device_id,
        summary="Signed encrypted profile envelope issued for local demo use.",
        metadata={
            "profile_id": profile_id,
            "device_id": device.device_id,
            "profile_type": profile_type,
            "envelope_mode": envelope_mode,
            "ttl_seconds": ttl_seconds,
            "routing_mode": payload["config"]["routing"]["mode"],
            "policy_version": decision["policy_version"],
            "issuer_key_id": issuer_key.key_id,
            "envelope_hash": envelope_hash,
            "encrypted_payload_hash": encrypted_payload_hash,
            "signature_hash": signature_hash,
        },
    )
    return envelope


def profile_metadata(profile: SessionProfile) -> dict[str, Any]:
    return {
        "profile_id": profile.profile_id,
        "device_id_hash": profile.device_id_hash,
        "profile_type": profile.profile_type,
        "issued_at": profile.issued_at,
        "expires_at": profile.expires_at,
        "status": _profile_status(profile, None),
        "policy_version": profile.policy_version,
        "redacted_routing_mode": profile.redacted_routing_mode,
        "safety_notes": _load_list(profile.safety_notes_json),
    }


def validate_profile(
    session: Session,
    profile_id: str,
    *,
    expected_audience: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    profile = session.get(SessionProfile, profile_id)
    if profile is None:
        return {
            "profile_id": profile_id,
            "valid": False,
            "status": "unknown",
            "checks": {
                "exists": "fail",
                "signature": "fail",
                "envelope_hash": "fail",
                "encrypted_payload_hash": "fail",
                "ttl": "fail",
                "revocation": "fail",
                "audience": "fail",
            },
        }
    status = _profile_status(profile, now)
    signed_fields = _load_signed_fields(profile)
    envelope_hash_ok = signed_fields is not None and sha256_json(signed_fields) == profile.envelope_hash
    encrypted_payload = signed_fields.get("encrypted_payload") if signed_fields else None
    encrypted_payload_hash_ok = (
        isinstance(encrypted_payload, str) and sha256_text(encrypted_payload) == profile.encrypted_payload_hash
    )
    signature_ok = _stored_signature_valid(profile, signed_fields)
    audience = signed_fields.get("audience") if signed_fields else None
    audience_ok = _audience_ok(
        session,
        profile,
        audience=audience,
        expected_audience=expected_audience,
    )
    checks = {
        "exists": "pass",
        "signature": "pass" if signature_ok else "fail",
        "envelope_hash": "pass" if envelope_hash_ok else "fail",
        "encrypted_payload_hash": "pass" if encrypted_payload_hash_ok else "fail",
        "ttl": "pass" if status != "expired" else "fail",
        "revocation": "pass" if status != "revoked" else "fail",
        "audience": "pass" if audience_ok else "fail",
    }
    response_status = "invalid_signature" if status == "active" and not signature_ok else status
    valid = response_status == "active" and all(value == "pass" for value in checks.values())
    record_audit(
        session,
        "profile.validated",
        actor_id=profile.device_id_hash,
        summary="Profile validation checked cryptographic envelope state, TTL, revocation, and audience.",
        metadata={"profile_id": profile.profile_id, "status": response_status, "checks": checks},
    )
    return {"profile_id": profile.profile_id, "valid": valid, "status": response_status, "checks": checks}


def _profile_status(profile: SessionProfile, now: datetime | None) -> str:
    if profile.status == "revoked":
        return "revoked"
    comparison_time = _aware(now or utc_now())
    if _aware(profile.expires_at) <= comparison_time:
        return "expired"
    return "active"


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _timestamp(value: datetime) -> str:
    return _aware(value).isoformat().replace("+00:00", "Z")


def _load_signed_fields(profile: SessionProfile) -> dict[str, Any] | None:
    try:
        loaded = json.loads(profile.signed_envelope_json)
    except ValueError:
        return None
    if not isinstance(loaded, dict):
        return None
    return loaded


def _stored_signature_valid(profile: SessionProfile, signed_fields: dict[str, Any] | None) -> bool:
    if signed_fields is None:
        return False
    if not profile.signature_format_valid or not profile.signature:
        return False
    if profile.signature_hash != _hash_base64(profile.signature):
        return False
    envelope = {**signed_fields, "signature": profile.signature}
    try:
        return verify_envelope_signature(envelope, profile.issuer_public_key)
    except ValueError:
        return False


def _audience_ok(
    session: Session,
    profile: SessionProfile,
    *,
    audience: object,
    expected_audience: str | None,
) -> bool:
    if audience != profile.audience_hash:
        return False
    if expected_audience is not None and expected_audience != audience:
        return False
    device = session.scalar(select(Device).where(Device.device_public_key_hash == profile.audience_hash))
    return device is not None


def _load_list(raw: str) -> list[str]:
    parsed = loads_json(raw)
    if isinstance(parsed, dict) and "items" in parsed and isinstance(parsed["items"], list):
        return [str(item) for item in parsed["items"]]
    try:
        import json

        loaded = json.loads(raw)
    except ValueError:
        return []
    if isinstance(loaded, list):
        return [str(item) for item in loaded]
    return []


def _hash_base64(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _is_base64(value: str) -> bool:
    try:
        base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, ValueError):
        return False
    return True
