# Demo Video Recording Commands

Use these commands from the repository root before recording:

```bash
make platform-check
make android-emulator-smoke-report
make phase4-screenshot-report
make demo-video-check
make production-readiness-check
make release-candidate-manifest
make phase4-example-reports
```

Suggested local recording steps:

```bash
# Terminal 1: keep reports fresh.
make phase4-check

# Terminal 2: open Android Studio manually and run android/gorz on an emulator.
# Capture the desktop with your local screen recorder.
```

Expected output:

```text
docs/demo/gozar-gorz-phase4-demo.mp4
```

If the video cannot be recorded in the current environment, keep `docs/demo/gozar-gorz-phase4-demo.placeholder.md` and `docs/demo/demo-video-link.md` marked as pending.
