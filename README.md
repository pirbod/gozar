# gozar

`gozar` is a lawful academic research prototype for studying resilient communications overlays. It is intentionally framed as defensive networking research: it explores how a desktop-edge client can feel VPN-like to the user while using a QUIC-first multi-path overlay instead of a single static tunnel.

## Safety Disclaimer

This repository is not offensive tooling, not malware, and not a productized circumvention system. It is a minimal, local-first research prototype for lawful experimentation in controlled environments. Do not deploy it to networks or jurisdictions where you do not have authorization to test. The demo uses development-only trust assumptions, including locally generated QUIC certificates and a shared control-plane secret, and must not be treated as production-grade security software.

## Project Status

The repository is now in a solid prototype state:

- Rust CI is green for formatting, clippy, and workspace tests.
- TypeScript CI is green for workspace typechecking and builds.
- GitHub Actions includes an end-to-end Docker smoke test that verifies both overlay paths.
- Docker Compose startup is hardened with a control-plane healthcheck, dependency gating, and recurring relay/gateway heartbeats.

## Verified Flows

These flows have been exercised against the live demo stack:

- `direct`: desktop client -> gateway -> echo service
- `relay`: desktop client -> relay -> gateway -> echo service
- Control-plane path switching from `direct` to `relay`
- Per-hop queue metadata visible in returned route strings
- Node registration visible through `/api/v1/state`

## What Is Included

- A Rust desktop-edge client that exposes a local TCP socket and forwards newline-delimited application traffic over the overlay.
- A Rust relay that receives QUIC traffic, enforces a queue limit, forwards to the gateway, and now re-heartbeats until the control plane is available.
- A Rust gateway that receives QUIC traffic, enforces a queue limit, forwards to a local echo service, and now re-heartbeats until the control plane is available.
- A Rust local echo service used to demonstrate safe end-to-end flow.
- A TypeScript control plane with authenticated control messages, path preference updates, in-memory node heartbeat tracking, and a `/healthz` endpoint for orchestration.
- OpenTelemetry bootstrap for Rust and TypeScript services.
- Docker Compose for local dev and GitHub Actions for Rust, TypeScript, and end-to-end CI.

## Demo Shape

The overlay has two available paths:

- `direct`: desktop client -> gateway
- `relay`: desktop client -> relay -> gateway

The client polls the control plane for a signed path preference and also has path switching hooks for runtime failures. Each hop appends queue-depth information to the returned route so the demo makes hop-level flow governance visible.

## Monorepo Layout

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
|- observability/
|- docker-compose.yml
`- .github/workflows/ci.yml
```

## Quick Start

The simplest path is Docker Compose:

```bash
docker compose up --build
```

Then send a line of traffic to the desktop client:

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

The client polls every five seconds by default, so the next line sent to `7000` should show the relay hop in the returned route.

For more complete instructions, see [docs/local-run.md](docs/local-run.md).

## CI Coverage

The repository now has three CI layers in [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

- `rust`: `cargo fmt --check`, `cargo clippy`, and `cargo test`
- `typescript`: workspace typecheck and build verification
- `e2e`: Docker Compose smoke test that waits for the control plane, verifies node registration, sends a `direct` message, switches to `relay`, and verifies relay-path traffic

## Design Notes

- QUIC is used for the overlay links.
- Path choice is controlled by a signed control-plane response and a local fallback hook.
- Each forwarding hop uses the shared `InFlightQueue` interface to cap in-flight work.
- Queue depth and hop identity are returned in the response so local testing can observe path behavior.
- The control plane and services exchange authenticated control messages using an HMAC-based envelope.
- Compose orchestration now treats control-plane readiness explicitly instead of relying on container start order alone.

## Docs

- [Architecture](docs/architecture.md)
- [Threat model](docs/threat-model.md)
- [Local run instructions](docs/local-run.md)
- [ADR 0001: Polyglot monorepo layout](docs/adr/0001-polyglot-monorepo.md)
- [ADR 0002: QUIC-first multi-path overlay](docs/adr/0002-quic-first-multipath.md)
- [ADR 0003: HMAC control messages for demo safety](docs/adr/0003-authenticated-control-messages.md)

## Known Limitations

- The demo uses generated development certificates and a shared secret.
- There is no persistence, key rotation, congestion control tuning, NAT traversal, or kernel-level tunnel device.
- The desktop client is a local edge proxy shim, not a full OS-integrated VPN adapter.
- Observability currently exports to stdout by default; an OTLP collector config is provided for future extension.
- The e2e CI job is a smoke test, not a full fault-injection or performance test harness.
