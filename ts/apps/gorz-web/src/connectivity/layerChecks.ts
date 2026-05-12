import type { AccessLayerScores } from "../types/connectivity";

export type LayerScoreKey = keyof AccessLayerScores;

export interface LayerCardDefinition {
  key: Exclude<LayerScoreKey, "safetyPenalty">;
  label: string;
  shortLabel: string;
}

export type LayerHealth = "healthy" | "limited" | "failed";

export const layerCardDefinitions: LayerCardDefinition[] = [
  { key: "dnsScore", label: "DNS", shortLabel: "DNS" },
  { key: "transportScore", label: "Transport", shortLabel: "TCP/QUIC" },
  { key: "tlsScore", label: "TLS/QUIC", shortLabel: "TLS" },
  { key: "applicationDeliveryScore", label: "Message delivery", shortLabel: "Delivery" },
  { key: "externalityScore", label: "Externality", shortLabel: "External" },
  { key: "corroborationScore", label: "Corroboration", shortLabel: "Corroboration" },
];

export function getLayerHealth(score: number): LayerHealth {
  if (score >= 0.75) {
    return "healthy";
  }

  if (score >= 0.4) {
    return "limited";
  }

  return "failed";
}

export function getLayerHealthLabel(score: number): string {
  const health = getLayerHealth(score);
  const labels: Record<LayerHealth, string> = {
    healthy: "Healthy",
    limited: "Limited",
    failed: "Weak",
  };
  return labels[health];
}
