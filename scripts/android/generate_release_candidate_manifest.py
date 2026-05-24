#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "runtime" / "reports"
SCREENSHOT_REPORT = ROOT / "runtime" / "reports" / "screenshots" / "phase4" / "screenshot-capture-report.json"
PLATFORM_SCREENSHOT_REPORT = ROOT / "runtime" / "reports" / "screenshots" / "phase4" / "platform-screenshot-report.json"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    version = read_text("VERSION").strip() or "unknown"
    gradle = read_text("android/gorz/app/build.gradle.kts")
    android_version = extract(r'versionName\s*=\s*"([^"]+)"', gradle)
    apk = ROOT / "android" / "gorz" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    screenshot_payload = read_json(SCREENSHOT_REPORT)
    platform_screenshot_payload = read_json(PLATFORM_SCREENSHOT_REPORT)
    production_payload = read_json(ROOT / "runtime" / "reports" / "production-readiness-report.json")
    emulator_payload = read_json(ROOT / "runtime" / "reports" / "android-emulator-smoke-report.json")

    manifest = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "phase": "Phase 4 Controlled Release Readiness",
        "appVersion": version,
        "androidVersionName": android_version or "unknown",
        "buildType": "debug_or_local",
        "commitSha": commit_sha(),
        "apkPath": str(apk.relative_to(ROOT)) if apk.exists() else "missing",
        "apkSha256": sha256(apk) if apk.exists() else "missing",
        "validationReportPath": "docs/vpn-product/phase-4-final-validation-report.md",
        "screenshotReportPath": str(SCREENSHOT_REPORT.relative_to(ROOT)),
        "screenshots": list(screenshot_payload.get("screenshotsCaptured", [])) + list(platform_screenshot_payload.get("screenshotsCaptured", [])),
        "screenshotStatus": screenshot_payload.get("status", "UNKNOWN"),
        "platformScreenshotStatus": platform_screenshot_payload.get("status", "UNKNOWN"),
        "safetyCheckStatus": "see phase4-check output",
        "emulatorSmokeStatus": emulator_payload.get("status", "UNKNOWN"),
        "productionReadinessStatus": production_payload.get("summary", {}).get("production_readiness", "NOT_READY"),
        "knownGaps": [
            "Android Keystore path is experimental and demo storage remains default.",
            "Release signing is not configured in this controlled release candidate manifest.",
            "Tenant auth and independent security review are not complete.",
            "Emulator and screenshot evidence may be SKIPPED when toolchain is unavailable.",
        ],
        "releaseDecision": "Controlled release candidate only; production readiness is NOT_READY.",
    }
    write_json(REPORT_DIR / "gorz-android-rc-manifest.json", manifest)
    write_markdown(REPORT_DIR / "gorz-android-rc-manifest.md", manifest)
    print(f"Release candidate manifest generated: {manifest['releaseDecision']}")
    return 0


def read_text(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# Gorz Android Release Candidate Manifest",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Phase: {payload['phase']}",
        f"App version: {payload['appVersion']}",
        f"Android versionName: {payload['androidVersionName']}",
        f"Build type: {payload['buildType']}",
        f"Commit SHA: {payload['commitSha']}",
        f"APK path: {payload['apkPath']}",
        f"APK SHA-256: {payload['apkSha256']}",
        f"Emulator smoke status: {payload['emulatorSmokeStatus']}",
        f"Android screenshot status: {payload['screenshotStatus']}",
        f"Platform screenshot status: {payload['platformScreenshotStatus']}",
        f"Production readiness status: {payload['productionReadinessStatus']}",
        f"Release decision: {payload['releaseDecision']}",
        "",
        "## Screenshots",
        "",
    ]
    screenshots = payload["screenshots"]
    lines.extend(f"- {shot}" for shot in screenshots)
    if not screenshots:
        lines.append("- none captured")
    lines.extend(["", "## Known Gaps", ""])
    lines.extend(f"- {gap}" for gap in payload["knownGaps"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def commit_sha() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
