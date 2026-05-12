import type {
  AccessClassification,
  AccessLayerScores,
  ConnectivityConfidenceResult,
  ConnectivityEvidence,
} from "../types/connectivity";

const classificationLabels: Record<AccessClassification, string> = {
  confirmed_external_access_likely: "Confirmed external access likely",
  probable_external_access: "Probable external access",
  selective_blocking_or_domestic_only_possible: "Selective blocking or domestic-only reachability possible",
  no_proof_of_external_access: "No proof of external access",
};

function clamp(value: number, minimum = 0, maximum = 1): number {
  return Math.min(Math.max(value, minimum), maximum);
}

function geometricMean(values: number[]): number {
  if (values.some((value) => value <= 0)) {
    return 0;
  }

  const product = values.reduce((current, value) => current * value, 1);
  return product ** (1 / values.length);
}

function normalizeScores(scores: AccessLayerScores): AccessLayerScores {
  return {
    dnsScore: clamp(scores.dnsScore),
    transportScore: clamp(scores.transportScore),
    tlsScore: clamp(scores.tlsScore),
    applicationDeliveryScore: clamp(scores.applicationDeliveryScore),
    externalityScore: clamp(scores.externalityScore),
    corroborationScore: clamp(scores.corroborationScore),
    safetyPenalty: clamp(scores.safetyPenalty),
  };
}

export function classifyAccessConfidence(score: number): AccessClassification {
  if (score >= 0.85) {
    return "confirmed_external_access_likely";
  }

  if (score >= 0.65) {
    return "probable_external_access";
  }

  if (score >= 0.4) {
    return "selective_blocking_or_domestic_only_possible";
  }

  return "no_proof_of_external_access";
}

export function getAccessClassificationLabel(classification: AccessClassification): string {
  return classificationLabels[classification];
}

export function calculateConnectivityConfidence(evidence: ConnectivityEvidence): ConnectivityConfidenceResult {
  const layerScores = normalizeScores(evidence.layerScores);
  const mandatoryScore = geometricMean([
    layerScores.dnsScore,
    layerScores.transportScore,
    layerScores.tlsScore,
    layerScores.applicationDeliveryScore,
  ]);
  const supportScore = clamp(layerScores.externalityScore * 0.65 + layerScores.corroborationScore * 0.35);
  const overallScore = clamp(
    mandatoryScore ** 0.7 * supportScore ** 0.3 * (1 - layerScores.safetyPenalty),
  );
  const classification = classifyAccessConfidence(overallScore);

  return {
    overallScore,
    classification,
    classificationLabel: getAccessClassificationLabel(classification),
    mandatoryScore,
    supportScore,
    layerScores,
    explanation: buildConfidenceExplanation(classification, evidence.evidenceSummary),
    lastCheckedAt: evidence.observedAt,
    safetyNote: evidence.safetyNote,
    technicalDetails: evidence.technicalDetails,
  };
}

export function buildConfidenceExplanation(
  classification: AccessClassification,
  evidenceSummary: string,
): string {
  const prefix: Record<AccessClassification, string> = {
    confirmed_external_access_likely:
      "The encrypted delivery path has strong multi-layer evidence and external reachability is likely.",
    probable_external_access:
      "The path has enough evidence for likely external reachability, with some remaining uncertainty.",
    selective_blocking_or_domestic_only_possible:
      "Mandatory layers or externality evidence are limited, so partial reachability remains possible.",
    no_proof_of_external_access:
      "The current evidence does not prove external Internet access for message delivery.",
  };

  return `${prefix[classification]} ${evidenceSummary}`;
}
