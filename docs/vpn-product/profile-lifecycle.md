# Profile Lifecycle

## Registration

The client generates a local demo device keypair and sends only the public key to the Profile API. The API stores the public key and a stable hash. The private key remains in the local demo client process.

## Issuance

The client requests an adaptive session profile with requested mode, risk tolerance, and local client context. The deterministic policy engine chooses a local template or denies issuance.

When issuance is allowed, the profile issuer:

1. Creates a `prof_...` identifier.
2. Adds `issued_at`, `expires_at`, and TTL.
3. Builds a simulated WireGuard-like or QUIC-like payload from templates.
4. Encrypts only the payload to the device public key.
5. Signs the envelope with the issuer signing key.
6. Stores redacted metadata.
7. Records audit events.

## Validation

Validation checks signature format, TTL, revocation state, and audience. Expired, revoked, unknown, or wrong-audience profiles fail validation.

## Revocation

Revocation records the profile ID, reason, and timestamp. Revoked profiles are not valid even if their TTL has not expired.

## Audit Export

Audit export creates a redacted JSON bundle under the `local_profile_lifecycle_demo` scope. It removes plaintext profile material, private keys, raw device public keys, and unredacted device identifiers.

