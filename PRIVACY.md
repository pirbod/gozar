# Privacy

## Local-First Prototype

Gozar/Gorz is a local-first controlled prototype. Most generated state is stored under `runtime/` or local Android app storage.

## Data Not Collected

- No phone number collection.
- No contact collection.
- No exact location collection.
- No public IP history collection.
- No automatic diagnostic upload.

## Evidence Export

Evidence export is user-initiated. Evidence packages are redacted and should not contain packet payloads, raw device IDs, raw session IDs, contacts, location, or public IP history.

## Diagnostics

Diagnostics are simulated and local-only unless explicitly documented otherwise. Android packet counters are local diagnostics only and packets are dropped.

## Data Retention For Local Demo

Local demo data may remain in `runtime/`, browser storage, Android app storage, or Docker volumes until the operator clears it.

## Delete Local Demo Data

Use:

```bash
make gorz-clean
make profile-clean
make eval-clean
```

On Android, use Settings to reset local identity, clear audit history, and clear diagnostics. Android system app storage can also be cleared from device settings.

## Production Privacy Policy Gap

A reviewed privacy policy, data map, retention policy, and deletion workflow are required before real alpha pilots.

## Phase 4 Privacy Review

The Android Phase 4 privacy review is documented in `docs/privacy/android-phase-4-privacy-review.md`. Evidence export remains user initiated, diagnostics remain local-only, and screenshots are operator-managed artifacts that require review before sharing.
