import { MessageCircle, Pin } from "lucide-react";

import type { Contact, Conversation } from "../types/chat";

interface ConversationListProps {
  conversations: Conversation[];
  contacts: Contact[];
  selectedConversationId: string;
  onSelectConversation: (conversationId: string) => void;
}

export function ConversationList({
  conversations,
  contacts,
  selectedConversationId,
  onSelectConversation,
}: ConversationListProps) {
  return (
    <nav className="conversation-list" aria-label="Conversations">
      <div className="section-heading">
        <span>Messages</span>
        <MessageCircle aria-hidden="true" size={18} />
      </div>
      <div className="conversation-items">
        {conversations.map((conversation) => (
          <button
            aria-current={conversation.id === selectedConversationId ? "true" : undefined}
            className="conversation-item"
            key={conversation.id}
            onClick={() => onSelectConversation(conversation.id)}
            type="button"
          >
            <span className="avatar">{getConversationInitials(conversation, contacts)}</span>
            <span className="conversation-copy">
              <span className="conversation-title-row">
                <span>{conversation.title}</span>
                {conversation.pinned ? <Pin aria-label="Pinned" size={13} /> : null}
              </span>
              <span className="conversation-preview">{conversation.lastMessagePreview}</span>
            </span>
            {conversation.unreadCount > 0 ? (
              <span className="unread-badge" aria-label={`${conversation.unreadCount} unread`}>
                {conversation.unreadCount}
              </span>
            ) : null}
          </button>
        ))}
      </div>
    </nav>
  );
}

function getConversationInitials(conversation: Conversation, contacts: Contact[]): string {
  if (conversation.kind !== "direct") {
    return conversation.title
      .split(" ")
      .map((word) => word[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();
  }

  const peerId = conversation.participantIds.find((id) => id !== "local-user");
  return contacts.find((contact) => contact.id === peerId)?.avatarInitials ?? "GR";
}
