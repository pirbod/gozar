import type {
  ConnectivityEvidence,
  DiagnosticScenario,
  DiagnosticScenarioId,
  MessageDeliveryPlan,
} from "../types/connectivity";

export const diagnosticScenarios: DiagnosticScenario[] = [
  {
    id: "normal_internet_access",
    label: "Normal Internet access",
    description: "All simulated layers are healthy and encrypted delivery is confirmed.",
    statusChip: "secure",
    evidence: {
      scenarioId: "normal_internet_access",
      scenarioLabel: "Normal Internet access",
      layerScores: {
        dnsScore: 0.98,
        transportScore: 0.96,
        tlsScore: 0.96,
        applicationDeliveryScore: 0.97,
        externalityScore: 0.95,
        corroborationScore: 0.9,
        safetyPenalty: 0.02,
      },
      evidenceSummary: "The simulated encrypted envelope reached the relay path and corroborating evidence agrees.",
      technicalDetails: [
        "DNS, transport, TLS/QUIC, and message delivery checks are simulated as successful.",
        "External path validation and independent corroboration are both high-confidence mock signals.",
      ],
      safetyNote: "Diagnostics remain local and use only mock evidence.",
    },
  },
  {
    id: "app_relay_blocked",
    label: "App relay blocked",
    description: "The app path appears selectively unavailable while other layers show partial reachability.",
    statusChip: "blocked_likely",
    evidence: {
      scenarioId: "app_relay_blocked",
      scenarioLabel: "App relay blocked",
      layerScores: {
        dnsScore: 0.9,
        transportScore: 0.65,
        tlsScore: 0.6,
        applicationDeliveryScore: 0.25,
        externalityScore: 0.4,
        corroborationScore: 0.6,
        safetyPenalty: 0.05,
      },
      evidenceSummary: "The mock app relay path is not confirming encrypted envelope delivery.",
      technicalDetails: [
        "The simulated transport partially opens but application delivery does not complete.",
        "The model avoids concluding why the path failed from a single signal.",
      ],
      safetyNote: "No real relay probing is performed.",
    },
  },
  {
    id: "dns_interference",
    label: "DNS interference",
    description: "Name resolution is unreliable in the local mock evidence.",
    statusChip: "limited",
    evidence: {
      scenarioId: "dns_interference",
      scenarioLabel: "DNS interference",
      layerScores: {
        dnsScore: 0.2,
        transportScore: 0.3,
        tlsScore: 0.25,
        applicationDeliveryScore: 0.15,
        externalityScore: 0.3,
        corroborationScore: 0.5,
        safetyPenalty: 0.04,
      },
      evidenceSummary: "The simulator reports weak DNS evidence, so later layers cannot be trusted.",
      technicalDetails: [
        "Mock DNS resolution is inconsistent.",
        "Later layers are downweighted because the path cannot be established cleanly.",
      ],
      safetyNote: "The DNS condition is simulated and does not query real destinations.",
    },
  },
  {
    id: "tls_handshake_failure",
    label: "TLS handshake failure",
    description: "The transport path opens, but the protected session is not validated.",
    statusChip: "limited",
    evidence: {
      scenarioId: "tls_handshake_failure",
      scenarioLabel: "TLS handshake failure",
      layerScores: {
        dnsScore: 0.85,
        transportScore: 0.8,
        tlsScore: 0.15,
        applicationDeliveryScore: 0.2,
        externalityScore: 0.45,
        corroborationScore: 0.4,
        safetyPenalty: 0.05,
      },
      evidenceSummary: "The protected mock session cannot be validated, so delivery confidence is low.",
      technicalDetails: [
        "The simulator marks TLS/QUIC validation as failed.",
        "Application delivery is limited because the encrypted path is not established.",
      ],
      safetyNote: "The failure is local demo data, not a live handshake.",
    },
  },
  {
    id: "domestic_only_connectivity",
    label: "Domestic-only connectivity",
    description: "Local reachability exists, but external path evidence is weak.",
    statusChip: "limited",
    evidence: {
      scenarioId: "domestic_only_connectivity",
      scenarioLabel: "Domestic-only connectivity",
      layerScores: {
        dnsScore: 0.85,
        transportScore: 0.75,
        tlsScore: 0.7,
        applicationDeliveryScore: 0.6,
        externalityScore: 0.18,
        corroborationScore: 0.45,
        safetyPenalty: 0.04,
      },
      evidenceSummary: "The simulator can reach local-looking paths, but external delivery is not confirmed.",
      technicalDetails: [
        "Mandatory layers are partly available.",
        "Externality evidence remains low, preventing a full delivery claim.",
      ],
      safetyNote: "The app reports uncertainty without attempting additional probing.",
    },
  },
  {
    id: "general_outage",
    label: "General outage",
    description: "Most simulated layers are unavailable.",
    statusChip: "outage_likely",
    evidence: {
      scenarioId: "general_outage",
      scenarioLabel: "General outage",
      layerScores: {
        dnsScore: 0.1,
        transportScore: 0.1,
        tlsScore: 0.05,
        applicationDeliveryScore: 0.05,
        externalityScore: 0.1,
        corroborationScore: 0.35,
        safetyPenalty: 0.03,
      },
      evidenceSummary: "The local mock network is broadly unavailable.",
      technicalDetails: [
        "DNS, transport, protected session, and application delivery all report poor evidence.",
        "Corroboration does not provide enough support to override mandatory layer failures.",
      ],
      safetyNote: "Queued messages remain local until the demo scenario changes.",
    },
  },
  {
    id: "intermittent_mobile_disruption",
    label: "Intermittent mobile disruption",
    description: "The path changes often enough that delivery is delayed.",
    statusChip: "limited",
    evidence: {
      scenarioId: "intermittent_mobile_disruption",
      scenarioLabel: "Intermittent mobile disruption",
      layerScores: {
        dnsScore: 0.65,
        transportScore: 0.55,
        tlsScore: 0.5,
        applicationDeliveryScore: 0.45,
        externalityScore: 0.55,
        corroborationScore: 0.5,
        safetyPenalty: 0.04,
      },
      evidenceSummary: "The simulated mobile path is unstable and cannot maintain enough evidence.",
      technicalDetails: [
        "Mandatory layers are possible but inconsistent.",
        "The confidence model keeps the result below probable access.",
      ],
      safetyNote: "Reduced diagnostic frequency can limit repeated local checks.",
    },
  },
  {
    id: "quic_degraded_tcp_available",
    label: "QUIC degraded, TCP available",
    description: "QUIC evidence is degraded, but the mock app still confirms delivery through TCP.",
    statusChip: "secure",
    evidence: {
      scenarioId: "quic_degraded_tcp_available",
      scenarioLabel: "QUIC degraded, TCP available",
      layerScores: {
        dnsScore: 0.9,
        transportScore: 0.82,
        tlsScore: 0.78,
        applicationDeliveryScore: 0.86,
        externalityScore: 0.82,
        corroborationScore: 0.7,
        safetyPenalty: 0.02,
      },
      evidenceSummary: "The mock encrypted envelope reaches the app layer despite degraded QUIC evidence.",
      technicalDetails: [
        "The simulator marks QUIC as degraded and TCP as available.",
        "This is a local product-state demo, not protocol camouflage.",
      ],
      safetyNote: "The app does not switch to hidden or evasive probing.",
    },
  },
  {
    id: "application_delivery_failure",
    label: "Application delivery failure",
    description: "Network setup looks plausible, but the encrypted message envelope does not arrive.",
    statusChip: "limited",
    evidence: {
      scenarioId: "application_delivery_failure",
      scenarioLabel: "Application delivery failure",
      layerScores: {
        dnsScore: 0.9,
        transportScore: 0.85,
        tlsScore: 0.8,
        applicationDeliveryScore: 0.25,
        externalityScore: 0.78,
        corroborationScore: 0.65,
        safetyPenalty: 0.04,
      },
      evidenceSummary: "The mock network path exists, but the message envelope is not delivered.",
      technicalDetails: [
        "Application-layer confirmation is the bottleneck.",
        "The score prevents lower-layer success from averaging away delivery failure.",
      ],
      safetyNote: "The app keeps raw message content out of diagnostics.",
    },
  },
  {
    id: "low_evidence_inconclusive",
    label: "Low evidence, inconclusive",
    description: "The app has too little local evidence for a confident classification.",
    statusChip: "inconclusive",
    evidence: {
      scenarioId: "low_evidence_inconclusive",
      scenarioLabel: "Low evidence, inconclusive",
      layerScores: {
        dnsScore: 0.5,
        transportScore: 0.5,
        tlsScore: 0.5,
        applicationDeliveryScore: 0.4,
        externalityScore: 0.35,
        corroborationScore: 0.25,
        safetyPenalty: 0.08,
      },
      evidenceSummary: "The simulator has insufficient evidence and avoids overclaiming delivery state.",
      technicalDetails: [
        "All layers have partial or low evidence.",
        "Safety penalty reflects uncertainty and reduced diagnostic collection.",
      ],
      safetyNote: "Inconclusive is safer than a false success claim.",
    },
  },
];

const deliveryPlans: Record<DiagnosticScenarioId, MessageDeliveryPlan> = {
  normal_internet_access: {
    scenarioId: "normal_internet_access",
    finalState: "delivered",
    userMessage: "Encrypted envelope reached the relay path.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "sent", delayMs: 550, statusText: "Encrypted envelope sent." },
      { state: "delivered", delayMs: 900, statusText: "Delivered with confirmed external access likely." },
    ],
  },
  app_relay_blocked: {
    scenarioId: "app_relay_blocked",
    finalState: "blocked_likely",
    userMessage: "Gorz cannot confirm the app relay path.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "queued", delayMs: 550, statusText: "Queued while the relay path is checked." },
      { state: "blocked_likely", delayMs: 900, statusText: "Relay path appears blocked or selectively unavailable." },
    ],
  },
  dns_interference: {
    scenarioId: "dns_interference",
    finalState: "delayed",
    userMessage: "Name resolution evidence is weak.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "delayed", delayMs: 700, statusText: "Delivery delayed because DNS evidence is weak." },
    ],
  },
  tls_handshake_failure: {
    scenarioId: "tls_handshake_failure",
    finalState: "failed",
    userMessage: "Protected session validation failed in the simulator.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "failed", delayMs: 700, statusText: "Protected delivery session was not validated." },
    ],
  },
  domestic_only_connectivity: {
    scenarioId: "domestic_only_connectivity",
    finalState: "delayed",
    userMessage: "Network appears limited. External delivery is not confirmed.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "delayed", delayMs: 700, statusText: "Network appears limited. External delivery is not confirmed." },
    ],
  },
  general_outage: {
    scenarioId: "general_outage",
    finalState: "queued",
    userMessage: "Message will retry when connectivity improves.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "queued", delayMs: 700, statusText: "Message will retry when connectivity improves." },
    ],
  },
  intermittent_mobile_disruption: {
    scenarioId: "intermittent_mobile_disruption",
    finalState: "delayed",
    userMessage: "Delivery delayed while the mobile path stabilizes.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "delayed", delayMs: 700, statusText: "Delivery delayed while the mobile path stabilizes." },
    ],
  },
  quic_degraded_tcp_available: {
    scenarioId: "quic_degraded_tcp_available",
    finalState: "delivered",
    userMessage: "Delivered while QUIC is degraded and TCP is available.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "sent", delayMs: 550, statusText: "Encrypted envelope sent." },
      { state: "delivered", delayMs: 900, statusText: "Delivered while QUIC is degraded and TCP is available." },
    ],
  },
  application_delivery_failure: {
    scenarioId: "application_delivery_failure",
    finalState: "failed",
    userMessage: "Encrypted envelope did not reach the app layer.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "failed", delayMs: 700, statusText: "Encrypted envelope did not reach the app layer." },
    ],
  },
  low_evidence_inconclusive: {
    scenarioId: "low_evidence_inconclusive",
    finalState: "delayed",
    userMessage: "Delivery uncertain. Gorz cannot safely determine network state.",
    steps: [
      { state: "encrypting", delayMs: 250, statusText: "Encrypting locally." },
      { state: "delayed", delayMs: 700, statusText: "Delivery uncertain. Gorz cannot safely determine network state." },
    ],
  },
};

export function getDiagnosticScenario(scenarioId: DiagnosticScenarioId): DiagnosticScenario {
  return diagnosticScenarios.find((scenario) => scenario.id === scenarioId) ?? diagnosticScenarios[0];
}

export function simulateDiagnosticScenario(
  scenarioId: DiagnosticScenarioId,
  observedAt = new Date().toISOString(),
): ConnectivityEvidence {
  const scenario = getDiagnosticScenario(scenarioId);
  return {
    ...scenario.evidence,
    observedAt,
  };
}

export function getMessageDeliveryPlan(scenarioId: DiagnosticScenarioId): MessageDeliveryPlan {
  return deliveryPlans[scenarioId];
}
