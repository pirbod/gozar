# Android Alpha Hardening

## Current Status

Gorz Android is a Jetpack Compose clickable prototype with Profile API integration, offline demo fallback, local audit, redacted evidence, and a local `VpnService` lifecycle. It is not production secure and not a public routing product.

## Safe Alpha Scope

- Controlled prototype demos.
- Android emulator and internal test devices.
- Offline demo mode and local Profile API mode.
- Local lifecycle validation only.
- No public traffic forwarding.
- No full-device route.

## Android Keystore Target Design

`DemoSecureValueStore` currently documents the storage gap. Before alpha, demo settings and local key material should move to Android Keystore-backed encrypted storage with migration and reset tests.

## Secure Settings Target Design

Settings should separate demo operator values from any future user credentials. Admin tokens should never be stored as production secrets in SharedPreferences.

## Permission Review

Allowed permissions are `INTERNET` and `FOREGROUND_SERVICE`. `BIND_VPN_SERVICE` must be scoped only to the service. Location, contacts, phone, camera, and microphone permissions are blocked by script.

## VpnService Route Policy

The service may add only `10.77.0.0/24` and local address `10.77.0.2/32`. It must not add a full-device IPv4 or IPv6 route.

## Diagnostics Privacy Model

Packets may be counted and dropped locally. Packet payloads, public IP history, contacts, phone numbers, and exact location must not be collected.

## Release Signing Gap

The app currently uses debug/development build flow. Alpha requires release signing, key custody, artifact provenance, and rollback procedure.

## Crash Reporting Gap

No crash reporter is configured. Any future crash reporting must be opt-in for demos, redact identifiers, and avoid automatic diagnostic upload.

## Emulator Test Gap

Gradle Managed Device `pixel2api30` is configured for smoke tests. Hosted emulator CI can be fragile, so the smoke workflow is manual/nightly until stable. PR gates should still run build, unit tests, and safety checks.

## Accessibility Gap

Phase 3 has basic Material 3 semantics. Alpha should add accessibility review for touch targets, contrast, screen reader labels, and keyboard navigation.
