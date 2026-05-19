from __future__ import annotations

import time

from fastapi.testclient import TestClient

from profile_api.profile_issuer import validate_profile
from profile_api.storage import session_factory

from .conftest import profile_request


def test_active_profile_validates(client: TestClient, registered_device: dict[str, object]) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    assert issued.status_code == 200
    validation = client.post(f"/api/profile/session-profiles/{issued.json()['profile_id']}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True
    assert validation.json()["status"] == "active"


def test_revoked_profile_fails(client: TestClient, registered_device: dict[str, object]) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    profile_id = issued.json()["profile_id"]
    revoked = client.post(f"/api/profile/session-profiles/{profile_id}/revoke", json={"reason": "manual_test"})
    assert revoked.status_code == 200
    validation = client.post(f"/api/profile/session-profiles/{profile_id}/validate")
    assert validation.json()["valid"] is False
    assert validation.json()["status"] == "revoked"


def test_expired_profile_fails(client: TestClient, registered_device: dict[str, object]) -> None:
    issued = client.post(
        "/api/profile/session-profiles",
        json=profile_request(str(registered_device["device_id"]), ttl_seconds=1),
    )
    profile_id = issued.json()["profile_id"]
    time.sleep(1.2)
    validation = client.post(f"/api/profile/session-profiles/{profile_id}/validate")
    assert validation.json()["valid"] is False
    assert validation.json()["status"] == "expired"


def test_wrong_audience_fails_validation(client: TestClient, registered_device: dict[str, object]) -> None:
    issued = client.post("/api/profile/session-profiles", json=profile_request(str(registered_device["device_id"])))
    profile_id = issued.json()["profile_id"]
    with session_factory()() as session:
        validation = validate_profile(session, profile_id, expected_audience="pkh_wrong_audience")
    assert validation["valid"] is False
    assert validation["checks"]["audience"] == "fail"
