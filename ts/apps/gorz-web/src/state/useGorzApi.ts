import { useCallback, useEffect, useMemo, useState } from "react";

import { gorzApi } from "../api/client";
import type {
  AuditResponse,
  ConversationDetail,
  ConversationSummary,
  DiagnosticResponse,
  HealthResponse,
  IdentityResponse,
  IncidentResponse,
  SafetyResponse,
  ScenarioId,
  ScenarioInfo,
} from "../api/types";

interface GorzApiState {
  health: HealthResponse | null;
  safety: SafetyResponse | null;
  identities: IdentityResponse[];
  conversations: ConversationSummary[];
  selectedConversation: ConversationDetail | null;
  scenarios: ScenarioInfo[];
  diagnostic: DiagnosticResponse | null;
  incidents: IncidentResponse[];
  audit: AuditResponse[];
  activeIdentityId: string;
  selectedConversationId: string;
  selectedScenario: ScenarioId;
  loading: boolean;
  error: string | null;
}

export function useGorzApi() {
  const [state, setState] = useState<GorzApiState>({
    health: null,
    safety: null,
    identities: [],
    conversations: [],
    selectedConversation: null,
    scenarios: [],
    diagnostic: null,
    incidents: [],
    audit: [],
    activeIdentityId: "",
    selectedConversationId: "",
    selectedScenario: "direct_ok",
    loading: true,
    error: null,
  });

  const setError = useCallback((error: unknown) => {
    setState((current) => ({
      ...current,
      loading: false,
      error: error instanceof Error ? error.message : "Unexpected Gorz API error",
    }));
  }, []);

  const refreshAuditAndIncidents = useCallback(async () => {
    const [incidents, audit] = await Promise.all([gorzApi.listIncidents(), gorzApi.listAudit()]);
    setState((current) => ({ ...current, incidents, audit: audit.items }));
  }, []);

  const loadConversation = useCallback(async (conversationId: string) => {
    const detail = await gorzApi.getConversation(conversationId);
    setState((current) => ({
      ...current,
      selectedConversation: detail,
      selectedConversationId: detail.conversation_id,
    }));
    return detail;
  }, []);

  const refresh = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [health, safety, identities, conversations, scenarios, incidents, auditPage] = await Promise.all([
        gorzApi.health(),
        gorzApi.getSafety(),
        gorzApi.listIdentities(),
        gorzApi.listConversations(),
        gorzApi.listScenarios(),
        gorzApi.listIncidents(),
        gorzApi.listAudit(),
      ]);
      const selectedConversationId = state.selectedConversationId || conversations[0]?.conversation_id || "";
      const selectedConversation = selectedConversationId
        ? await gorzApi.getConversation(selectedConversationId)
        : null;
      const selectedScenario = state.selectedScenario;
      const diagnostic = await gorzApi.simulateDiagnostics(selectedScenario);
      setState((current) => ({
        ...current,
        health,
        safety,
        identities,
        conversations,
        selectedConversation,
        selectedConversationId,
        scenarios,
        diagnostic,
        incidents,
        audit: auditPage.items,
        activeIdentityId: current.activeIdentityId || identities[0]?.identity_id || "",
        loading: false,
        error: null,
      }));
    } catch (error) {
      setError(error);
    }
  }, [setError, state.selectedConversationId, state.selectedScenario]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const activeIdentity = useMemo(
    () => state.identities.find((identity) => identity.identity_id === state.activeIdentityId) ?? null,
    [state.activeIdentityId, state.identities],
  );

  const selectIdentity = useCallback((identityId: string) => {
    setState((current) => ({ ...current, activeIdentityId: identityId }));
  }, []);

  const selectConversation = useCallback(
    async (conversationId: string) => {
      try {
        await loadConversation(conversationId);
      } catch (error) {
        setError(error);
      }
    },
    [loadConversation, setError],
  );

  const createIdentity = useCallback(
    async (displayName: string, deviceLabel: string) => {
      try {
        const identity = await gorzApi.createIdentity(displayName, deviceLabel);
        setState((current) => ({
          ...current,
          identities: [...current.identities, identity],
          activeIdentityId: current.activeIdentityId || identity.identity_id,
          error: null,
        }));
        await refreshAuditAndIncidents();
      } catch (error) {
        setError(error);
      }
    },
    [refreshAuditAndIncidents, setError],
  );

  const createConversation = useCallback(
    async (title: string, participantIds: string[]) => {
      try {
        const conversation = await gorzApi.createConversation(title, participantIds);
        setState((current) => ({
          ...current,
          conversations: [...current.conversations, conversation],
          selectedConversationId: conversation.conversation_id,
        }));
        await loadConversation(conversation.conversation_id);
        await refreshAuditAndIncidents();
      } catch (error) {
        setError(error);
      }
    },
    [loadConversation, refreshAuditAndIncidents, setError],
  );

  const sendMessage = useCallback(
    async (body: string) => {
      if (!state.selectedConversationId || !state.activeIdentityId) {
        setState((current) => ({ ...current, error: "Create an identity and conversation first." }));
        return;
      }
      try {
        await gorzApi.createMessage(
          state.selectedConversationId,
          state.activeIdentityId,
          body,
          state.selectedScenario,
        );
        await loadConversation(state.selectedConversationId);
        await refreshAuditAndIncidents();
      } catch (error) {
        setError(error);
      }
    },
    [
      loadConversation,
      refreshAuditAndIncidents,
      setError,
      state.activeIdentityId,
      state.selectedConversationId,
      state.selectedScenario,
    ],
  );

  const selectScenario = useCallback(
    async (scenario: ScenarioId) => {
      setState((current) => ({ ...current, selectedScenario: scenario }));
      try {
        const diagnostic = await gorzApi.simulateDiagnostics(scenario);
        setState((current) => ({ ...current, diagnostic, error: null }));
        await refreshAuditAndIncidents();
      } catch (error) {
        setError(error);
      }
    },
    [refreshAuditAndIncidents, setError],
  );

  const generateIncident = useCallback(
    async (messageId: string) => {
      try {
        await gorzApi.createIncident(messageId);
        await refreshAuditAndIncidents();
      } catch (error) {
        setError(error);
      }
    },
    [refreshAuditAndIncidents, setError],
  );

  const pause = useCallback(async () => {
    try {
      const safety = await gorzApi.pause();
      setState((current) => ({ ...current, safety, error: null }));
      await refreshAuditAndIncidents();
    } catch (error) {
      setError(error);
    }
  }, [refreshAuditAndIncidents, setError]);

  const resume = useCallback(async () => {
    try {
      const safety = await gorzApi.resume();
      setState((current) => ({ ...current, safety, error: null }));
      await refreshAuditAndIncidents();
    } catch (error) {
      setError(error);
    }
  }, [refreshAuditAndIncidents, setError]);

  return {
    ...state,
    activeIdentity,
    refresh,
    selectIdentity,
    selectConversation,
    createIdentity,
    createConversation,
    sendMessage,
    selectScenario,
    generateIncident,
    pause,
    resume,
  };
}

