# Research Alignment

This document maps Gozar evaluation scenarios to research questions for a PhD-grade proposal. The platform is intended to produce bounded, reproducible evidence from local simulations rather than unsupported claims about real-world deployment.

| Research Question | Scenario | Metrics | Evidence Produced |
|---|---|---|---|
| Can adaptive path selection improve resilience under selective blocking? | `relay-blocked.yaml`, `adaptive-failover.yaml` | request success rate, failover time, recovery time, failed requests before recovery, selected path over time | Compares static relay failure against adaptive fallback behavior after a controlled relay outage. |
| How quickly can the overlay recover from relay or gateway disruption? | `adaptive-failover.yaml`, `gateway-restart.yaml`, `intermittent-connectivity.yaml` | disruption detection time, recovery time, path switches, error counts by category | Shows measured recovery timing and whether requests resume after local service disruption. |
| What is the latency and throughput cost of relay-based fallback? | `baseline-direct.yaml`, `baseline-relay.yaml`, `bandwidth-512kbps.yaml` | median latency, p95 latency, throughput estimate, request success rate | Quantifies the local overhead of relay fallback relative to direct-path baseline behavior. |
| How does packet loss affect direct vs relay vs adaptive mode? | `packet-loss-5pct.yaml`, `packet-loss-15pct.yaml`, future direct-loss variants | request success rate, p95 latency, error categories, selected path over time | Produces controlled packet-loss measurements for comparing path modes across repeated runs. |
| Can local telemetry support path decisions without exposing sensitive user data? | `baseline-direct.yaml`, `baseline-relay.yaml`, `adaptive-failover.yaml` | path score logs, selected path over time, error categories, node heartbeat freshness | Demonstrates whether coarse local telemetry is enough for path decisions without recording payload content or user credentials. |

## Proposal Use

These mappings help turn engineering runs into research evidence. Each row should be backed by repeated measurements, saved result artifacts, and a short discussion of confounders before it becomes part of a thesis or paper.

## Safety Boundary

The evaluation design stays local-first and consent-based. It does not include real-world evasion deployment logic, offensive behavior, exploit code, stealth persistence, credential collection, or abuse of third-party infrastructure.
