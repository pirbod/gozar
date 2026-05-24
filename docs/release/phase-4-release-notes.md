# Phase 4 Release Notes

## Summary

Version `0.4.0-rc1` completes the four-phase roadmap as Controlled Release Readiness.

## Scope

The release candidate supports local profile lifecycle, Android local VPN lifecycle, clickable Android product experience, safety controls, confidence scoring, evidence export, diagnostics, emulator validation hooks, screenshots, and release documentation.

## Safety Boundaries

Controlled prototype only. No public traffic forwarding. No full-device route. Not production secure. Not a public routing product. Not a circumvention tool.

## New Features

- SecureValueStore abstraction with demo storage default and experimental Android Keystore path.
- RoutePolicyGuard structured result.
- Deterministic confidence model with blocking reasons.
- Evidence Package V2 with checksum and screenshot references.
- Safety pause reasons and history.
- Local diagnostics hardening.
- Screenshot capture/report script.
- Emulator smoke report script.
- Release candidate manifest.
- Final validation, privacy, security, backend, and release docs.

## Validation Evidence

Reports are generated under `runtime/reports/`. Android unit and emulator tests require local Gradle and Android SDK tooling.

## Screenshots

Screenshots should be stored under `docs/vpn-product/images/phase4/`. If unavailable, use the skipped screenshot report.

## Known Limitations And Production Gaps

Demo storage remains default. Android Keystore path needs more validation. Release signing is not configured. Tenant auth, independent security review, formal retention policy, and production crypto review are not complete.

## Install Instructions

Open `android/gorz` in Android Studio, sync Gradle, install debug build on a Pixel 2 API 30 emulator, and use offline demo mode or local Profile API at `http://10.0.2.2:8095`.

## Rollback Instructions

Stop using the debug APK, clear Android app data, remove local runtime reports if necessary, and regenerate evidence after fixes.
