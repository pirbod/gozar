from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_device(client: TestClient, device_keypair: tuple[str, str]) -> None:
    public_key, _private_key = device_keypair
    response = client.post(
        "/api/profile/devices/register",
        json={
            "display_name": "Demo Laptop",
            "platform": "linux",
            "app_version": "0.1.0",
            "device_public_key": public_key,
            "capabilities": {"supports_wireguard_like": True},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["device_id"].startswith("dev_")
    assert body["device_public_key_hash"].startswith("pkh_")
    assert body["registration_status"] == "registered"


def test_duplicate_key_handling(client: TestClient, device_keypair: tuple[str, str]) -> None:
    public_key, _private_key = device_keypair
    payload = {
        "display_name": "Demo Laptop",
        "platform": "linux",
        "app_version": "0.1.0",
        "device_public_key": public_key,
        "capabilities": {"supports_wireguard_like": True},
    }
    first = client.post("/api/profile/devices/register", json=payload)
    second = client.post("/api/profile/devices/register", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["device_id"] == first.json()["device_id"]
    assert second.json()["registration_status"] == "already_registered"


def test_list_devices_omits_raw_public_key(client: TestClient, registered_device: dict[str, object]) -> None:
    response = client.get("/api/profile/devices")
    assert response.status_code == 200
    device = response.json()[0]
    assert device["device_public_key_hash"] == registered_device["device_public_key_hash"]
    assert "device_public_key" not in device

