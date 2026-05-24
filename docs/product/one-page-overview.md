# Gozar/Gorz One-Page Overview

## What Gozar Is

Gozar Core is a research overlay and path-scoring prototype for controlled censorship-resilience experiments. It studies path selection, signed control messages, and lab-only forwarding behavior in authorized environments.

## What Gorz Is

Gorz Web is a local-first confidence-aware messaging demo. It makes confidence scoring, redacted incident evidence, audit trails, and safety pause controls visible to product and research reviewers.

## What Profile API Is

Profile API is a local backend for short-lived adaptive session profiles. It demonstrates signed encrypted demo profiles, deterministic policy selection, validation, revocation, redacted audit export, and safety pause behavior.

## What Gorz Android Is

Gorz Android is the mobile experience and local VPN lifecycle prototype. It uses Android `VpnService` only for local lifecycle validation, applies only the controlled demo route, and does not forward public traffic.

## What Evaluation Is

Evaluation is the controlled lab evidence engine. It runs reproducible scenarios for outage, latency, loss, bandwidth, and path scoring without making real-world deployment claims.

## In Scope

- Lawful academic evaluation.
- Lab simulation.
- Consent-based pilots.
- Local demo services.
- Safety-gated UX and evidence flows.
- Redacted audit and validation reports.

## Out Of Scope

- Production VPN service.
- Public routing product.
- Offensive tooling.
- Field deployment.
- Real sensitive communications.
- Public traffic forwarding.
- Public network probing.

## Current Maturity Level

The repository is a professionally governed alpha-readiness prototype. It has meaningful architecture, tests, safety checks, and docs, but it remains not production secure.

## Safety Boundaries

- Not a circumvention tool.
- Not a field-deployment routing product.
- No public relay discovery.
- No public gateway.
- No public network probing.
- No automatic diagnostic upload.
- No sensitive Android permissions.

## Next Milestone

Move from demo-ready alpha to reviewed alpha by closing release blockers for Android keystore storage, tenant auth, CI emulator coverage, dependency audits, privacy review, and independent threat-model validation.
