from __future__ import annotations

from sqlalchemy.orm import Session

from .models import AuditEvent
from .storage import dumps_json, new_id


def record_audit(
    session: Session,
    event_type: str,
    *,
    actor_id: str | None = None,
    summary: str,
    metadata: dict[str, object] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_id=new_id("audit"),
        event_type=event_type,
        actor_id=actor_id,
        summary=summary,
        metadata_json=dumps_json(metadata or {}),
    )
    session.add(event)
    return event

