from __future__ import annotations

from fastapi.testclient import TestClient

from profile_api.config import DEVELOPMENT_ENROLLMENT_TOKEN
from profile_api.crypto import verify_envelope_signature

ENROLLMENT_HEADERS = {"x-gozar-enrollment-token": DEVELOPMENT_ENROLLMENT_TOKEN}
ADMIN_HEADERS = {"x-profile-admin-token": "local-profile-admin-token"}


def _enroll(client: TestClient, public_key: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/enrollment",
        headers=ENROLLMENT_HEADERS,
        json={
            "display_name": "Android test device",
            "app_version": "1.0.0",
            "device_public_key": public_key,
            "wireguard_public_key": public_key,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_enrollment_requires_bootstrap_credential(
    client: TestClient,
    device_keypair: tuple[str, str],
) -> None:
    public_key, _ = device_keypair
    payload = {
        "display_name": "Android test device",
        "app_version": "1.0.0",
        "device_public_key": public_key,
        "wireguard_public_key": public_key,
    }

    assert client.post("/api/v1/enrollment", json=payload).status_code == 401
    assert (
        client.post(
            "/api/v1/enrollment",
            headers={"x-gozar-enrollment-token": "wrong"},
            json=payload,
        ).status_code
        == 401
    )


def test_private_access_lifecycle(
    client: TestClient,
    device_keypair: tuple[str, str],
) -> None:
    public_key, _ = device_keypair
    enrollment = _enroll(client, public_key)
    device_headers = {"authorization": f"Bearer {enrollment['device_token']}"}

    me = client.get("/api/v1/me", headers=device_headers)
    assert me.status_code == 200
    assert me.json()["status"] == "active"
    assert me.json()["approved_routes"] == ["10.88.0.0/24"]

    issued = client.post("/api/v1/access-profiles", headers=device_headers, json={})
    assert issued.status_code == 200, issued.text
    profile = issued.json()
    assert profile["client_address"] == enrollment["assigned_address"]
    assert profile["approved_routes"] == ["10.88.0.0/24"]
    assert profile["approved_services"][0]["host"] == "10.88.0.10"
    assert "0.0.0.0/0" not in profile["approved_routes"]
    assert verify_envelope_signature(profile, profile["issuer_public_key"])

    validation = client.post(
        f"/api/v1/access-profiles/{profile['profile_id']}/validate",
        headers=device_headers,
    )
    assert validation.status_code == 200
    assert validation.json()["valid"] is True

    peers = client.get("/api/v1/admin/wireguard/peers", headers=ADMIN_HEADERS)
    assert peers.status_code == 200
    assert peers.json() == [
        {
            "device_id": enrollment["device_id"],
            "public_key": public_key,
            "allowed_ip": f"{enrollment['assigned_address']}/32",
        }
    ]


def test_device_token_is_rotated_on_reenrollment(
    client: TestClient,
    device_keypair: tuple[str, str],
) -> None:
    public_key, _ = device_keypair
    first = _enroll(client, public_key)
    second = _enroll(client, public_key)

    assert second["device_id"] == first["device_id"]
    assert second["device_token"] != first["device_token"]
    assert client.get(
        "/api/v1/me",
        headers={"authorization": f"Bearer {first['device_token']}"},
    ).status_code == 401
    assert client.get(
        "/api/v1/me",
        headers={"authorization": f"Bearer {second['device_token']}"},
    ).status_code == 200


def test_operator_pause_fails_closed(
    client: TestClient,
    device_keypair: tuple[str, str],
) -> None:
    public_key, _ = device_keypair
    enrollment = _enroll(client, public_key)
    headers = {"authorization": f"Bearer {enrollment['device_token']}"}

    assert client.post("/api/v1/admin/access/pause", headers=ADMIN_HEADERS).status_code == 200
    blocked = client.post("/api/v1/access-profiles", headers=headers, json={})
    assert blocked.status_code == 423
    assert client.post("/api/v1/admin/access/resume", headers=ADMIN_HEADERS).status_code == 200


def test_invalid_device_token_is_rejected(client: TestClient) -> None:
    assert client.get(
        "/api/v1/me",
        headers={"authorization": "Bearer invalid"},
    ).status_code == 401
