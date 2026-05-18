import type {
  AuditPage,
  ConversationDetail,
  ConversationSummary,
  DiagnosticResponse,
  HealthResponse,
  IdentityResponse,
  IncidentResponse,
  SafetyResponse,
  ScenarioId,
  ScenarioInfo,
  MessageResponse,
} from "./types";

const env = (import.meta as ImportMeta & { env?: { VITE_GORZ_API_BASE_URL?: string } }).env;
export const API_BASE_URL = env?.VITE_GORZ_API_BASE_URL ?? "http://localhost:8090";

export class GorzApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "GorzApiError";
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const message = await response
      .json()
      .then((body: unknown) => extractDetail(body))
      .catch(() => response.statusText);
    throw new GorzApiError(message, response.status);
  }

  return (await response.json()) as T;
}

function extractDetail(body: unknown): string {
  if (isRecord(body) && typeof body.detail === "string") {
    return body.detail;
  }
  return "Gorz API request failed";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export const gorzApi = {
  health: () => requestJson<HealthResponse>("/api/gorz/health"),
  listIdentities: () => requestJson<IdentityResponse[]>("/api/gorz/identities"),
  createIdentity: (displayName: string, deviceLabel: string) =>
    requestJson<IdentityResponse>("/api/gorz/identities", {
      method: "POST",
      body: JSON.stringify({ display_name: displayName, device_label: deviceLabel }),
    }),
  listConversations: () => requestJson<ConversationSummary[]>("/api/gorz/conversations"),
  createConversation: (title: string, participantIds: string[]) =>
    requestJson<ConversationSummary>("/api/gorz/conversations", {
      method: "POST",
      body: JSON.stringify({ title, participant_ids: participantIds }),
    }),
  getConversation: (conversationId: string) =>
    requestJson<ConversationDetail>(`/api/gorz/conversations/${conversationId}`),
  createMessage: (conversationId: string, senderId: string, body: string, scenario: ScenarioId) =>
    requestJson<MessageResponse>("/api/gorz/messages", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId, sender_id: senderId, body, scenario }),
    }),
  listScenarios: () => requestJson<ScenarioInfo[]>("/api/gorz/diagnostics/scenarios"),
  simulateDiagnostics: (scenario: ScenarioId) =>
    requestJson<DiagnosticResponse>("/api/gorz/diagnostics/simulate", {
      method: "POST",
      body: JSON.stringify({ scenario }),
    }),
  createIncident: (messageId: string) =>
    requestJson<IncidentResponse>(`/api/gorz/incidents/from-message/${messageId}`, {
      method: "POST",
    }),
  listIncidents: () => requestJson<IncidentResponse[]>("/api/gorz/incidents"),
  listAudit: () => requestJson<AuditPage>("/api/gorz/audit?limit=80"),
  getSafety: () => requestJson<SafetyResponse>("/api/gorz/safety"),
  pause: () => requestJson<SafetyResponse>("/api/gorz/safety/pause", { method: "POST" }),
  resume: () => requestJson<SafetyResponse>("/api/gorz/safety/resume", { method: "POST" }),
};

export function incidentDownloadUrl(incidentId: string): string {
  return `${API_BASE_URL}/api/gorz/incidents/${incidentId}/download`;
}

