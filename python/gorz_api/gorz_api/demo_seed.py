from __future__ import annotations

from fastapi.testclient import TestClient

from .main import app


def seed_demo_data() -> dict[str, object]:
    client = TestClient(app)
    alice = client.post(
        "/api/gorz/identities",
        json={"display_name": "Ari Local", "device_label": "Laptop"},
    ).json()
    blair = client.post(
        "/api/gorz/identities",
        json={"display_name": "Blair Demo", "device_label": "Phone"},
    ).json()
    conversation = client.post(
        "/api/gorz/conversations",
        json={
            "title": "Local demo conversation",
            "participant_ids": [alice["identity_id"], blair["identity_id"]],
        },
    ).json()
    return {"identities": [alice, blair], "conversation": conversation}

