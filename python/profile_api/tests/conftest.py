from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from profile_api.config import Settings
from profile_api.crypto import generate_device_keypair
from profile_api.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient]:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'profile-test.sqlite3'}", default_ttl_seconds=900)
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def device_keypair() -> tuple[str, str]:
    return generate_device_keypair()


@pytest.fixture()
def registered_device(client: TestClient, device_keypair: tuple[str, str]) -> dict[str, object]:
    public_key, _private_key = device_keypair
    response = client.post(
        "/api/profile/devices/register",
        json={
            "display_name": "Test Laptop",
            "platform": "linux",
            "app_version": "0.1.0",
            "device_public_key": public_key,
            "capabilities": {
                "supports_wireguard_like": True,
                "supports_quic_like": True,
                "supports_split_tunnel_demo": True,
            },
        },
    )
    assert response.status_code == 200
    return response.json()


def profile_request(device_id: str, ttl_seconds: int | None = None) -> dict[str, object]:
    body: dict[str, object] = {
        "device_id": device_id,
        "requested_mode": "demo_split_tunnel",
        "risk_tolerance": "low",
        "client_context": {
            "network_type": "wifi",
            "region_hint": "local-demo",
            "previous_failure_class": "none",
        },
    }
    if ttl_seconds is not None:
        body["ttl_seconds"] = ttl_seconds
    return body

