# Prototype Safety Boundaries

Gorz is a lawful, local-first, safety-aware prototype.

## Allowed

- Local demo identities.
- Local conversations.
- Demo encrypted-envelope records.
- Deterministic local diagnostic simulations.
- Local SQLite persistence.
- Redacted incident export.
- Audit trail review.
- Emergency pause.

## Out Of Scope

- Production secure messaging.
- Public relay operation.
- Bridge discovery.
- Relay discovery.
- Public network scanning.
- External target probing.
- Real IP address collection.
- Exact location collection.
- Phone number collection.
- Automatic diagnostic upload.

## Operator Notes

Run the prototype only in local development or a documented lab environment. Do not use it for real
sensitive communication. Do not present the demo cryptography or simulated diagnostics as production
security evidence.

