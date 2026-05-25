#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "vpn-product" / "images" / "phase4"
RUNTIME_DIR = ROOT / "runtime" / "reports" / "screenshots" / "phase4"
sys.path.insert(0, str(ROOT / "scripts" / "reports"))
from phase4_artifact_utils import ANDROID_SCREENSHOTS, PLACEHOLDER_LABEL, write_placeholder_png, write_screenshot_readme

REQUIRED_SCREENSHOTS = [name for name, _related in ANDROID_SCREENSHOTS]

MANUAL_INSTRUCTIONS = """From repository root:

```bash
cd android/gorz
./gradlew installDebug
adb shell am start -n com.pirbod.gorz/.MainActivity
adb exec-out screencap -p > ../../docs/vpn-product/images/phase4/phase4-home.png
```

Repeat after navigating to each required Phase 4 screen. Store final files under
`docs/vpn-product/images/phase4/` and keep runtime copies under
`runtime/reports/screenshots/phase4/` when possible.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    adb = shutil.which("adb")
    devices: list[str] = []
    captured: list[str] = []
    placeholder: list[str] = []
    reason = ""
    generated = datetime.now(UTC).isoformat()
    previous_placeholder = previous_placeholder_names()

    if adb:
        devices = connected_devices(adb)
    else:
        reason = "adb is not available in PATH."

    if not args.report_only and adb and devices:
        result = capture_current_home(adb)
        if result:
            captured.append("phase4-home.png")
        else:
            reason = "adb was available, but screencap failed."
    elif not reason and not devices:
        reason = "No connected Android emulator or device was reported by adb."
    elif args.report_only:
        reason = "Report-only mode did not attempt screenshot capture."

    existing = [name for name in REQUIRED_SCREENSHOTS if (DOCS_DIR / name).exists() and name not in previous_placeholder]
    captured = sorted(set(captured + existing))

    for name, related in ANDROID_SCREENSHOTS:
        path = DOCS_DIR / name
        if path.exists():
            if name in previous_placeholder and name not in placeholder:
                placeholder.append(name)
            continue
        write_placeholder_png(path, "Android screenshot placeholder", related)
        shutil.copy2(path, RUNTIME_DIR / name)
        placeholder.append(name)

    missing = [name for name in REQUIRED_SCREENSHOTS if not (DOCS_DIR / name).exists()]
    captured = [name for name in captured if name not in placeholder]
    screenshot_records = []
    for name, related in ANDROID_SCREENSHOTS:
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
                    "captureMethod": "adb screencap" if name == "phase4-home.png" and name in captured else "existing real capture",
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

    if missing:
        status = "FAIL"
    elif any(item["status"] == "PLACEHOLDER" for item in screenshot_records):
        status = "PARTIAL"
    else:
        status = "PASS"
    if adb and devices and not captured and not placeholder and not args.report_only:
        status = "FAIL"
    if placeholder and not reason:
        reason = "Screenshot capture was unavailable or incomplete; visibly labelled placeholders were generated."

    payload = {
        "generatedAt": generated,
        "adbAvailability": "available" if adb else "missing",
        "connectedDevices": devices,
        "screenshotsCaptured": captured,
        "screenshotsPlaceholder": placeholder,
        "screenshotsMissing": missing,
        "screenshots": screenshot_records,
        "status": status,
        "reason": "" if status == "PASS" else reason,
        "manualCaptureInstructions": MANUAL_INSTRUCTIONS.strip(),
    }
    write_reports(payload)
    write_screenshot_readme(ROOT)
    print(f"Phase 4 screenshot capture status: {status}")
    if reason and status != "PASS":
        print(reason)
    return 1 if status == "FAIL" else 0


def connected_devices(adb: str) -> list[str]:
    output = subprocess.run([adb, "devices"], text=True, capture_output=True, check=False).stdout
    devices = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(redact_device_id(parts[0]))
    return devices


def redact_device_id(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"redacted-device-{digest}"


def previous_placeholder_names() -> set[str]:
    report = RUNTIME_DIR / "screenshot-capture-report.json"
    if not report.exists():
        return set()
    payload = json.loads(report.read_text(encoding="utf-8"))
    return {
        str(item.get("filename"))
        for item in payload.get("screenshots", [])
        if str(item.get("status")) == "PLACEHOLDER"
    }


def capture_current_home(adb: str) -> bool:
    subprocess.run([adb, "shell", "am", "start", "-n", "com.pirbod.gorz/.MainActivity"], check=False)
    target_docs = DOCS_DIR / "phase4-home.png"
    target_runtime = RUNTIME_DIR / "phase4-home.png"
    with target_docs.open("wb") as handle:
        result = subprocess.run([adb, "exec-out", "screencap", "-p"], stdout=handle, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0 or target_docs.stat().st_size == 0:
        target_docs.unlink(missing_ok=True)
        return False
    shutil.copy2(target_docs, target_runtime)
    return True


def write_reports(payload: dict[str, object]) -> None:
    (RUNTIME_DIR / "screenshot-capture-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 4 Screenshot Capture Report",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        f"adb availability: {payload['adbAvailability']}",
        f"Connected devices: {', '.join(payload['connectedDevices']) if payload['connectedDevices'] else 'none'}",
        f"Reason: {payload['reason'] or 'n/a'}",
        "",
        "## Screenshots Captured",
        "",
    ]
    lines.extend(f"- {name}" for name in payload["screenshotsCaptured"])
    if not payload["screenshotsCaptured"]:
        lines.append("- none")
    lines.extend(["", "## Placeholder Screenshots", ""])
    lines.extend(f"- {name}: {PLACEHOLDER_LABEL}" for name in payload["screenshotsPlaceholder"])
    if not payload["screenshotsPlaceholder"]:
        lines.append("- none")
    lines.extend(["", "## Screenshots Missing", ""])
    lines.extend(f"- {name}" for name in payload["screenshotsMissing"])
    if not payload["screenshotsMissing"]:
        lines.append("- none")
    lines.extend(["", "## Manual Capture Instructions", "", payload["manualCaptureInstructions"], ""])
    (RUNTIME_DIR / "screenshot-capture-report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
