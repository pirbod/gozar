#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "vpn-product" / "images" / "phase4"
RUNTIME_DIR = ROOT / "runtime" / "reports" / "screenshots" / "phase4"

PLATFORM_SCREENSHOTS = [
    "phase4-github-actions.png",
    "phase4-terraform-validate.png",
    "phase4-kubernetes-manifests.png",
    "phase4-prometheus-alerts.png",
    "phase4-grafana-dashboard.png",
    "phase4-siem-detection-report.png",
    "phase4-incident-summary.png",
    "phase4-production-readiness-report.png",
]


def main() -> int:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    captured = [name for name in PLATFORM_SCREENSHOTS if (DOCS_DIR / name).exists()]
    missing = [name for name in PLATFORM_SCREENSHOTS if name not in captured]
    status = "PASS" if not missing else "SKIPPED" if not captured else "PARTIAL"
    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": status,
        "screenshotsCaptured": captured,
        "screenshotsMissing": missing,
        "reason": "Platform screenshots require a local browser or desktop capture workflow." if missing else "",
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
    print(f"Platform screenshot capture status: {status}")
    if payload["reason"]:
        print(payload["reason"])
    return 0


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
    lines.extend(["", "## Missing", ""])
    lines.extend(f"- {name}" for name in payload["screenshotsMissing"])
    if not payload["screenshotsMissing"]:
        lines.append("- none")
    lines.extend(["", "## Manual Instructions", ""])
    lines.extend(f"- {item}" for item in payload["manualInstructions"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
