from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Literal

Classification = Literal[
    "delivered_confirmed",
    "delivered_probable",
    "degraded_or_partial",
    "not_delivered_or_no_proof",
]


@dataclass(frozen=True, slots=True)
class ConfidenceInputs:
    envelope_score: float
    transport_score: float
    relay_or_peer_score: float
    app_delivery_score: float
    path_diversity_score: float
    source_independence_score: float
    baseline_consistency_score: float
    safety_score: float
    risk_penalty: float

    def as_dict(self) -> dict[str, float]:
        return {
            "envelope_score": self.envelope_score,
            "transport_score": self.transport_score,
            "relay_or_peer_score": self.relay_or_peer_score,
            "app_delivery_score": self.app_delivery_score,
            "path_diversity_score": self.path_diversity_score,
            "source_independence_score": self.source_independence_score,
            "baseline_consistency_score": self.baseline_consistency_score,
            "safety_score": self.safety_score,
            "risk_penalty": self.risk_penalty,
        }


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    confidence: float
    classification: Classification
    mandatory_score: float
    support_score: float
    top_positive_factors: list[str]
    top_negative_factors: list[str]
    human_summary: str
    recommended_user_message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "confidence": self.confidence,
            "classification": self.classification,
            "mandatory_score": self.mandatory_score,
            "support_score": self.support_score,
            "top_positive_factors": self.top_positive_factors,
            "top_negative_factors": self.top_negative_factors,
            "human_summary": self.human_summary,
            "recommended_user_message": self.recommended_user_message,
        }


SCENARIO_INPUTS: dict[str, ConfidenceInputs] = {
    "direct_ok": ConfidenceInputs(1.0, 0.95, 0.90, 0.92, 0.70, 0.70, 0.90, 1.0, 0.00),
    "relay_ok": ConfidenceInputs(1.0, 0.88, 0.86, 0.84, 0.85, 0.76, 0.82, 1.0, 0.02),
    "delayed": ConfidenceInputs(1.0, 0.62, 0.58, 0.45, 0.50, 0.60, 0.55, 1.0, 0.02),
    "degraded": ConfidenceInputs(1.0, 0.50, 0.42, 0.38, 0.45, 0.52, 0.50, 1.0, 0.05),
    "domestic_only": ConfidenceInputs(1.0, 0.45, 0.30, 0.25, 0.20, 0.50, 0.35, 1.0, 0.05),
    "blocked": ConfidenceInputs(1.0, 0.10, 0.05, 0.05, 0.10, 0.40, 0.20, 1.0, 0.05),
    "peer_offline": ConfidenceInputs(1.0, 0.80, 0.20, 0.10, 0.70, 0.60, 0.60, 1.0, 0.01),
}

SCENARIO_LABELS: dict[str, str] = {
    "direct_ok": "Direct local delivery accepted",
    "relay_ok": "Local relay path accepted",
    "delayed": "Delayed local delivery",
    "degraded": "Degraded local path",
    "domestic_only": "Domestic-only simulation",
    "blocked": "Blocked simulation",
    "peer_offline": "Peer offline simulation",
}


def scenario_ids() -> list[str]:
    return list(SCENARIO_INPUTS)


def inputs_for_scenario(scenario: str) -> ConfidenceInputs:
    try:
        return SCENARIO_INPUTS[scenario]
    except KeyError as exc:
        raise ValueError(f"Unknown Gorz diagnostic scenario: {scenario}") from exc


def calculate_confidence(inputs: ConfidenceInputs) -> ConfidenceResult:
    normalized = ConfidenceInputs(**{key: _clamp(value) for key, value in inputs.as_dict().items()})
    mandatory_values = [
        normalized.envelope_score,
        normalized.transport_score,
        normalized.relay_or_peer_score,
        normalized.app_delivery_score,
    ]
    mandatory_score = _geometric_mean(mandatory_values)
    support_score = _weighted_average(
        [
            (normalized.path_diversity_score, 0.30),
            (normalized.source_independence_score, 0.25),
            (normalized.baseline_consistency_score, 0.25),
            (normalized.safety_score, 0.20),
        ]
    )
    confidence = _clamp((mandatory_score**0.7) * (support_score**0.3) * (1 - normalized.risk_penalty))
    classification = classify(confidence, mandatory_values)
    positives, negatives = _factor_lists(normalized)

    return ConfidenceResult(
        confidence=confidence,
        classification=classification,
        mandatory_score=mandatory_score,
        support_score=support_score,
        top_positive_factors=positives,
        top_negative_factors=negatives,
        human_summary=_human_summary(classification),
        recommended_user_message=_recommended_user_message(classification),
    )


def classify(confidence: float, mandatory_scores: list[float] | None = None) -> Classification:
    mandatory_scores = mandatory_scores or []
    if confidence >= 0.85 and all(score >= 0.80 for score in mandatory_scores):
        return "delivered_confirmed"
    if confidence >= 0.65:
        return "delivered_probable"
    if confidence >= 0.40:
        return "degraded_or_partial"
    return "not_delivered_or_no_proof"


def _factor_lists(inputs: ConfidenceInputs) -> tuple[list[str], list[str]]:
    labels = {
        "envelope_score": "encrypted envelope was created locally",
        "transport_score": "local transport evidence",
        "relay_or_peer_score": "peer or relay acceptance evidence",
        "app_delivery_score": "app-level receipt evidence",
        "path_diversity_score": "path diversity evidence",
        "source_independence_score": "source independence evidence",
        "baseline_consistency_score": "baseline consistency",
        "safety_score": "safety controls active",
    }
    scores = inputs.as_dict()
    ordered = sorted(
        ((key, value) for key, value in scores.items() if key != "risk_penalty"),
        key=lambda item: item[1],
        reverse=True,
    )
    positives = [labels[key] for key, value in ordered if value >= 0.75][:3]
    negatives = [labels[key] for key, value in reversed(ordered) if value < 0.55][:3]
    if inputs.risk_penalty > 0:
        negatives.append("risk penalty applied for uncertainty")
    return positives or ["local demo evidence was recorded"], negatives or ["no major bottleneck"]


def _human_summary(classification: Classification) -> str:
    summaries: dict[Classification, str] = {
        "delivered_confirmed": "The local prototype has strong evidence that the encrypted envelope was accepted.",
        "delivered_probable": "The local prototype has enough evidence to treat delivery as probable.",
        "degraded_or_partial": "The local prototype saw partial or degraded evidence and cannot confirm delivery.",
        "not_delivered_or_no_proof": "The local prototype does not have enough evidence to prove delivery.",
    }
    return summaries[classification]


def _recommended_user_message(classification: Classification) -> str:
    messages: dict[Classification, str] = {
        "delivered_confirmed": "Message appears delivered in the local demo.",
        "delivered_probable": "Message probably arrived, but evidence is incomplete.",
        "degraded_or_partial": "Delivery is uncertain. Review evidence before relying on it.",
        "not_delivered_or_no_proof": "No reliable proof of delivery in this simulation.",
    }
    return messages[classification]


def _weighted_average(values: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in values)
    return _clamp(sum(value * weight for value, weight in values) / total_weight)


def _geometric_mean(values: list[float]) -> float:
    if any(value <= 0 for value in values):
        return 0.0
    return prod(values) ** (1 / len(values))


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return min(max(value, minimum), maximum)

