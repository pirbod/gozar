import assert from "node:assert/strict";
import test from "node:test";

import { loadControlPlaneConfig } from "./config";

test("control-plane config rejects missing secrets by default", () => {
  assert.throws(
    () => loadControlPlaneConfig({}),
    /CONTROL_SECRET is required/,
  );
});

test("control-plane config rejects local demo secrets unless dev defaults are explicit", () => {
  assert.throws(
    () =>
      loadControlPlaneConfig({
        CONTROL_SECRET: "gozar-local-shared-secret",
        ADMIN_TOKEN: "gozar-admin-token",
      }),
    /CONTROL_SECRET is set to the local demo value/,
  );
});

test("control-plane config permits local demo secrets when explicitly enabled", () => {
  const config = loadControlPlaneConfig({
    GOZAR_ALLOW_INSECURE_DEV_DEFAULTS: "true",
    CONTROL_SECRET: "gozar-local-shared-secret",
    ADMIN_TOKEN: "gozar-admin-token",
  });

  assert.equal(config.controlSecret, "gozar-local-shared-secret");
  assert.equal(config.adminToken, "gozar-admin-token");
  assert.equal(config.allowInsecureDevDefaults, true);
});

test("control-plane config accepts non-demo secrets without dev mode", () => {
  const config = loadControlPlaneConfig({
    PORT: "8090",
    CONTROL_SECRET: "control-secret-from-secret-manager",
    ADMIN_TOKEN: "admin-token-from-secret-manager",
  });

  assert.equal(config.port, 8090);
  assert.equal(config.controlSecret, "control-secret-from-secret-manager");
  assert.equal(config.adminToken, "admin-token-from-secret-manager");
  assert.equal(config.allowInsecureDevDefaults, false);
});
