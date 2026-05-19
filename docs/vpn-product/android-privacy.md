# Android Privacy

The Android Phase 2 prototype is local-first. It demonstrates consent, profile validation, and local `VpnService` lifecycle without public network behavior.

## Data Collected Locally

- Profile API URL.
- Local demo admin token.
- Demo device ID and public key hash.
- Demo key material for Android local prototype crypto.
- Current profile ID, expiry, status, and last error.
- Local packet counters: `packets_read` and `packets_dropped_demo`.

## Data Not Collected

- No public network probing.
- No public gateway use.
- No public relay discovery.
- No location, contacts, SMS, camera, microphone, or external storage permissions.
- No plaintext profile logs.
- No packet forwarding in Phase 2.

## Profile Handling

The app verifies the issuer signature, decrypts the profile locally, validates safety notes and backend status, then stores only redacted metadata. Plaintext profile payloads are used in memory for validation and are not exported.

## Demo Key Handling

The prototype may store Android local demo key material in app preferences. This is acceptable only for local lab validation. It is not production secure. Future production work would need Android Keystore-backed key handling and independent review.

## Audit Redaction

The Profile API audit export removes plaintext profile payloads, private keys, device public keys, local endpoint details, exact identifiers, and exact timestamps. The default timestamp bucket is 60 minutes to reduce precision while preserving enough sequence evidence for local tests.
