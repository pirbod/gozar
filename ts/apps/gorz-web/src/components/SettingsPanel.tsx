import { Info, RotateCcw, Save, SlidersHorizontal } from "lucide-react";

import type { DiagnosticScenario, DiagnosticScenarioId, SafetyControls } from "../types/connectivity";

interface SettingsPanelProps {
  controls: SafetyControls;
  scenarios: DiagnosticScenario[];
  selectedScenarioId: DiagnosticScenarioId;
  theme: "light" | "dark";
  onControlsChange: (controls: SafetyControls) => void;
  onScenarioChange: (scenarioId: DiagnosticScenarioId) => void;
  onThemeChange: (theme: "light" | "dark") => void;
  onExportIncident: () => void;
  onResetDemoData: () => void;
}

export function SettingsPanel({
  controls,
  scenarios,
  selectedScenarioId,
  theme,
  onControlsChange,
  onScenarioChange,
  onThemeChange,
  onExportIncident,
  onResetDemoData,
}: SettingsPanelProps) {
  return (
    <section className="panel-card" aria-labelledby="settings-title">
      <div className="panel-title-row">
        <div>
          <h2 id="settings-title">Settings</h2>
          <p>Demo controls for the local prototype.</p>
        </div>
        <SlidersHorizontal aria-hidden="true" size={22} />
      </div>

      <label className="toggle-row primary-toggle">
        <span>
          <strong>Safety mode</strong>
          <small>Keep diagnostics minimized and local-first.</small>
        </span>
        <input
          checked={controls.safetyModeEnabled}
          onChange={(event) =>
            onControlsChange({
              ...controls,
              safetyModeEnabled: event.target.checked,
            })
          }
          type="checkbox"
        />
      </label>

      <label className="field-label" htmlFor="theme-select">
        Theme
      </label>
      <select
        className="select-input"
        id="theme-select"
        onChange={(event) => onThemeChange(event.target.value as "light" | "dark")}
        value={theme}
      >
        <option value="dark">Dark</option>
        <option value="light">Light</option>
      </select>

      <label className="field-label" htmlFor="settings-scenario-select">
        Diagnostic scenario
      </label>
      <select
        className="select-input"
        id="settings-scenario-select"
        onChange={(event) => onScenarioChange(event.target.value as DiagnosticScenarioId)}
        value={selectedScenarioId}
      >
        {scenarios.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.label}
          </option>
        ))}
      </select>

      <div className="button-row stacked-buttons">
        <button className="secondary-action" onClick={onExportIncident} type="button">
          <Save aria-hidden="true" size={16} />
          <span>Export current incident record</span>
        </button>
        <button className="secondary-action" onClick={onResetDemoData} type="button">
          <RotateCcw aria-hidden="true" size={16} />
          <span>Reset demo data</span>
        </button>
      </div>

      <div className="about-box">
        <h3>
          <Info aria-hidden="true" size={16} />
          About Gorz
        </h3>
        <p>
          Gorz is a research-inspired encrypted messaging PoC based on the Gozar framework for
          confidence-scored, multi-layer Internet access evidence. This prototype demonstrates how a
          messenger can communicate delivery confidence without exposing users to unnecessary measurement risk.
        </p>
      </div>
    </section>
  );
}
