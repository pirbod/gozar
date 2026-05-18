import type { ScenarioId } from "../api/types";
import { DiagnosticScenarioPanel } from "../components/DiagnosticScenarioPanel";
import { EvidenceBreakdown } from "../components/EvidenceBreakdown";

interface DiagnosticsPageProps {
  scenarios: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["scenarios"];
  selectedScenario: ScenarioId;
  diagnostic: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["diagnostic"];
  onSelectScenario: (scenario: ScenarioId) => void;
}

export function DiagnosticsPage({
  scenarios,
  selectedScenario,
  diagnostic,
  onSelectScenario,
}: DiagnosticsPageProps) {
  return (
    <div className="page-grid">
      <DiagnosticScenarioPanel
        diagnostic={diagnostic}
        onSelectScenario={onSelectScenario}
        scenarios={scenarios}
        selectedScenario={selectedScenario}
      />
      <EvidenceBreakdown diagnostic={diagnostic} message={null} />
    </div>
  );
}

