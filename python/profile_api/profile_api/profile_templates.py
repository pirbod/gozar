from __future__ import annotations

from copy import deepcopy
from typing import Any

WIREGUARD_LIKE_DEMO = {
    "kind": "wireguard_like_demo",
    "interface": {
        "address": "10.77.0.2/32",
        "dns": "10.77.0.1",
    },
    "peer": {
        "public_key": "demo-server-public-key",
        "endpoint": "local-gateway:51820",
        "allowed_ips": ["10.77.0.0/24"],
        "persistent_keepalive": 25,
    },
    "routing": {
        "mode": "demo_split_tunnel",
        "routes": ["10.77.0.0/24"],
    },
    "limitations": [
        "simulated profile",
        "not installed into OS",
        "no public gateway",
    ],
}

QUIC_LIKE_DEMO = {
    "kind": "quic_like_demo",
    "endpoint": "local-relay:7443",
    "alpn": "gorz-demo",
    "routing": {
        "mode": "messaging_only",
    },
    "limitations": [
        "simulated profile",
        "not a real VPN",
        "local Docker only",
    ],
}


def build_profile_payload(
    *,
    profile_id: str,
    profile_type: str,
    routing_mode: str,
    issued_at: str,
    expires_at: str,
    ttl_seconds: int,
    audience: str,
    policy_version: str,
    policy_reasons: list[str],
    safety_notes: list[str],
) -> dict[str, Any]:
    template = _template(profile_type)
    template["routing"]["mode"] = _template_routing_mode(profile_type, routing_mode)
    return {
        "profile_id": profile_id,
        "profile_type": profile_type,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "ttl_seconds": ttl_seconds,
        "audience": audience,
        "policy_version": policy_version,
        "policy_reasons": policy_reasons,
        "config": template,
        "safety_notes": safety_notes,
    }


def _template(profile_type: str) -> dict[str, Any]:
    if profile_type == "wireguard_like_demo":
        return deepcopy(WIREGUARD_LIKE_DEMO)
    if profile_type == "quic_like_demo":
        return deepcopy(QUIC_LIKE_DEMO)
    raise ValueError(f"unsupported profile type: {profile_type}")


def _template_routing_mode(profile_type: str, routing_mode: str) -> str:
    if profile_type == "quic_like_demo":
        return "messaging_only"
    if routing_mode == "demo_full_tunnel":
        return "demo_full_tunnel"
    return "demo_split_tunnel"

