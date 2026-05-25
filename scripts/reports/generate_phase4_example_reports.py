#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from phase4_artifact_utils import status_from_report

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_REPORTS = ROOT / "runtime" / "reports"
EXAMPLES_DIR = ROOT / "docs" / "reports" / "examples"

REQUIRED_REPORTS = {
    "production-readiness-report.md": RUNTIME_REPORTS / "production-readiness-report.md",
    "production-readiness-report.json": RUNTIME_REPORTS / "production-readiness-report.json",
    "android-emulator-smoke-report.md": RUNTIME_REPORTS / "android-emulator-smoke-report.md",
    "android-emulator-smoke-report.json": RUNTIME_REPORTS / "android-emulator-smoke-report.json",
    "screenshot-capture-report.md": RUNTIME_REPORTS / "screenshots" / "phase4" / "screenshot-capture-report.md",
    "platform-screenshot-report.md": RUNTIME_REPORTS / "screenshots" / "phase4" / "platform-screenshot-report.md",
    "terraform-check-report.md": RUNTIME_REPORTS / "terraform-check-report.md",
    "terraform-check-report.json": RUNTIME_REPORTS / "terraform-check-report.json",
    "kubernetes-check-report.md": RUNTIME_REPORTS / "kubernetes-check-report.md",
    "kubernetes-check-report.json": RUNTIME_REPORTS / "kubernetes-check-report.json",
    "observability-check-report.md": RUNTIME_REPORTS / "observability-check-report.md",
    "observability-check-report.json": RUNTIME_REPORTS / "observability-check-report.json",
    "siem-detection-report.md": RUNTIME_REPORTS / "siem-detection-report.md",
    "siem-detection-report.json": RUNTIME_REPORTS / "siem-detection-report.json",
    "incident-summary.md": RUNTIME_REPORTS / "incident-summary.md",
    "gorz-android-rc-manifest.md": RUNTIME_REPORTS / "gorz-android-rc-manifest.md",
    "gorz-android-rc-manifest.json": RUNTIME_REPORTS / "gorz-android-rc-manifest.json",
    "phase4-10of10-check.md": RUNTIME_REPORTS / "phase4-10of10-check.md",
    "phase4-10of10-check.json": RUNTIME_REPORTS / "phase4-10of10-check.json",
}

COMMANDS_ATTEMPTED = [
    "make terraform-check",
    "make k8s-check",
    "make observability-check",
    "make detection-check",
    "make incident-summary-demo",
    "make android-emulator-smoke-report",
    "make phase4-screenshot-report",
    "make demo-video-check",
    "make production-readiness-check",
    "make release-candidate-manifest",
    "make phase4-example-reports",
]


def main() -> int:
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat()
    copied: list[str] = []
    missing: list[str] = []

    for target_name, source_path in REQUIRED_REPORTS.items():
        target = EXAMPLES_DIR / target_name
        if source_path.exists():
            shutil.copy2(source_path, target)
            copied.append(target_name)
        elif target_name.endswith(".json"):
            write_missing_json(target, source_path, generated)
            missing.append(target_name)
        else:
            write_missing_markdown(target, source_path, generated)
            missing.append(target_name)

    summary = build_summary(generated, copied, missing)
    (EXAMPLES_DIR / "phase4-check-summary.md").write_text(render_summary_markdown(summary), encoding="utf-8")
    print(f"Phase 4 example reports generated in {EXAMPLES_DIR.relative_to(ROOT)}")
    print(f"Copied: {len(copied)}; missing placeholders: {len(missing)}")
    return 0


def write_missing_json(target: Path, source_path: Path, generated: str) -> None:
    payload = {
        "generatedAt": generated,
        "status": "MISSING",
        "sourcePath": str(source_path.relative_to(ROOT)),
        "detail": "Runtime report was not present when example reports were generated. This is not a successful result.",
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_missing_markdown(target: Path, source_path: Path, generated: str) -> None:
    lines = [
        f"# Missing Runtime Report: {target.name}",
        "",
        f"Generated: {generated}",
        "Status: MISSING",
        "",
        f"Expected source: `{source_path.relative_to(ROOT)}`",
        "",
        "This file exists so the proof trail is complete, but it does not claim a successful runtime result.",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def build_summary(generated: str, copied: list[str], missing: list[str]) -> dict[str, Any]:
    production = load_json(EXAMPLES_DIR / "production-readiness-report.json")
    manifest = load_json(EXAMPLES_DIR / "gorz-android-rc-manifest.json")
    ten = load_json(EXAMPLES_DIR / "phase4-10of10-check.json")
    statuses = {
        "productionReadiness": production.get("summary", {}).get("production_readiness", "UNKNOWN"),
        "productionReadyForRealUse": production.get("summary", {}).get("production_ready_for_real_use", "NO"),
        "controlledReleaseReadiness": production.get("summary", {}).get("controlled_release_readiness", "UNKNOWN"),
        "terraform": status_from_report(EXAMPLES_DIR / "terraform-check-report.json"),
        "kubernetes": status_from_report(EXAMPLES_DIR / "kubernetes-check-report.json"),
        "observability": status_from_report(EXAMPLES_DIR / "observability-check-report.json"),
        "detection": status_from_report(EXAMPLES_DIR / "siem-detection-report.json"),
        "androidEmulatorSmoke": status_from_report(EXAMPLES_DIR / "android-emulator-smoke-report.json"),
        "phase4TenOfTen": ten.get("status", "UNKNOWN"),
        "releaseDecision": manifest.get("releaseDecision", "UNKNOWN"),
    }
    return {
        "generatedAt": generated,
        "toolAvailability": tool_availability(),
        "commandsAttempted": COMMANDS_ATTEMPTED,
        "reportsCopied": copied,
        "reportsMissingAtGeneration": missing,
        "finalReadinessSummary": statuses,
    }


def tool_availability() -> dict[str, str]:
    tools = ["python3", "git", "terraform", "kubectl", "adb", "gradle", "docker", "npm"]
    return {tool: "available" if shutil.which(tool) else "missing" for tool in tools}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 4 Check Summary",
        "",
        f"Generated: {summary['generatedAt']}",
        "",
        "## Tool Availability",
        "",
        "| Tool | Availability |",
        "| --- | --- |",
    ]
    for tool, availability in summary["toolAvailability"].items():
        lines.append(f"| `{tool}` | {availability} |")
    lines.extend(["", "## Commands Attempted", ""])
    lines.extend(f"- `{command}`" for command in summary["commandsAttempted"])
    lines.extend(["", "## Final Readiness Summary", "", "| Area | Status |", "| --- | --- |"])
    for area, status in summary["finalReadinessSummary"].items():
        lines.append(f"| {area} | {status} |")
    lines.extend(["", "## Reports Copied", ""])
    lines.extend(f"- `{name}`" for name in summary["reportsCopied"])
    if not summary["reportsCopied"]:
        lines.append("- none")
    lines.extend(["", "## Missing Runtime Reports At Generation", ""])
    lines.extend(f"- `{name}`" for name in summary["reportsMissingAtGeneration"])
    if not summary["reportsMissingAtGeneration"]:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Missing entries are explicit `MISSING` artifacts, not successful results.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
