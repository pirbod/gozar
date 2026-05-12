import type { MockEncryptedEnvelope } from "../types/chat";

export interface MockIdentityKey {
  id: string;
  publicKey: string;
  privateKey: string;
  createdAt: string;
}

const mockAlphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";

function createMockToken(length: number): string {
  return Array.from({ length }, () => mockAlphabet[Math.floor(Math.random() * mockAlphabet.length)] ?? "X").join("");
}

function reverseText(value: string): string {
  return Array.from(value).reverse().join("");
}

function normalizeSafetyNumber(input: string): string {
  return input.replace(/\D/g, "").slice(0, 60);
}

/**
 * PoC mock only: this generates a display identity key for demos and must be replaced with
 * audited cryptographic libraries before production.
 */
export function generateMockIdentityKey(ownerId = "local-user"): MockIdentityKey {
  const keyMaterial = createMockToken(32);
  return {
    id: `${ownerId}-${createMockToken(8).toLowerCase()}`,
    publicKey: `mock_public_${keyMaterial}`,
    privateKey: `mock_private_${createMockToken(32)}`,
    createdAt: new Date().toISOString(),
  };
}

/**
 * PoC mock only: this derives a reversible demo session string and must be replaced with
 * audited cryptographic libraries before production.
 */
export function deriveMockSessionKey(identityKey: MockIdentityKey, peerPublicKey: string): string {
  const joined = `${identityKey.publicKey}:${peerPublicKey}`;
  return `mock_session_${reverseText(joined).slice(0, 48)}`;
}

/**
 * PoC mock only: this simulates encryption for interface behavior and must be replaced with
 * audited cryptographic libraries before production.
 */
export function encryptMessageMock(plaintext: string, sessionKey: string): MockEncryptedEnvelope {
  const nonce = createMockToken(12).toLowerCase();
  const encodedPayload = encodeURIComponent(`${plaintext}::${sessionKey.slice(0, 12)}::${nonce}`);
  return {
    algorithm: "mock-reversible-v1",
    ciphertext: reverseText(encodedPayload),
    nonce,
    createdAt: new Date().toISOString(),
  };
}

/**
 * PoC mock only: this reverses the demo envelope format and must be replaced with audited
 * cryptographic libraries before production.
 */
export function decryptMessageMock(envelope: MockEncryptedEnvelope, sessionKey: string): string {
  const decodedPayload = decodeURIComponent(reverseText(envelope.ciphertext));
  const expectedSuffix = `::${sessionKey.slice(0, 12)}::${envelope.nonce}`;

  if (!decodedPayload.endsWith(expectedSuffix)) {
    throw new Error("Mock session key mismatch");
  }

  return decodedPayload.slice(0, -expectedSuffix.length);
}

/**
 * PoC mock only: this creates a readable verification number for demos and must be replaced with
 * audited cryptographic libraries before production.
 */
export function generateSafetyNumber(localPublicKey: string, peerPublicKey: string): string {
  const source = `${localPublicKey}:${peerPublicKey}`;
  const digits = Array.from(source).map((character) => String(character.charCodeAt(0) % 10));
  const padded = digits.join("").padEnd(60, "0").slice(0, 60);
  return padded.match(/.{1,5}/g)?.join(" ") ?? padded;
}

/**
 * PoC mock only: this compares demo safety numbers and must be replaced with audited
 * cryptographic libraries before production.
 */
export function verifySafetyNumberMock(expected: string, presented: string): boolean {
  return normalizeSafetyNumber(expected) === normalizeSafetyNumber(presented);
}
