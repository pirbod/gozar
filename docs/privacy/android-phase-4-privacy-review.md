# Android Phase 4 Privacy Review

## Data Map

The Android app stores demo settings, local profile metadata, safety pause state, audit events, diagnostics counters, evidence JSON, and optional screenshot artifacts.

## Local Storage Inventory

Local SharedPreferences hold demo state and default secure value storage. Experimental Android Keystore storage can encrypt values, but it is not the default.

## Evidence Export Inventory

Evidence includes redacted device and session references, confidence signals, route policy result, diagnostics summary, safety pause state, storage mode, audit event count, operator note, screenshot references, and checksum.

## Screenshot Inventory

Screenshots are operator-created artifacts stored under `docs/vpn-product/images/phase4/` or reported as skipped. They may contain visible local state and should be reviewed before sharing.

## Diagnostics Inventory

Diagnostics include local endpoint status, route validation, confidence status, storage mode, safety pause state, packet counters, and mock path quality. They do not collect packet contents.

## Permission Review

The manifest avoids contacts, phone number, and location permissions. VPN permission is used for local lifecycle validation.

## Data Not Collected

No contacts, phone numbers, exact location, coarse location, public IP history, packet contents, or automatic diagnostics upload.

## User-Initiated Export Only

Evidence sharing uses the Android share sheet and requires operator action.

## Deletion Workflow

Settings can reset local identity, clear audit history, clear diagnostics, clear secure storage, and clear evidence. Android app storage can also be cleared from system settings.

## Retention Gap

Formal retention policy and deletion SLAs are not implemented.

## Production Privacy Policy Gap

A reviewed production privacy policy and data processing map are required before real alpha or production expansion.
