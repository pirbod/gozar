# Gozar Evaluation Platform

This directory contains local-first evaluation scenarios, scripts, configs, and example outputs for adaptive censorship-resilience research.

The evaluation platform is designed for lawful academic work in controlled environments. It simulates degraded paths inside the local Docker Compose stack and reports measured behavior. It does not provide production circumvention claims, deployment guidance, or offensive functionality.

## Layout

```text
eval/
|- configs/      # local runner defaults
|- results/      # generated outputs plus synthetic examples
|- scenarios/    # YAML scenario definitions
`- scripts/      # netem helpers and the evaluation runner
```

## Quick Commands

```bash
make eval-baseline
make eval-adaptive
make eval
make eval-smoke
make eval-clean
```

`make eval` builds and starts the local stack, runs all scenario definitions, clears impairments after each run, and writes:

```text
eval/results/latest/results.json
eval/results/latest/summary.md
```

## Dependencies

- Docker with Compose v2
- Python 3
- GNU Make
- Linux `tc` inside containers for full local netem scenarios

CI smoke evaluation does not require privileged network manipulation. It runs only scenarios marked `ci_safe: true`.

## Scenario Modes

- `static-direct`: keeps traffic on the direct path unless the data plane itself fails.
- `static-relay`: switches the control-plane preference to relay before traffic measurement starts.
- `adaptive`: applies an impairment, detects request failures, requests a control-plane fallback, and measures recovery.

## Scenario Set

| Scenario | Local Behavior |
|---|---|
| `baseline-direct.yaml` | No impairment, direct path selected. |
| `baseline-relay.yaml` | No impairment, relay path selected. |
| `latency-200ms.yaml` | Adds 200 ms relay delay using netem. |
| `packet-loss-5pct.yaml` | Adds moderate relay packet loss using netem. |
| `packet-loss-15pct.yaml` | Adds harsher relay packet loss using netem. |
| `bandwidth-512kbps.yaml` | Adds a relay bandwidth cap using netem. |
| `relay-blocked.yaml` | Stops relay while pinned to relay mode. |
| `gateway-restart.yaml` | Restarts the gateway and measures recovery. |
| `intermittent-connectivity.yaml` | Repeatedly pauses and unpauses relay locally. |
| `adaptive-failover.yaml` | Starts on relay, stops relay, then requests direct fallback after the first observed failure. |

## Metrics

The runner records connection setup time, time to first successful request, request success rate, median latency, p95 latency, throughput estimate, failover time, recovery time, disruption detection time, path switches, selected path over time, error categories, and scenario timestamps.

## Interpreting Results

Compare impaired scenarios against `baseline-direct` and `baseline-relay` from the same run. Treat results as local experimental evidence only; repeat runs before making research claims, and report measured values rather than broad deployment conclusions.

## Safety Boundary

Scenarios are local Docker experiments. Network impairment uses `tc netem` only inside Compose services that already run with `NET_ADMIN`. The CI smoke mode does not require privileged network manipulation and uses application-level control actions instead.

Do not point the research gateway, overlay, or evaluation runner at third-party systems without explicit authorization.
