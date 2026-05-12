import { diagnosticScenarios } from "../connectivity/diagnosticSimulator";

export const mockNetworkEvents = diagnosticScenarios.map((scenario, index) => ({
  id: `event-${scenario.id}`,
  scenarioId: scenario.id,
  label: scenario.label,
  observedAt: new Date(Date.now() - index * 15 * 60_000).toISOString(),
}));
