from __future__ import annotations

import json

from fastapi.testclient import TestClient

from profile_api.crypto import decrypt_for_device_for_demo_client, verify_envelope_signature
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
                "signature_hash": profile.signature_hash,
            }
        )
    assert "local-gateway" not in stored
    assert "demo-server-public-key" not in stored

