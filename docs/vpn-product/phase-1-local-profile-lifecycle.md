# Phase 1 Local Profile Lifecycle

Phase 1 implements a local-only profile lifecycle for adaptive session profiles. A demo client registers a device public key, requests a fresh short-lived demo config, receives a signed encrypted profile envelope, decrypts it locally, validates TTL and revocation state, and exports redacted audit evidence.

This is not a production VPN implementation. It does not install OS VPN profiles, create a real VPN tunnel, contact public gateways, perform public network probing, scrape endpoints, or claim production security. It is not a circumvention tool and is not for real sensitive communication.

## Run

```bash
make profile-install
make profile-demo
```

Or:

```bash
docker compose -f docker-compose.profile.yml up --build
```

Open:

- Profile API: `http://localhost:8095/api/profile/health`
- API docs: `http://localhost:8095/docs`

## Demonstrated Lifecycle

1. Device registration with a public key.
2. Local demo device keypair generation in the client.
3. Session profile request.
4. Deterministic policy engine selection.
5. Signed encrypted profile envelope creation.
6. Local client decryption.
7. Profile validation.
8. TTL expiry handling.
9. Revocation handling.
10. Demo issuer key rotation.
11. Redacted audit record generation.
12. Evidence export without plaintext profile secrets.

## Why Profiles Are Signed And Encrypted

The encrypted payload keeps the simulated profile config out of logs and audit exports. The envelope signature lets the demo client verify that the API issued the exact envelope it received. The API stores canonical signed envelope fields and hashes so validation can re-check the signature later without storing plaintext profile payloads. This is a local-only proof of lifecycle mechanics, not a production security guarantee.

## Why Policy Is Deterministic

The Phase 1 policy engine is a fixed ruleset. AI may later assist with policy recommendations, but it must not directly generate arbitrary unvalidated configs. The deterministic policy engine owns final decisions. The issuer chooses only from local templates, applies explicit TTL and safety notes, and signs the resulting envelope.

## Blocked Scenarios

Phase 1 denies blocked scenarios instead of trying to route around them. That keeps the prototype aligned with local-only safety boundaries while still demonstrating how diagnostics can produce a conservative policy result.

## Future Preparation

The lifecycle prepares for future consent-based OS integration by separating device identity, policy selection, profile issuance, validation, revocation, and audit redaction. Future work can replace simulated payloads with platform-specific adapters after independent security audit, legal review, app store compliance review, and production key management design.
