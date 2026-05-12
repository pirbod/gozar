export type MessageDeliveryState =
  | "draft"
  | "queued"
  | "encrypting"
  | "sent"
  | "delivered"
  | "delayed"
  | "blocked_likely"
  | "failed";

export type ConversationKind = "direct" | "group" | "system";

export interface Contact {
  id: string;
  displayName: string;
  handle: string;
  avatarInitials: string;
  presence: "available" | "away" | "offline";
  safetyNumber: string;
  verified: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  kind: ConversationKind;
  participantIds: string[];
  lastMessagePreview: string;
  unreadCount: number;
  pinned?: boolean;
}

export interface MockEncryptedEnvelope {
  algorithm: "mock-reversible-v1";
  ciphertext: string;
  nonce: string;
  createdAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  authorId: string;
  authorName: string;
  body: string;
  createdAt: string;
  deliveryState: MessageDeliveryState;
  statusText?: string;
  encryptedEnvelope?: MockEncryptedEnvelope;
  disappearsAt?: string;
  isLocalOnly?: boolean;
}

export interface DraftMessage {
  conversationId: string;
  body: string;
  disappearing: boolean;
}
