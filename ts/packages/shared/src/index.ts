import { createHmac, randomUUID } from "node:crypto";
import type { IncomingMessage } from "node:http";

export const CONTROL_MESSAGE_MAX_AGE_SECONDS = 120;

export type PathKind = "direct" | "relay";

export interface PathDescriptor {
  id: string;
  kind: PathKind;
  ingress_addr: string;
  hops: string[];
  queue_limit: number;
  relay_id?: string | null;
  last_observed_at_unix?: number | null;
  operator_preference?: number;
  supports_research_gateway?: boolean;
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
  research_gateway_allowed: boolean;
}

export interface ClientConfigEnvelope {
  request_nonce: string;
  response_nonce: string;
  issued_at_unix: number;
  config: ClientConfig;
  signature: string;
}

export interface RelayDirectoryEntry {
  relay_id: string;
  ingress_addr: string;
  gateway_addr: string;
  observed_at_unix: number;
  status: string;
  queue_limit: number;
  supports_research_gateway: boolean;
  features: string[];
}

export interface RelayDirectory {
  requester_node_id: string;
  valid_for_seconds: number;
  entries: RelayDirectoryEntry[];
}

export interface RelayDirectoryEnvelope {
  request_nonce: string;
  response_nonce: string;
  issued_at_unix: number;
  directory: RelayDirectory;
  signature: string;
}

export interface HeartbeatRequest {
  node_id: string;
  role: string;
  listen_addr: string;
  status: string;
  features: string[];
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

// The shared replay cache gives both the control plane and tests the same simple
// duplicate-detection behavior without introducing a database dependency.
export class ReplayCache {
  private readonly seen = new Map<string, number>();

  constructor(private readonly ttlSeconds: number) {}

  checkAndRecord(key: string, observedAtUnix: number): void {
    for (const [candidate, timestamp] of this.seen.entries()) {
      if (observedAtUnix - timestamp > this.ttlSeconds) {
        this.seen.delete(candidate);
      }
    }

    if (this.seen.has(key)) {
      throw new Error(`replayed control message detected for key ${key}`);
    }

    this.seen.set(key, observedAtUnix);
  }
}

export function nowUnix(): number {
  return Math.floor(Date.now() / 1000);
}

export function controlRequestNonce(): string {
  return randomUUID();
}

export function controlResponseNonce(): string {
  return randomUUID();
}

export function sign(secret: string, payload: string): string {
  return createHmac("sha256", secret).update(payload, "utf8").digest("hex");
}

export function verify(secret: string, payload: string, signature: string): boolean {
  return sign(secret, payload) === signature;
}

export function verifyTimestampFreshness(
  timestamp: number,
  maxAgeSeconds: number = CONTROL_MESSAGE_MAX_AGE_SECONDS,
): void {
  const age = nowUnix() - timestamp;
  if (age > maxAgeSeconds) {
    throw new Error(`control message timestamp is stale: age=${age}s max=${maxAgeSeconds}s`);
  }
}

export function configRequestSignatureBase(node_id: string, timestamp: number, nonce: string): string {
  return `GET\n/api/v1/client/config\n${node_id}\n${timestamp}\n${nonce}`;
}

export function relayDirectoryRequestSignatureBase(
  node_id: string,
  timestamp: number,
  nonce: string,
): string {
  return `GET\n/api/v1/relay-directory\n${node_id}\n${timestamp}\n${nonce}`;
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
    payload.features.join(","),
  ].join("\n");
}

function pathSummary(paths: PathDescriptor[]): string {
  return paths
    .map(
      (path) =>
        `${path.id}:${path.kind}:${path.ingress_addr}:${path.hops.join(">")}:${path.queue_limit}:${path.relay_id ?? ""}:${path.last_observed_at_unix ?? 0}:${path.operator_preference ?? 0}:${Boolean(path.supports_research_gateway)}`,
    )
    .join(",");
}

function queueSummary(queue_limits: QueueLimits): string {
  return `client=${queue_limits.client}|relay=${queue_limits.relay}|gateway=${queue_limits.gateway}`;
}

function directorySummary(entries: RelayDirectoryEntry[]): string {
  return entries
    .map(
      (entry) =>
        `${entry.relay_id}:${entry.ingress_addr}:${entry.gateway_addr}:${entry.observed_at_unix}:${entry.status}:${entry.queue_limit}:${entry.supports_research_gateway}:${entry.features.join("+")}`,
    )
    .join(",");
}

// Signature-base helpers stay explicit and stable because both the TypeScript control
// plane and Rust client verify the exact same byte-for-byte control envelopes.
export function configResponseSignatureBase(envelope: ClientConfigEnvelope): string {
  return [
    "CONFIG",
    envelope.request_nonce,
    envelope.response_nonce,
    String(envelope.issued_at_unix),
    envelope.config.node_id,
    envelope.config.preferred_path,
    envelope.config.switch_reason,
    String(envelope.config.valid_for_seconds),
    pathSummary(envelope.config.paths),
    queueSummary(envelope.config.queue_limits),
    String(envelope.config.research_gateway_allowed),
  ].join("\n");
}

export function relayDirectoryResponseSignatureBase(envelope: RelayDirectoryEnvelope): string {
  return [
    "DIRECTORY",
    envelope.request_nonce,
    envelope.response_nonce,
    String(envelope.issued_at_unix),
    envelope.directory.requester_node_id,
    String(envelope.directory.valid_for_seconds),
    directorySummary(envelope.directory.entries),
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