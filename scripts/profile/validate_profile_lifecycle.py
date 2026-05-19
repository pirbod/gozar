#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "profile_api"))

from profile_api.crypto import decrypt_for_device_for_demo_client, generate_device_keypair, verify_envelope_signature


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the local-only profile lifecycle API.")
    parser.add_argument("--api", default="http://127.0.0.1:8095", help="Profile API base URL.")
    args = parser.parse_args()
    try:
        validate(args.api)
    except Exception as exc:
        print(f"profile lifecycle validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def validate(api_base: str) -> None:
    public_key, private_key = generate_device_keypair()
    with httpx.Client(base_url=api_base, timeout=10.0) as client:
        health = _request(client, "GET", "/api/profile/health")
        assert health["status"] == "ok"

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

        paused = _request(client, "POST", "/api/profile/safety/pause")
        assert paused["pause_enabled"] is True
        blocked = client.post(
            "/api/profile/session-profiles",
            json=_profile_request(device["device_id"]),
        )
        assert blocked.status_code == 423
        resumed = _request(client, "POST", "/api/profile/safety/resume")
        assert resumed["pause_enabled"] is False

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


def _profile_request(device_id: str) -> dict[str, Any]:
    return {
        "device_id": device_id,
        "requested_mode": "demo_split_tunnel",
        "risk_tolerance": "low",
        "client_context": {
            "network_type": "wifi",
            "region_hint": "local-demo",
            "previous_failure_class": "none",
        },
    }


def _request(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    data = response.json()
    assert isinstance(data, dict)
    return data


def _assert_audit_redacted(bundle: dict[str, Any], private_key: str) -> None:
    assert bundle["redaction"]["plaintext_profile_removed"] is True
    assert bundle["redaction"]["private_keys_removed"] is True
    raw = json.dumps(bundle, sort_keys=True)
    forbidden = [
        private_key,
        "demo-server-public-key",
        "local-gateway:51820",
        "10.77.0.2/32",
        "encrypted_payload",
        "device_public_key",
        "device_private_key",
    ]
    leaked = [item for item in forbidden if item and item in raw]
    assert not leaked, f"audit export leaked {leaked[0]}"


if __name__ == "__main__":
    main()
