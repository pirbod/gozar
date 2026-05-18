# Redaction Policy

Gorz incident packages are designed for safe local demos and stakeholder review. They are not
automatic submissions.

## Removed

- Plaintext message body.
- Phone-like values in free text.
- IP-like values in free text.
- Exact locations, which are never collected by the prototype.

## Hashed

- Internal message identifiers.
- Internal conversation identifiers.

Hashes are truncated SHA-256 values for local package readability.

## Bucketed

- Incident timestamps.
- Message timestamps in incident exports.

Timestamps are bucketed to 15-minute windows.

## Withheld

- Raw ciphertext download as a standalone artifact.
- Demo private key material.
- Browser-local state.

## Metadata Included

- Redaction summary.
- Classification.
- Confidence.
- Layer scores.
- Envelope hash.
- Safety notes.
- Fusion model summary.

