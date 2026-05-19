from __future__ import annotations

from fastapi.testclient import TestClient

from profile_api.crypto import decrypt_android_local_demo_for_tests, verify_envelope_signature

from .conftest import profile_request

ADMIN_HEADERS = {"x-profile-admin-token": "local-profile-admin-token"}


def test_health(client: TestClient) -> None:
    response = client.get("/api/profile/health")
    assert response.status_code == 200
    assert response.json()["service"] == "profile-api"


def test_full_api_lifecycle(client: TestClient, registered_device: dict[str, object]) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert issued.status_code == 200
    profile_id = issued.json()["profile_id"]

    metadata = client.get(f"/api/profile/session-profiles/{profile_id}")
    assert metadata.status_code == 200
    assert "encrypted_payload" not in metadata.json()

    validation = client.post(f"/api/profile/session-profiles/{profile_id}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True

    revoked = client.post(
        f"/api/profile/session-profiles/{profile_id}/revoke",
        headers=ADMIN_HEADERS,
        json={"reason": "manual_test"},
    )
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"

    export = client.get("/api/profile/audit/export")
    assert export.status_code == 200
    assert export.json()["scope"] == "local_profile_lifecycle_demo"


def test_safety_pause_blocks_issuance(client: TestClient, registered_device: dict[str, object]) -> None:
    pause = client.post("/api/profile/safety/pause", headers=ADMIN_HEADERS)
    assert pause.status_code == 200
    blocked = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert blocked.status_code == 423
    audit_export = client.get("/api/profile/audit/export")
    assert audit_export.status_code == 200
    resume = client.post("/api/profile/safety/resume", headers=ADMIN_HEADERS)
    assert resume.status_code == 200
    assert resume.json()["pause_enabled"] is False


def test_diagnostics_simulate(client: TestClient) -> None:
    response = client.post("/api/profile/diagnostics/simulate", json={"scenario": "blocked_local"})
    assert response.status_code == 200
    body = response.json()
    assert body["profile_recommendation"] == "no_profile"
    assert body["risk"] == "high"


def test_issuer_rotation_endpoint(client: TestClient) -> None:
    response = client.post(
        "/api/profile/issuer/rotate-demo-key",
        headers=ADMIN_HEADERS,
        json={"reason": "manual_test"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["old_key_id"].startswith("issuer_")
    assert body["new_key_id"].startswith("issuer_")
    assert body["active"] is True


def test_admin_token_required_for_sensitive_endpoints(
    client: TestClient,
    registered_device: dict[str, object],
) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert issued.status_code == 200
    profile_id = issued.json()["profile_id"]

    assert client.post("/api/profile/safety/pause").status_code == 401
    assert client.post("/api/profile/safety/pause", headers={"x-profile-admin-token": "wrong"}).status_code == 401
    assert client.post("/api/profile/safety/resume").status_code == 401
    assert client.post("/api/profile/issuer/rotate-demo-key", json={"reason": "manual_test"}).status_code == 401
    assert (
        client.post(f"/api/profile/session-profiles/{profile_id}/revoke", json={"reason": "manual_test"}).status_code
        == 401
    )


def test_profile_revocation_with_admin_token_succeeds(
    client: TestClient,
    registered_device: dict[str, object],
) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert issued.status_code == 200
    profile_id = issued.json()["profile_id"]

    revoked = client.post(
        f"/api/profile/session-profiles/{profile_id}/revoke",
        headers=ADMIN_HEADERS,
        json={"reason": "manual_test"},
    )

    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"


def test_mobile_bootstrap_endpoint(client: TestClient) -> None:
    response = client.get("/api/profile/mobile/bootstrap")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "profile-api"
    assert body["mode"] == "local-demo"
    assert body["android_emulator_api_url_hint"] == "http://10.0.2.2:8095"
    assert "wireguard_like_demo" in body["supported_profile_types"]
    assert "local_demo_only" in body["safety_notes"]


def test_android_local_demo_profile_issuance(
    client: TestClient,
    registered_device: dict[str, object],
    device_keypair: tuple[str, str],
) -> None:
    public_key, _private_key = device_keypair
    request = profile_request(str(registered_device["device_id"]))
    request["envelope_mode"] = "android_local_demo"

    issued = client.post("/api/profile/session-profiles", json=request)

    assert issued.status_code == 200
    envelope = issued.json()
    assert envelope["envelope_mode"] == "android_local_demo"
    assert verify_envelope_signature(envelope, envelope["issuer_public_key"])
    decrypted = decrypt_android_local_demo_for_tests(envelope["encrypted_payload"], public_key)
    assert decrypted["profile_id"] == envelope["profile_id"]
    assert decrypted["audience"] == envelope["audience"]
    assert "local_demo_only" in decrypted["safety_notes"]
