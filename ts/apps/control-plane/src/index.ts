import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import type { AddressInfo } from "node:net";

import {
  configRequestSignatureBase,
  configResponseSignatureBase,
  heartbeatSignatureBase,
  parseSignedHeaders,
  readJsonBody,
  sign,
  verify,
  type ClientConfig,
  type ClientConfigEnvelope,
  type HeartbeatRequest,
  type PathDescriptor,
  type QueueLimits,
} from "@gozar/shared";
import { SpanStatusCode, trace } from "@opentelemetry/api";
import { Resource } from "@opentelemetry/resources";
import { BatchSpanProcessor, ConsoleSpanExporter } from "@opentelemetry/sdk-trace-base";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { SemanticResourceAttributes } from "@opentelemetry/semantic-conventions";

type PreferredPath = "direct" | "relay";

interface NodeObservation {
  node_id: string;
  role: string;
  listen_addr: string;
  status: string;
  observed_at_unix: number;
}

interface ControlState {
  preferred_path: PreferredPath;
  switch_reason: string;
  relay_quic_addr: string;
  gateway_quic_addr: string;
  queue_limits: QueueLimits;
  nodes: Map<string, NodeObservation>;
}

interface AdminSwitchRequest {
  preferred_path: PreferredPath;
  switch_reason?: string;
}

const port = Number(process.env.PORT ?? "8080");
const controlSecret = process.env.CONTROL_SECRET ?? "gozar-local-shared-secret";
const adminToken = process.env.ADMIN_TOKEN ?? "gozar-admin-token";
const serviceName = process.env.OTEL_SERVICE_NAME ?? "gozar-control-plane";

const state: ControlState = {
  preferred_path: "direct",
  switch_reason: "default direct path for lab demo",
  relay_quic_addr: process.env.RELAY_QUIC_ADDR ?? "127.0.0.1:6100",
  gateway_quic_addr: process.env.GATEWAY_QUIC_ADDR ?? "127.0.0.1:6200",
  queue_limits: {
    client: Number(process.env.CLIENT_QUEUE_LIMIT ?? "16"),
    relay: Number(process.env.RELAY_QUEUE_LIMIT ?? "32"),
    gateway: Number(process.env.GATEWAY_QUEUE_LIMIT ?? "64"),
  },
  nodes: new Map(),
};

const tracer = initTelemetry(serviceName);

const server = createServer((req, res) => {
  tracer.startActiveSpan(`${req.method ?? "GET"} ${req.url ?? "/"}`, async (span) => {
    try {
      await route(req, res);
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : String(error),
      });
      writeJson(res, 500, {
        error: error instanceof Error ? error.message : "unexpected error",
      });
    } finally {
      span.end();
    }
  });
});

server.listen(port, () => {
  const address = server.address() as AddressInfo;
  console.log(
    JSON.stringify({
      level: "info",
      msg: "control plane ready",
      port: address.port,
      preferred_path: state.preferred_path,
    }),
  );
});

async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const method = req.method ?? "GET";
  const url = new URL(req.url ?? "/", "http://gozar-control-plane.local");

  if (method === "GET" && url.pathname === "/healthz") {
    writeJson(res, 200, { ok: true, service: "gozar-control-plane" });
    return;
  }

  if (method === "GET" && url.pathname === "/api/v1/client/config") {
    const headers = parseSignedHeaders(req);
    const payload = configRequestSignatureBase(headers.node_id, headers.timestamp, headers.nonce);
    if (!verify(controlSecret, payload, headers.signature)) {
      writeJson(res, 401, { error: "invalid control signature" });
      return;
    }

    const envelope = issueConfig(headers.node_id, headers.nonce);
    writeJson(res, 200, envelope);
    return;
  }

  if (method === "POST" && url.pathname === "/api/v1/nodes/heartbeat") {
    const headers = parseSignedHeaders(req);
    const heartbeat = await readJsonBody<HeartbeatRequest>(req);
    if (headers.node_id !== heartbeat.node_id) {
      writeJson(res, 400, { error: "header and body node ids differ" });
      return;
    }

    const payload = heartbeatSignatureBase(headers.node_id, headers.timestamp, headers.nonce, heartbeat);
    if (!verify(controlSecret, payload, headers.signature)) {
      writeJson(res, 401, { error: "invalid heartbeat signature" });
      return;
    }

    const observed_at_unix = nowUnix();
    state.nodes.set(heartbeat.node_id, {
      ...heartbeat,
      observed_at_unix,
    });

    writeJson(res, 200, {
      accepted: true,
      observed_at_unix,
    });
    return;
  }

  if (method === "POST" && url.pathname === "/api/v1/admin/preferred-path") {
    if (req.headers["x-gozar-admin-token"] !== adminToken) {
      writeJson(res, 401, { error: "missing or invalid admin token" });
      return;
    }

    const body = await readJsonBody<AdminSwitchRequest>(req);
    if (body.preferred_path !== "direct" && body.preferred_path !== "relay") {
      writeJson(res, 400, { error: "preferred_path must be direct or relay" });
      return;
    }

    state.preferred_path = body.preferred_path;
    state.switch_reason =
      body.switch_reason ?? `operator requested ${body.preferred_path} path`;

    writeJson(res, 200, {
      preferred_path: state.preferred_path,
      switch_reason: state.switch_reason,
    });
    return;
  }

  if (method === "GET" && url.pathname === "/api/v1/state") {
    if (req.headers["x-gozar-admin-token"] !== adminToken) {
      writeJson(res, 401, { error: "missing or invalid admin token" });
      return;
    }

    writeJson(res, 200, {
      preferred_path: state.preferred_path,
      switch_reason: state.switch_reason,
      queue_limits: state.queue_limits,
      nodes: Array.from(state.nodes.values()),
      paths: buildPaths(state),
    });
    return;
  }

  writeJson(res, 404, { error: "not found" });
}

function issueConfig(node_id: string, request_nonce: string): ClientConfigEnvelope {
  const config: ClientConfig = {
    node_id,
    preferred_path: state.preferred_path,
    switch_reason: state.switch_reason,
    valid_for_seconds: 30,
    queue_limits: state.queue_limits,
    paths: buildPaths(state),
  };

  const envelope: ClientConfigEnvelope = {
    request_nonce,
    issued_at_unix: nowUnix(),
    config,
    signature: "",
  };
  envelope.signature = sign(controlSecret, configResponseSignatureBase(envelope));
  return envelope;
}

function buildPaths(currentState: ControlState): PathDescriptor[] {
  return [
    {
      id: "direct",
      kind: "direct",
      ingress_addr: currentState.gateway_quic_addr,
      hops: ["gateway-1"],
      queue_limit: currentState.queue_limits.gateway,
    },
    {
      id: "relay",
      kind: "relay",
      ingress_addr: currentState.relay_quic_addr,
      hops: ["relay-1", "gateway-1"],
      queue_limit: currentState.queue_limits.relay,
    },
  ];
}

function writeJson(res: ServerResponse, statusCode: number, body: unknown): void {
  if (res.headersSent) {
    return;
  }

  const payload = JSON.stringify(body, null, 2);
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("content-length", Buffer.byteLength(payload));
  res.end(payload);
}

function nowUnix(): number {
  return Math.floor(Date.now() / 1000);
}

function initTelemetry(name: string) {
  const provider = new NodeTracerProvider({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: name,
    }),
  });
  provider.addSpanProcessor(new BatchSpanProcessor(new ConsoleSpanExporter()));
  provider.register();
  return trace.getTracer(name);
}
