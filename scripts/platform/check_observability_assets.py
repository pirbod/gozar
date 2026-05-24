#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "runtime" / "reports"

REQUIRED = [
    "observability/prometheus/prometheus.yml",
    "observability/prometheus/rules/gozar-profile-api-alerts.yml",
    "observability/prometheus/rules/gozar-android-demo-alerts.yml",
    "observability/prometheus/rules/gozar-safety-alerts.yml",
    "observability/grafana/dashboards/gozar-controlled-release-dashboard.json",
    "observability/grafana/dashboards/gozar-security-ops-dashboard.json",
    "observability/grafana/provisioning/datasources.yml",
    "observability/grafana/provisioning/dashboards.yml",
]


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    status = "PASS" if not missing else "FAIL"
    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": status,
        "required": REQUIRED,
        "missing": missing,
    }
    (REPORT_DIR / "observability-check-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Observability Check Report", "", f"Generated: {payload['generatedAt']}", f"Status: {status}", "", "## Missing", ""]
    lines.extend(f"- {path}" for path in missing)
    if not missing:
        lines.append("- none")
    (REPORT_DIR / "observability-check-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Observability check: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
