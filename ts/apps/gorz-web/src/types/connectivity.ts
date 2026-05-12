import type { MessageDeliveryState } from "./chat";

export interface AccessLayerScores {
  dnsScore: number;
  transportScore: number;
  tlsScore: number;
  applicationDeliveryScore: number;
  externalityScore: number;
  corroborationScore: number;
  safetyPenalty: number;
}

export type AccessClassification =
  | "confirmed_external_access_likely"
  | "probable_external_access"
  | "selective_blocking_or_domestic_only_possible"
  | "no_proof_of_external_access";

export type DiagnosticScenarioId =
  | "normal_internet_access"
  | "app_relay_blocked"
  | "dns_interference"
  | "tls_handshake_failure"
  | "domestic_only_connectivity"
  | "general_outage"
  | "intermittent_mobile_disruption"
  | "quic_degraded_tcp_available"
  | "application_delivery_failure"
  | "low_evidence_inconclusive";

export type NetworkStatusChip = "secure" | "limited" | "blocked_likely" | "outage_likely" | "inconclusive";

export interface ConnectivityEvidence {
  scenarioId: DiagnosticScenarioId;
  scenarioLabel: string;
  observedAt: string;
  layerScores: AccessLayerScores;
  evidenceSummary: string;
  technicalDetails: string[];
  safetyNote: string;
}

export interface ConnectivityConfidenceResult {
  overallScore: number;
  classification: AccessClassification;
  classificationLabel: string;
  mandatoryScore: number;
  supportScore: number;
  layerScores: AccessLayerScores;
  explanation: string;
  lastCheckedAt: string;
  safetyNote: string;
  technicalDetails: string[];
}

export interface DiagnosticScenario {
  id: DiagnosticScenarioId;
  label: string;
  description: string;
  statusChip: NetworkStatusChip;
  evidence: Omit<ConnectivityEvidence, "observedAt">;
}

export interface MessageDeliveryStep {
  state: MessageDeliveryState;
  delayMs: number;
  statusText: string;
}

export interface MessageDeliveryPlan {
  scenarioId: DiagnosticScenarioId;
  finalState: MessageDeliveryState;
  steps: MessageDeliveryStep[];
  userMessage: string;
}

export interface SafetyControls {
  safetyModeEnabled: boolean;
  localDiagnosticsOnly: boolean;
  disableAutomaticDiagnosticUpload: boolean;
  delayIncidentExport: boolean;
  hideAdvancedTechnicalDetails: boolean;
  reduceDiagnosticFrequency: boolean;
  emergencyPause: boolean;
}
