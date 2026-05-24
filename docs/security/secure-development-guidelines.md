# Secure Development Guidelines

- Do not add unsafe routing.
- Do not add public probing.
- Do not add sensitive Android permissions.
- Do not hardcode production secrets.
- Do not make production crypto claims.
- Redaction is required for evidence exports.
- Safety pause must remain enforceable.
- Every new feature must update safety checks when it changes routing, diagnostics, permissions, profile lifecycle, audit, or evidence behavior.
- Use `PRODUCTION_GAP:` comments for security-critical deferred work.
- Run `make production-readiness-check` before opening a PR.
