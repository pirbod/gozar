from __future__ import annotations

from profile_api.policy_engine import select_profile_policy


def _device(platform: str = "linux") -> dict[str, object]:
    return {
        "platform": platform,
        "capabilities": {
            "supports_wireguard_like": True,
            "supports_quic_like": True,
            "supports_split_tunnel_demo": True,
        },
    }


def test_normal_request_issues_wireguard_like_demo() -> None:
    decision = select_profile_policy(
        device=_device(),
        requested_mode="demo_split_tunnel",
        risk_tolerance="medium",
        client_context={"previous_failure_class": "none"},
        safety_pause_enabled=False,
    )
    assert decision["decision"] == "issue"
    assert decision["selected_profile_type"] == "wireguard_like_demo"


def test_messaging_request_issues_quic_like_demo() -> None:
    decision = select_profile_policy(
        device=_device(),
        requested_mode="demo_messaging_only",
        risk_tolerance="medium",
        client_context={"previous_failure_class": "none"},
        safety_pause_enabled=False,
    )
    assert decision["selected_profile_type"] == "quic_like_demo"


def test_blocked_previous_failure_denies_profile_in_phase_1() -> None:
    decision = select_profile_policy(
        device=_device(),
        requested_mode="demo_split_tunnel",
        risk_tolerance="medium",
        client_context={"previous_failure_class": "blocked"},
        safety_pause_enabled=False,
    )
    assert decision["decision"] == "deny"
    assert decision["selected_profile_type"] == "no_profile"


def test_safety_pause_denies_profile() -> None:
    decision = select_profile_policy(
        device=_device(),
        requested_mode="demo_split_tunnel",
        risk_tolerance="medium",
        client_context={"previous_failure_class": "none"},
        safety_pause_enabled=True,
    )
    assert decision["decision"] == "deny"
    assert "safety_pause_enabled" in decision["safety_notes"]


def test_low_risk_tolerance_uses_split_tunnel_note() -> None:
    decision = select_profile_policy(
        device=_device(),
        requested_mode="demo_full_tunnel",
        risk_tolerance="low",
        client_context={"previous_failure_class": "none"},
        safety_pause_enabled=False,
    )
    assert decision["routing_mode"] == "demo_split_tunnel"
    assert "split tunnel mode" in " ".join(decision["reasons"])

