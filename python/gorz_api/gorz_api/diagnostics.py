from __future__ import annotations

from .confidence import SCENARIO_LABELS, calculate_confidence, inputs_for_scenario, scenario_ids

SCENARIO_EXPLANATIONS: dict[str, str] = {
    "direct_ok": "A local direct path accepts the envelope and returns simulated peer receipt.",
    "relay_ok": "A local relay class path accepts the envelope with slightly lower transport certainty.",
    "delayed": "The local demo records queueing and delayed receipt evidence.",
    "degraded": "Transport and app delivery evidence are both weak in the local simulation.",
    "domestic_only": "The local demo marks path diversity as low and delivery evidence as partial.",
    "blocked": "The local demo records a failed path with no reliable proof of app delivery.",
    "peer_offline": "Local transport looks available, but peer receipt evidence is weak.",
}


def available_scenarios() -> list[dict[str, str]]:
    return [
        {"id": scenario_id, "label": SCENARIO_LABELS[scenario_id], "explanation": SCENARIO_EXPLANATIONS[scenario_id]}
        for scenario_id in scenario_ids()
    ]


def simulate_scenario(scenario: str) -> dict[str, object]:
    inputs = inputs_for_scenario(scenario)
    result = calculate_confidence(inputs)
    return {
        "scenario": scenario,
        "label": SCENARIO_LABELS[scenario],
        "dns_score": inputs.baseline_consistency_score,
        "transport_score": inputs.transport_score,
        "tls_or_quic_score": min(inputs.envelope_score, inputs.transport_score),
        "app_delivery_score": inputs.app_delivery_score,
        "path_diversity_score": inputs.path_diversity_score,
        "source_independence_score": inputs.source_independence_score,
        "risk_penalty": inputs.risk_penalty,
        "confidence": result.confidence,
        "classification": result.classification,
        "mandatory_score": result.mandatory_score,
        "support_score": result.support_score,
        "explanation": {
            "top_positive_factors": result.top_positive_factors,
            "top_negative_factors": result.top_negative_factors,
            "human_summary": result.human_summary,
            "recommended_user_message": result.recommended_user_message,
            "scenario_summary": SCENARIO_EXPLANATIONS[scenario],
        },
    }


def delivery_evidence_for_message(scenario: str, envelope_hash: str) -> dict[str, object]:
    simulated = simulate_scenario(scenario)
    return {
        "envelope_hash": envelope_hash,
        "scenario": scenario,
        "delivery_path_class": _path_class(scenario),
        "peer_receipt_simulated": scenario in {"direct_ok", "relay_ok", "delayed"},
        "diagnostic": simulated,
        "safety_notes": [
            "Diagnostics are simulated and local-only.",
            "No public network scanning, relay discovery, or external probing was performed.",
        ],
    }


def _path_class(scenario: str) -> str:
    if scenario == "direct_ok":
        return "direct"
    if scenario in {"relay_ok", "delayed"}:
        return "local_relay"
    if scenario == "domestic_only":
        return "domestic_only_simulation"
    if scenario == "blocked":
        return "blocked_simulation"
    if scenario == "peer_offline":
        return "peer_offline_simulation"
    return "degraded_simulation"

