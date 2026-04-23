# ADR 0001: Polyglot Monorepo Layout

## Status

Accepted

## Context

The prototype needs Rust dataplane services, a TypeScript control plane, shared tooling, containerized local development, and one place for docs and CI.

## Decision

Use a single repository with:

- A Cargo workspace for Rust crates and services
- An npm workspace for TypeScript packages and apps
- Shared docs, Docker assets, and CI at the repository root

## Consequences

- Cross-cutting docs, CI, and local dev assets stay versioned together.
- The Rust and TypeScript control contracts can evolve in the same review surface.
- The repo favors coherence for a small research team over independent release cadence.

