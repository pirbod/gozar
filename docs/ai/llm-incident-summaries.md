# LLM-Generated Incident Summaries

The incident summary demo produces local deterministic summaries from redacted events. It is designed to demonstrate how AI-assisted security operations could be reviewed without requiring an external provider.

## Deterministic Mode

```bash
make incident-summary-demo
```

This writes `runtime/reports/incident-summary.md` without internet access.

## Optional Local LLM Mode

`ollama-local` is documented as a future local-only option, but it is disabled by default.

## External API Mode

External API mode is not implemented for the controlled release candidate.

## Privacy Boundaries

Inputs must not include raw device IDs, raw session IDs, tokens, keys, packet contents, public IP history, contacts, phone numbers, or location.

## SOC Workflow Support

The summary includes incident title, severity, affected component, what happened, why it matters, safety boundary impact, recommended action, evidence references, and limitations.

## Limitations

The deterministic output is a reviewer aid, not a security review completion or production incident response system.
