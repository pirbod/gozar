# Incident Response Runbook

## Enable Safety Pause

Enable safety pause when a demo behaves unexpectedly, unsafe wording appears, validation fails, or an operator suspects misuse.

## Export Evidence

Generate a redacted evidence package from the UI. Do not collect packet payloads, contacts, phone numbers, exact location, or public IP history.

## Review Audit Logs

Review local audit timeline, Profile API audit export, and runtime logs. Keep exported evidence redacted.

## Revoke Profile

Use the Profile API settings/action flow or local validation scripts to revoke current demo profiles.

## Reset Local Demo State

Clear Android local state and run clean targets for backend/runtime state.

## Document Incident

Record:

- Date and time.
- Component.
- Trigger.
- Safety pause status.
- Evidence package path.
- Remediation.
- Follow-up owner.

## What Not To Collect

- Packet payloads.
- Contacts.
- Phone numbers.
- Exact location.
- Public IP history.
- Unredacted device or session identifiers.
