#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["deterministic", "ollama-local", "external-api"], default="deterministic")
    args = parser.parse_args()

    if args.mode == "external-api":
        raise SystemExit("external-api mode is not implemented for the controlled release candidate.")
    if args.mode == "ollama-local":
        raise SystemExit("ollama-local mode is optional and disabled by default; use deterministic mode.")

    event_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    event = json.loads(event_path.read_text(encoding="utf-8"))
    summary = deterministic_summary(event, event_path)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Incident summary written to {output_path}")
    return 0


def deterministic_summary(event: dict[str, Any], event_path: Path) -> str:
    event_type = str(event.get("event_type", "unknown_event"))
    component = str(event.get("component", "unknown_component"))
    severity = severity_for(event_type)
    title = title_for(event_type)
    what = what_happened(event)
    action = action_for(event_type)
    generated = datetime.now(UTC).isoformat()
    return "\n".join(
        [
            f"# {title}",
            "",
            f"Generated: {generated}",
            f"Severity: {severity}",
            f"Affected component: {component}",
            "",
            "## What Happened",
            "",
            what,
            "",
            "## Why It Matters",
            "",
            "This event affects controlled release readiness because it touches a safety, validation, evidence, or operations boundary.",
            "",
            "## Safety Boundary Impact",
            "",
            "The event is handled inside the local controlled demo. It does not indicate public traffic forwarding or production security assurance.",
            "",
            "## Recommended Action",
            "",
            action,
            "",
            "## Evidence References",
            "",
            f"- Source event: `{event_path.as_posix()}`",
            "- Detection report: `runtime/reports/siem-detection-report.md`",
            "- Production readiness report: `runtime/reports/production-readiness-report.md`",
            "",
            "## Known Limitations",
            "",
            "This deterministic summary uses redacted event fields only. It is not an external LLM result and should be reviewed by an operator.",
            "",
        ]
    )


def severity_for(event_type: str) -> str:
    if "redaction_failure" in event_type or "route_policy" in event_type:
        return "high"
    if "safety_pause" in event_type or "validation_failure" in event_type:
        return "medium"
    return "low"


def title_for(event_type: str) -> str:
    words = event_type.replace("_", " ").title()
    return f"Incident Summary: {words}"


def what_happened(event: dict[str, Any]) -> str:
    pairs = [
        f"- `{key}`: `{value}`"
        for key, value in sorted(event.items())
        if key not in {"raw_device_id", "raw_session_id", "token", "private_key"}
    ]
    return "\n".join(pairs)


def action_for(event_type: str) -> str:
    if event_type == "route_policy_violation":
        return "Keep connection blocked, preserve redacted evidence, and review route guard changes."
    if event_type == "safety_pause_enabled":
        return "Confirm new sessions remain blocked and record an operator note."
    if event_type == "evidence_redaction_failure":
        return "Stop sharing the export, clear local evidence, and inspect redaction logic."
    return "Review the event, update the audit timeline, and rerun readiness checks."


if __name__ == "__main__":
    raise SystemExit(main())
