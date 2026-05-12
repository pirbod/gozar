import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import type { AddressInfo } from "node:net";

import {
  CONTROL_MESSAGE_MAX_AGE_SECONDS,
  configRequestSignatureBase,
  heartbeatSignatureBase,
  parseSignedHeaders,
  readJsonBody,
  relayDirectoryRequestSignatureBase,
  verify,
  verifyTimestampFreshness,
  type HeartbeatRequest,
} from "@gozar/shared";
import { SpanStatusCode, trace } from "@opentelemetry/api";
import { Resource } from "@opentelemetry/resources";
import { BatchSpanProcessor, ConsoleSpanExporter } from "@opentelemetry/sdk-trace-base";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { SemanticResourceAttributes } from "@opentelemetry/semantic-conventions";

import {
  appendAuditLog,
  buildPaths,
  createRuntimeState,
  defaultPersistentState,
  issueConfigEnvelope,
  issueRelayDirectoryEnvelope,
  loadPersistentState,
  persistState,
  requestReplayKey,
  snapshotState,
  upsertNodeObservation,
  type AdminSwitchRequest,
  type ControlRuntimeState,
} from "./state";

class HttpError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
  ) {
    super(message);
  }
}

const port = Number(process.env.PORT ?? "8080");
const controlSecret = process.env.CONTROL_SECRET ?? "gozar-local-shared-secret";
const adminToken = process.env.ADMIN_TOKEN ?? "gozar-admin-token";
const serviceName = process.env.OTEL_SERVICE_NAME ?? "gozar-control-plane";
const stateFile =
  process.env.CONTROL_STATE_FILE ?? "./runtime/control-plane/control-plane-state.json";
const auditLogFile =
  process.env.AUDIT_LOG_FILE ?? "./runtime/control-plane/audit.log.ndjson";

const tracer = initTelemetry(serviceName);

start().catch((error) => {
  console.error(error);
  process.exit(1);
});

async function start(): Promise<void> {
  const persistent = await loadPersistentState(stateFile, defaultPersistentState(process.env));
  const state = createRuntimeState(persistent, {
    control_secret: controlSecret,
    admin_token: adminToken,
    state_file: stateFile,
    audit_log_file: auditLogFile,
  });

  await persistState(state);
  await appendAuditLog(state, "startup", {
    preferred_path: state.preferred_path,
    research_gateway_allowed: state.research_gateway_allowed,
  });

  const server = createServer((req, res) => {
    tracer.startActiveSpan(`${req.method ?? "GET"} ${req.url ?? "/"}`, async (span) => {
      try {
        await route(req, res, state);
        span.setStatus({ code: SpanStatusCode.OK });
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : String(error),
        });
        const statusCode = error instanceof HttpError ? error.statusCode : 500;
        writeJson(res, statusCode, {
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
        research_gateway_allowed: state.research_gateway_allowed,
      }),
    );
  });
}

async function route(
  req: IncomingMessage,
  res: ServerResponse,
  state: ControlRuntimeState,
): Promise<void> {
  const method = req.method ?? "GET";
  const url = new URL(req.url ?? "/", "http://gozar-control-plane.local");

  if (method === "GET" && url.pathname === "/healthz") {
    writeJson(res, 200, {
      ok: true,
      service: "gozar-control-plane",
      research_gateway_allowed: state.research_gateway_allowed,
    });
    return;
  }

  if (method === "GET" && url.pathname === "/api/v1/client/config") {
    // Every signed control read is freshness-checked and replay-checked before we even
    // look at the HMAC, which keeps stale nonces from driving route changes.
    const headers = parseSignedHeaders(req);
    verifyTimestampFreshness(headers.timestamp, CONTROL_MESSAGE_MAX_AGE_SECONDS);
    state.replay_cache.checkAndRecord(
      requestReplayKey("config", headers.node_id, headers.nonce),
      headers.timestamp,
    );

    const payload = configRequestSignatureBase(headers.node_id, headers.timestamp, headers.nonce);
    if (!verify(controlSecret, payload, headers.signature)) {
      throw new HttpError(401, "invalid control signature");
    }

    const envelope = issueConfigEnvelope(state, headers.node_id, headers.nonce);
    await appendAuditLog(state, "config_issued", {
      node_id: headers.node_id,
      request_nonce: headers.nonce,
      response_nonce: envelope.response_nonce,
      preferred_path: state.preferred_path,
    });
    writeJson(res, 200, envelope);
    return;
  }

  if (method === "GET" && url.pathname === "/api/v1/relay-directory") {
    const headers = parseSignedHeaders(req);
    verifyTimestampFreshness(headers.timestamp, CONTROL_MESSAGE_MAX_AGE_SECONDS);
    state.replay_cache.checkAndRecord(
      requestReplayKey("relay-directory", headers.node_id, headers.nonce),
      headers.timestamp,
    );

    const payload = relayDirectoryRequestSignatureBase(
      headers.node_id,
      headers.timestamp,
      headers.nonce,
    );
    if (!verify(controlSecret, payload, headers.signature)) {
      throw new HttpError(401, "invalid relay directory signature");
    }

    const envelope = issueRelayDirectoryEnvelope(state, headers.node_id, headers.nonce);
    await appendAuditLog(state, "relay_directory_issued", {
      node_id: headers.node_id,
      request_nonce: headers.nonce,
      response_nonce: envelope.response_nonce,
      relay_count: envelope.directory.entries.length,
    });
    writeJson(res, 200, envelope);
    return;
  }

  if (method === "POST" && url.pathname === "/api/v1/nodes/heartbeat") {
    // Heartbeats feed both the live in-memory view and the persisted audit trail so
    // experiments can correlate route decisions with what the control plane observed.
    const headers = parseSignedHeaders(req);
    verifyTimestampFreshness(headers.timestamp, CONTROL_MESSAGE_MAX_AGE_SECONDS);
    state.replay_cache.checkAndRecord(
      requestReplayKey("heartbeat", headers.node_id, headers.nonce),
      headers.timestamp,
    );

    const heartbeat = await readJsonBody<HeartbeatRequest>(req);
    if (headers.node_id !== heartbeat.node_id) {
      throw new HttpError(400, "header and body node ids differ");
    }

    const payload = heartbeatSignatureBase(headers.node_id, headers.timestamp, headers.nonce, heartbeat);
    if (!verify(controlSecret, payload, headers.signature)) {
      throw new HttpError(401, "invalid heartbeat signature");
    }

    const observed_at_unix = Math.floor(Date.now() / 1000);
    upsertNodeObservation(state, {
      ...heartbeat,
      observed_at_unix,
      features: heartbeat.features ?? [],
    });
    await persistState(state);
    await appendAuditLog(state, "heartbeat_accepted", {
      node_id: heartbeat.node_id,
      role: heartbeat.role,
      listen_addr: heartbeat.listen_addr,
      features: heartbeat.features ?? [],
    });

    writeJson(res, 200, {
      accepted: true,
      observed_at_unix,
    });
    return;
  }

  if (method === "POST" && url.pathname === "/api/v1/admin/preferred-path") {
    assertAdmin(req, state.admin_token);
    const body = await readJsonBody<AdminSwitchRequest>(req);
    if (body.preferred_path !== "direct" && body.preferred_path !== "relay") {
      throw new HttpError(400, "preferred_path must be direct or relay");
    }

    state.preferred_path = body.preferred_path;
    state.switch_reason = body.switch_reason ?? `operator requested ${body.preferred_path} path`;
    await persistState(state);
    await appendAuditLog(state, "preferred_path_updated", {
      preferred_path: state.preferred_path,
      switch_reason: state.switch_reason,
    });

    writeJson(res, 200, {
      preferred_path: state.preferred_path,
      switch_reason: state.switch_reason,
    });
    return;
  }

  if (method === "GET" && url.pathname === "/api/v1/state") {
    assertAdmin(req, state.admin_token);
    writeJson(res, 200, {
      ...snapshotState(state),
      paths: buildPaths(state),
    });
    return;
  }

  throw new HttpError(404, "not found");
}

function assertAdmin(req: IncomingMessage, expectedToken: string): void {
  const token = req.headers["x-gozar-admin-token"];
  if (token !== expectedToken) {
    throw new HttpError(401, "missing or invalid admin token");
  }
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