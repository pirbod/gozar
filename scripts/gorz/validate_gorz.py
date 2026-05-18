#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any

import httpx

SCENARIOS = [
    "direct_ok",
    "relay_ok",
    "delayed",
    "degraded",
    "domestic_only",
    "blocked",
    "peer_offline",
]


@dataclass
class CheckSummary:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def ok(self, label: str) -> None:
        self.passed.append(label)

    def fail(self, label: str, reason: str) -> None:
        self.failed.append(f"{label}: {reason}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the local Gorz demo API flow.")
    parser.add_argument("--api", default="http://127.0.0.1:8090", help="Local Gorz API base URL")
    args = parser.parse_args()

    summary = CheckSummary()
    with httpx.Client(base_url=args.api, timeout=10.0) as client:
        try:
            health = client.get("/api/gorz/health")
            health.raise_for_status()
            summary.ok("health")

            alice = post_json(
                client,
                "/api/gorz/identities",
                {"display_name": "Demo Alice", "device_label": "Laptop"},
            )
            bob = post_json(
                client,
                "/api/gorz/identities",
                {"display_name": "Demo Bob", "device_label": "Phone"},
            )
            summary.ok("identities")

            conversation = post_json(
                client,
                "/api/gorz/conversations",
                {
                    "title": "Gorz validation conversation",
                    "participant_ids": [alice["identity_id"], bob["identity_id"]],
                },
            )
            summary.ok("conversation")

            messages: dict[str, dict[str, Any]] = {}
            for scenario in SCENARIOS:
                body = f"validation plaintext for {scenario}"
                message = post_json(
                    client,
                    "/api/gorz/messages",
                    {
                        "conversation_id": conversation["conversation_id"],
                        "sender_id": alice["identity_id"],
                        "body": body,
                        "scenario": scenario,
                    },
                )
                if body in json.dumps(message):
                    raise AssertionError(f"plaintext leaked in message response for {scenario}")
                if not str(message["envelope_hash"]).startswith("sha256:"):
                    raise AssertionError(f"missing envelope hash for {scenario}")
                messages[scenario] = message
            summary.ok("scenario messages")

            for scenario in ("blocked", "domestic_only"):
                incident = post_json(
                    client,
                    f"/api/gorz/incidents/from-message/{messages[scenario]['message_id']}",
                    None,
                )
                download = client.get(f"/api/gorz/incidents/{incident['incident_id']}/download")
                download.raise_for_status()
                exported = download.text
                if "validation plaintext" in exported:
                    raise AssertionError(f"plaintext leaked in {scenario} incident export")
                if messages[scenario]["message_id"] in exported:
                    raise AssertionError(f"internal message id leaked in {scenario} incident export")
            summary.ok("incident exports")

            audit = client.get("/api/gorz/audit")
            audit.raise_for_status()
            event_types = {item["event_type"] for item in audit.json()["items"]}
            required = {
                "identity.created",
                "conversation.created",
                "message.envelope_created",
                "message.delivery_scored",
                "incident.generated",
            }
            missing = sorted(required - event_types)
            if missing:
                raise AssertionError(f"missing audit events: {', '.join(missing)}")
            summary.ok("audit")
        except Exception as exc:
            summary.fail("validation", str(exc))

    print_summary(summary)
    return 1 if summary.failed else 0


def post_json(client: httpx.Client, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    response = client.post(path, json=body) if body is not None else client.post(path)
    response.raise_for_status()
    parsed = response.json()
    if not isinstance(parsed, dict):
        raise TypeError(f"Expected object response from {path}")
    return parsed


def print_summary(summary: CheckSummary) -> None:
    print("Gorz validation summary")
    for item in summary.passed:
        print(f"PASS {item}")
    for item in summary.failed:
        print(f"FAIL {item}")


if __name__ == "__main__":
    sys.exit(main())

