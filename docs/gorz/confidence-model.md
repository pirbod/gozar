# Confidence Model

Gorz treats delivery as an evidence fusion problem. A message is not simply sent or failed; status
is inferred from required and supporting layers.

## Inputs

Mandatory scores:

- `envelope_score`
- `transport_score`
- `relay_or_peer_score`
- `app_delivery_score`

Support scores:

- `path_diversity_score`
- `source_independence_score`
- `baseline_consistency_score`
- `safety_score`

Risk:

- `risk_penalty`

## Formula

```text
mandatory_score = geometric_mean(envelope, transport, relay_or_peer, app_delivery)
support_score = weighted_average(path_diversity, source_independence, baseline_consistency, safety)
confidence = clip((mandatory_score ^ 0.7) * (support_score ^ 0.3) * (1 - risk_penalty), 0, 1)
```

## Classifications

- `delivered_confirmed`: confidence >= 0.85 and every mandatory score >= 0.80
- `delivered_probable`: confidence >= 0.65
- `degraded_or_partial`: confidence >= 0.40
- `not_delivered_or_no_proof`: confidence below 0.40

## Scenario Defaults

The backend defines seven scenarios: `direct_ok`, `relay_ok`, `delayed`, `degraded`,
`domestic_only`, `blocked`, and `peer_offline`. Each scenario is deterministic so demos, tests,
and incident records are repeatable.

## Rationale

The geometric mean makes mandatory bottlenecks matter. Strong envelope evidence cannot hide weak
app delivery evidence. Support scores can improve confidence, but they cannot fully overcome a
failed mandatory layer.

