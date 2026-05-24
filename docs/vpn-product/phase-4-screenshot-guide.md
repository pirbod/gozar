# Phase 4 Screenshot Guide

Screenshots demonstrate UI state only. They do not prove public routing or production security.

## Required Screenshots

### Android

1. `phase4-home.png`
2. `phase4-connect-flow.png`
3. `phase4-session.png`
4. `phase4-confidence.png`
5. `phase4-route-policy.png`
6. `phase4-diagnostics.png`
7. `phase4-evidence.png`
8. `phase4-safety-pause.png`
9. `phase4-audit.png`
10. `phase4-settings.png`
11. `phase4-storage-mode.png`
12. `phase4-emulator-smoke-result.png`

### Platform

1. `phase4-github-actions.png`
2. `phase4-terraform-validate.png`
3. `phase4-kubernetes-manifests.png`
4. `phase4-prometheus-alerts.png`
5. `phase4-grafana-dashboard.png`
6. `phase4-siem-detection-report.png`
7. `phase4-incident-summary.png`
8. `phase4-production-readiness-report.png`

## Storage Paths

Store final screenshots in `docs/vpn-product/images/phase4/`. Runtime capture reports are written to `runtime/reports/screenshots/phase4/`.

## Android Studio Capture

Open `android/gorz`, run the debug app on a Pixel 2 API 30 emulator, navigate to each screen, and use Android Studio screenshot capture. Keep filenames exactly as listed above.

## adb Capture

From repository root:

```bash
cd android/gorz
./gradlew installDebug
adb shell am start -n com.pirbod.gorz/.MainActivity
adb exec-out screencap -p > ../../docs/vpn-product/images/phase4/phase4-home.png
```

Repeat after navigating to each screen.

## Scripted Report

Run:

```bash
make phase4-screenshots
make phase4-screenshot-report
make platform-screenshots
```

If an emulator is unavailable, the script writes a SKIPPED report with the exact reason and manual capture instructions.

Platform screenshots are captured manually or reported as SKIPPED by `scripts/platform/capture_platform_screenshots.py`.

## Validation Report References

The final validation report references either captured screenshot paths or the skipped screenshot report.
