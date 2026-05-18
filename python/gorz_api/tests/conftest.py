from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from gorz_api.config import Settings
from gorz_api.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient]:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'gorz-test.sqlite3'}")
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def demo_conversation(client: TestClient) -> dict[str, object]:
    alice = client.post(
        "/api/gorz/identities",
        json={"display_name": "Alice Demo", "device_label": "Laptop"},
    )
    bob = client.post(
        "/api/gorz/identities",
        json={"display_name": "Bob Demo", "device_label": "Phone"},
    )
    assert alice.status_code == 200
    assert bob.status_code == 200
    conversation = client.post(
        "/api/gorz/conversations",
        json={
            "title": "Test conversation",
            "participant_ids": [alice.json()["identity_id"], bob.json()["identity_id"]],
        },
    )
    assert conversation.status_code == 200
    return {"alice": alice.json(), "bob": bob.json(), "conversation": conversation.json()}

