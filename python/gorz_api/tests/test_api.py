from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_expected_fields(client: TestClient) -> None:
    response = client.get("/api/gorz/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["safety_mode"] == "local-demo"
    assert body["storage_backend"] == "sqlite"


def test_message_creation_stores_hash_and_not_plaintext(
    client: TestClient, demo_conversation: dict[str, object]
) -> None:
    alice = demo_conversation["alice"]
    conversation = demo_conversation["conversation"]
    assert isinstance(alice, dict)
    assert isinstance(conversation, dict)
    plaintext = "This plaintext must not be stored"

    response = client.post(
        "/api/gorz/messages",
        json={
            "conversation_id": conversation["conversation_id"],
            "sender_id": alice["identity_id"],
            "body": plaintext,
            "scenario": "direct_ok",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["envelope_hash"].startswith("sha256:")
    assert plaintext not in str(body)
    assert body["redacted_preview"].startswith("[redacted demo message")
    assert body["delivery_status"] == "delivered_confirmed"


def test_safety_pause_rejects_message_creation(
    client: TestClient, demo_conversation: dict[str, object]
) -> None:
    alice = demo_conversation["alice"]
    conversation = demo_conversation["conversation"]
    assert isinstance(alice, dict)
    assert isinstance(conversation, dict)

    pause = client.post("/api/gorz/safety/pause")
    assert pause.status_code == 200
    assert pause.json()["pause_enabled"] is True

    response = client.post(
        "/api/gorz/messages",
        json={
            "conversation_id": conversation["conversation_id"],
            "sender_id": alice["identity_id"],
            "body": "blocked while paused",
            "scenario": "blocked",
        },
    )
    assert response.status_code == 423


def test_incident_export_hides_plaintext(client: TestClient, demo_conversation: dict[str, object]) -> None:
    alice = demo_conversation["alice"]
    conversation = demo_conversation["conversation"]
    assert isinstance(alice, dict)
    assert isinstance(conversation, dict)
    plaintext = "incident secret text"

    message = client.post(
        "/api/gorz/messages",
        json={
            "conversation_id": conversation["conversation_id"],
            "sender_id": alice["identity_id"],
            "body": plaintext,
            "scenario": "blocked",
        },
    ).json()
    incident = client.post(f"/api/gorz/incidents/from-message/{message['message_id']}")
    assert incident.status_code == 200
    incident_id = incident.json()["incident_id"]
    download = client.get(f"/api/gorz/incidents/{incident_id}/download")
    assert download.status_code == 200
    assert plaintext not in download.text
    assert message["message_id"] not in download.text


def test_audit_events_exist_after_flow(client: TestClient, demo_conversation: dict[str, object]) -> None:
    response = client.get("/api/gorz/audit")
    assert response.status_code == 200
    event_types = {item["event_type"] for item in response.json()["items"]}
    assert "identity.created" in event_types
    assert "conversation.created" in event_types

