from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from .audit import record_audit
from .policy_engine import select_profile_policy
from .safety import SAFETY_NOTES, get_safety_state


def simulate_diagnostic(session: Session, scenario: str) -> dict[str, Any]:
    state = get_safety_state(session)
    context = {
        "healthy": {"previous_failure_class": "none"},
        "degraded": {"previous_failure_class": "degraded"},
        "blocked_local": {"previous_failure_class": "blocked"},
        "expired_profile": {"previous_failure_class": "timeout"},
        "revoked_profile": {"previous_failure_class": "timeout"},
        "safety_pause": {"previous_failure_class": "none"},
    }[scenario]
    decision = select_profile_policy(
        device={
            "platform": "linux",
            "capabilities": {
                "supports_wireguard_like": True,
                "supports_quic_like": True,
                "supports_split_tunnel_demo": True,
            },
        },
        requested_mode="demo_split_tunnel",
        risk_tolerance="low",
        client_context={"network_type": "wifi", "region_hint": "local-demo", **context},
        safety_pause_enabled=state.pause_enabled or scenario == "safety_pause",
        diagnostics_scenario=scenario,
    )
    explanation = _explanation(scenario, decision)
    result = {
        "scenario": scenario,
        "profile_recommendation": decision["selected_profile_type"],
        "confidence": decision["confidence"],
        "risk": decision["risk"],
        "explanation": explanation,
        "safety_notes": sorted(set(SAFETY_NOTES + list(decision["safety_notes"]))),
    }
    record_audit(
        session,
        "diagnostic.simulated",
        summary="Privacy-preserving local diagnostic scenario simulated.",
        metadata={"scenario": scenario, "profile_recommendation": decision["selected_profile_type"]},
    )
    return result


def _explanation(scenario: str, decision: dict[str, Any]) -> str:
    if scenario == "blocked_local":
        return "Phase 1 denies blocked local scenarios and does not attempt routing workaround behavior."
    if scenario == "expired_profile":
        return "The deterministic policy recommends requesting a fresh short-lived demo config."
    if scenario == "revoked_profile":
        return "The deterministic policy recommends no reuse of revoked demo profile material."
    if scenario == "safety_pause":
        return "Safety pause is active, so new profile issuance is disabled."
    reasons = decision.get("reasons") or ["local diagnostic completed"]
    return str(reasons[0])
