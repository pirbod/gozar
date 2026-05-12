import type { Conversation, Message } from "../types/chat";
import { minutesFromNow } from "../utils/time";

const now = Date.now();

function minutesAgo(minutes: number): string {
  return new Date(now - minutes * 60_000).toISOString();
}

export const mockConversations: Conversation[] = [
  {
    id: "sara",
    title: "Sara",
    kind: "direct",
    participantIds: ["local-user", "sara"],
    lastMessagePreview: "Can you receive this?",
    unreadCount: 0,
    pinned: true,
  },
  {
    id: "arman",
    title: "Arman",
    kind: "direct",
    participantIds: ["local-user", "arman"],
    lastMessagePreview: "I may be offline for a while.",
    unreadCount: 1,
  },
  {
    id: "family",
    title: "Family",
    kind: "group",
    participantIds: ["local-user", "sara", "mina", "reza"],
    lastMessagePreview: "Safety mode is active.",
    unreadCount: 0,
  },
  {
    id: "network-status",
    title: "Network Status",
    kind: "system",
    participantIds: ["local-user", "gorz-notes"],
    lastMessagePreview: "Message queued until network improves.",
    unreadCount: 0,
  },
];

export const mockMessages: Message[] = [
  {
    id: "msg-sara-1",
    conversationId: "sara",
    authorId: "sara",
    authorName: "Sara",
    body: "Can you receive this?",
    createdAt: minutesAgo(28),
    deliveryState: "delivered",
  },
  {
    id: "msg-sara-2",
    conversationId: "sara",
    authorId: "local-user",
    authorName: "You",
    body: "Yes. Safety mode is active.",
    createdAt: minutesAgo(25),
    deliveryState: "delivered",
    statusText: "Delivered with confirmed external access likely.",
    isLocalOnly: true,
  },
  {
    id: "msg-sara-3",
    conversationId: "sara",
    authorId: "sara",
    authorName: "Sara",
    body: "Thanks. I may be offline for a while.",
    createdAt: minutesAgo(18),
    deliveryState: "delivered",
  },
  {
    id: "msg-arman-1",
    conversationId: "arman",
    authorId: "arman",
    authorName: "Arman",
    body: "I may be offline for a while.",
    createdAt: minutesAgo(42),
    deliveryState: "delivered",
  },
  {
    id: "msg-arman-2",
    conversationId: "arman",
    authorId: "local-user",
    authorName: "You",
    body: "Message queued until network improves.",
    createdAt: minutesAgo(34),
    deliveryState: "queued",
    statusText: "Message will retry when connectivity improves.",
    isLocalOnly: true,
  },
  {
    id: "msg-family-1",
    conversationId: "family",
    authorId: "mina",
    authorName: "Mina",
    body: "Safety mode is active.",
    createdAt: minutesAgo(55),
    deliveryState: "delivered",
  },
  {
    id: "msg-family-2",
    conversationId: "family",
    authorId: "local-user",
    authorName: "You",
    body: "I can send a short update later.",
    createdAt: minutesAgo(44),
    deliveryState: "delivered",
    disappearsAt: minutesFromNow(120),
    isLocalOnly: true,
  },
  {
    id: "msg-status-1",
    conversationId: "network-status",
    authorId: "gorz-notes",
    authorName: "Gorz Notes",
    body: "Gorz currently uses simulated diagnostics. Nothing is uploaded automatically.",
    createdAt: minutesAgo(12),
    deliveryState: "delivered",
  },
];
