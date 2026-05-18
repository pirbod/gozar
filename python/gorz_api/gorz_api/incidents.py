from __future__ import annotations

import hashlib
import ipaddress
import re
from datetime import UTC, datetime, timedelta

from .storage import loads_json

PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")


def redacted_preview(plaintext: str) -> str:
    return f"[redacted demo message length={len(plaintext)}]"


def contains_forbidden_plaintext(record: object, plaintext: str) -> bool:
    if not plaintext:
        return False
    return plaintext in str(record)


def hash_internal_id(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def bucket_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    minute_bucket = (value.minute // 15) * 15
    bucketed = value.replace(minute=minute_bucket, second=0, microsecond=0)
    if value.minute % 15 == 0 and value.second == 0:
        bucketed = value.replace(second=0, microsecond=0)
    if bucketed > value:
        bucketed -= timedelta(minutes=15)
    return bucketed.isoformat().replace("+00:00", "Z")


def sanitize_free_text(value: str) -> str:
    without_phones = PHONE_RE.sub("[redacted phone-like value]", value)
    tokens = without_phones.split()
    sanitized: list[str] = []
    for token in tokens:
        stripped = token.strip(".,;:()[]{}")
        try:
            ipaddress.ip_address(stripped)
            sanitized.append(token.replace(stripped, "[redacted ip-like value]"))
        except ValueError:
            sanitized.append(token)
    return " ".join(sanitized)


def build_incident_record(
    *,
    incident_id: str,
    created_at: datetime,
    message_id: str,
    conversation_id: str,
    message_created_at: datetime,
    classification: str,
    confidence: float,
    envelope_hash: str,
    scenario: str,
    evidence_json: str,
) -> dict[str, object]:
    evidence = loads_json(evidence_json)
    diagnostic = evidence.get("diagnostic", {})
    if not isinstance(diagnostic, dict):
        diagnostic = {}
    explanation = diagnostic.get("explanation", {})
    if not isinstance(explanation, dict):
        explanation = {}

    return {
        "incident_id": incident_id,
        "created_at": bucket_timestamp(created_at),
        "source_type": "message_delivery",
        "message_id": hash_internal_id(message_id),
        "conversation_id": hash_internal_id(conversation_id),
        "claim": (
            "Local demo delivery evidence indicates the message was not simply sent or failed; "
            "status is inferred from multiple simulated evidence layers."
        ),
        "classification": classification,
        "confidence": confidence,
        "layers": {
            "envelope_created": 1.0,
            "encrypted_envelope_accepted_by_local_backend": 1.0,
            "delivery_path_class": evidence.get("delivery_path_class", "unknown"),
            "peer_receipt_simulated": evidence.get("peer_receipt_simulated", False),
        },
        "support": {
            "path_diversity_score": diagnostic.get("path_diversity_score"),
            "source_independence_score": diagnostic.get("source_independence_score"),
            "support_score": diagnostic.get("support_score"),
        },
        "risk": {
            "risk_penalty": diagnostic.get("risk_penalty"),
            "classification": classification,
        },
        "evidence": {
            "scenario": scenario,
            "envelope_hash": envelope_hash,
            "message_created_at_bucket": bucket_timestamp(message_created_at),
            "diagnostic_scores": {
                "dns_score": diagnostic.get("dns_score"),
                "transport_score": diagnostic.get("transport_score"),
                "tls_or_quic_score": diagnostic.get("tls_or_quic_score"),
                "app_delivery_score": diagnostic.get("app_delivery_score"),
            },
            "explanation": explanation,
        },
        "redactions": [
            "Plaintext message body withheld.",
            "Internal message and conversation identifiers hashed.",
            "Timestamps bucketed to 15 minutes.",
            "No real IP addresses, exact locations, or phone numbers included.",
        ],
        "artifacts": [
            {
                "name": "redacted-message-delivery-evidence.json",
                "type": "application/json",
                "contains_plaintext": False,
            }
        ],
        "fusion": {
            "model": "bottleneck-aware local evidence fusion",
            "mandatory_layers": [
                "envelope_score",
                "transport_score",
                "relay_or_peer_score",
                "app_delivery_score",
            ],
            "support_layers": [
                "path_diversity_score",
                "source_independence_score",
                "baseline_consistency_score",
                "safety_score",
            ],
        },
        "safety_notes": [
            "This is a local prototype incident package.",
            "Diagnostics are simulated and were not uploaded automatically.",
            "The package is not proof of production security or real-world delivery.",
        ],
        "analyst_notes": "",
    }
