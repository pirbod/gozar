from __future__ import annotations

import pytest

from gorz_api.confidence import ConfidenceInputs, calculate_confidence, inputs_for_scenario


@pytest.mark.parametrize(
    ("scenario", "classification"),
        [
            ("direct_ok", "delivered_confirmed"),
            ("relay_ok", "delivered_confirmed"),
            ("delayed", "degraded_or_partial"),
            ("degraded", "degraded_or_partial"),
            ("domestic_only", "degraded_or_partial"),
            ("blocked", "not_delivered_or_no_proof"),
            ("peer_offline", "degraded_or_partial"),
    ],
)
def test_scenarios_map_to_expected_classifications(scenario: str, classification: str) -> None:
    result = calculate_confidence(inputs_for_scenario(scenario))
    assert result.classification == classification
    assert 0 <= result.confidence <= 1


def test_confirmed_requires_all_mandatory_scores() -> None:
    result = calculate_confidence(
        ConfidenceInputs(
            envelope_score=1.0,
            transport_score=0.95,
            relay_or_peer_score=0.92,
            app_delivery_score=0.79,
            path_diversity_score=1.0,
            source_independence_score=1.0,
            baseline_consistency_score=1.0,
            safety_score=1.0,
            risk_penalty=0.0,
        )
    )
    assert result.confidence >= 0.65
    assert result.classification == "delivered_probable"
