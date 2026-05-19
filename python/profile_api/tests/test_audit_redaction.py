from __future__ import annotations

import json

from fastapi.testclient import TestClient

from .conftest import profile_request


def test_audit_export_is_redacted(
    client: TestClient,
    registered_device: dict[str, object],
    device_keypair: tuple[str, str],
) -> None:
    _public_key, private_key = device_keypair
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert issued.status_code == 200
    profile_id = issued.json()["profile_id"]
    client.post(f"/api/profile/session-profiles/{profile_id}/validate")
    client.post(f"/api/profile/session-profiles/{profile_id}/revoke", json={"reason": "manual_test"})
    export = client.get("/api/profile/audit/export")
    assert export.status_code == 200
    bundle = export.json()
    assert bundle["redaction"]["private_keys_removed"] is True
    assert bundle["redaction"]["plaintext_profile_removed"] is True
    assert bundle["redaction"]["device_public_keys_removed"] is True
    assert bundle["redaction"]["encrypted_payload_replaced_with_hash"] is True
    assert bundle["redaction"]["signature_replaced_with_hash"] is True
    assert bundle["redaction"]["device_ids_hashed"] is True
    assert bundle["redaction"]["local_endpoints_removed"] is True
    raw = _without_allowed_hash_names(json.dumps(bundle, sort_keys=True))
    assert private_key not in raw
    assert "local-gateway:51820" not in raw
    assert "local-relay:7443" not in raw
    assert "demo-server-public-key" not in raw
    assert "encrypted_payload" not in raw
    assert "signature" not in raw
    assert "device_public_key" not in raw
    assert "private_key" not in raw
    assert "private_key_demo" not in raw
    assert "device_private_key" not in raw
    assert "10.77.0.2/32" not in raw
    assert "10.77.0.1" not in raw
    assert "local-gateway" not in raw
    assert "local-relay" not in raw
    assert "envelope_hash" in json.dumps(bundle, sort_keys=True)
    assert "encrypted_payload_hash" in json.dumps(bundle, sort_keys=True)
    assert "signature_hash" in json.dumps(bundle, sort_keys=True)


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
