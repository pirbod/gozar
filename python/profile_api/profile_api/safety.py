from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SafetyState, utc_now

LIMITATIONS = [
    "Local-only profile lifecycle demonstration.",
    "Short-lived demo config payloads are not installed into an OS.",
    "No public gateways or public network probing are used.",
    "Simulated WireGuard-like profile content is not a production VPN.",
    "Not production secure and not for real sensitive communication.",
    "Not a circumvention tool.",
]

SAFETY_NOTES = [
    "local_demo_only",
    "not_production_vpn",
    "no_public_gateway",
    "no_external_probing",
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
    state.updated_at = utc_now()
    session.add(state)
    return state


def safety_response(state: SafetyState) -> dict[str, object]:
    return {
        "local_only": True,
        "public_network_probing": False,
        "os_vpn_installation": False,
        "production_vpn": False,
        "relay_discovery": False,
        "external_gateway": False,
        "pause_enabled": state.pause_enabled,
        "limitations": LIMITATIONS,
        "updated_at": state.updated_at,
    }

