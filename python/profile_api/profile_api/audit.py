from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import AuditEvent, utc_now
from .safety import SAFETY_NOTES
from .storage import dumps_json, loads_json, new_id

REDACTION = {
    "plaintext_profile_removed": True,
    "private_keys_removed": True,
    "device_public_keys_removed": True,
    "encrypted_payload_replaced_with_hash": True,
    "signature_replaced_with_hash": True,
    "device_ids_hashed": True,
    "timestamps_bucketed": True,
    "local_endpoints_removed": True,
}

SAFE_HASH_KEYS = {
    "device_public_key_hash",
    "encrypted_payload_hash",
    "signature_hash",
    "envelope_hash",
    "profile_id_hash",
    "device_id_hash",
}

SENSITIVE_KEY_FRAGMENTS = (
    "private_key",
    "plaintext",
    "encrypted_payload",
    "signature",
    "device_public_key",
    "raw_device_public_key",
    "payload",
    "config",
    "ip_address",
    "location",
)


def hash_identifier(value: str) -> str:
    if value.startswith("pkh_") or value.startswith("hash_"):
        return value
    return "hash_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def record_audit(
    session: Session,
    event_type: str,
    *,
    actor_id: str | None = None,
    summary: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_id=new_id("audit"),
        event_type=event_type,
        actor_id_hash=hash_identifier(actor_id) if actor_id else None,
        summary=summary,
        metadata_json=dumps_json(redact_metadata(metadata or {})),
    )
    session.add(event)
    return event


def redact_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lowered = key.lower()
            if lowered in SAFE_HASH_KEYS or lowered.endswith("_hash"):
                redacted[key] = redact_metadata(item)
            elif any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
                redacted[_redacted_key_name(lowered)] = "[redacted]"
            elif lowered.endswith("_id") or lowered.endswith("_ids") or lowered == "device_id":
                redacted[key] = _hash_value_or_list(item)
            else:
                redacted[key] = redact_metadata(item)
        return redacted
    if isinstance(value, list):
        return [redact_metadata(item) for item in value]
    return value


def audit_page(session: Session, *, limit: int, offset: int) -> dict[str, Any]:
    total = session.scalar(select(func.count()).select_from(AuditEvent)) or 0
    statement = select(AuditEvent).order_by(AuditEvent.created_at, AuditEvent.event_id).limit(limit).offset(offset)
    events = session.scalars(statement)
    return {
        "items": [audit_event_response(event) for event in events],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


def audit_event_response(event: AuditEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "actor_id_hash": event.actor_id_hash,
        "summary": event.summary,
        "metadata": loads_json(event.metadata_json),
        "created_at": event.created_at,
    }


def export_audit_bundle(session: Session) -> dict[str, Any]:
    events = session.scalars(select(AuditEvent).order_by(AuditEvent.created_at, AuditEvent.event_id)).all()
    return {
        "bundle_id": new_id("bundle"),
        "created_at": utc_now(),
        "scope": "local_profile_lifecycle_demo",
        "entries": [_export_event(event) for event in events],
        "redaction": REDACTION,
        "safety_notes": SAFETY_NOTES,
    }


def _export_event(event: AuditEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "actor_id_hash": event.actor_id_hash,
        "summary": event.summary,
        "metadata": loads_json(event.metadata_json),
        "created_at_bucket": _bucket_timestamp(event.created_at),
    }


def _bucket_timestamp(value: datetime) -> str:
    bucket = value.replace(minute=0, second=0, microsecond=0)
    return bucket.isoformat()


def _hash_value_or_list(value: Any) -> Any:
    if isinstance(value, list):
        return [hash_identifier(str(item)) for item in value]
    return hash_identifier(str(value))


def _redacted_key_name(lowered_key: str) -> str:
    if "private_key" in lowered_key:
        return "redacted_key_material"
    if lowered_key == "signature":
        return "redacted_crypto_check"
    if "device_public_key" in lowered_key or "raw_device_public_key" in lowered_key:
        return "redacted_device_key"
    if "plaintext" in lowered_key:
        return "redacted_plaintext"
    if "payload" in lowered_key or "config" in lowered_key:
        return "redacted_profile_material"
    if "ip_address" in lowered_key or "location" in lowered_key:
        return "redacted_network_context"
    return "redacted_field"
