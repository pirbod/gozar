import { createHmac } from "node:crypto";
import type { IncomingMessage } from "node:http";

export type PathKind = "direct" | "relay";

export interface PathDescriptor {
  id: string;
  kind: PathKind;
  ingress_addr: string;
  hops: string[];
  queue_limit: number;
}

export interface QueueLimits {
  client: number;
  relay: number;
  gateway: number;
}

export interface ClientConfig {
  node_id: string;
  preferred_path: string;
  switch_reason: string;
  valid_for_seconds: number;
  queue_limits: QueueLimits;
  paths: PathDescriptor[];
}

export interface ClientConfigEnvelope {
  request_nonce: string;
  issued_at_unix: number;
  config: ClientConfig;
  signature: string;
}

export interface HeartbeatRequest {
  node_id: string;
  role: string;
  listen_addr: string;
  status: string;
}

export interface HeartbeatResponse {
  accepted: boolean;
  observed_at_unix: number;
}

export interface SignedHeaders {
  node_id: string;
  timestamp: number;
  nonce: string;
  signature: string;
}

export function sign(secret: string, payload: string): string {
  return createHmac("sha256", secret).update(payload, "utf8").digest("hex");
}

export function verify(secret: string, payload: string, signature: string): boolean {
  return sign(secret, payload) === signature;
}

export function configRequestSignatureBase(node_id: string, timestamp: number, nonce: string): string {
  return `GET\n/api/v1/client/config\n${node_id}\n${timestamp}\n${nonce}`;
}

export function heartbeatSignatureBase(
  node_id: string,
  timestamp: number,
  nonce: string,
  payload: HeartbeatRequest,
): string {
  return [
    "POST",
    "/api/v1/nodes/heartbeat",
    node_id,
    String(timestamp),
    nonce,
    payload.role,
    payload.listen_addr,
    payload.status,
  ].join("\n");
}

function pathSummary(paths: PathDescriptor[]): string {
  return paths
    .map((path) => `${path.id}:${path.kind}:${path.ingress_addr}:${path.hops.join(">")}`)
    .join(",");
}

function queueSummary(queue_limits: QueueLimits): string {
  return `client=${queue_limits.client}|relay=${queue_limits.relay}|gateway=${queue_limits.gateway}`;
}

export function configResponseSignatureBase(envelope: ClientConfigEnvelope): string {
  return [
    "CONFIG",
    envelope.request_nonce,
    String(envelope.issued_at_unix),
    envelope.config.node_id,
    envelope.config.preferred_path,
    envelope.config.switch_reason,
    String(envelope.config.valid_for_seconds),
    pathSummary(envelope.config.paths),
    queueSummary(envelope.config.queue_limits),
  ].join("\n");
}

export function parseSignedHeaders(req: IncomingMessage): SignedHeaders {
  const node_id = getHeader(req, "x-gozar-node-id");
  const timestamp = Number(getHeader(req, "x-gozar-timestamp"));
  const nonce = getHeader(req, "x-gozar-nonce");
  const signature = getHeader(req, "x-gozar-signature");

  if (!Number.isFinite(timestamp)) {
    throw new Error("x-gozar-timestamp must be numeric");
  }

  return { node_id, timestamp, nonce, signature };
}

export async function readJsonBody<T>(req: IncomingMessage): Promise<T> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }

  const body = Buffer.concat(chunks).toString("utf8");
  if (!body) {
    throw new Error("request body is empty");
  }

  return JSON.parse(body) as T;
}

function getHeader(req: IncomingMessage, key: string): string {
  const value = req.headers[key];
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`missing header ${key}`);
  }
  return value;
}

