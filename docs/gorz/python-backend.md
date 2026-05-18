# Python Backend

The Gorz backend lives in `python/gorz_api` and is the source of truth for local state,
confidence scoring, diagnostics, incidents, audit, and safety controls.

## Run Locally

```bash
python -m pip install -e "python/gorz_api[dev]"
uvicorn gorz_api.main:app --host 127.0.0.1 --port 8090
```

## Storage

SQLite is used by default at `runtime/gorz/gorz.sqlite3`. The schema includes identities,
devices, conversations, participants, messages, message evidence, incidents, audit events, and
safety state.

## Message Handling

The backend accepts plaintext only long enough to create a demo envelope. It stores:

- redacted preview
- simulated ciphertext
- envelope hash
- scenario
- delivery status
- confidence
- evidence
- redaction status

Plaintext body is not stored in the message record.

## Demo Cryptography

`crypto_demo.py` uses PyNaCl sealed boxes when available and a clearly labeled deterministic
fallback if needed. This is not production cryptography and must not be used for real sensitive
communication.

## Diagnostics

Diagnostics are deterministic local simulations. They do not scan, probe, or discover external
targets.

## Tests

```bash
cd python/gorz_api
pytest
ruff check .
mypy gorz_api
```

