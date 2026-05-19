from __future__ import annotations

from typing import Any

POLICY_VERSION = "local-policy-0.1.0"


def select_profile_policy(
    *,
    device: dict[str, Any],
    requested_mode: str,
    risk_tolerance: str,
    client_context: dict[str, Any],
    safety_pause_enabled: bool,
    diagnostics_scenario: str | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    safety_notes = ["local_demo_only", "deterministic_policy_engine"]
    capabilities = device.get("capabilities", {})
    platform = str(device.get("platform", "unknown"))
    previous_failure_class = str(client_context.get("previous_failure_class", "none"))

    if safety_pause_enabled:
        return _deny("safety pause is enabled", "high", 1.0, safety_notes + ["safety_pause_enabled"])

    if diagnostics_scenario == "safety_pause":
        return _deny("diagnostic scenario recommends no profile during safety pause", "high", 0.9, safety_notes)

    if previous_failure_class == "blocked" or diagnostics_scenario == "blocked_local":
        return _deny(
            "blocked scenarios are denied in Phase 1 instead of attempting adaptive routing behavior",
            "high",
            0.95,
            safety_notes + ["blocked_scenario_denied"],
        )

    routing_mode = requested_mode
    if risk_tolerance == "low":
        routing_mode = "demo_split_tunnel"
        reasons.append("low risk tolerance keeps the demo in split tunnel mode")

    if requested_mode == "demo_messaging_only":
        reasons.append("messaging-only request selects the QUIC-like demo profile")
        return _issue("quic_like_demo", routing_mode, "low", 0.9, reasons, safety_notes)

    if previous_failure_class == "degraded" or diagnostics_scenario == "degraded":
        reasons.append("degraded previous failure class selects the QUIC-like demo profile")
        return _issue("quic_like_demo", "messaging_only", "medium", 0.74, reasons, safety_notes)

    if platform == "unknown":
        reasons.append("unknown platform falls back to the QUIC-like demo profile")
        return _issue("quic_like_demo", "messaging_only", "medium", 0.68, reasons, safety_notes)

    if platform in {"android", "ios"} and capabilities.get("supports_wireguard_like"):
        reasons.append("mobile platform supports WireGuard-like demo profiles; real OS integration is future work")
        safety_notes.append("future_os_integration_required")
        return _issue("wireguard_like_demo", routing_mode, "low", 0.86, reasons, safety_notes)

    if capabilities.get("supports_wireguard_like"):
        reasons.append("device supports WireGuard-like demo profiles")
        return _issue("wireguard_like_demo", routing_mode, "low", 0.88, reasons, safety_notes)

    if capabilities.get("supports_quic_like"):
        reasons.append("device supports QUIC-like demo profiles")
        return _issue("quic_like_demo", "messaging_only", "medium", 0.7, reasons, safety_notes)

    return _deny("device capabilities do not support a Phase 1 demo profile", "medium", 0.6, safety_notes)


def _issue(
    selected_profile_type: str,
    routing_mode: str,
    risk: str,
    confidence: float,
    reasons: list[str],
    safety_notes: list[str],
) -> dict[str, Any]:
    return {
        "selected_profile_type": selected_profile_type,
        "decision": "issue",
        "confidence": confidence,
        "risk": risk,
        "routing_mode": routing_mode,
        "reasons": reasons,
        "safety_notes": safety_notes,
        "policy_version": POLICY_VERSION,
    }


def _deny(reason: str, risk: str, confidence: float, safety_notes: list[str]) -> dict[str, Any]:
    return {
        "selected_profile_type": "no_profile",
        "decision": "deny",
        "confidence": confidence,
        "risk": risk,
        "routing_mode": "none",
        "reasons": [reason],
        "safety_notes": safety_notes,
        "policy_version": POLICY_VERSION,
    }

