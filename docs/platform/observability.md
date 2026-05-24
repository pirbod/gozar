# Observability

The observability layer models Prometheus metrics, alert rules, and Grafana dashboards for the controlled release candidate.

## Metrics

- profile issuance count
- profile validation failure count
- revoked profile count
- expired profile count
- safety pause active
- evidence package generated count
- diagnostics run count
- route policy blocked count
- backend health
- API latency
- audit event count
- emulator smoke status
- readiness check status

## Alerts

Prometheus rules include `SafetyPauseActive`, `RoutePolicyViolationDetected`, `ProfileValidationFailuresHigh`, `EvidenceRedactionFailure`, `BackendUnavailable`, `EmulatorSmokeFailed`, and `ProductionReadinessFailed`.

## Dashboards

- Controlled Release Overview
- Security Operations View

Dashboard JSON lives under `observability/grafana/dashboards/`.

## Local Use

Render the Kubernetes config maps with:

```bash
make k8s-lint
```

Prometheus and Grafana server deployment is intentionally left as a local lab integration task.

## Screenshots

Required platform screenshots include Prometheus alerts and Grafana dashboard views. If capture is unavailable, the screenshot report must state SKIPPED.

## Production Gaps

Real scrape endpoints, alert routing, retention, access control, dashboard ownership, and production SLOs remain future work.
