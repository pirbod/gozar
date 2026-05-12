import { describe, expect, it } from "vitest";

import {
  decryptMessageMock,
  deriveMockSessionKey,
  encryptMessageMock,
  generateMockIdentityKey,
  generateSafetyNumber,
  verifySafetyNumberMock,
} from "./mockE2EE";

describe("mock E2EE helpers", () => {
  it("round trips a mock encrypted message", () => {
    const identity = generateMockIdentityKey("sender");
    const sessionKey = deriveMockSessionKey(identity, "mock_peer_public_sara");
    const envelope = encryptMessageMock("Safety mode is active.", sessionKey);

    expect(decryptMessageMock(envelope, sessionKey)).toBe("Safety mode is active.");
  });

  it("verifies generated mock safety numbers", () => {
    const safetyNumber = generateSafetyNumber("mock_public_a", "mock_public_b");

    expect(verifySafetyNumberMock(safetyNumber, safetyNumber.replaceAll(" ", ""))).toBe(true);
  });
});
