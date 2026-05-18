# Gorz API

Python FastAPI backend for the local Gorz prototype. It stores only demo data in SQLite,
computes confidence-aware delivery status, simulates diagnostics locally, exports redacted
incident packages, and records an audit trail.

This service is not production secure and is not for real sensitive communication. Demo
cryptography and diagnostics exist to show the architecture and product flow.

## Run

```bash
python -m pip install -e ".[dev]"
uvicorn gorz_api.main:app --host 127.0.0.1 --port 8090
```

## Test

```bash
pytest
ruff check .
mypy gorz_api
```

