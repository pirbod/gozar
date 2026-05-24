# SIEM-Style Detection Logic

The detection layer uses local YAML rules and redacted sample events. It does not require Splunk, Elastic, Wazuh, Microsoft Sentinel, Chronicle, or any external SIEM.

## Strategy

Rules focus on controlled release safety and readiness events: route policy violations, sensitive Android permissions, profile validation failures, safety pause, evidence redaction failures, local admin token failures, emulator smoke failures, and unusual demo state changes.

## Testing

```bash
make detection-check
```

The script loads rules and sample JSON events, evaluates simple field equality conditions, and writes:

- `runtime/reports/siem-detection-report.md`
- `runtime/reports/siem-detection-report.json`

## Limitations

The local evaluator is intentionally simple. Future integrations can translate these rules to Splunk, Elastic, Wazuh, Microsoft Sentinel, or Chronicle.

## Safety Boundary

Events must remain redacted and local. The test script does not call external systems.
