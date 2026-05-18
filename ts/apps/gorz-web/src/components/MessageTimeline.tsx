import { FileJson } from "lucide-react";

import type { IdentityResponse, MessageResponse } from "../api/types";
import { formatPercent, formatStatus, formatTimestamp, statusTone } from "../utils/formatting";

interface MessageTimelineProps {
  messages: MessageResponse[];
  identities: IdentityResponse[];
  selectedMessageId: string;
  onSelectMessage: (messageId: string) => void;
  onGenerateIncident: (messageId: string) => void;
}

export function MessageTimeline({
  messages,
  identities,
  selectedMessageId,
  onSelectMessage,
  onGenerateIncident,
}: MessageTimelineProps) {
  const namesById = new Map(identities.map((identity) => [identity.identity_id, identity.display_name]));

  return (
    <section className="timeline" aria-label="Message timeline">
      {messages.length === 0 ? (
        <div className="empty-state large-empty">
          Create two identities, start a conversation, and send a local demo message.
        </div>
      ) : (
        messages.map((message) => (
          <article
            className="message-card"
            data-selected={message.message_id === selectedMessageId}
            key={message.message_id}
          >
            <button className="message-main" onClick={() => onSelectMessage(message.message_id)} type="button">
              <span>{namesById.get(message.sender_id) ?? "Demo sender"}</span>
              <strong>{message.redacted_preview}</strong>
              <small>{formatTimestamp(message.created_at)}</small>
            </button>
            <div className="message-meta">
              <span className={`pill ${statusTone(message.delivery_status)}`}>
                {formatStatus(message.delivery_status)}
              </span>
              <span className="score-text">{formatPercent(message.confidence)}</span>
              <button
                className="icon-text-button"
                onClick={() => onGenerateIncident(message.message_id)}
                type="button"
              >
                <FileJson aria-hidden="true" size={15} />
                Incident
              </button>
            </div>
          </article>
        ))
      )}
    </section>
  );
}

