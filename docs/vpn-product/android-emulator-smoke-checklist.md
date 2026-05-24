# Android Emulator Smoke Checklist

- [ ] App builds.
- [ ] App installs.
- [ ] App launches.
- [ ] Onboarding visible.
- [ ] Home visible.
- [ ] Controlled prototype label visible.
- [ ] Offline mode works.
- [ ] Connect flow visible.
- [ ] Confidence screen visible.
- [ ] Route policy visible.
- [ ] `10.77.0.0/24` shown as applied.
- [ ] `0.0.0.0/0` shown as blocked.
- [ ] Diagnostics visible.
- [ ] Evidence generation visible.
- [ ] Redaction wording visible.
- [ ] Settings visible.
- [ ] Disconnect works.
- [ ] No public forwarding claim.
- [ ] No production secure claim.
## Phase 4 Checklist

- Pixel 2 API 30 emulator exists.
- App launches.
- Controlled prototype label is visible.
- No public forwarding label is visible.
- Offline demo mode can be enabled.
- Connect flow stages render.
- Session dashboard renders.
- Confidence screen renders.
- Route policy screen shows `10.77.0.0/24`, `0.0.0.0/0`, and `::/0`.
- Diagnostics screen shows local-only and no public probing labels.
- Evidence screen generates redacted JSON and integrity checksum.
- Safety pause can enable and resume.
- Settings screen shows storage mode and demo warning.
- Screenshot report is PASS, PARTIAL, or SKIPPED with reason.
- Emulator smoke report is PASS or SKIPPED with reason.
