# Key Management

## Device Keys

The demo client generates a device keypair locally. The API receives the public key and stores a public key hash for lookup and audit correlation. The backend does not store device private keys.

## Issuer Signing Key

The API creates an ephemeral issuer signing key at startup and stores only issuer public key metadata. The private signing key is held in process memory for local demo issuance.

## Envelope Signature

The issuer signs canonical JSON for the envelope without the `signature` field. The encrypted payload is included in the signed envelope, so client-side verification detects envelope tampering.

## Payload Encryption

The profile payload is encrypted to the device public key. The API returns encrypted payload bytes and never returns the plaintext simulated config.

## Short TTL

The default TTL is 900 seconds. Tests and validation scripts can request a shorter local TTL to verify expiry behavior.

## Revocation

Revocation is stored separately from the profile metadata. Validation fails when a profile is revoked.

