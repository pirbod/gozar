import { mkdir, appendFile, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import {
  CONTROL_MESSAGE_MAX_AGE_SECONDS,
  ReplayCache,
  configResponseSignatureBase,
  controlResponseNonce,
  nowUnix,
  relayDirectoryResponseSignatureBase,
  sign,
  type ClientConfig,
  type ClientConfigEnvelope,
  type PathDescriptor,
  type QueueLimits,
  type RelayDirectory,
  type RelayDirectoryEntry,
  type RelayDirectoryEnvelope,
} from "@gozar/shared";

export type PreferredPath = "direct" | "relay";

export interface NodeObservation {
  node_id: string;
  role: string;
  listen_addr: string;
  status: string;
  observed_at_unix: number;
  features: string[];
}

export interface PersistentControlState {
  preferred_path: PreferredPath;
  switch_reason: string;
  relay_quic_addr: string;
  gateway_quic_addr: string;
  queue_limits: QueueLimits;
  research_gateway_allowed: boolean;
  nodes: NodeObservation[];
}

export interface ControlRuntimeState {
  preferred_path: PreferredPath;
  switch_reason: string;
  relay_quic_addr: string;
  gateway_quic_addr: string;
  queue_limits: QueueLimits;
  research_gateway_allowed: boolean;
  nodes: Map<string, NodeObservation>;
  control_secret: string;
  admin_token: string;
  state_file: string;
  audit_log_file: string;
  replay_cache: ReplayCache;
}

export interface AdminSwitchRequest {
  preferred_path: PreferredPath;
  switch_reason?: string;
}

interface RuntimeOptions {
  control_secret: string;
  admin_token: string;
  state_file: string;
  audit_log_file: string;
}

export function defaultPersistentState(env: NodeJS.ProcessEnv): PersistentControlState {
  return {
    preferred_path: env.PREFERRED_PATH === "relay" ? "relay" : "direct",
    switch_reason: env.DEFAULT_SWITCH_REASON ?? "default direct path for lab demo",
    relay_quic_addr: env.RELAY_QUIC_ADDR ?? "127.0.0.1:6100",
    gateway_quic_addr: env.GATEWAY_QUIC_ADDR ?? "127.0.0.1:6200",
    queue_limits: {
      client: Number(env.CLIENT_QUEUE_LIMIT ?? "16"),
      relay: Number(env.RELAY_QUEUE_LIMIT ?? "32"),
      gateway: Number(env.GATEWAY_QUEUE_LIMIT ?? "64"),
    },
    research_gateway_allowed: parseBoolean(env.RESEARCH_GATEWAY_ALLOWED, false),
    nodes: [],
  };
}

export function createRuntimeState(
  persistent: PersistentControlState,
  options: RuntimeOptions,
): ControlRuntimeState {
  return {
    preferred_path: persistent.preferred_path,
    switch_reason: persistent.switch_reason,
    relay_quic_addr: persistent.relay_quic_addr,
    gateway_quic_addr: persistent.gateway_quic_addr,
    queue_limits: persistent.queue_limits,
    research_gateway_allowed: persistent.research_gateway_allowed,
    nodes: new Map(persistent.nodes.map((node) => [node.node_id, node])),
    control_secret: options.control_secret,
    admin_token: options.admin_token,
    state_file: options.state_file,
    audit_log_file: options.audit_log_file,
    replay_cache: new ReplayCache(CONTROL_MESSAGE_MAX_AGE_SECONDS),
  };
}

// Only operator intent and observations are restored from disk; connect addresses and
// queue defaults still come from the current environment so local runs stay predictable.
export async function loadPersistentState(
  stateFile: string,
  fallback: PersistentControlState,
): Promise<PersistentControlState> {
  try {
    const raw = await readFile(stateFile, "utf8");
    const parsed = JSON.parse(raw) as Partial<PersistentControlState>;
    return {
      preferred_path: parsed.preferred_path === "relay" ? "relay" : fallback.preferred_path,
      switch_reason: parsed.switch_reason ?? fallback.switch_reason,
      relay_quic_addr: fallback.relay_quic_addr,
      gateway_quic_addr: fallback.gateway_quic_addr,
      queue_limits: fallback.queue_limits,
      research_gateway_allowed: fallback.research_gateway_allowed,
      nodes: Array.isArray(parsed.nodes) ? parsed.nodes : fallback.nodes,
    };
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return fallback;
    }
    throw error;
  }
}

export async function persistState(state: ControlRuntimeState): Promise<void> {
  const snapshot = snapshotState(state);
  await ensureParentDirectory(state.state_file);
  await writeFile(state.state_file, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
}

export async function appendAuditLog(
  state: ControlRuntimeState,
  event: string,
  details: Record<string, unknown>,
): Promise<void> {
  await ensureParentDirectory(state.audit_log_file);
  const line = JSON.stringify({
    ts_unix: nowUnix(),
    event,
    details,
  });
  await appendFile(state.audit_log_file, `${line}\n`, "utf8");
}

export function snapshotState(state: ControlRuntimeState): PersistentControlState {
  return {
    preferred_path: state.preferred_path,
    switch_reason: state.switch_reason,
    relay_quic_addr: state.relay_quic_addr,
    gateway_quic_addr: state.gateway_quic_addr,
    queue_limits: state.queue_limits,
    research_gateway_allowed: state.research_gateway_allowed,
    nodes: Array.from(state.nodes.values()).sort((left, right) =>
      left.node_id.localeCompare(right.node_id),
    ),
  };
}

// The control plane keeps the canonical direct/relay path list small on purpose and
// derives its scoring hints from the latest persisted observations.
export function buildPaths(state: ControlRuntimeState): PathDescriptor[] {
  const gateway = findNode(state, "gateway")?.observed_at_unix ?? null;
  const relay = findNode(state, "relay");

  return [
    {
      id: "direct",
      kind: "direct",
      ingress_addr: state.gateway_quic_addr,
      hops: ["gateway-1"],
      queue_limit: state.queue_limits.gateway,
      relay_id: null,
      last_observed_at_unix: gateway,
      operator_preference: state.preferred_path === "direct" ? 50 : 10,
      supports_research_gateway: state.research_gateway_allowed,
    },
    {
      id: "relay",
      kind: "relay",
      ingress_addr: state.relay_quic_addr,
      hops: [relay?.node_id ?? "relay-1", "gateway-1"],
      queue_limit: state.queue_limits.relay,
      relay_id: relay?.node_id ?? "relay-1",
      last_observed_at_unix: relay?.observed_at_unix ?? null,
      operator_preference: state.preferred_path === "relay" ? 55 : 5,
      supports_research_gateway: state.research_gateway_allowed,
    },
  ];
}

// Relay-directory responses are built from the latest observed relay heartbeats rather
// than static config so clients can score fresh relay availability.
export function buildRelayDirectoryEntries(state: ControlRuntimeState): RelayDirectoryEntry[] {
  return Array.from(state.nodes.values())
    .filter((node) => node.role === "relay")
    .sort((left, right) => left.node_id.localeCompare(right.node_id))
    .map((node) => ({
      relay_id: node.node_id,
      ingress_addr: state.relay_quic_addr,
      gateway_addr: state.gateway_quic_addr,
      observed_at_unix: node.observed_at_unix,
      status: node.status,
      queue_limit: state.queue_limits.relay,
      supports_research_gateway: state.research_gateway_allowed,
      features: node.features,
    }));
}

export function issueConfigEnvelope(
  state: ControlRuntimeState,
  node_id: string,
  request_nonce: string,
): ClientConfigEnvelope {
  const config: ClientConfig = {
    node_id,
    preferred_path: state.preferred_path,
    switch_reason: state.switch_reason,
    valid_for_seconds: 30,
    queue_limits: state.queue_limits,
    paths: buildPaths(state),
    research_gateway_allowed: state.research_gateway_allowed,
  };

  const envelope: ClientConfigEnvelope = {
    request_nonce,
    response_nonce: controlResponseNonce(),
    issued_at_unix: nowUnix(),
    config,
    signature: "",
  };
  envelope.signature = sign(state.control_secret, configResponseSignatureBase(envelope));
  return envelope;
}

export function issueRelayDirectoryEnvelope(
  state: ControlRuntimeState,
  requester_node_id: string,
  request_nonce: string,
): RelayDirectoryEnvelope {
  const directory: RelayDirectory = {
    requester_node_id,
    valid_for_seconds: 30,
    entries: buildRelayDirectoryEntries(state),
  };

  const envelope: RelayDirectoryEnvelope = {
    request_nonce,
    response_nonce: controlResponseNonce(),
    issued_at_unix: nowUnix(),
    directory,
    signature: "",
  };
  envelope.signature = sign(state.control_secret, relayDirectoryResponseSignatureBase(envelope));
  return envelope;
}

export function requestReplayKey(scope: string, nodeId: string, nonce: string): string {
  return `${scope}:${nodeId}:${nonce}`;
}

export function upsertNodeObservation(
  state: ControlRuntimeState,
  observation: NodeObservation,
): void {
  state.nodes.set(observation.node_id, observation);
}

function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }
  return value === "true" || value === "1" || value === "yes";
}

function findNode(state: ControlRuntimeState, role: string): NodeObservation | undefined {
  return Array.from(state.nodes.values()).find((node) => node.role === role);
}

async function ensureParentDirectory(path: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
}