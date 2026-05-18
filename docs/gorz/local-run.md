# Gorz Local Run

Gorz now runs as a Python FastAPI backend plus a Vite React web UI.

## One-Command Demo

```bash
make gorz-install
make gorz-demo
```

`make gorz-demo` starts:

- Gorz Web: `http://localhost:5174`
- Gorz API: `http://localhost:8090/api/gorz/health`
- API Docs: `http://localhost:8090/docs`

## Local Checks

```bash
make gorz-test
make gorz-lint
make gorz-validate
```

If host Python tooling is unavailable, the Make targets use the Gorz API Docker image for backend
tests, linting, and validation.

## Demo Checklist

1. Create two local demo identities.
2. Create a local conversation.
3. Send messages under `direct_ok`, `degraded`, and `blocked`.
4. Compare confidence scores and evidence.
5. Generate an incident package.
6. Download the redacted JSON.
7. Review audit events.
8. Enable emergency pause and confirm sends are blocked.
9. Resume demo sends.

## Limits

The prototype does not perform external probing, public relay discovery, public network scanning,
automatic upload, or production secure messaging. Diagnostics are simulated and local-only.

