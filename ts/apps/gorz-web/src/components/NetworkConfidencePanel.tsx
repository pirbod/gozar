import { ChevronDown, ChevronUp, Gauge, RefreshCw } from "lucide-react";
import { useState } from "react";

import { getLayerHealth, getLayerHealthLabel, layerCardDefinitions } from "../connectivity/layerChecks";
import type {
  ConnectivityConfidenceResult,
  DiagnosticScenario,
  DiagnosticScenarioId,
} from "../types/connectivity";
import { formatPercent } from "../utils/format";
import { formatDateTime } from "../utils/time";

interface NetworkConfidencePanelProps {
  confidence: ConnectivityConfidenceResult;
  scenarios: DiagnosticScenario[];
  selectedScenarioId: DiagnosticScenarioId;
  hideAdvancedDetails: boolean;
  onScenarioChange: (scenarioId: DiagnosticScenarioId) => void;
}

export function NetworkConfidencePanel({
  confidence,
  scenarios,
  selectedScenarioId,
  hideAdvancedDetails,
  onScenarioChange,
}: NetworkConfidencePanelProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  return (
    <section className="panel-card" aria-labelledby="network-confidence-title">
      <div className="panel-title-row">
        <div>
          <h2 id="network-confidence-title">Network Confidence</h2>
          <p>Local simulated evidence for the current message path.</p>
        </div>
        <Gauge aria-hidden="true" size={22} />
      </div>

      <label className="field-label" htmlFor="scenario-select">
        Demo scenario
      </label>
      <select
        className="select-input"
        id="scenario-select"
        onChange={(event) => onScenarioChange(event.target.value as DiagnosticScenarioId)}
        value={selectedScenarioId}
      >
        {scenarios.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.label}
          </option>
        ))}
      </select>

      <div className="confidence-hero">
        <span>{formatPercent(confidence.overallScore)}</span>
        <strong>{confidence.classificationLabel}</strong>
      </div>

      <div className="layer-grid" aria-label="Layer scores">
        {layerCardDefinitions.map((definition) => {
          const score = confidence.layerScores[definition.key];
          const health = getLayerHealth(score);
          return (
            <article className={`layer-card layer-${health}`} key={definition.key}>
              <span>{definition.label}</span>
              <strong>{formatPercent(score)}</strong>
              <small>{getLayerHealthLabel(score)}</small>
            </article>
          );
        })}
      </div>

      <p className="panel-explanation">{confidence.explanation}</p>

      <div className="check-row">
        <RefreshCw aria-hidden="true" size={15} />
        <span>Last checked {formatDateTime(confidence.lastCheckedAt)}</span>
      </div>
      <p className="safety-note">{confidence.safetyNote}</p>

      <button
        aria-expanded={advancedOpen}
        className="secondary-action full-width"
        disabled={hideAdvancedDetails}
        onClick={() => setAdvancedOpen((open) => !open)}
        type="button"
      >
        {advancedOpen ? <ChevronUp aria-hidden="true" size={16} /> : <ChevronDown aria-hidden="true" size={16} />}
        <span>{hideAdvancedDetails ? "Advanced details hidden by Safety mode" : "Advanced details"}</span>
      </button>

      {advancedOpen && !hideAdvancedDetails ? (
        <ul className="advanced-list">
          {confidence.technicalDetails.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
          <li>Mandatory score: {formatPercent(confidence.mandatoryScore)}</li>
          <li>Support score: {formatPercent(confidence.supportScore)}</li>
        </ul>
      ) : null}
    </section>
  );
}
