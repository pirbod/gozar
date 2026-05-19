# Phase 2 Test Plan

## Backend Tests

- Admin token protection for safety pause, resume, issuer rotation, and profile revocation.
- Demo private key startup guard.
- Audit timestamp bucket config for 60 and 15 minutes, plus invalid config rejection.
- Mobile bootstrap endpoint.
- Android local demo envelope issuance and decryption test helper.
- Existing profile issuance, validation, expiry, revocation, audit redaction, and deterministic policy tests.

## Android Unit Tests

- `SafetyGuards` rejects `0.0.0.0/0`.
- `SafetyGuards` rejects missing `local_demo_only`.
- `SafetyGuards` rejects public endpoints.
- `SafetyGuards` accepts `local-gateway` and `local-relay` style endpoints.
- `ProfileModels` parses profile response JSON.
- `ProfileStateStore` stores and clears metadata.
- `ProfileCrypto` handles invalid signatures as a failure.
- `VpnSessionController` maps errors to user-friendly states.

## Manual Emulator Test

1. Run `make profile-demo`.
2. Open `android/gorz` in Android Studio.
3. Run the app on an Android emulator.
4. Confirm Settings uses `http://10.0.2.2:8095`.
5. Tap Connect.
6. Grant Android VPN permission.
7. Confirm status becomes Connected.
8. Open Settings and validate the current profile.
9. Run diagnostics.
10. Revoke the current profile.
11. Return to the main screen and tap Disconnect.

## Lifecycle Acceptance Checklist

- App starts.
- Connect requests VPN permission.
- Device registration succeeds against the local Profile API.
- Signed encrypted profile is received.
- Issuer signature is checked.
- Android local demo profile decrypts locally.
- TTL, audience, revocation, routing, endpoint, and safety notes are validated.
- `GorzVpnService` starts with only the local demo route.
- Disconnect stops the service.
- Settings can revoke the profile and reset local demo state.

## Static Checks

```bash
make safety-wording-check
make android-check
make phase2-check
```

CI does not require an emulator. Android Gradle unit tests run only when the Android SDK is available.
