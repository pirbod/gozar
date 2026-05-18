from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SafetyState

LIMITATIONS = [
    "Local demo only.",
    "Simulated diagnostics only.",
    "Not production secure.",
    "Not a bypass product.",
    "Not for real sensitive communication.",
    "No public network scanning, bridge discovery, relay discovery, or external probing.",
    "No real IP addresses, exact locations, phone numbers, or plaintext message bodies are retained.",
]


def get_safety_state(session: Session) -> SafetyState:
    state = session.scalar(select(SafetyState).where(SafetyState.state_id == "singleton"))
    if state is None:
        state = SafetyState(state_id="singleton", pause_enabled=False)
        session.add(state)
        session.flush()
    return state


def set_pause(session: Session, enabled: bool) -> SafetyState:
    state = get_safety_state(session)
    state.pause_enabled = enabled
    state.updated_at = datetime.now(UTC).replace(microsecond=0)
    session.add(state)
    return state

