from __future__ import annotations

from datetime import UTC, datetime

from gorz_api.diagnostics import delivery_evidence_for_message
from gorz_api.incidents import build_incident_record
from gorz_api.storage import dumps_json


def test_incident_record_is_redacted() -> None:
    evidence = delivery_evidence_for_message("blocked", "sha256:abc")
    record = build_incident_record(
        incident_id="inc_123",
        created_at=datetime(2026, 5, 18, 12, 37, tzinfo=UTC),
        message_id="msg_secret",
        conversation_id="conv_secret",
        message_created_at=datetime(2026, 5, 18, 12, 36, tzinfo=UTC),
        classification="not_delivered_or_no_proof",
        confidence=0.1,
        envelope_hash="sha256:abc",
        scenario="blocked",
        evidence_json=dumps_json(evidence),
    )

    serialized = str(record)
    assert "msg_secret" not in serialized
    assert "conv_secret" not in serialized
    assert record["message_id"].startswith("sha256:")
    assert record["created_at"] == "2026-05-18T12:30:00Z"
    assert "Plaintext message body withheld." in record["redactions"]

