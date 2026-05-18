export type ScenarioId =
  | "direct_ok"
  | "relay_ok"
  | "delayed"
  | "degraded"
  | "domestic_only"
  | "blocked"
  | "peer_offline";

export type DeliveryClassification =
  | "delivered_confirmed"
  | "delivered_probable"
  | "degraded_or_partial"
  | "not_delivered_or_no_proof";

export interface HealthResponse {
  service: string;
  status: string;
  version: string;
  safety_mode: string;
  storage_backend: string;
  timestamp: string;
}

export interface IdentityResponse {
  identity_id: string;
  device_id: string | null;
  display_name: string;
  device_label: string | null;
  public_key_demo: string;
  safety_notice: string;
  created_at: string | null;
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  participant_ids: string[];
  created_at: string;
}

export interface ConfidenceExplanation {
  top_positive_factors: string[];
  top_negative_factors: string[];
  human_summary: string;
  recommended_user_message: string;
  scenario_summary?: string | null;
}

export interface DiagnosticResponse {
  scenario: ScenarioId;
  label: string;
  dns_score: number;
  transport_score: number;
  tls_or_quic_score: number;
  app_delivery_score: number;
  path_diversity_score: number;
  source_independence_score: number;
  risk_penalty: number;
  confidence: number;
  classification: DeliveryClassification;
  mandatory_score: number;
  support_score: number;
  explanation: ConfidenceExplanation;
}

export interface MessageResponse {
  message_id: string;
  conversation_id: string;
  sender_id: string;
  scenario: ScenarioId;
  redacted_preview: string;
  envelope_hash: string;
  delivery_status: DeliveryClassification;
  confidence: number;
  evidence: {
    delivery_path_class?: string;
    peer_receipt_simulated?: boolean;
    safety_notes?: string[];
    diagnostic?: DiagnosticResponse;
    [key: string]: unknown;
  };
  redaction_status: string;
  created_at: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: MessageResponse[];
}

export interface ScenarioInfo {
  id: ScenarioId;
  label: string;
  explanation: string;
}

export interface IncidentResponse {
  incident_id: string;
  created_at: string;
  record: {
    classification?: DeliveryClassification;
    confidence?: number;
    redactions?: string[];
    evidence?: Record<string, unknown>;
    [key: string]: unknown;
  };
}

export interface AuditResponse {
  event_id: string;
  event_type: string;
  actor_id: string | null;
  summary: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AuditPage {
  items: AuditResponse[];
  limit: number;
  offset: number;
  total: number;
}

export interface SafetyResponse {
  safety_mode: string;
  pause_enabled: boolean;
  limitations: string[];
  updated_at: string | null;
}

export function isDeliveryClassification(value: string): value is DeliveryClassification {
  return (
    value === "delivered_confirmed" ||
    value === "delivered_probable" ||
    value === "degraded_or_partial" ||
    value === "not_delivered_or_no_proof"
  );
}

