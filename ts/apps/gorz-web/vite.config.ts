import react from "@vitejs/plugin-react";
import { mkdirSync } from "node:fs";
import { defineConfig } from "vitest/config";

const testTempDir = "/tmp/gorz-vitest";
mkdirSync(testTempDir, { recursive: true });
process.env.TMPDIR = testTempDir;
process.env.TEMP = testTempDir;
process.env.TMP = testTempDir;

export default defineConfig({
  cacheDir: "node_modules/.vite-gorz",
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
