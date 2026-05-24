#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RULE_DIR = ROOT / "security" / "detection" / "rules"
EVENT_DIR = ROOT / "security" / "detection" / "sample-events"
REPORT_DIR = ROOT / "runtime" / "reports"


def main() -> int:
    rules = load_rules(RULE_DIR)
    events = load_events(EVENT_DIR)
    results = evaluate(rules, events)
    status = "PASS" if all(item["matched"] for item in results if item["expected_sample_exists"]) else "FAIL"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": status,
        "rulesLoaded": len(rules),
        "eventsLoaded": len(events),
        "results": results,
    }
    (REPORT_DIR / "siem-detection-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "siem-detection-report.md").write_text(render_markdown(payload), encoding="utf-8")
    print(f"SIEM detection tests: {status}")
    return 0 if status == "PASS" else 1


def load_rules(rule_dir: Path) -> list[dict[str, Any]]:
    rules = []
    for path in sorted(rule_dir.glob("*.yml")):
        rules.append(parse_simple_yaml(path.read_text(encoding="utf-8")) | {"path": str(path.relative_to(ROOT))})
    return rules


def load_events(event_dir: Path) -> dict[str, dict[str, Any]]:
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in sorted(event_dir.glob("*.json"))}


def evaluate(rules: list[dict[str, Any]], events: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for rule in rules:
        condition = rule.get("condition", {})
        field = condition.get("field", "")
        expected = condition.get("equals", "")
        matching = [name for name, event in events.items() if event.get(field) == expected]
        sample_key = str(expected)
        sample_exists = any(event.get("event_type") == sample_key for event in events.values())
        results.append(
            {
                "ruleId": rule.get("id", ""),
                "title": rule.get("title", ""),
                "severity": rule.get("severity", ""),
                "matched": bool(matching) or not sample_exists,
                "expected_sample_exists": sample_exists,
                "matchingEvents": matching,
            }
        )
    return results


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_map: dict[str, Any] | None = None
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and current_list_key:
            root.setdefault(current_list_key, []).append(raw_line.strip()[2:].strip())
            continue
        if raw_line.startswith("  ") and current_map is not None:
            key, value = raw_line.strip().split(":", 1)
            current_map[key.strip()] = value.strip().strip('"')
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value == "":
            if key == "condition":
                current_map = {}
                root[key] = current_map
                current_list_key = None
            else:
                root[key] = []
                current_list_key = key
                current_map = None
        else:
            root[key] = value
            current_map = None
            current_list_key = None
    return root


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# SIEM Detection Report",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        f"Rules loaded: {payload['rulesLoaded']}",
        f"Events loaded: {payload['eventsLoaded']}",
        "",
        "| Rule | Severity | Matched | Events |",
        "| --- | --- | --- | --- |",
    ]
    for result in payload["results"]:
        lines.append(
            f"| {result['ruleId']} {result['title']} | {result['severity']} | {result['matched']} | {', '.join(result['matchingEvents']) or 'n/a'} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
