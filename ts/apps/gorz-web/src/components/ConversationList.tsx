import { MessageSquarePlus } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import type { ConversationSummary, IdentityResponse } from "../api/types";
import { formatTimestamp } from "../utils/formatting";

interface ConversationListProps {
  conversations: ConversationSummary[];
  identities: IdentityResponse[];
  activeIdentityId: string;
  selectedConversationId: string;
  onSelectConversation: (conversationId: string) => void;
  onCreateConversation: (title: string, participantIds: string[]) => void;
}

export function ConversationList({
  conversations,
  identities,
  activeIdentityId,
  selectedConversationId,
  onSelectConversation,
  onCreateConversation,
}: ConversationListProps) {
  const [title, setTitle] = useState("Local demo conversation");
  const otherIdentity = useMemo(
    () => identities.find((identity) => identity.identity_id !== activeIdentityId) ?? null,
    [activeIdentityId, identities],
  );
  const canCreate = Boolean(activeIdentityId && otherIdentity);

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!canCreate || !otherIdentity) {
      return;
    }
    onCreateConversation(title.trim() || "Local demo conversation", [
      activeIdentityId,
      otherIdentity.identity_id,
    ]);
  }

  return (
    <section className="panel compact-panel" aria-labelledby="conversation-list-title">
      <div className="section-title">
        <h2 id="conversation-list-title">Conversations</h2>
        <MessageSquarePlus aria-hidden="true" size={18} />
      </div>

      <form className="stacked-form" onSubmit={handleSubmit}>
        <label htmlFor="conversation-title">New local conversation</label>
        <input
          id="conversation-title"
          onChange={(event) => setTitle(event.target.value)}
          value={title}
        />
        <button className="secondary-button" disabled={!canCreate} type="submit">
          Create
        </button>
        {!canCreate ? <p className="muted-copy">Create two demo identities first.</p> : null}
      </form>

      <div className="list-stack">
        {conversations.length === 0 ? (
          <p className="empty-state">No conversations yet.</p>
        ) : (
          conversations.map((conversation) => (
            <button
              aria-current={conversation.conversation_id === selectedConversationId ? "page" : undefined}
              className="list-row"
              key={conversation.conversation_id}
              onClick={() => onSelectConversation(conversation.conversation_id)}
              type="button"
            >
              <strong>{conversation.title}</strong>
              <span>{conversation.participant_ids.length} participants</span>
              <small>{formatTimestamp(conversation.created_at)}</small>
            </button>
          ))
        )}
      </div>
    </section>
  );
}

