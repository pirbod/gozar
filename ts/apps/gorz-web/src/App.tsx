import { FileJson, MessageCircle, Settings, ShieldCheck, Wifi } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { ChatShell } from "./components/ChatShell";
import { ConversationList } from "./components/ConversationList";
import { Header } from "./components/Header";
import { IncidentRecordPanel } from "./components/IncidentRecordPanel";
import { NetworkConfidencePanel } from "./components/NetworkConfidencePanel";
import { SafetyModePanel } from "./components/SafetyModePanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { calculateConnectivityConfidence } from "./connectivity/confidenceModel";
import {
  diagnosticScenarios,
  getDiagnosticScenario,
  getMessageDeliveryPlan,
  simulateDiagnosticScenario,
} from "./connectivity/diagnosticSimulator";
import { createIncidentRecord } from "./connectivity/incidentRecord";
import { createMockKeyStore } from "./crypto/keyStore";
import { encryptMessageMock } from "./crypto/mockE2EE";
import { localUser, mockContacts } from "./data/mockContacts";
import { mockConversations, mockMessages } from "./data/mockMessages";
import type { DraftMessage, Message } from "./types/chat";
import type { DiagnosticScenarioId, SafetyControls } from "./types/connectivity";
import { createId } from "./utils/id";
import { minutesFromNow } from "./utils/time";

type AppPanel = "chat" | "network" | "safety" | "incident" | "settings";
type ThemePreference = "light" | "dark";

const defaultSafetyControls: SafetyControls = {
  safetyModeEnabled: true,
  localDiagnosticsOnly: true,
  disableAutomaticDiagnosticUpload: true,
  delayIncidentExport: true,
  hideAdvancedTechnicalDetails: true,
  reduceDiagnosticFrequency: true,
  emergencyPause: false,
};

const panelButtons: Array<{ id: AppPanel; label: string; icon: typeof MessageCircle }> = [
  { id: "chat", label: "Chat", icon: MessageCircle },
  { id: "network", label: "Network", icon: Wifi },
  { id: "safety", label: "Safety", icon: ShieldCheck },
  { id: "incident", label: "Incident", icon: FileJson },
  { id: "settings", label: "Settings", icon: Settings },
];

function App() {
  const [selectedConversationId, setSelectedConversationId] = useState("sara");
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [scenarioId, setScenarioId] = useState<DiagnosticScenarioId>("normal_internet_access");
  const [safetyControls, setSafetyControls] = useState<SafetyControls>(defaultSafetyControls);
  const [activePanel, setActivePanel] = useState<AppPanel>("chat");
  const [activeInsightPanel, setActiveInsightPanel] = useState<Exclude<AppPanel, "chat">>("network");
  const [theme, setTheme] = useState<ThemePreference>("dark");

  const keyStore = useMemo(() => createMockKeyStore(mockContacts), []);
  const selectedConversation =
    mockConversations.find((conversation) => conversation.id === selectedConversationId) ?? mockConversations[0];
  const scenario = useMemo(() => getDiagnosticScenario(scenarioId), [scenarioId]);
  const evidence = useMemo(() => simulateDiagnosticScenario(scenarioId), [scenarioId]);
  const confidence = useMemo(() => calculateConnectivityConfidence(evidence), [evidence]);
  const deliveryPlan = useMemo(() => getMessageDeliveryPlan(scenarioId), [scenarioId]);
  const activeMessages = useMemo(
    () => messages.filter((message) => message.conversationId === selectedConversation.id),
    [messages, selectedConversation.id],
  );
  const latestDeliveryState = useMemo(() => {
    const latestLocalMessage = [...activeMessages].reverse().find((message) => message.authorId === localUser.id);
    return latestLocalMessage?.deliveryState ?? deliveryPlan.finalState;
  }, [activeMessages, deliveryPlan.finalState]);
  const incidentRecord = useMemo(
    () =>
      createIncidentRecord(
        {
          scenarioId,
          scenarioLabel: scenario.label,
          confidence,
          messageDeliveryState: latestDeliveryState,
          safetyControls,
        },
        evidence.observedAt,
      ),
    [confidence, evidence.observedAt, latestDeliveryState, safetyControls, scenario.label, scenarioId],
  );

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  function handleScenarioChange(nextScenarioId: DiagnosticScenarioId): void {
    const nextPlan = getMessageDeliveryPlan(nextScenarioId);
    setScenarioId(nextScenarioId);
    setMessages((currentMessages) =>
      currentMessages.map((message) => {
        const shouldUpdate =
          message.authorId === localUser.id &&
          message.deliveryState !== "delivered" &&
          message.deliveryState !== "draft";

        if (!shouldUpdate) {
          return message;
        }

        return {
          ...message,
          deliveryState: nextPlan.finalState,
          statusText: nextPlan.userMessage,
        };
      }),
    );
  }

  function handleSendMessage(draft: DraftMessage): void {
    const recipientId = getPrimaryRecipientId(selectedConversation);
    const sessionKey = keyStore.sessionsByContactId[recipientId] ?? keyStore.sessionsByContactId.sara ?? "mock_session";
    const encryptedEnvelope = encryptMessageMock(draft.body, sessionKey);
    const messageId = createId("msg");
    const newMessage: Message = {
      id: messageId,
      conversationId: draft.conversationId,
      authorId: localUser.id,
      authorName: localUser.displayName,
      body: draft.body,
      createdAt: new Date().toISOString(),
      deliveryState: "encrypting",
      statusText: "Encrypting locally.",
      encryptedEnvelope,
      disappearsAt: draft.disappearing ? minutesFromNow(60) : undefined,
      isLocalOnly: true,
    };

    setMessages((currentMessages) => [...currentMessages, newMessage]);

    for (const step of deliveryPlan.steps) {
      window.setTimeout(() => {
        setMessages((currentMessages) =>
          currentMessages.map((message) =>
            message.id === messageId
              ? {
                  ...message,
                  deliveryState: step.state,
                  statusText: step.statusText,
                }
              : message,
          ),
        );
      }, step.delayMs);
    }
  }

  function handlePanelSelect(panel: AppPanel): void {
    setActivePanel(panel);
    if (panel !== "chat") {
      setActiveInsightPanel(panel);
    }
  }

  function handleExportIncident(): void {
    setActivePanel("incident");
    setActiveInsightPanel("incident");
  }

  function handleResetDemoData(): void {
    setMessages(mockMessages);
    setSelectedConversationId("sara");
    handleScenarioChange("normal_internet_access");
  }

  return (
    <div className="app-root">
      <Header
        classificationLabel={confidence.classificationLabel}
        confidenceScore={confidence.overallScore}
        safetyModeEnabled={safetyControls.safetyModeEnabled}
        statusChip={scenario.statusChip}
      />

      <main className="app-layout" data-active-panel={activePanel}>
        <aside className="conversation-sidebar">
          <ConversationList
            contacts={mockContacts}
            conversations={mockConversations}
            onSelectConversation={(conversationId) => {
              setSelectedConversationId(conversationId);
              setActivePanel("chat");
            }}
            selectedConversationId={selectedConversationId}
          />
        </aside>

        <section className="chat-column" aria-label="Active chat">
          <ChatShell
            composerDisabled={safetyControls.emergencyPause}
            composerDisabledReason="Emergency pause is active"
            contacts={mockContacts}
            conversation={selectedConversation}
            messages={activeMessages}
            onSendMessage={handleSendMessage}
          />
        </section>

        <aside className="insight-panel" aria-label="Gorz panels">
          <div className="panel-switcher desktop-only" role="tablist" aria-label="Panel navigation">
            {panelButtons
              .filter((button) => button.id !== "chat")
              .map((button) => {
                const Icon = button.icon;
                return (
                  <button
                    aria-current={activeInsightPanel === button.id ? "page" : undefined}
                    className="panel-tab"
                    key={button.id}
                    onClick={() => setActiveInsightPanel(button.id as Exclude<AppPanel, "chat">)}
                    type="button"
                  >
                    <Icon aria-hidden="true" size={16} />
                    <span>{button.label}</span>
                  </button>
                );
              })}
          </div>

          <div hidden={activeInsightPanel !== "network"}>
            <NetworkConfidencePanel
              confidence={confidence}
              hideAdvancedDetails={safetyControls.hideAdvancedTechnicalDetails}
              onScenarioChange={handleScenarioChange}
              scenarios={diagnosticScenarios}
              selectedScenarioId={scenarioId}
            />
          </div>
          <div hidden={activeInsightPanel !== "safety"}>
            <SafetyModePanel controls={safetyControls} onControlsChange={setSafetyControls} />
          </div>
          <div hidden={activeInsightPanel !== "incident"}>
            <IncidentRecordPanel record={incidentRecord} />
          </div>
          <div hidden={activeInsightPanel !== "settings"}>
            <SettingsPanel
              controls={safetyControls}
              onControlsChange={setSafetyControls}
              onExportIncident={handleExportIncident}
              onResetDemoData={handleResetDemoData}
              onScenarioChange={handleScenarioChange}
              onThemeChange={setTheme}
              scenarios={diagnosticScenarios}
              selectedScenarioId={scenarioId}
              theme={theme}
            />
          </div>
        </aside>
      </main>

      <nav className="mobile-tabs" aria-label="Primary navigation">
        {panelButtons.map((button) => {
          const Icon = button.icon;
          return (
            <button
              aria-current={activePanel === button.id ? "page" : undefined}
              key={button.id}
              onClick={() => handlePanelSelect(button.id)}
              type="button"
            >
              <Icon aria-hidden="true" size={18} />
              <span>{button.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}

function getPrimaryRecipientId(conversation: { participantIds: string[] }): string {
  return conversation.participantIds.find((participantId) => participantId !== localUser.id) ?? "sara";
}

export default App;
