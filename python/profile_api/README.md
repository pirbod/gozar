# Profile API

`profile-api` is a local-only FastAPI service for demonstrating the Phase 1 adaptive session profile lifecycle. It issues short-lived signed encrypted demo profiles for registered local demo devices, validates TTL and revocation state, and exports redacted audit evidence.

It does not create a real VPN, install OS VPN profiles, use public gateways, perform public network probing, or make production security claims. The generated payloads are simulated WireGuard-like or QUIC-like profile documents for local Docker development only.

## Run Locally

```bash
python3 -m pip install -e "python/profile_api[dev]"
uvicorn profile_api.main:app --reload --host 0.0.0.0 --port 8095
```

Open:

- Profile API: `http://localhost:8095/api/profile/health`
- API docs: `http://localhost:8095/docs`

## Lifecycle Demo

```bash
python3 scripts/profile/run_profile_lifecycle_demo.py
```

The demo client generates a device keypair locally, registers the public key, requests a signed encrypted profile envelope, verifies the signature, decrypts the profile locally, validates it, revokes it, validates again, and exports a redacted audit bundle.

The demo client private key exists only for local Phase 1 demonstration and is never sent to or stored by the API.

