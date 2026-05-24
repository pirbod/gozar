# Android Studio Emulator Smoke Test

## Purpose

Validate that the Gorz Android prototype opens, renders key screens, and supports the safe offline demo flow on an emulator.

## Prerequisites

- Android Studio.
- JDK 17.
- Android SDK API 30 or newer.
- Optional local Profile API for backend-connected mode.

## Open Android Studio

Open `android/gorz` as the project root and sync Gradle.

## Create Emulator

- Device: Pixel 2 or Pixel 5.
- API: 30 or newer.
- System image: AOSP is enough.

## Run App

Run the `app` configuration.

## Optional Backend

Start Profile API:

```bash
make profile-demo
```

Use this Android emulator API URL:

```text
http://10.0.2.2:8095
```

## Offline Demo Path

1. Launch app.
2. Start demo.
3. Open Home.
4. Connect in offline demo mode.
5. Open Confidence.
6. Open Route Policy.
7. Verify `10.77.0.0/24` is applied.
8. Verify `0.0.0.0/0` is blocked.
9. Open Diagnostics.
10. Open Evidence.
11. Generate redacted evidence.
12. Open Settings.
13. Disconnect.

## Manual VPN Permission Path

1. Tap Connect.
2. Accept Android VPN permission.
3. Verify local lifecycle wording.
4. Verify no public traffic forwarding wording.
5. Verify no full-device route wording.

## Expected Results

- App launches.
- Screens render without backend.
- Offline demo mode is clear.
- Route policy remains local-only.
- Evidence redaction wording appears.
- VPN permission path does not claim production VPN behavior.

## Known Issues

- VPN permission dialog can block automation.
- Managed devices can be unavailable on some CI runners.
- Profile API must use `10.0.2.2` from emulator.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Gradle sync failure | Confirm JDK 17 and Android SDK are installed. |
| Emulator not starting | Use an API 30 or newer AOSP image and cold boot. |
| API URL wrong | Use `http://10.0.2.2:8095` on emulator. |
| Profile API unavailable | Use offline demo mode. |
| VPN permission dialog blocks automation | Use manual VPN path and CI smoke without VPN permission. |
| Managed device unavailable in CI | Run `workflow_dispatch` or Android Studio manual smoke. |
