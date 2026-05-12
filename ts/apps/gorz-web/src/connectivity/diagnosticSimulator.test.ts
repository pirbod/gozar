import { describe, expect, it } from "vitest";

import { diagnosticScenarios, getMessageDeliveryPlan } from "./diagnosticSimulator";

describe("message delivery plans", () => {
  it("maps every diagnostic scenario to a final delivery state", () => {
    for (const scenario of diagnosticScenarios) {
      const plan = getMessageDeliveryPlan(scenario.id);

      expect(plan.scenarioId).toBe(scenario.id);
      expect(plan.steps.length).toBeGreaterThan(0);
      expect(plan.steps.at(-1)?.state).toBe(plan.finalState);
    }
  });

  it("queues messages during a general outage", () => {
    expect(getMessageDeliveryPlan("general_outage").finalState).toBe("queued");
  });

  it("marks app relay blocking as blocked likely", () => {
    expect(getMessageDeliveryPlan("app_relay_blocked").finalState).toBe("blocked_likely");
  });
});
