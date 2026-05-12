# Path Scoring

The desktop client now selects routes using a scoring module instead of blindly following a single static tunnel preference.

## Inputs

Current scoring inputs are intentionally simple and observable:

- operator preference from the signed control config
- preferred-path bonus from the control plane
- path kind bias (`direct` vs `relay`)
- queue-capacity bonus
- relay freshness from the signed relay directory
- research-gateway support requirement when lab HTTP mode is used

## Output

The client logs a score breakdown similar to:

```text
path_scores=direct=... [operator_preference=..., preferred_path_bonus=..., ...] | relay=... [...]
```

This makes the route-selection rationale visible during experiments.

## Why It Matters

The goal is not to claim production-grade routing intelligence. The goal is to give researchers a place to plug in richer decision models while keeping the current logic explainable and easy to verify.

## Future Work

Potential future scoring inputs:

- RTT estimates
- packet-loss estimates
- per-hop saturation
- relay diversity
- censorship-event simulations
- user safety policies for allowed destinations