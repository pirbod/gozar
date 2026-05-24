# Phase 4 Screenshot Capture Report

Generated: 2026-05-24T20:28:49.781194+00:00
Status: PARTIAL
adb availability: missing
Connected devices: none
Reason: Report-only mode did not attempt screenshot capture.

## Screenshots Captured

- none

## Placeholder Screenshots

- phase4-home.png: PLACEHOLDER - screenshot capture pending
- phase4-connect-flow.png: PLACEHOLDER - screenshot capture pending
- phase4-session.png: PLACEHOLDER - screenshot capture pending
- phase4-confidence.png: PLACEHOLDER - screenshot capture pending
- phase4-route-policy.png: PLACEHOLDER - screenshot capture pending
- phase4-diagnostics.png: PLACEHOLDER - screenshot capture pending
- phase4-evidence.png: PLACEHOLDER - screenshot capture pending
- phase4-safety-pause.png: PLACEHOLDER - screenshot capture pending
- phase4-audit.png: PLACEHOLDER - screenshot capture pending
- phase4-settings.png: PLACEHOLDER - screenshot capture pending
- phase4-storage-mode.png: PLACEHOLDER - screenshot capture pending
- phase4-emulator-smoke-result.png: PLACEHOLDER - screenshot capture pending

## Screenshots Missing

- none

## Manual Capture Instructions

From repository root:

```bash
cd android/gorz
./gradlew installDebug
adb shell am start -n com.pirbod.gorz/.MainActivity
adb exec-out screencap -p > ../../docs/vpn-product/images/phase4/phase4-home.png
```

Repeat after navigating to each required Phase 4 screen. Store final files under
`docs/vpn-product/images/phase4/` and keep runtime copies under
`runtime/reports/screenshots/phase4/` when possible.
