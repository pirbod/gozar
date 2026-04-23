# ADR 0002: QUIC-First Multi-Path Overlay

## Status

Accepted

## Context

The prototype is meant to feel VPN-like to the user while exploring a more resilient architecture than a single static tunnel.

## Decision

Model the overlay as a QUIC-first edge-to-gateway path with an alternate relay-assisted path:

- `direct`: desktop client to gateway
- `relay`: desktop client to relay to gateway

The desktop client polls the control plane for a preferred path and can also switch locally on send failure.

## Consequences

- The user-facing entry point stays simple.
- Path choice becomes explicit and observable.
- The lab stays small while still exercising multi-path concepts.
- Future work can add concurrent path scoring instead of simple active-path selection.

