# Observability

## Current Assets

- `observability/otel-collector-config.yaml` provides a local debug OpenTelemetry collector configuration.
- Profile API and Gorz API expose local health endpoints.
- Local audit events are stored in runtime folders and Android app storage.
- Readiness and health scripts write reports to `runtime/reports`.

## Local Metrics And Logs

Current observability is local and demo-scoped. Docker logs, audit exports, and generated reports are the primary troubleshooting artifacts.

## Audit Log Locations

- `runtime/control-plane/audit.log.ndjson`
- `runtime/gorz`
- `runtime/profile`
- Android local audit timeline in app storage

## Future Production Gaps

- Central metrics.
- Alerting.
- Error budgets.
- Crash reporting.
- Log retention.
- Tenant-aware audit queries.
- Redaction verification.

## Redaction Requirements

Logs and reports must not include packet payloads, contacts, phone numbers, exact location, public IP history, or raw sensitive identifiers.
