# ADR 0003: Authenticated Control Messages For Demo Safety

## Status

Accepted

## Context

A research prototype still needs basic protection against forged control messages and accidental path manipulation.

## Decision

Use HMAC-authenticated control messages with:

- A signed request envelope for client config fetches
- A signed heartbeat request for node observations
- A nonce-bound signed response for client config delivery

## Consequences

- The desktop client can reject forged or mismatched control responses.
- The control plane can reject unsigned heartbeats and config requests.
- The scheme is intentionally simple and local-lab friendly, but it is not a substitute for production identity and key management.

