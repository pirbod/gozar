# Evaluation Platform

Gozar's evaluation platform turns the local Docker Compose demo into a reproducible lab for adaptive censorship-resilience research. It measures how the overlay behaves when direct, relay, or gateway paths are degraded by controlled local impairments.

This is defensive academic infrastructure. It does not provide production circumvention claims, deployment guidance, offensive tooling, credential collection, or instructions for illegal use.

## What It Runs

The evaluation runner starts the existing local stack, exercises the desktop-client echo interface on `127.0.0.1:7000`, applies a scenario impairment, records request-level measurements, clears impairments, and writes results under `eval/results/latest`.

```bash
make eval-baseline
make eval-adaptive
make eval
make eval-clean
```

`make eval-smoke` is the CI-safe form. It avoids privileged `tc/netem` manipulation and uses application-level relay outage simulation instead.

## Dependencies

- Docker with Compose v2
- Python 3
- GNU Make
- Linux `tc` inside Docker containers for full local netem scenarios

The Compose services already grant `NET_ADMIN` to relay and gateway containers for local-only netem tests. GitHub Actions smoke evaluation does not depend on `tc`.

## Scenario Files

Scenario definitions live in `eval/scenarios`. Each file describes the mode, impairment, affected path, expected behavior, and metrics to collect.

Key modes:

- `static-direct`: pin control preference to the direct gateway path.
- `static-relay`: pin control preference to the relay path.
- `adaptive`: start from an initial path and let the runner request a fallback after a measured failure.

Current scenarios:

| Scenario | Purpose |
|---|---|
| `baseline-direct.yaml` | Direct-path reference run. |
| `baseline-relay.yaml` | Relay-path reference run. |
| `latency-200ms.yaml` | Relay latency sensitivity with local netem. |
| `packet-loss-5pct.yaml` | Moderate packet-loss sensitivity. |
| `packet-loss-15pct.yaml` | Higher packet-loss stress case. |
| `bandwidth-512kbps.yaml` | Relay bandwidth constraint estimate. |
| `relay-blocked.yaml` | Static relay behavior when the relay is unavailable. |
| `gateway-restart.yaml` | Common gateway-hop restart and recovery. |
| `intermittent-connectivity.yaml` | Alternating relay pause/unpause behavior. |
| `adaptive-failover.yaml` | Relay outage followed by direct-path fallback request. |

## Metrics

The runner records:

- connection setup time
- time to first successful request
- request success rate
- median latency
- p95 latency
- throughput estimate
- failover time
- recovery time
- disruption detection time
- number of path switches
- selected path over time
- error counts by category
- scenario start and end timestamps

OpenTelemetry hooks remain available in the services, while the evaluation runner adds lightweight JSON and Markdown outputs for repeatable proposal work.

## Results

Measured outputs are written to:

```text
eval/results/latest/results.json
eval/results/latest/summary.md
```

The repository also includes `eval/results/example` with clearly marked synthetic data to show the report shape. Do not cite the example values as measured results.

## Interpreting Results

Use baseline scenarios as the local reference before interpreting impaired runs. A single local run is not enough evidence for a broad conclusion; repeat scenarios and compare confidence intervals before writing research claims.

Report only what was measured. For example, "adaptive mode recovered after N failed requests in this Docker lab" is appropriate; "Gozar defeats censorship" is not.

## Limitations

- Docker-local impairments model symptoms such as loss and delay, not a complete censor.
- `tc/netem` scenarios require local privileges and are intentionally excluded from CI smoke runs.
- The echo workload is minimal and should be expanded before publication-grade network claims.
- Adaptive mode currently uses a simple runner-triggered fallback after observed errors; future work should evaluate richer path-health estimators.

## Safety And Ethics

All scenarios are designed for authorized lab systems. Do not point the research gateway or overlay at third-party systems without explicit permission. Keep pilots consent-based, documented, and reviewed through the relevant academic or organizational process.
