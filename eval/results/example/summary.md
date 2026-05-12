# Synthetic Example Evaluation Summary

This report is example data only. It is included to demonstrate the shape of generated evaluation output and must not be cited as a measured benchmark.

| Scenario | Mode | Impairment | Success Rate | Median Latency (ms) | P95 Latency (ms) | Path Switches |
|---|---|---|---:|---:|---:|---:|
| baseline-direct | static-direct | none | 1.000 | 8.2 | 12.9 | 0 |
| baseline-relay | static-relay | none | 1.000 | 15.4 | 21.8 | 0 |
| adaptive-failover | adaptive | relay_outage | 0.850 | 11.6 | 31.2 | 1 |

## Short Interpretation

The synthetic baseline rows illustrate how direct and relay modes can be compared in the same local Docker lab. The synthetic adaptive row shows the intended reporting pattern for a relay outage: failures are counted, a path switch is recorded, and recovery timing is reported only after a later request succeeds.

## Limitations

- The numbers above are invented example values, not empirical results.
- The local Docker lab cannot represent internet-scale censorship behavior by itself.
- Netem impairments model selected link symptoms, not a complete adversary.

## Next Experiment Suggestions

- Run `make eval-baseline` to collect measured direct and relay reference values.
- Run `make eval-adaptive` to validate failover timing in the local lab.
- Repeat packet-loss scenarios across multiple runs before drawing conclusions.
