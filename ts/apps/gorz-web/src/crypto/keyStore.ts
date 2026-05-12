import type { Contact } from "../types/chat";

import { deriveMockSessionKey, generateMockIdentityKey, generateSafetyNumber } from "./mockE2EE";

export interface MockKeyStore {
  localIdentity: ReturnType<typeof generateMockIdentityKey>;
  sessionsByContactId: Record<string, string>;
  safetyNumbersByContactId: Record<string, string>;
}

export function createMockKeyStore(contacts: Contact[]): MockKeyStore {
  const localIdentity = generateMockIdentityKey();
  const sessionsByContactId: Record<string, string> = {};
  const safetyNumbersByContactId: Record<string, string> = {};

  for (const contact of contacts) {
    const peerPublicKey = `mock_peer_public_${contact.id}`;
    sessionsByContactId[contact.id] = deriveMockSessionKey(localIdentity, peerPublicKey);
    safetyNumbersByContactId[contact.id] = generateSafetyNumber(localIdentity.publicKey, peerPublicKey);
  }

  return {
    localIdentity,
    sessionsByContactId,
    safetyNumbersByContactId,
  };
}
