# Contributing

## Run Checks

```bash
make production-readiness-check
make safety-check
make docs-check
```

Use language-specific checks when touching those areas:

```bash
make profile-test
make gorz-test
make android-check
make eval-smoke
```

## Add Android Features Safely

- Keep local lifecycle wording.
- Do not add sensitive permissions.
- Do not add full-device routes.
- Add Compose test tags for new screens.
- Update Android safety checks if route or permission behavior changes.

## Add Backend Features Safely

- Keep diagnostics local or simulated.
- Preserve safety pause.
- Redact evidence and audit data.
- Add tests for admin, validation, and redaction behavior.

## Update Docs

Update product, security, privacy, operations, and release docs when behavior or gaps change.

## Required Safety Checks Before PR

- `make production-readiness-check`
- `make android-safety-check`
- `make backend-safety-check`
- `make safety-wording-check`

## Commit Message Guidance

Use short imperative messages, for example `Add production readiness report`.

## PR Checklist

Use `.github/pull_request_template.md` and document any production gaps explicitly.
