import assert from "node:assert/strict";
import test from "node:test";

import {
  ClientConfigEnvelope,
  CONTROL_MESSAGE_MAX_AGE_SECONDS,
  RelayDirectoryEnvelope,
  ReplayCache,
  configRequestSignatureBase,
  configResponseSignatureBase,
  controlResponseNonce,
  relayDirectoryResponseSignatureBase,
  sign,
  verify,
  verifyTimestampFreshness,
} from "./index";

test("shared signatures round trip", () => {
  const payload = configRequestSignatureBase("desktop-client-1", 10, "nonce-a");
  const signature = sign("secret", payload);
  assert.equal(verify("secret", payload, signature), true);
});

test("config response signature is stable", () => {
  const envelope: ClientConfigEnvelope = {
    request_nonce: "nonce-a",
    response_nonce: controlResponseNonce(),
    issued_at_unix: 42,
    config: {
      node_id: "desktop-client-1",
      preferred_path: "relay",
      switch_reason: "operator prefers relay",
      valid_for_seconds: 30,
      queue_limits: {
        client: 16,
        relay: 32,
        gateway: 64,
      },
      paths: [
        {
          id: "relay",
          kind: "relay",
          ingress_addr: "relay:6100",
          hops: ["relay-1", "gateway-1"],
          queue_limit: 32,
          relay_id: "relay-1",
          last_observed_at_unix: 40,
          operator_preference: 50,
          supports_research_gateway: true,
        },
      ],
      research_gateway_allowed: true,
    },
    signature: "",
  };

  const base = configResponseSignatureBase(envelope);
  assert.match(base, /operator prefers relay/);
  assert.match(base, /relay:relay:6100/);
});

test("relay directory signature is stable", () => {
  const envelope: RelayDirectoryEnvelope = {
    request_nonce: "nonce-b",
    response_nonce: controlResponseNonce(),
    issued_at_unix: 50,
    directory: {
      requester_node_id: "desktop-client-1",
      valid_for_seconds: 30,
      entries: [
        {
          relay_id: "relay-1",
          ingress_addr: "relay:6100",
          gateway_addr: "gateway:6200",
          observed_at_unix: 48,
          status: "ready",
          queue_limit: 32,
          supports_research_gateway: true,
          features: ["quic_relay"],
        },
      ],
    },
    signature: "",
  };

  const base = relayDirectoryResponseSignatureBase(envelope);
  assert.match(base, /relay-1:relay:6100:gateway:6200/);
});

test("replay cache rejects duplicates", () => {
  const replay = new ReplayCache(CONTROL_MESSAGE_MAX_AGE_SECONDS);
  replay.checkAndRecord("config:one", 100);
  assert.throws(() => replay.checkAndRecord("config:one", 100), /replayed control message/);
});

test("freshness verifier rejects stale timestamps", () => {
  assert.throws(
    () => verifyTimestampFreshness(1, 1),
    /control message timestamp is stale/,
  );
});