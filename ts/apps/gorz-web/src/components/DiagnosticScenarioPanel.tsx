import type { DiagnosticResponse, ScenarioId, ScenarioInfo } from "../api/types";
import { formatPercent, formatStatus, statusTone } from "../utils/formatting";

interface DiagnosticScenarioPanelProps {
  scenarios: ScenarioInfo[];
  selectedScenario: ScenarioId;
  diagnostic: DiagnosticResponse | null;
  onSelectScenario: (scenario: ScenarioId) => void;
}

export function DiagnosticScenarioPanel({
  scenarios,
  selectedScenario,
  diagnostic,
  onSelectScenario,
}: DiagnosticScenarioPanelProps) {
  return (
    <section className="panel diagnostic-panel" aria-labelledby="diagnostic-title">
      <div className="section-title">
        <h2 id="diagnostic-title">Simulated Diagnostics</h2>
      </div>
      <div className="scenario-grid">
        {scenarios.map((scenario) => (
          <button
            aria-current={scenario.id === selectedScenario ? "page" : undefined}
            key={scenario.id}
            onClick={() => onSelectScenario(scenario.id)}
            type="button"
          >
            <strong>{scenario.label}</strong>
            <span>{scenario.explanation}</span>
          </button>
        ))}
      </div>
      {diagnostic ? (
        <div className="diagnostic-result">
          <div className="confidence-meter">
            <span>{formatPercent(diagnostic.confidence)}</span>
            <div className="meter-track" aria-hidden="true">
              <div style={{ width: formatPercent(diagnostic.confidence) }} />
            </div>
          </div>
          <span className={`pill ${statusTone(diagnostic.classification)}`}>
            {formatStatus(diagnostic.classification)}
          </span>
          <p>{diagnostic.explanation.recommended_user_message}</p>
        </div>
      ) : null}
    </section>
  );
}

