import type { MessageDeliveryState } from "./chat";
import type { AccessLayerScores, SafetyControls } from "./connectivity";

export type IncidentClassification =
  | "confirmed_external_access_likely"
  | "probable_external_access"
  | "selective_blocking_possible"
  | "domestic_only_possible"
  | "general_outage_possible"
  | "no_proof_of_external_access"
  | "inconclusive";

export interface IncidentRecord {
  incidentId: string;
  appName: "Gorz";
  generatedAt: string;
  timeWindow: {
    startedAt: string;
    endedAt: string;
  };
  scenario: string;
  classification: IncidentClassification;
  confidenceScore: number;
  layerScores: AccessLayerScores;
  evidenceSummary: string[];
  messageDeliveryState: MessageDeliveryState;
  safetyControls: SafetyControls;
  redactions: string[];
  notes: string[];
}
