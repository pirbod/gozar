from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from profile_api.config import Settings
from profile_api.crypto import decrypt_for_device_for_demo_client, verify_envelope_signature
from profile_api.issuer_keys import get_or_create_active_issuer_key
from profile_api.main import create_app
from profile_api.models import SessionProfile
from profile_api.storage import session_factory

from .conftest import profile_request


def test_profile_has_ttl_and_signed_envelope(
    client: TestClient,
    registered_device: dict[str, object],
    device_keypair: tuple[str, str],
) -> None:
    _public_key, private_key = device_keypair
    response = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["ttl_seconds"] == 900
    assert verify_envelope_signature(envelope, envelope["issuer_public_key"])
    decrypted = decrypt_for_device_for_demo_client(envelope["encrypted_payload"], private_key)
    assert decrypted["profile_id"] == envelope["profile_id"]


def test_encrypted_payload_does_not_contain_plaintext_template(
    client: TestClient,
    registered_device: dict[str, object],
) -> None:
    response = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert response.status_code == 200
    encrypted_payload = response.json()["encrypted_payload"]
    assert "local-gateway" not in encrypted_payload
    assert "demo-server-public-key" not in encrypted_payload


def test_metadata_stored_redacted(client: TestClient, registered_device: dict[str, object]) -> None:
    response = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert response.status_code == 200
    profile_id = response.json()["profile_id"]
    with session_factory()() as session:
        profile = session.get(SessionProfile, profile_id)
        assert profile is not None
        stored = json.dumps(
            {
                "profile_id": profile.profile_id,
                "profile_type": profile.profile_type,
                "routing": profile.redacted_routing_mode,
                "envelope_hash": profile.envelope_hash,
                "encrypted_payload_hash": profile.encrypted_payload_hash,
                "signature_hash": profile.signature_hash,
                "issuer_key_id": profile.issuer_key_id,
            }
        )
    assert "local-gateway" not in stored
    assert "demo-server-public-key" not in stored


def test_tampered_stored_envelope_fails_validation(
    client: TestClient,
    registered_device: dict[str, object],
) -> None:
    response = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert response.status_code == 200
    profile_id = response.json()["profile_id"]
    with session_factory()() as session:
        profile = session.get(SessionProfile, profile_id)
        assert profile is not None
        signed_fields = json.loads(profile.signed_envelope_json)
        signed_fields["profile_type"] = "quic_like_demo"
        profile.signed_envelope_json = json.dumps(signed_fields, sort_keys=True, separators=(",", ":"))
        session.commit()
    validation = client.post(f"/api/profile/session-profiles/{profile_id}/validate")
    assert validation.status_code == 200
    body = validation.json()
    assert body["valid"] is False
    assert body["status"] == "invalid_signature"
    assert body["checks"]["signature"] == "fail"
    assert body["checks"]["envelope_hash"] == "fail"


def test_old_profile_validates_after_issuer_rotation(client: TestClient, registered_device: dict[str, object]) -> None:
    first = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert first.status_code == 200
    first_envelope = first.json()
    rotated = client.post("/api/profile/issuer/rotate-demo-key", json={"reason": "manual_test"})
    assert rotated.status_code == 200
    assert rotated.json()["old_key_id"] == first_envelope["issuer_key_id"]
    second = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert second.status_code == 200
    assert second.json()["issuer_key_id"] == rotated.json()["new_key_id"]
    assert second.json()["issuer_key_id"] != first_envelope["issuer_key_id"]
    validation = client.post(f"/api/profile/session-profiles/{first_envelope['profile_id']}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True


def test_issuer_key_persists_across_app_reinitialization(tmp_path: Path) -> None:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'persisted-issuer.sqlite3'}")
    create_app(settings)
    with session_factory()() as session:
        first_key = get_or_create_active_issuer_key(session)
        first_key_id = first_key.key_id
        session.commit()
    create_app(settings)
    with session_factory()() as session:
        second_key = get_or_create_active_issuer_key(session)
        assert second_key.key_id == first_key_id
