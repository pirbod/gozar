#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "profile_api"))

from profile_api.crypto import decrypt_for_device_for_demo_client, generate_device_keypair, verify_envelope_signature

ADMIN_TOKEN = os.getenv("PROFILE_ADMIN_TOKEN", "local-profile-admin-token")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the local-only profile lifecycle API.")
    parser.add_argument("--api", default="http://127.0.0.1:8095", help="Profile API base URL.")
    parser.add_argument(
        "--wait-seconds",
        type=float,
        default=60.0,
        help="Seconds to wait for the Profile API health endpoint before running lifecycle checks.",
    )
    args = parser.parse_args()
    try:
        validate(args.api, wait_seconds=args.wait_seconds)
    except Exception as exc:
        print(f"profile lifecycle validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def validate(api_base: str, *, wait_seconds: float = 60.0) -> None:
    public_key, private_key = generate_device_keypair()
    with httpx.Client(base_url=api_base, timeout=10.0) as client:
        _wait_for_health(client, wait_seconds=wait_seconds)

        device = _register_device(client, public_key)
        envelope = _request_profile(client, device["device_id"])
        assert verify_envelope_signature(envelope, envelope["issuer_public_key"])
        decrypted = decrypt_for_device_for_demo_client(envelope["encrypted_payload"], private_key)
        assert decrypted["profile_id"] == envelope["profile_id"]
        assert decrypted["config"]["kind"] == envelope["profile_type"]
        assert "local-gateway:51820" not in json.dumps(envelope)

        active = _request(client, "POST", f"/api/profile/session-profiles/{envelope['profile_id']}/validate")
        assert active["valid"] is True
        assert active["status"] == "active"

        revoked = _request(
            client,
            "POST",
            f"/api/profile/session-profiles/{envelope['profile_id']}/revoke",
            headers=_admin_headers(),
            json={"reason": "manual_test"},
        )
        assert revoked["status"] == "revoked"
        revoked_validation = _request(client, "POST", f"/api/profile/session-profiles/{envelope['profile_id']}/validate")
        assert revoked_validation["valid"] is False
        assert revoked_validation["status"] == "revoked"

        short_lived = _request_profile(client, device["device_id"], ttl_seconds=1)
        time.sleep(1.2)
        expired = _request(client, "POST", f"/api/profile/session-profiles/{short_lived['profile_id']}/validate")
        assert expired["valid"] is False
        assert expired["status"] == "expired"

        paused = _request(client, "POST", "/api/profile/safety/pause", headers=_admin_headers())
        assert paused["pause_enabled"] is True
        blocked = client.post(
            "/api/profile/session-profiles",
            json=_profile_request(device["device_id"]),
        )
        assert blocked.status_code == 423
        resumed = _request(client, "POST", "/api/profile/safety/resume", headers=_admin_headers())
        assert resumed["pause_enabled"] is False
        blocked_scenario = client.post(
            "/api/profile/session-profiles",
            json=_profile_request(device["device_id"], previous_failure_class="blocked_local"),
        )
        assert blocked_scenario.status_code == 400
        blocked_detail = blocked_scenario.json()["detail"]
        assert blocked_detail["decision"] == "deny"
        assert blocked_detail["selected_profile_type"] == "no_profile"

        audit_bundle = _request(client, "GET", "/api/profile/audit/export")
        _assert_audit_redacted(audit_bundle, private_key)
    print("profile lifecycle validation passed")


def _register_device(client: httpx.Client, public_key: str) -> dict[str, Any]:
    return _request(
        client,
        "POST",
        "/api/profile/devices/register",
        json={
            "display_name": "Validation Laptop",
            "platform": "linux",
            "app_version": "0.1.0",
            "device_public_key": public_key,
            "capabilities": {
                "supports_wireguard_like": True,
                "supports_quic_like": True,
                "supports_split_tunnel_demo": True,
            },
        },
    )


def _request_profile(client: httpx.Client, device_id: str, ttl_seconds: int | None = None) -> dict[str, Any]:
    body = _profile_request(device_id)
    if ttl_seconds is not None:
        body["ttl_seconds"] = ttl_seconds
    return _request(client, "POST", "/api/profile/session-profiles", json=body)


def _profile_request(device_id: str, *, previous_failure_class: str = "none") -> dict[str, Any]:
    return {
        "device_id": device_id,
        "requested_mode": "demo_split_tunnel",
        "risk_tolerance": "low",
        "client_context": {
            "network_type": "wifi",
            "region_hint": "local-demo",
            "previous_failure_class": previous_failure_class,
        },
    }


def _request(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    data = response.json()
    assert isinstance(data, dict)
    return data


def _admin_headers() -> dict[str, str]:
    return {"x-profile-admin-token": ADMIN_TOKEN}


def _wait_for_health(client: httpx.Client, *, wait_seconds: float) -> None:
    deadline = time.monotonic() + wait_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            health = _request(client, "GET", "/api/profile/health")
        except (httpx.HTTPError, AssertionError) as exc:
            last_error = exc
            time.sleep(1.0)
            continue
        if health.get("status") == "ok":
            return
        last_error = RuntimeError(f"unexpected health response: {health}")
        time.sleep(1.0)
    raise TimeoutError(f"Profile API did not become healthy within {wait_seconds:.0f}s: {last_error}")


def _assert_audit_redacted(bundle: dict[str, Any], private_key: str) -> None:
    assert bundle["redaction"]["plaintext_profile_removed"] is True
    assert bundle["redaction"]["private_keys_removed"] is True
    assert bundle["redaction"]["device_public_keys_removed"] is True
    assert bundle["redaction"]["encrypted_payload_replaced_with_hash"] is True
    assert bundle["redaction"]["signature_replaced_with_hash"] is True
    assert bundle["redaction"]["local_endpoints_removed"] is True
    raw = _without_allowed_hash_names(json.dumps(bundle, sort_keys=True))
    forbidden = [
        private_key,
        "demo-server-public-key",
        "local-gateway:51820",
        "local-relay:7443",
        "10.77.0.2/32",
        "10.77.0.1",
        "encrypted_payload",
        "signature",
        "device_public_key",
        "private_key",
        "private_key_demo",
        "device_private_key",
        "local-gateway",
        "local-relay",
    ]
    leaked = [item for item in forbidden if item and item in raw]
    assert not leaked, f"audit export leaked {leaked[0]}"


def _without_allowed_hash_names(raw: str) -> str:
    allowed = [
        "device_public_key_hash",
        "device_public_keys_removed",
        "encrypted_payload_hash",
        "encrypted_payload_replaced_with_hash",
        "private_keys_removed",
        "signature_hash",
        "signature_replaced_with_hash",
    ]
    sanitized = raw
    for value in allowed:
        sanitized = sanitized.replace(value, "")
    return sanitized


if __name__ == "__main__":
    main()
