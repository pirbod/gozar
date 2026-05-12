import { Send, TimerReset } from "lucide-react";
import { FormEvent, useState } from "react";

import type { DraftMessage } from "../types/chat";

interface MessageComposerProps {
  conversationId: string;
  disabled: boolean;
  disabledReason?: string;
  onSendMessage: (draft: DraftMessage) => void;
}

export function MessageComposer({
  conversationId,
  disabled,
  disabledReason,
  onSendMessage,
}: MessageComposerProps) {
  const [body, setBody] = useState("");
  const [disappearing, setDisappearing] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const trimmed = body.trim();

    if (!trimmed || disabled) {
      return;
    }

    onSendMessage({
      conversationId,
      body: trimmed,
      disappearing,
    });
    setBody("");
  }

  return (
    <form className="message-composer" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="message-body">
        Message
      </label>
      <textarea
        disabled={disabled}
        id="message-body"
        onChange={(event) => setBody(event.target.value)}
        placeholder={disabled ? disabledReason : "Write a private message"}
        rows={2}
        value={body}
      />
      <div className="composer-actions">
        <label className="icon-toggle">
          <input
            checked={disappearing}
            disabled={disabled}
            onChange={(event) => setDisappearing(event.target.checked)}
            type="checkbox"
          />
          <TimerReset aria-hidden="true" size={16} />
          <span>Disappearing</span>
        </label>
        <button aria-label="Send message" className="primary-action" disabled={disabled || !body.trim()} type="submit">
          <Send aria-hidden="true" size={18} />
          <span>Send</span>
        </button>
      </div>
    </form>
  );
}
