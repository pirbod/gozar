from __future__ import annotations

import argparse
import json
import time
from typing import Any

import httpx

from .crypto import decrypt_for_device_for_demo_client, generate_device_keypair, verify_envelope_signature


def run_lifecycle_demo(api_base: str, *, show_demo_payload: bool = False) -> dict[str, Any]:
    public_key, private_key = generate_device_keypair()
    # The demo client private key is held only in this local process for Phase 1 demonstration.
    with httpx.Client(base_url=api_base, timeout=10.0) as client:
        _wait_for_health(client, wait_seconds=60.0)

        registered = client.post(
            "/api/profile/devices/register",
            json={
                "display_name": "Demo Laptop",
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
        registered.raise_for_status()
        device = registered.json()

        issued = client.post(
            "/api/profile/session-profiles",
            json={
                "device_id": device["device_id"],
                "requested_mode": "demo_split_tunnel",
                "risk_tolerance": "low",
                "client_context": {
                    "network_type": "wifi",
                    "region_hint": "local-demo",
                    "previous_failure_class": "none",
                },
            },
        )
        issued.raise_for_status()
        envelope = issued.json()
        signature_ok = verify_envelope_signature(envelope, envelope["issuer_public_key"])
        decrypted = decrypt_for_device_for_demo_client(envelope["encrypted_payload"], private_key)
        summary = {
            "profile_id": envelope["profile_id"],
            "type": envelope["profile_type"],
            "ttl": envelope["ttl_seconds"],
            "routing_mode": decrypted["config"]["routing"]["mode"],
            "safety_notes": envelope["safety_notes"],
            "signature_verified": signature_ok,
        }
        print("Issued signed encrypted profile envelope:")
        print(json.dumps(summary, indent=2, sort_keys=True))
        if show_demo_payload:
            print("WARNING: showing decrypted local demo payload for debugging only.")
            print(json.dumps(decrypted, indent=2, sort_keys=True))

        validation = client.post(f"/api/profile/session-profiles/{envelope['profile_id']}/validate")
        validation.raise_for_status()
        revoked = client.post(
            f"/api/profile/session-profiles/{envelope['profile_id']}/revoke",
            json={"reason": "manual_test"},
        )
        revoked.raise_for_status()
        validation_after_revoke = client.post(f"/api/profile/session-profiles/{envelope['profile_id']}/validate")
        validation_after_revoke.raise_for_status()
        audit_export = client.get("/api/profile/audit/export")
        audit_export.raise_for_status()
        bundle = audit_export.json()
        _assert_redacted(bundle, private_key)

        result = {
            "device": device,
            "summary": summary,
            "validation": validation.json(),
            "revocation": revoked.json(),
            "validation_after_revoke": validation_after_revoke.json(),
            "audit_bundle_id": bundle["bundle_id"],
            "audit_redaction": bundle["redaction"],
        }
        print("Lifecycle complete:")
        print(
            json.dumps(
                {
                    "active_validation": result["validation"]["status"],
                    "post_revoke_validation": result["validation_after_revoke"]["status"],
                    "audit_bundle_id": result["audit_bundle_id"],
                    "audit_redaction": result["audit_redaction"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return result


def _assert_redacted(bundle: dict[str, Any], private_key: str) -> None:
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
    if leaked:
        raise RuntimeError(f"audit export contains non-redacted demo material: {leaked[0]}")


def _wait_for_health(client: httpx.Client, *, wait_seconds: float) -> None:
    deadline = time.monotonic() + wait_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = client.get("/api/profile/health")
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            time.sleep(1.0)
            continue
        if body.get("status") == "ok":
            return
        last_error = RuntimeError(f"unexpected health response: {body}")
        time.sleep(1.0)
    raise TimeoutError(f"Profile API did not become healthy within {wait_seconds:.0f}s: {last_error}")


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local-only profile lifecycle demo.")
    parser.add_argument("--api", default="http://127.0.0.1:8095", help="Profile API base URL.")
    parser.add_argument(
        "--show-demo-payload",
        action="store_true",
        help="Print the decrypted simulated profile payload for local debugging only.",
    )
    args = parser.parse_args()
    run_lifecycle_demo(args.api, show_demo_payload=args.show_demo_payload)


if __name__ == "__main__":
    main()
