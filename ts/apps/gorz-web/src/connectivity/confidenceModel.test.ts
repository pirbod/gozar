import { describe, expect, it } from "vitest";

import { calculateConnectivityConfidence } from "./confidenceModel";
import { simulateDiagnosticScenario } from "./diagnosticSimulator";

describe("calculateConnectivityConfidence", () => {
  it("classifies strong multi-layer evidence as confirmed external access likely", () => {
    const result = calculateConnectivityConfidence(
      simulateDiagnosticScenario("normal_internet_access", "2026-01-01T00:00:00.000Z"),
    );

    expect(result.classification).toBe("confirmed_external_access_likely");
    expect(result.overallScore).toBeGreaterThanOrEqual(0.85);
  });

  it("does not average away a failed mandatory layer", () => {
    const result = calculateConnectivityConfidence(
      simulateDiagnosticScenario("application_delivery_failure", "2026-01-01T00:00:00.000Z"),
    );

    expect(result.classification).toBe("selective_blocking_or_domestic_only_possible");
    expect(result.overallScore).toBeLessThan(0.65);
  });

  it("classifies a broad outage as no proof of external access", () => {
    const result = calculateConnectivityConfidence(
      simulateDiagnosticScenario("general_outage", "2026-01-01T00:00:00.000Z"),
    );

    expect(result.classification).toBe("no_proof_of_external_access");
  });
});
