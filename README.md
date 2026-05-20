# gozar

`gozar` is a censorship-resilience research prototype for studying multi-path QUIC overlays in controlled environments. It is designed for lawful academic evaluation, lab simulation, and consent-based pilots only. It is not a circumvention tool, not a field-deployment routing product, and not offensive tooling.

## Safety Disclaimer

This repository must be used only in environments where you are authorized to test. It intentionally avoids production claims and keeps high-risk features constrained:

- research gateway mode is disabled by default
- relay and gateway behavior are scoped to lab-only configuration
- QUIC trust is development-only
- control messages use demo HMAC signing plus replay checks
- simulation scripts target local Docker services for safe fault injection

See [docs/safety-boundaries.md](docs/safety-boundaries.md).

## What The Prototype Does

- runs a Rust desktop client, relay, gateway, and echo service over a QUIC-first overlay
- exposes a TypeScript control plane with signed config and signed relay-directory responses
- scores direct and relay paths on the client and logs the score breakdown
- supports a lab-only research gateway mode for controlled HTTP forwarding tests
- persists control-plane state and writes audit logs for operator actions and node observations
- includes store-and-forward and mesh-adapter skeletons for future research

## Current Research Features

- Signed client config responses
- Signed relay directory responses
- Replay protection for control messages
- Persistent control-plane state in `runtime/control-plane`
- Audit log output in `runtime/control-plane/audit.log.ndjson`
- Per-hop queue-limit visibility in returned route metadata
- Client path scoring with logged rationale
- Lab-only HTTP forwarding when explicitly enabled
- Fault-injection scripts for outage, latency, and loss simulations

## Repository Layout

```text
gozar/
|- rust/
|  |- crates/gozar-core/
|  |- services/desktop-client/
|  |- services/relay/
|  |- services/gateway/
|  `- services/echo-service/
|- ts/
|  |- packages/shared/
|  `- apps/control-plane/
|- docs/
|- eval/
|- observability/
|- scripts/simulations/
|- docker-compose.yml
`- .github/workflows/ci.yml
```

## Quick Start

Default demo mode keeps research HTTP forwarding off:

```bash
docker compose up --build
```

Send traffic through the default direct path:

```bash
printf 'hello from gozar\n' | nc 127.0.0.1 7000
```

Switch the preferred path to the relay route:

```bash
curl -X POST http://127.0.0.1:8080/api/v1/admin/preferred-path \
  -H 'content-type: application/json' \
  -H 'x-gozar-admin-token: gozar-admin-token' \
  -d '{"preferred_path":"relay","switch_reason":"simulate direct path degradation"}'
```

Check control-plane state:

```bash
curl http://127.0.0.1:8080/api/v1/state \
  -H 'x-gozar-admin-token: gozar-admin-token'
```

## Research Gateway Mode

Enable the controlled lab HTTP forwarder explicitly:

```bash
GOZAR_ENABLE_RESEARCH_GATEWAY=true docker compose up --build
```

Then test a safe internal HTTP target through the overlay:

```bash
curl 'http://127.0.0.1:7100/research-fetch?url=http://control-plane:8080/healthz'
```

The gateway will only forward to configured lab allowlist origins. By default that allowlist is:

```text
http://control-plane:8080
```

See [docs/research-gateway.md](docs/research-gateway.md).

## Research Evaluation Platform

Gozar now includes a local-first evaluation platform for measuring adaptive path behavior under simulated blocking, outage, latency, loss, and bandwidth constraints. The goal is to support reproducible PhD research evidence in a controlled lab, not to claim production circumvention capability.

```bash
make eval-baseline
make eval-adaptive
make eval
make eval-clean
```

Results are written to `eval/results/latest/results.json` and `eval/results/latest/summary.md`. See [docs/evaluation.md](docs/evaluation.md) for run details and [docs/research-alignment.md](docs/research-alignment.md) for the research-question-to-metric mapping.

## Gorz

Gorz is now a local-first, Python-backed messaging prototype for confidence-aware delivery and
redacted incident evidence. It remains a prototype, uses demo cryptography, and is not for real
sensitive communication.

### What Changed

- FastAPI backend in `python/gorz_api`.
- SQLite persistence for demo identities, conversations, envelopes, evidence, incidents, audit,
  and safety state.
- Python confidence engine and local diagnostic simulator.
- Redacted incident package generation and downloadable JSON.
- React UI backed by the Python API.
- Gorz-specific Docker Compose, Makefile targets, validation script, and CI workflow.

### Run The Demo

```bash
make gorz-install
make gorz-demo
```

After `make gorz-demo` starts services:

- Gorz Web: `http://localhost:5174`
- Gorz API: `http://localhost:8090/api/gorz/health`
- API Docs: `http://localhost:8090/docs`

### Safety Boundaries

- Local demo only.
- Simulated diagnostics only.
- Not production secure.
- Not a field-deployment routing product.
- Not for real sensitive communication.
- No public network scanning, bridge discovery, relay discovery, real IP collection, exact location
  collection, phone number collection, or automatic diagnostic upload.

### Demo Flow

Create two demo identities, create a conversation, send messages under `direct_ok`, `degraded`, and
`blocked`, inspect the confidence evidence, export a redacted incident package, review the audit
trail, enable emergency pause, confirm sends are blocked, then resume.

### Gorz Docs

- [Production prototype plan](docs/gorz/production-prototype-plan.md)
- [API contract](docs/gorz/api-contract.md)
- [Python backend](docs/gorz/python-backend.md)
- [Confidence model](docs/gorz/confidence-model.md)
- [Redaction policy](docs/gorz/redaction-policy.md)
- [Demo script](docs/gorz/demo-script.md)
- [Prototype safety boundaries](docs/gorz/prototype-safety-boundaries.md)
- [Homebrew install](docs/gorz/homebrew-install.md)

## Adaptive Session Profile Phase 1

Phase 1 adds a local-only adaptive session profile service in `python/profile_api`. It demonstrates
short-lived signed encrypted demo profiles, deterministic policy selection, profile validation,
revocation, redacted audit export, and safety pause handling.

```bash
make profile-install
make profile-demo
```

After `make profile-demo` starts the service:

- Profile API: `http://localhost:8095/api/profile/health`
- API docs: `http://localhost:8095/docs`

Safety boundaries:

- Local-only Docker demo.
- Signed encrypted demo profiles only.
- No OS VPN install.
- No real VPN tunnel.
- No public gateways.
- No public network probing.
- No public relay discovery.
- Not production secure.
- Not for real sensitive communication.

See [docs/vpn-product/phase-1-local-profile-lifecycle.md](docs/vpn-product/phase-1-local-profile-lifecycle.md).

## Android Phase 2 Prototype

Phase 2 adds a minimal Android app with Connect / Disconnect and Settings. It uses Android `VpnService` for local VPN lifecycle validation only and requests short-lived signed encrypted demo profiles from the local Profile API. It does not install a production VPN profile, does not forward traffic to public gateways, does not perform public network probing, and does not route `0.0.0.0/0` in Phase 2.

Safety boundaries:

- Android local VPN lifecycle prototype.
- Adaptive session profile from the local Profile API.
- Signed encrypted profile with short-lived demo config.
- Deterministic policy engine.
- Controlled lab gateway profile shape only.
- No public gateway.
- No public network probing.
- No public relay discovery.
- Not production secure.
- Not for real sensitive communication.

Run the local Profile API:

```bash
make profile-demo
```

Then in another terminal:

```bash
make android-check
make phase2-check
```

Android Studio:

- Open `android/gorz`.
- Run the app on an emulator.
- Use Profile API URL `http://10.0.2.2:8095`.
- Tap Connect.
- Grant VPN permission.
- Confirm status becomes Connected.
- Tap Disconnect.

Prototype screenshot:
[docs/vpn-product/images/android-phase2-screenshot.png](docs/vpn-product/images/android-phase2-screenshot.png)

See [docs/vpn-product/phase-2-android-vpnservice.md](docs/vpn-product/phase-2-android-vpnservice.md).

## Install Gorz with Homebrew

```bash
brew install pirbod/tap/gorz
gorz doctor
gorz demo
```

After `gorz demo` starts the local prototype:

```text
Web:      http://localhost:5174
API:      http://localhost:8090/api/gorz/health
API docs: http://localhost:8090/docs
```

Caveats:

- Requires Docker Desktop or Docker Engine with the Compose plugin.
- Installs a CLI launcher that manages the local prototype.
- Does not install a production messenger.
- Does not enable public relay or external probing.

See [docs/gorz/homebrew-install.md](docs/gorz/homebrew-install.md) for tap setup and release
instructions.

## CI Coverage

[.github/workflows/ci.yml](.github/workflows/ci.yml) now runs four layers:

- `rust`: format, clippy, and workspace tests
- `typescript`: typecheck, TypeScript tests, and build verification
- `e2e`: Docker smoke test for direct path, relay path, default-disabled research gateway, and explicitly enabled research gateway mode
- `eval-smoke`: CI-safe evaluation run with generated result artifacts

## Simulation Scripts

Lab-only simulation helpers live in [scripts/simulations](scripts/simulations):

- `partial-outage.sh`
- `relay-failure.sh`
- `high-latency.sh`
- `packet-loss.sh`
- `gateway-unavailable.sh`
- `clear-netem.sh`

These scripts are intended for local Docker-based experiments only.

## Docs

- [Architecture](docs/architecture.md)
- [Threat model](docs/threat-model.md)
- [Local run instructions](docs/local-run.md)
- [Research gateway mode](docs/research-gateway.md)
- [Signed relay directory](docs/relay-directory.md)
- [Path scoring](docs/path-scoring.md)
- [Store-and-forward skeleton](docs/store-forward.md)
- [Evaluation platform](docs/evaluation.md)
- [Research alignment](docs/research-alignment.md)
- [Safety boundaries](docs/safety-boundaries.md)
- [Gorz product brief](docs/gorz/product-brief.md)
- [Gorz architecture](docs/gorz/architecture.md)
- [Gorz threat model](docs/gorz/threat-model.md)
- [Gorz safety model](docs/gorz/safety-model.md)
- [Gorz incident record schema](docs/gorz/incident-record-schema.md)
- [Gorz local run](docs/gorz/local-run.md)
- [ADR 0001: Polyglot monorepo layout](docs/adr/0001-polyglot-monorepo.md)
- [ADR 0002: QUIC-first multi-path overlay](docs/adr/0002-quic-first-multipath.md)
- [ADR 0003: HMAC control messages for demo safety](docs/adr/0003-authenticated-control-messages.md)

## Known Limitations

- This is still a research prototype, not a production system.
- QUIC certificates are generated for development convenience only.
- Control-plane authentication uses a shared secret for demo simplicity.
- The research gateway is intentionally narrow and does not attempt generic web compatibility.
- Store-and-forward and mesh adapters are scaffolding for future milestones, not finished subsystems.
