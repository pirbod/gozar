# Local Run Instructions

## Prerequisites

- Docker and Docker Compose for the containerized path.
- Or a local Rust toolchain plus Node.js 20+ if you want to run services directly.

This repository was scaffolded in an environment that did not have Rust, Node, or Docker installed, so the commands below are provided as the intended run path and should be executed on a machine with those toolchains available.

## Option 1: Docker Compose

Bring the whole lab up:

```bash
docker compose up --build
```

Expected externally reachable ports:

- `7000`: desktop client local edge listener
- `8080`: control plane

Send a test message from a Unix-like shell:

```bash
printf 'hello from direct path\n' | nc 127.0.0.1 7000
```

Send a test message from PowerShell:

```powershell
$client = [System.Net.Sockets.TcpClient]::new("127.0.0.1", 7000)
$stream = $client.GetStream()
$writer = [System.IO.StreamWriter]::new($stream)
$writer.AutoFlush = $true
$reader = [System.IO.StreamReader]::new($stream)
$writer.WriteLine("hello from direct path")
$reader.ReadLine()
$client.Dispose()
```

Force the relay path:

```bash
curl -X POST http://127.0.0.1:8080/api/v1/admin/preferred-path \
  -H 'content-type: application/json' \
  -H 'x-gozar-admin-token: gozar-admin-token' \
  -d '{"preferred_path":"relay","switch_reason":"simulate direct path degradation"}'
```

Inspect control-plane state:

```bash
curl http://127.0.0.1:8080/api/v1/state \
  -H 'x-gozar-admin-token: gozar-admin-token'
```

## Option 2: Run Components Directly

Install TypeScript dependencies:

```bash
npm install
npm run build:ts
```

Run the control plane:

```bash
npm run dev:control-plane
```

In separate terminals, run the Rust services:

```bash
cargo run --bin echo-service
cargo run --bin gateway
cargo run --bin relay
cargo run --bin desktop-client
```

Recommended local environment variables for direct execution:

```bash
export GOZAR_CONTROL_PLANE_URL=http://127.0.0.1:8080
export GOZAR_CONTROL_SECRET=gozar-local-shared-secret
```

On Windows PowerShell:

```powershell
$env:GOZAR_CONTROL_PLANE_URL = "http://127.0.0.1:8080"
$env:GOZAR_CONTROL_SECRET = "gozar-local-shared-secret"
```

## What Success Looks Like

A successful client response looks roughly like this:

```text
trace=<uuid> path=relay route=relay-1(depth=1/32) -> gateway-1(depth=1/64) terminus=echo-service payload=echo-service observed: hello from relay path
```

