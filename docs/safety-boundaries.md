# Safety Boundaries

`gozar` is a censorship-resilience research prototype. It is not positioned as a production circumvention system and must not be represented that way.

## Allowed Project Scope

- lawful lab testing
- academic measurement
- consent-based pilots
- resilience experiments against simulated outages, loss, and latency
- observability and path-selection research

## Out of Scope

- malware behavior
- covert persistence
- exploit logic
- stealthy abuse of third-party infrastructure
- instructions for unlawful deployment
- product claims about bypassing real-world blocking environments
- production privacy or anonymity guarantees

## Implementation Boundaries In This Repository

- research gateway mode is disabled by default
- forwarding is restricted to a configured allowlist
- simulation scripts target local Docker services only
- control messages use demo HMAC authentication and replay checks
- QUIC trust remains development-only and is documented as such

## Documentation Rule

Every public description of `gozar` should frame it as a research system for controlled environments, not a ready-to-deploy field tool.