from __future__ import annotations

from fastapi.testclient import TestClient

from .conftest import profile_request


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

    revoked = client.post(f"/api/profile/session-profiles/{profile_id}/revoke", json={"reason": "manual_test"})
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"

    export = client.get("/api/profile/audit/export")
    assert export.status_code == 200
    assert export.json()["scope"] == "local_profile_lifecycle_demo"


def test_safety_pause_blocks_issuance(client: TestClient, registered_device: dict[str, object]) -> None:
    pause = client.post("/api/profile/safety/pause")
    assert pause.status_code == 200
    blocked = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert blocked.status_code == 423
    audit_export = client.get("/api/profile/audit/export")
    assert audit_export.status_code == 200
    resume = client.post("/api/profile/safety/resume")
    assert resume.status_code == 200
    assert resume.json()["pause_enabled"] is False


def test_diagnostics_simulate(client: TestClient) -> None:
    response = client.post("/api/profile/diagnostics/simulate", json={"scenario": "blocked_local"})
    assert response.status_code == 200
    body = response.json()
    assert body["profile_recommendation"] == "no_profile"
    assert body["risk"] == "high"


def test_issuer_rotation_endpoint(client: TestClient) -> None:
    response = client.post("/api/profile/issuer/rotate-demo-key", json={"reason": "manual_test"})
    assert response.status_code == 200
    body = response.json()
    assert body["old_key_id"].startswith("issuer_")
    assert body["new_key_id"].startswith("issuer_")
    assert body["active"] is True
