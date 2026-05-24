# Incident Summary Demo

This tool generates deterministic incident summaries from redacted local events. It does not call external LLM APIs by default.

```bash
python ai/incident-summary/incident_summary.py \
  --input security/detection/sample-events/route_policy_violation.json \
  --output runtime/reports/incident-summary.md \
  --mode deterministic
```

Optional local Ollama mode is documented but disabled by default. External API mode is not implemented.
