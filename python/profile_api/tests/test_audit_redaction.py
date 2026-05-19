from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from profile_api.config import Settings
from profile_api.crypto import generate_device_keypair
from profile_api.main import create_app

from .conftest import profile_request

ADMIN_HEADERS = {"x-profile-admin-token": "local-profile-admin-token"}


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
    client.post(
        f"/api/profile/session-profiles/{profile_id}/revoke",
        headers=ADMIN_HEADERS,
        json={"reason": "manual_test"},
    )
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


def test_default_audit_timestamp_bucket_is_60_minutes(
    client: TestClient,
    registered_device: dict[str, object],
) -> None:
    assert registered_device["device_id"]
    export = client.get("/api/profile/audit/export")

    assert export.status_code == 200
    body = export.json()
    assert body["timestamp_bucket_minutes"] == 60
    assert datetime.fromisoformat(body["entries"][0]["created_at_bucket"]).minute == 0


def test_15_minute_audit_timestamp_bucket(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'profile-test.sqlite3'}",
        audit_timestamp_bucket_minutes=15,
    )
    app = create_app(settings)
    with TestClient(app) as client:
        public_key, _private_key = generate_device_keypair()
        registered = client.post(
            "/api/profile/devices/register",
            json={
                "display_name": "Bucket Test Device",
                "platform": "linux",
                "app_version": "0.1.0",
                "device_public_key": public_key,
                "capabilities": {"supports_wireguard_like": True},
            },
        )
        assert registered.status_code == 200
        export = client.get("/api/profile/audit/export")

    assert export.status_code == 200
    body = export.json()
    assert body["timestamp_bucket_minutes"] == 15
    assert datetime.fromisoformat(body["entries"][0]["created_at_bucket"]).minute in {0, 15, 30, 45}
