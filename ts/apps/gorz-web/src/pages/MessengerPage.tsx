import { useMemo, useState } from "react";

import type { ScenarioId } from "../api/types";
import { ConversationList } from "../components/ConversationList";
import { DeliveryConfidenceCard } from "../components/DeliveryConfidenceCard";
import { EvidenceBreakdown } from "../components/EvidenceBreakdown";
import { IdentityPanel } from "../components/IdentityPanel";
import { MessageComposer } from "../components/MessageComposer";
import { MessageTimeline } from "../components/MessageTimeline";

interface MessengerPageProps {
  api: {
    identities: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["identities"];
    conversations: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["conversations"];
    selectedConversation: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["selectedConversation"];
    scenarios: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["scenarios"];
    diagnostic: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["diagnostic"];
    activeIdentityId: string;
    selectedConversationId: string;
    selectedScenario: ScenarioId;
    safety: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["safety"];
    selectIdentity: (identityId: string) => void;
    selectConversation: (conversationId: string) => void;
    createIdentity: (displayName: string, deviceLabel: string) => void;
    createConversation: (title: string, participantIds: string[]) => void;
    sendMessage: (body: string) => void;
    selectScenario: (scenario: ScenarioId) => void;
    generateIncident: (messageId: string) => void;
  };
}

export function MessengerPage({ api }: MessengerPageProps) {
  const [selectedMessageId, setSelectedMessageId] = useState("");
  const messages = api.selectedConversation?.messages ?? [];
  const selectedMessage = useMemo(
    () =>
      messages.find((message) => message.message_id === selectedMessageId) ??
      messages[messages.length - 1] ??
      null,
    [messages, selectedMessageId],
  );
  const composerDisabled = Boolean(api.safety?.pause_enabled || !api.selectedConversation || !api.activeIdentityId);

  return (
    <div className="messenger-layout">
      <aside className="left-rail">
        <IdentityPanel
          activeIdentityId={api.activeIdentityId}
          identities={api.identities}
          onCreateIdentity={api.createIdentity}
          onSelectIdentity={api.selectIdentity}
        />
        <ConversationList
          activeIdentityId={api.activeIdentityId}
          conversations={api.conversations}
          identities={api.identities}
          onCreateConversation={api.createConversation}
          onSelectConversation={api.selectConversation}
          selectedConversationId={api.selectedConversationId}
        />
      </aside>

      <main className="message-workspace" aria-label="Messenger">
        <div className="conversation-header">
          <div>
            <span>Conversation</span>
            <h2>{api.selectedConversation?.title ?? "No conversation selected"}</h2>
          </div>
          <span className="pill ok">{api.selectedScenario}</span>
        </div>
        <MessageTimeline
          identities={api.identities}
          messages={messages}
          onGenerateIncident={api.generateIncident}
          onSelectMessage={setSelectedMessageId}
          selectedMessageId={selectedMessage?.message_id ?? ""}
        />
        <MessageComposer
          disabled={composerDisabled}
          disabledReason={
            api.safety?.pause_enabled
              ? "Emergency pause is active"
              : "Create an identity and conversation first"
          }
          onScenarioChange={api.selectScenario}
          onSendMessage={api.sendMessage}
          scenarios={api.scenarios}
          selectedScenario={api.selectedScenario}
        />
      </main>

      <aside className="right-rail">
        <DeliveryConfidenceCard diagnostic={api.diagnostic} message={selectedMessage} />
        <EvidenceBreakdown diagnostic={api.diagnostic} message={selectedMessage} />
      </aside>
    </div>
  );
}

