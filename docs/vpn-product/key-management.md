# Key Management

## Device Keys

The demo client generates a device keypair locally. The API receives the public key and stores a public key hash for lookup and audit correlation. The backend does not store device private keys.

## Issuer Signing Key

The API stores a local demo issuer signing key in SQLite so profiles issued before service restart can still be verified. The private key column is deliberately named `private_key_demo` to make the boundary explicit. It is for local Phase 1 demonstration only, is never returned by the API, and must not appear in audit export.

Production requires KMS, secure enclave, or HSM-backed signing before any real deployment. The Phase 1 key store is not production secure.

## Envelope Signature

The issuer signs canonical JSON for the envelope without the `signature` field. The encrypted payload is included in the signed envelope, so client-side verification detects envelope tampering.

The API stores the canonical signed envelope fields, the raw signature for local validation, the issuer key ID, the issuer public key, and hashes for the envelope, encrypted payload, and signature. Validation re-checks the signature and hashes instead of trusting metadata alone.

## Payload Encryption

The profile payload is encrypted to the device public key. The API returns encrypted payload bytes and never returns the plaintext simulated config.

## Short TTL

The default TTL is 900 seconds. Tests and validation scripts can request a shorter local TTL to verify expiry behavior.

## Revocation

Revocation is stored separately from the profile metadata. Validation fails when a profile is revoked.

## Demo Rotation

`POST /api/profile/issuer/rotate-demo-key` rotates the local demo signing key. Existing profiles can still validate because their issuer key ID and public key are stored with the signed envelope metadata.
