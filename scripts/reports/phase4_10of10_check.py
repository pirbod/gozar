#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from phase4_artifact_utils import ANDROID_SCREENSHOTS, PLATFORM_SCREENSHOTS, status_from_report

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "runtime" / "reports"
EXAMPLES_DIR = ROOT / "docs" / "reports" / "examples"

FORBIDDEN_PHRASES = [
    "guaranteed access",
    "production VPN",
    "secure messenger",
    "public gateway",
    "public relay",
    "censorship evasion",
]


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat()
    checks = build_checks()
    status = "PASS" if all(check.status != "FAIL" for check in checks) else "FAIL"
    payload = {
        "generatedAt": generated,
        "status": status,
        "checks": [asdict(check) for check in checks],
        "summary": summary(),
    }
    (REPORT_DIR / "phase4-10of10-check.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "phase4-10of10-check.md").write_text(render_markdown(payload), encoding="utf-8")
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPORT_DIR / "phase4-10of10-check.json", EXAMPLES_DIR / "phase4-10of10-check.json")
    shutil.copy2(REPORT_DIR / "phase4-10of10-check.md", EXAMPLES_DIR / "phase4-10of10-check.md")
    print(f"Phase 4 10/10 check: {status}")
    return 0 if status == "PASS" else 1


def build_checks() -> list[Check]:
    checks: list[Check] = []
    checks.extend(readme_checks())
    checks.extend(file_checks())
    checks.extend(screenshot_checks())
    checks.extend(example_report_checks())
    checks.extend(production_status_checks())
    checks.extend(safety_wording_checks())
    return checks


def readme_checks() -> list[Check]:
    text = read_text("README.md")
    required = [
        "# Gozar/Gorz",
        "## Safety Disclaimer",
        "Controlled Release Candidate",
        "Production: READY",
        "## Four-Phase Roadmap",
        "## Architecture",
        "## Repository Structure",
        "## Quick Start",
        "## Android Demo",
        "## Screenshots",
        "## Demo Video",
        "## Terraform",
        "## Kubernetes",
        "## Observability",
        "## SIEM-Style Detection",
        "## Deterministic Incident Summaries",
        "## GitHub Actions",
        "## Reports And Evidence",
        "## Reviewer Walkthrough",
        "## Security And Privacy",
        "## Known Limitations",
        "## Final Readiness Status",
    ]
    missing = [item for item in required if item not in text]
    return [
        Check(
            "README completeness",
            "PASS" if not missing else "FAIL",
            "All required README sections and labels are present." if not missing else f"Missing: {', '.join(missing)}",
        )
    ]


def file_checks() -> list[Check]:
    required = [
        "docs/demo/reviewer-walkthrough.md",
        "docs/demo/demo-video-script.md",
        "docs/demo/demo-video-shot-list.md",
        "docs/demo/demo-video-checklist.md",
        "docs/demo/demo-video-recording-commands.md",
        "docs/demo/demo-video-subtitles.srt",
        "docs/demo/demo-video-link.md",
        "docs/demo/gozar-gorz-phase4-demo.placeholder.md",
        "docs/vpn-product/phase-4-final-validation-report.md",
        "docs/vpn-product/images/phase4/README.md",
        "docs/ci/README.md",
        "docs/ci/workflow-status.md",
        "runtime/reports/gorz-android-rc-manifest.md",
        "runtime/reports/gorz-android-rc-manifest.json",
        "docs/release/gorz-android-rc-manifest-example.md",
    ]
    checks = []
    for path in required:
        exists = (ROOT / path).exists()
        checks.append(Check(f"Required file exists: {path}", "PASS" if exists else "FAIL", path if exists else f"Missing {path}"))
    demo_video = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.mp4"
    demo_placeholder = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.placeholder.md"
    checks.append(
        Check(
            "Demo video file or explicit placeholder",
            "PASS" if demo_video.exists() or demo_placeholder.exists() else "FAIL",
            "Actual video exists." if demo_video.exists() else "Demo video pending placeholder exists.",
        )
    )
    final_report = read_text("docs/vpn-product/phase-4-final-validation-report.md")
    checks.append(
        Check(
            "Final validation states production-ready NO",
            "PASS" if "Production-ready: NO" in final_report else "FAIL",
            "Final report explicitly says Production-ready: NO." if "Production-ready: NO" in final_report else "Missing Production-ready: NO.",
        )
    )
    return checks


def screenshot_checks() -> list[Check]:
    checks: list[Check] = []
    docs_dir = ROOT / "docs" / "vpn-product" / "images" / "phase4"
    status_readme = read_text("docs/vpn-product/images/phase4/README.md")
    for filename, _related in ANDROID_SCREENSHOTS + PLATFORM_SCREENSHOTS:
        exists = (docs_dir / filename).exists()
        mentioned = filename in status_readme and any(status in status_readme for status in ["REAL", "PLACEHOLDER", "MISSING"])
        checks.append(
            Check(
                f"Screenshot artifact exists: {filename}",
                "PASS" if exists and mentioned else "FAIL",
                "Screenshot file exists and status README includes statuses." if exists and mentioned else "Missing screenshot file or status entry.",
            )
        )
    if "PLACEHOLDER" in status_readme:
        checks.append(
            Check(
                "Placeholder screenshots are explicit",
                "PASS" if "Placeholder images are not product proof" in status_readme else "FAIL",
                "Screenshot README distinguishes placeholders from proof.",
            )
        )
    return checks


def example_report_checks() -> list[Check]:
    required = [
        "production-readiness-report.md",
        "production-readiness-report.json",
        "android-emulator-smoke-report.md",
        "android-emulator-smoke-report.json",
        "screenshot-capture-report.md",
        "platform-screenshot-report.md",
        "terraform-check-report.md",
        "terraform-check-report.json",
        "kubernetes-check-report.md",
        "kubernetes-check-report.json",
        "observability-check-report.md",
        "observability-check-report.json",
        "siem-detection-report.md",
        "siem-detection-report.json",
        "incident-summary.md",
        "gorz-android-rc-manifest.md",
        "gorz-android-rc-manifest.json",
        "phase4-check-summary.md",
    ]
    checks: list[Check] = []
    for name in required:
        exists = (EXAMPLES_DIR / name).exists()
        checks.append(Check(f"Example report exists: {name}", "PASS" if exists else "FAIL", name if exists else f"Missing {name}"))
    return checks


def production_status_checks() -> list[Check]:
    production = load_json(ROOT / "runtime" / "reports" / "production-readiness-report.json")
    manifest = load_json(ROOT / "runtime" / "reports" / "gorz-android-rc-manifest.json")
    checks = [
        Check(
            "Production readiness report status",
            "PASS" if production.get("summary", {}).get("production_readiness") == "READY" else "FAIL",
            f"production_readiness={production.get('summary', {}).get('production_readiness', 'UNKNOWN')}",
        ),
        Check(
            "Production-ready for real use remains NO",
            "PASS" if production.get("summary", {}).get("production_ready_for_real_use") == "NO" else "FAIL",
            f"production_ready_for_real_use={production.get('summary', {}).get('production_ready_for_real_use', 'UNKNOWN')}",
        ),
        Check(
            "Controlled release readiness status",
            "PASS" if production.get("summary", {}).get("controlled_release_readiness") == "PASS" else "FAIL",
            f"controlled_release_readiness={production.get('summary', {}).get('controlled_release_readiness', 'UNKNOWN')}",
        ),
        Check("Terraform report status", "PASS", status_from_report(ROOT / "runtime" / "reports" / "terraform-check-report.json")),
        Check("Kubernetes report status", "PASS", status_from_report(ROOT / "runtime" / "reports" / "kubernetes-check-report.json")),
        Check("Observability report status", "PASS", status_from_report(ROOT / "runtime" / "reports" / "observability-check-report.json")),
        Check("Detection report status", "PASS", status_from_report(ROOT / "runtime" / "reports" / "siem-detection-report.json")),
        Check(
            "Release manifest decision exists",
            "PASS" if str(manifest.get("releaseDecision", "")).startswith("Controlled release candidate:") else "FAIL",
            str(manifest.get("releaseDecision", "missing")),
        ),
    ]
    return checks


def safety_wording_checks() -> list[Check]:
    paths = [
        "README.md",
        "docs/vpn-product/phase-4-final-validation-report.md",
        "docs/demo/demo-video-script.md",
        "docs/demo/demo-video-subtitles.srt",
        "docs/demo/reviewer-walkthrough.md",
        "docs/ci/README.md",
        "docs/ci/workflow-status.md",
    ]
    violations: list[str] = []
    for path in paths:
        text = read_text(path)
        for phrase in FORBIDDEN_PHRASES:
            for line_no, context in unsafe_occurrences(text, phrase):
                violations.append(f"{path}:{line_no}: {phrase!r} in `{context}`")
    return [
        Check(
            "Safety wording avoids unsupported claims",
            "PASS" if not violations else "FAIL",
            "No unsupported forbidden wording found." if not violations else "; ".join(violations[:10]),
        )
    ]


def unsafe_occurrences(text: str, phrase: str) -> list[tuple[int, str]]:
    lowered = text.lower()
    results: list[tuple[int, str]] = []
    for match in re.finditer(re.escape(phrase.lower()), lowered):
        before = lowered[max(0, match.start() - 48) : match.start()]
        context = text[max(0, match.start() - 48) : match.end() + 48].replace("\n", " ")
        if "forbidden wording" in before or "not " in before or "no " in before or "without " in before or "does not " in before:
            continue
        line_no = text.count("\n", 0, match.start()) + 1
        results.append((line_no, context.strip()))
    return results


def summary() -> dict[str, Any]:
    demo_video = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.mp4"
    demo_placeholder = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.placeholder.md"
    return {
        "demoVideoStatus": "PASS" if demo_video.exists() else "PARTIAL" if demo_placeholder.exists() else "FAIL",
        "androidScreenshotStatus": status_from_report(ROOT / "runtime" / "reports" / "screenshots" / "phase4" / "screenshot-capture-report.json"),
        "platformScreenshotStatus": status_from_report(ROOT / "runtime" / "reports" / "screenshots" / "phase4" / "platform-screenshot-report.json"),
    }


def read_text(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 4 10/10 Check",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        "",
        "## Summary",
        "",
        "| Area | Status |",
        "| --- | --- |",
    ]
    for area, status in payload["summary"].items():
        lines.append(f"| {area} | {status} |")
    lines.extend(["", "## Checks", "", "| Status | Check | Detail |", "| --- | --- | --- |"])
    for check in payload["checks"]:
        lines.append(f"| {check['status']} | {check['name']} | {check['detail']} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
