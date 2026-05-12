import { describe, expect, it } from "vitest";

import { calculateConnectivityConfidence } from "./confidenceModel";
import { simulateDiagnosticScenario } from "./diagnosticSimulator";
import { createIncidentRecord, serializeIncidentRecord } from "./incidentRecord";
import type { SafetyControls } from "../types/connectivity";

const safetyControls: SafetyControls = {
  safetyModeEnabled: true,
  localDiagnosticsOnly: true,
  disableAutomaticDiagnosticUpload: true,
  delayIncidentExport: true,
  hideAdvancedTechnicalDetails: true,
  reduceDiagnosticFrequency: true,
  emergencyPause: false,
};

describe("createIncidentRecord", () => {
  it("creates a redacted record without personal identifiers or message content", () => {
    const evidence = simulateDiagnosticScenario("domestic_only_connectivity", "2026-01-01T00:00:00.000Z");
    const record = createIncidentRecord(
      {
        scenarioId: "domestic_only_connectivity",
        scenarioLabel: "Domestic-only connectivity",
        confidence: calculateConnectivityConfidence(evidence),
        messageDeliveryState: "delayed",
        safetyControls,
      },
      "2026-01-01T00:10:00.000Z",
    );
    const json = serializeIncidentRecord(record);

    expect(record.appName).toBe("Gorz");
    expect(record.classification).toBe("domestic_only_possible");
    expect(record.redactions).toContain("No real IP address");
    expect(json).not.toContain("Sara");
    expect(json).not.toContain("Can you receive this?");
    expect(json).not.toMatch(/\b\d{1,3}(?:\.\d{1,3}){3}\b/);
  });
});
