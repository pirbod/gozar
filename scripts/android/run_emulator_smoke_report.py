#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANDROID_DIR = ROOT / "android" / "gorz"
REPORT_DIR = ROOT / "runtime" / "reports"

EMULATOR_INFRASTRUCTURE_FAILURE_PATTERNS = [
    "EmulatorSnapshotCannotCreatedException",
    "Gradle was not able to complete device setup",
    "emulator failed to open the managed device",
    "emulator closed unexpectedly",
    "Unable to create Android virtual device",
    "No space left on device",
    "KVM is required",
    "x86 emulation currently requires hardware acceleration",
]


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if os.environ.get("GORZ_EMULATOR_REPORT_ONLY") == "1":
        payload = payload_for("SKIPPED", "Report-only mode did not attempt emulator execution.", "", 0)
        write_reports(payload)
        print("Android emulator smoke status: SKIPPED")
        return 0

    gradlew = ANDROID_DIR / "gradlew"
    if not gradlew.exists():
        payload = payload_for("SKIPPED", "Gradle wrapper is missing.", "", 127)
        write_reports(payload)
        print("Android emulator smoke status: SKIPPED")
        return 0

    if not android_sdk_available():
        payload = payload_for("SKIPPED", "Android SDK is not available in this shell.", "", 127)
        write_reports(payload)
        print("Android emulator smoke status: SKIPPED")
        return 0

    command = ["./gradlew", "pixel2api30DebugAndroidTest"]
    result = subprocess.run(command, cwd=ANDROID_DIR, text=True, capture_output=True, check=False)
    output = result.stdout + "\n" + result.stderr
    if result.returncode == 0:
        status = "PASS"
        detail = "Managed-device smoke tests completed."
        exit_code = 0
    elif is_emulator_infrastructure_failure(output):
        status = "SKIPPED"
        detail = "Managed-device smoke could not run because the CI emulator infrastructure failed during device setup."
        exit_code = 0
    else:
        status = "FAIL"
        detail = "Managed-device smoke tests failed after emulator execution started."
        exit_code = result.returncode
    payload = payload_for(status, detail, output, result.returncode)
    write_reports(payload)
    print(f"Android emulator smoke status: {status}")
    return exit_code


def is_emulator_infrastructure_failure(output: str) -> bool:
    lowered = output.lower()
    return any(pattern.lower() in lowered for pattern in EMULATOR_INFRASTRUCTURE_FAILURE_PATTERNS)


def payload_for(status: str, detail: str, output: str, exit_code: int) -> dict[str, object]:
    return {
        "generatedAt": datetime.now(UTC).isoformat(),
        "status": status,
        "detail": detail,
        "command": "cd android/gorz && ./gradlew pixel2api30DebugAndroidTest",
        "exitCode": exit_code,
        "outputTail": "\n".join(output.splitlines()[-120:]),
        "artifacts": [
            "android/gorz/app/build/reports/androidTests/managedDevice",
            "android/gorz/app/build/outputs/apk/debug",
            "runtime/reports/android-emulator-smoke-report.md",
            "runtime/reports/android-emulator-smoke-report.json",
        ],
    }


def android_sdk_available() -> bool:
    candidates = [
        os.environ.get("ANDROID_HOME", ""),
        os.environ.get("ANDROID_SDK_ROOT", ""),
        str(Path.home() / "Android" / "Sdk"),
    ]
    return any(candidate and Path(candidate).exists() for candidate in candidates)


def write_reports(payload: dict[str, object]) -> None:
    (REPORT_DIR / "android-emulator-smoke-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Android Emulator Smoke Report",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        f"Detail: {payload['detail']}",
        f"Command: `{payload['command']}`",
        f"Exit code: {payload['exitCode']}",
        "",
        "## Output Tail",
        "",
        "```text",
        str(payload["outputTail"]).strip() or "No command output.",
        "```",
        "",
    ]
    (REPORT_DIR / "android-emulator-smoke-report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
