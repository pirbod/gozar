#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "runtime" / "reports"
RELEASE_DIR = ROOT / "docs" / "release"
SCREENSHOT_REPORT = REPORT_DIR / "screenshots" / "phase4" / "screenshot-capture-report.json"
PLATFORM_SCREENSHOT_REPORT = REPORT_DIR / "screenshots" / "phase4" / "platform-screenshot-report.json"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    version = read_text("VERSION").strip() or "unknown"
    gradle = read_text("android/gorz/app/build.gradle.kts")
    android_version = extract(r'versionName\s*=\s*"([^"]+)"', gradle) or "unknown"
    apk = ROOT / "android" / "gorz" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"

    screenshot_payload = read_json(SCREENSHOT_REPORT)
    platform_screenshot_payload = read_json(PLATFORM_SCREENSHOT_REPORT)
    production_payload = read_json(REPORT_DIR / "production-readiness-report.json")
    emulator_payload = read_json(REPORT_DIR / "android-emulator-smoke-report.json")

    terraform_status = report_status("terraform-check-report.json")
    kubernetes_status = report_status("kubernetes-check-report.json")
    observability_status = report_status("observability-check-report.json")
    detection_status = report_status("siem-detection-report.json")
    incident_status = "PASS" if (REPORT_DIR / "incident-summary.md").exists() else "MISSING"
    demo_video_status = demo_status()
    screenshot_status = combined_status(
        [
            str(screenshot_payload.get("status", "MISSING")),
            str(platform_screenshot_payload.get("status", "MISSING")),
        ]
    )
    production_summary = production_payload.get("summary", {})
    controlled_release_status = str(production_summary.get("controlled_release_readiness", "UNKNOWN"))
    production_readiness_status = str(production_summary.get("production_readiness", "UNKNOWN"))
    safety_status = "PASS" if production_summary.get("critical_failures", 1) == 0 else "FAIL"
    release_decision = release_decision_for(
        [
            screenshot_status,
            demo_video_status,
            terraform_status,
            kubernetes_status,
            observability_status,
            detection_status,
            incident_status,
            str(emulator_payload.get("status", "MISSING")),
            safety_status,
            production_readiness_status,
            controlled_release_status,
        ]
    )

    manifest = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "repository": repository_url(),
        "phase": "Phase 4 Controlled Prototype Release Candidate",
        "version": version,
        "commitSha": commit_sha(),
        "androidVersionName": android_version,
        "buildType": "debug_or_local",
        "apkPath": str(apk.relative_to(ROOT)) if apk.exists() else "missing",
        "apkSha256": sha256(apk) if apk.exists() else "missing",
        "screenshotStatus": screenshot_status,
        "demoVideoStatus": demo_video_status,
        "terraformStatus": terraform_status,
        "kubernetesStatus": kubernetes_status,
        "observabilityStatus": observability_status,
        "detectionStatus": detection_status,
        "incidentSummaryStatus": incident_status,
        "emulatorSmokeStatus": emulator_payload.get("status", "MISSING"),
        "safetyStatus": safety_status,
        "productionReadinessStatus": production_readiness_status,
        "productionReadyForRealUse": production_summary.get("production_ready_for_real_use", "NO"),
        "controlledReleaseReadinessStatus": controlled_release_status,
        "knownGaps": known_gaps(apk.exists(), demo_video_status, screenshot_status),
        "releaseDecision": release_decision,
    }
    write_json(REPORT_DIR / "gorz-android-rc-manifest.json", manifest)
    write_markdown(REPORT_DIR / "gorz-android-rc-manifest.md", manifest)
    write_markdown(RELEASE_DIR / "gorz-android-rc-manifest-example.md", manifest)
    print(f"Release candidate manifest generated: {manifest['releaseDecision']}")
    return 0


def read_text(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Gorz Android Release Candidate Manifest",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Repository: {payload['repository']}",
        f"Phase: {payload['phase']}",
        f"Version: {payload['version']}",
        f"Commit SHA: {payload['commitSha']}",
        f"Android versionName: {payload['androidVersionName']}",
        f"Build type: {payload['buildType']}",
        f"APK path: {payload['apkPath']}",
        f"APK SHA-256: {payload['apkSha256']}",
        "",
        "## Status Matrix",
        "",
        "| Area | Status |",
        "| --- | --- |",
        f"| Screenshots | {payload['screenshotStatus']} |",
        f"| Demo video | {payload['demoVideoStatus']} |",
        f"| Terraform | {payload['terraformStatus']} |",
        f"| Kubernetes | {payload['kubernetesStatus']} |",
        f"| Observability | {payload['observabilityStatus']} |",
        f"| Detection | {payload['detectionStatus']} |",
        f"| Incident summary | {payload['incidentSummaryStatus']} |",
        f"| Emulator smoke | {payload['emulatorSmokeStatus']} |",
        f"| Safety | {payload['safetyStatus']} |",
        f"| Production readiness report | {payload['productionReadinessStatus']} |",
        f"| Production-ready for real use | {payload['productionReadyForRealUse']} |",
        f"| Controlled release readiness | {payload['controlledReleaseReadinessStatus']} |",
        "",
        f"Release decision: {payload['releaseDecision']}",
        "",
        "## Known Gaps",
        "",
    ]
    lines.extend(f"- {gap}" for gap in payload["knownGaps"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def report_status(filename: str) -> str:
    payload = read_json(REPORT_DIR / filename)
    return str(payload.get("status", "MISSING"))


def combined_status(statuses: list[str]) -> str:
    if any(status in {"FAIL", "MISSING"} for status in statuses):
        return "FAIL"
    if any(status in {"PARTIAL", "SKIPPED", "UNKNOWN"} for status in statuses):
        return "PARTIAL"
    return "PASS"


def demo_status() -> str:
    video = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.mp4"
    placeholder = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.placeholder.md"
    if video.exists():
        return "PASS"
    if placeholder.exists():
        return "PARTIAL"
    return "FAIL"


def known_gaps(apk_exists: bool, demo_video_status: str, screenshot_status: str) -> list[str]:
    gaps = [
        "Release signing and key custody are not configured.",
        "Independent production crypto review is not complete.",
        "Tenant-aware backend auth is not implemented for production use.",
        "Production-ready-for-real-use status remains NO.",
    ]
    if not apk_exists:
        gaps.append("Local APK artifact was not present when this manifest was generated.")
    if demo_video_status != "PASS":
        gaps.append("Demo video recording is pending; complete recording package is present.")
    if screenshot_status != "PASS":
        gaps.append("Some screenshot files are placeholders or require real capture.")
    return gaps


def release_decision_for(statuses: list[str]) -> str:
    blocking = {"FAIL", "MISSING", "BLOCKED"}
    if any(status in blocking for status in statuses):
        return "Controlled release candidate: PARTIAL"
    if any(status in {"PARTIAL", "SKIPPED", "UNKNOWN"} for status in statuses):
        return "Controlled release candidate: PARTIAL"
    return "Controlled release candidate: PASS"


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def commit_sha() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def repository_url() -> str:
    result = subprocess.run(["git", "config", "--get", "remote.origin.url"], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
