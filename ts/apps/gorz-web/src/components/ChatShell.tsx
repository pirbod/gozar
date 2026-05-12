import type { Contact, Conversation, DraftMessage, Message } from "../types/chat";

import { MessageComposer } from "./MessageComposer";
import { MessageThread } from "./MessageThread";

interface ChatShellProps {
  conversation: Conversation;
  contacts: Contact[];
  messages: Message[];
  composerDisabled: boolean;
  composerDisabledReason?: string;
  onSendMessage: (draft: DraftMessage) => void;
}

export function ChatShell({
  conversation,
  contacts,
  messages,
  composerDisabled,
  composerDisabledReason,
  onSendMessage,
}: ChatShellProps) {
  return (
    <div className="chat-shell">
      <MessageThread conversation={conversation} contacts={contacts} messages={messages} />
      <MessageComposer
        conversationId={conversation.id}
        disabled={composerDisabled}
        disabledReason={composerDisabledReason}
        onSendMessage={onSendMessage}
      />
    </div>
  );
}
