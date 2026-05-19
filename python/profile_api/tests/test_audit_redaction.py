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
    assert bundle["redaction"]["device_ids_hashed"] is True
    raw = json.dumps(bundle, sort_keys=True)
    assert private_key not in raw
    assert "local-gateway:51820" not in raw
    assert "demo-server-public-key" not in raw
    assert "encrypted_payload" not in raw
    assert "device_public_key" not in raw
    assert "device_private_key" not in raw
