#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "vpn-product" / "images" / "phase4"
RUNTIME_DIR = ROOT / "runtime" / "reports" / "screenshots" / "phase4"

REQUIRED_SCREENSHOTS = [
    "phase4-home.png",
    "phase4-connect-flow.png",
    "phase4-session.png",
    "phase4-confidence.png",
    "phase4-route-policy.png",
    "phase4-diagnostics.png",
    "phase4-evidence.png",
    "phase4-safety-pause.png",
    "phase4-audit.png",
    "phase4-settings.png",
    "phase4-storage-mode.png",
    "phase4-emulator-smoke-result.png",
]

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
    reason = ""

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

    existing = [name for name in REQUIRED_SCREENSHOTS if (DOCS_DIR / name).exists()]
    captured = sorted(set(captured + existing))
    missing = [name for name in REQUIRED_SCREENSHOTS if name not in captured]
    status = "PASS" if not missing else "PARTIAL" if captured else "SKIPPED"
    if adb and devices and not captured and not args.report_only:
        status = "FAIL"

    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "adbAvailability": "available" if adb else "missing",
        "connectedDevices": devices,
        "screenshotsCaptured": captured,
        "screenshotsMissing": missing,
        "status": status,
        "reason": "" if status == "PASS" else reason,
        "manualCaptureInstructions": MANUAL_INSTRUCTIONS.strip(),
    }
    write_reports(payload)
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
            devices.append(parts[0])
    return devices


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
    lines.extend(["", "## Screenshots Missing", ""])
    lines.extend(f"- {name}" for name in payload["screenshotsMissing"])
    if not payload["screenshotsMissing"]:
        lines.append("- none")
    lines.extend(["", "## Manual Capture Instructions", "", payload["manualCaptureInstructions"], ""])
    (RUNTIME_DIR / "screenshot-capture-report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
