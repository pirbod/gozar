# Research Gateway Mode

`gozar` now includes a controlled research-gateway mode for lab HTTP forwarding tests. This mode exists to support academic measurement and consent-based pilot experiments. It is disabled by default and must be explicitly enabled by the operator.

## Safety Boundaries

- This is not a production browser proxy.
- It is not a generic circumvention appliance.
- It must only be used in environments where the operator is authorized to test.
- The implementation intentionally restricts forwarding to a configured allowlist of lab origins.
- The default Docker flow keeps the feature off.

## Enable It

```bash
GOZAR_ENABLE_RESEARCH_GATEWAY=true docker compose up --build
```

When enabled:

- The desktop client binds a local lab-only HTTP listener on `127.0.0.1:7100`.
- The gateway accepts `research_http` overlay requests.
- The control plane marks `research_gateway_allowed: true` in the signed client config.
- The gateway only forwards to `GOZAR_RESEARCH_ALLOWED_ORIGINS`.

Default allowlist:

```text
http://control-plane:8080
```

## Local Test

```bash
curl 'http://127.0.0.1:7100/research-fetch?url=http://control-plane:8080/healthz'
```

Expected result:

- HTTP `200`
- body containing `gozar-control-plane`
- `x-gozar-path`, `x-gozar-route`, and `x-gozar-terminus` headers showing the overlay route

## Design Notes

- The desktop client exposes a local HTTP shim instead of a transparent OS-wide interception path.
- Only `GET` and `HEAD` are supported.
- The gateway enforces the lab allowlist before making an upstream request.
- The overlay still uses the same QUIC relay/gateway path as the echo demo.
- Route choice is based on the client path-scoring module.