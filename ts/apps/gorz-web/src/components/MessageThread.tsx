import { Timer, Users } from "lucide-react";

import type { Contact, Conversation, Message } from "../types/chat";
import { formatSafetyNumberPreview } from "../crypto/safetyNumbers";
import { formatTime } from "../utils/time";

import { DeliveryStatus } from "./DeliveryStatus";

interface MessageThreadProps {
  conversation: Conversation;
  contacts: Contact[];
  messages: Message[];
}

export function MessageThread({ conversation, contacts, messages }: MessageThreadProps) {
  const directContact = getDirectContact(conversation, contacts);

  return (
    <section className="message-thread" aria-label={`${conversation.title} conversation`}>
      <div className="thread-header">
        <div>
          <h2>{conversation.title}</h2>
          <p>{getConversationMeta(conversation, directContact)}</p>
        </div>
        {directContact ? (
          <div className="safety-number-card">
            <span>Safety number</span>
            <strong>{formatSafetyNumberPreview(directContact.safetyNumber)}</strong>
          </div>
        ) : (
          <div className="safety-number-card">
            <span>Group safety</span>
            <strong>
              <Users aria-hidden="true" size={14} /> {conversation.participantIds.length} members
            </strong>
          </div>
        )}
      </div>

      <div className="messages" role="list">
        {messages.map((message) => {
          const outgoing = message.authorId === "local-user";
          return (
            <article className={`message-row ${outgoing ? "outgoing" : "incoming"}`} key={message.id} role="listitem">
              <div className="message-bubble">
                <div className="message-meta">
                  <span>{message.authorName}</span>
                  <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
                </div>
                <p>{message.body}</p>
                <div className="message-footer">
                  {message.disappearsAt ? (
                    <span className="disappearing-indicator">
                      <Timer aria-hidden="true" size={13} />
                      Disappearing
                    </span>
                  ) : null}
                  {outgoing ? <DeliveryStatus state={message.deliveryState} statusText={message.statusText} /> : null}
                </div>
                {message.statusText && outgoing ? <p className="status-note">{message.statusText}</p> : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function getDirectContact(conversation: Conversation, contacts: Contact[]): Contact | undefined {
  if (conversation.kind !== "direct") {
    return undefined;
  }

  const peerId = conversation.participantIds.find((id) => id !== "local-user");
  return contacts.find((contact) => contact.id === peerId);
}

function getConversationMeta(conversation: Conversation, contact?: Contact): string {
  if (conversation.kind === "system") {
    return "Local system notes";
  }

  if (conversation.kind === "group") {
    return "Mock group conversation";
  }

  return contact?.verified ? "Verified mock safety number" : "Safety number unverified";
}
