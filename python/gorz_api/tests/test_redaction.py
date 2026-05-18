from __future__ import annotations

from datetime import UTC, datetime

from gorz_api.incidents import bucket_timestamp, hash_internal_id, redacted_preview, sanitize_free_text


def test_redacted_preview_removes_plaintext() -> None:
    body = "Meet at private location with code 1234"
    preview = redacted_preview(body)
    assert body not in preview
    assert "length=" in preview


def test_export_ids_are_hashed() -> None:
    original = "msg_abc123"
    hashed = hash_internal_id(original)
    assert original not in hashed
    assert hashed.startswith("sha256:")


def test_bucket_timestamp_to_fifteen_minutes() -> None:
    bucketed = bucket_timestamp(datetime(2026, 5, 18, 12, 37, 44, tzinfo=UTC))
    assert bucketed == "2026-05-18T12:30:00Z"


def test_sanitize_free_text_removes_ip_and_phone_like_values() -> None:
    sanitized = sanitize_free_text("host 203.0.113.10 phone +1 202 555 0199")
    assert "203.0.113.10" not in sanitized
    assert "202 555 0199" not in sanitized

