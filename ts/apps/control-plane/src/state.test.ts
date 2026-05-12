import assert from "node:assert/strict";
import test from "node:test";

import { createRuntimeState, buildPaths, buildRelayDirectoryEntries } from "./state";

test("buildPaths follows preferred path and research flag", () => {
  const state = createRuntimeState(
    {
      preferred_path: "relay",
      switch_reason: "operator forced relay",
      relay_quic_addr: "relay:6100",
      gateway_quic_addr: "gateway:6200",
      queue_limits: {
        client: 16,
        relay: 32,
        gateway: 64,
      },
      research_gateway_allowed: true,
      nodes: [
        {
          node_id: "relay-1",
          role: "relay",
          listen_addr: "relay:6100",
          status: "ready",
          observed_at_unix: 42,
          features: ["quic_relay"],
        },
      ],
    },
    {
      control_secret: "secret",
      admin_token: "token",
      state_file: "state.json",
      audit_log_file: "audit.log",
    },
  );

  const paths = buildPaths(state);
  assert.equal(paths[1]?.operator_preference! > paths[0]?.operator_preference!, true);
  assert.equal(paths[1]?.supports_research_gateway, true);
});

test("relay directory reflects observed relay nodes", () => {
  const state = createRuntimeState(
    {
      preferred_path: "direct",
      switch_reason: "default",
      relay_quic_addr: "relay:6100",
      gateway_quic_addr: "gateway:6200",
      queue_limits: {
        client: 16,
        relay: 32,
        gateway: 64,
      },
      research_gateway_allowed: false,
      nodes: [
        {
          node_id: "relay-1",
          role: "relay",
          listen_addr: "relay:6100",
          status: "ready",
          observed_at_unix: 24,
          features: ["quic_relay", "lab_simulation_ready"],
        },
      ],
    },
    {
      control_secret: "secret",
      admin_token: "token",
      state_file: "state.json",
      audit_log_file: "audit.log",
    },
  );

  const entries = buildRelayDirectoryEntries(state);
  assert.equal(entries.length, 1);
  assert.deepEqual(entries[0]?.features, ["quic_relay", "lab_simulation_ready"]);
  assert.equal(entries[0]?.gateway_addr, "gateway:6200");
});