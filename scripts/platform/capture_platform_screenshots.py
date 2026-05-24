#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import shutil
from datetime import UTC, datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "vpn-product" / "images" / "phase4"
RUNTIME_DIR = ROOT / "runtime" / "reports" / "screenshots" / "phase4"
sys.path.insert(0, str(ROOT / "scripts" / "reports"))
from phase4_artifact_utils import PLATFORM_SCREENSHOTS, PLACEHOLDER_LABEL, write_placeholder_png, write_screenshot_readme

REQUIRED_SCREENSHOTS = [name for name, _related in PLATFORM_SCREENSHOTS]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    parser.parse_args()

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat()
    previous_placeholder = previous_placeholder_names()
    captured = [name for name in REQUIRED_SCREENSHOTS if (DOCS_DIR / name).exists() and name not in previous_placeholder]
    placeholder: list[str] = []
    for name, related in PLATFORM_SCREENSHOTS:
        path = DOCS_DIR / name
        if path.exists():
            if name in previous_placeholder and name not in placeholder:
                placeholder.append(name)
            continue
        write_placeholder_png(path, "Platform screenshot placeholder", related)
        shutil.copy2(path, RUNTIME_DIR / name)
        placeholder.append(name)
    missing = [name for name in REQUIRED_SCREENSHOTS if not (DOCS_DIR / name).exists()]
    captured = [name for name in captured if name not in placeholder]
    screenshot_records = []
    for name, related in PLATFORM_SCREENSHOTS:
        if name in placeholder:
            screenshot_records.append(
                {
                    "filename": name,
                    "status": "PLACEHOLDER",
                    "captureMethod": PLACEHOLDER_LABEL,
                    "lastUpdated": generated,
                    "related": related,
                }
            )
        elif (DOCS_DIR / name).exists():
            screenshot_records.append(
                {
                    "filename": name,
                    "status": "REAL",
                    "captureMethod": "existing real capture",
                    "lastUpdated": generated,
                    "related": related,
                }
            )
        else:
            screenshot_records.append(
                {
                    "filename": name,
                    "status": "MISSING",
                    "captureMethod": "n/a",
                    "lastUpdated": "n/a",
                    "related": related,
                }
            )
    status = "FAIL" if missing else "PARTIAL" if placeholder else "PASS"
    payload = {
        "generatedAt": generated,
        "status": status,
        "screenshotsCaptured": captured,
        "screenshotsPlaceholder": placeholder,
        "screenshotsMissing": missing,
        "screenshots": screenshot_records,
        "reason": "Platform screenshots require a local browser or desktop capture workflow; placeholders are visibly labelled." if placeholder else "",
        "manualInstructions": [
            "Open GitHub Actions workflow page and capture phase4-github-actions.png.",
            "Run make terraform-check and capture phase4-terraform-validate.png.",
            "Run make k8s-lint and capture phase4-kubernetes-manifests.png.",
            "Open Prometheus rules and capture phase4-prometheus-alerts.png.",
            "Open Grafana dashboard JSON or local Grafana and capture phase4-grafana-dashboard.png.",
            "Open runtime/reports/siem-detection-report.md and capture phase4-siem-detection-report.png.",
            "Open runtime/reports/incident-summary.md and capture phase4-incident-summary.png.",
            "Open runtime/reports/production-readiness-report.md and capture phase4-production-readiness-report.png.",
        ],
    }
    (RUNTIME_DIR / "platform-screenshot-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (RUNTIME_DIR / "platform-screenshot-report.md").write_text(render_markdown(payload), encoding="utf-8")
    write_screenshot_readme(ROOT)
    print(f"Platform screenshot capture status: {status}")
    if payload["reason"]:
        print(payload["reason"])
    return 0


def previous_placeholder_names() -> set[str]:
    report = RUNTIME_DIR / "platform-screenshot-report.json"
    if not report.exists():
        return set()
    payload = json.loads(report.read_text(encoding="utf-8"))
    return {
        str(item.get("filename"))
        for item in payload.get("screenshots", [])
        if str(item.get("status")) == "PLACEHOLDER"
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Phase 4 Platform Screenshot Report",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        f"Reason: {payload['reason'] or 'n/a'}",
        "",
        "## Captured",
        "",
    ]
    lines.extend(f"- {name}" for name in payload["screenshotsCaptured"])
    if not payload["screenshotsCaptured"]:
        lines.append("- none")
    lines.extend(["", "## Placeholder", ""])
    lines.extend(f"- {name}: {PLACEHOLDER_LABEL}" for name in payload["screenshotsPlaceholder"])
    if not payload["screenshotsPlaceholder"]:
        lines.append("- none")
    lines.extend(["", "## Missing", ""])
    lines.extend(f"- {name}" for name in payload["screenshotsMissing"])
    if not payload["screenshotsMissing"]:
        lines.append("- none")
    lines.extend(["", "## Manual Instructions", ""])
    lines.extend(f"- {item}" for item in payload["manualInstructions"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
