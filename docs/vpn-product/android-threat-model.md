# Android Threat Model

Phase 2 is a local prototype for adaptive session profile lifecycle validation. It is not production secure and not for real sensitive communication.

## Assets

- Android demo device key material.
- Issuer public key.
- Signed encrypted profile envelope.
- Decrypted short-lived demo config in memory.
- Profile ID, expiry, validation status, and revocation status.
- Local packet counters.

## Trust Boundaries

- Android app process to local Profile API over emulator host networking.
- Local Profile API to SQLite demo issuer key storage.
- Android app to Android `VpnService` permission boundary.
- App preferences to local device storage.

## Key Risks

- Demo key material stored in normal preferences can be read on compromised devices.
- A malicious local app could try to influence user consent or observe app state.
- A compromised backend could issue unsafe routes or stale profiles.
- A stale profile could remain active if revocation is not checked.
- Unsafe routing could capture broader device traffic than intended.
- Logs could leak profile payloads or key material if future code adds verbose logging.

## Safety Controls

- Short-lived demo configs.
- Issuer signature verification before decryption is trusted.
- Local decryption only.
- Backend validation checks TTL, audience, revocation, and envelope integrity.
- Android `SafetyGuards` reject `0.0.0.0/0`, unknown profile types, public endpoints, missing `local_demo_only`, expired profiles, and revoked profiles.
- `GorzVpnService` adds only `10.77.0.0/24`.
- Packets are counted and dropped locally; they are not forwarded externally.
- Audit export redacts payloads, keys, endpoint details, and buckets timestamps.

## Residual Risk

The Android local demo envelope mode is prototype crypto for emulator and lab use. Production work would need platform key storage, external security review, hardened transport, stronger backend deployment controls, and dedicated privacy review.
