# Security Policy

## Supported Status

Gozar/Gorz is a research prototype for controlled environments only. It is not production secure, not a production VPN, not a public routing product, and not offensive tooling.

## Reporting Vulnerabilities

Report vulnerabilities to the maintainer through a private GitHub security advisory when available, or open a minimal issue that does not include exploit details or sensitive data. Maintainer contact is currently the repository owner placeholder: `pirbod`.

## Out-Of-Scope Claims

This project does not claim production security, real secure messaging, field deployment readiness, or public traffic routing capability.

## Bounty

There is no bug bounty program.

## Safety Boundaries

- Not a circumvention tool.
- No public relay discovery.
- No public network probing.
- No full-device Android route.
- No automatic diagnostic upload.
- No collection of contacts, phone numbers, exact location, or public IP history.

## Phase 4 Security Review

Phase 4 adds a controlled Android threat model at `docs/security/android-phase-4-threat-model.md`. Remaining gaps include demo storage default, experimental Android Keystore validation, release signing, tenant auth, independent review, and release artifact governance.

## Responsible Disclosure

Do not post working exploit steps, credentials, private keys, sensitive personal data, or real-world targeting details in public issues.
