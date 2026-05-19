# Phase 2 Android VpnService Prototype

Phase 2 adds a minimal Android local VPN lifecycle prototype under `android/gorz`. The app has one Connect / Disconnect button and one Settings button. It requests Android `VpnService` permission, registers a demo Android device with the local Profile API, requests a short-lived signed encrypted profile, verifies the issuer signature, decrypts the Android local demo envelope, validates the adaptive session profile, and starts a controlled local `VpnService` session.

This phase is not a circumvention tool. It uses no public gateway, no public network probing, and no public relay discovery. It is not production secure and not for real sensitive communication.

## What Phase 2 Adds

- Android Kotlin app prototype.
- Connect / Disconnect lifecycle.
- Settings screen for API URL, local admin token, profile status, and diagnostics.
- Android `VpnService` permission and service lifecycle integration.
- Android local demo envelope mode for local prototype crypto.
- Safety guards for TTL, audience, revocation, routing, endpoint, and safety notes.
- Revocation and diagnostics actions from Settings.

## What Phase 2 Does Not Add

- No production VPN service.
- No public gateway.
- No public network probing.
- No public relay discovery.
- No packet forwarding to the public internet.
- No route for `0.0.0.0/0`.
- No iOS implementation.

## Run The Profile API

From the repository root:

```bash
make profile-demo
```

The local Profile API listens on `http://127.0.0.1:8095`. Android emulator networking reaches host localhost through:

```text
http://10.0.2.2:8095
```

## Open The Android Project

Open `android/gorz` in Android Studio and run the `app` configuration on an emulator. The default Profile API URL is already `http://10.0.2.2:8095`.

## Connect / Disconnect Lifecycle

1. Tap Connect.
2. Android asks for `VpnService` consent if needed.
3. The app generates or loads local demo device key material.
4. The app registers the device with the local Profile API.
5. The app requests a signed encrypted profile with `android_local_demo` envelope mode.
6. The app verifies the issuer signature.
7. The app decrypts the short-lived demo config locally.
8. The app validates TTL, audience, revocation status, route scope, endpoint scope, and safety notes.
9. `GorzVpnService` opens a local TUN interface with `10.77.0.2/32`.
10. The app displays Connected.
11. Tap Disconnect to stop the controlled local service session.

## Routing Boundary

Phase 2 only adds the local demo route `10.77.0.0/24`. It does not add `0.0.0.0/0` because this prototype is for lifecycle validation, not full-device traffic handling. `GorzVpnService` reads packets only to count and drop them for local diagnostics. It does not forward packets externally.

## Profile API Compatibility

The existing PyNaCl sealed-box path remains the Phase 1 default. Android uses a separate `android_local_demo` envelope mode because exact sealed-box compatibility is intentionally not pulled into the minimal app. The Android mode is a local prototype crypto path and is not production secure.

## Blocked Scenarios

Blocked diagnostic scenarios are denied by the deterministic policy engine rather than routed around. The app surfaces the denial as a profile error and does not attempt alternate public endpoints.

## Testing

```bash
make android-check
make phase2-check
```

`android-check` validates structure and safety wording. If Java, Gradle, and the Android SDK are installed, it also runs Android unit tests.

## Known Limitations

- Local demo key material may be stored in normal app preferences for the prototype.
- The app does not forward traffic.
- The Android local demo envelope mode is for emulator and lab use only.
- The UI is intentionally minimal.
- The prototype is not production secure and not for real sensitive communication.
