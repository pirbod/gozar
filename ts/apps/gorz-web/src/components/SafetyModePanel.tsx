import { PauseCircle, ShieldCheck } from "lucide-react";

import type { SafetyControls } from "../types/connectivity";

interface SafetyModePanelProps {
  controls: SafetyControls;
  onControlsChange: (controls: SafetyControls) => void;
}

type SafetyToggleKey = keyof SafetyControls;

const toggleRows: Array<{ key: SafetyToggleKey; label: string; description: string }> = [
  {
    key: "localDiagnosticsOnly",
    label: "Local diagnostics only",
    description: "Use simulated local evidence and avoid network requests.",
  },
  {
    key: "disableAutomaticDiagnosticUpload",
    label: "Disable automatic diagnostic upload",
    description: "Keep records on this device unless the user exports them.",
  },
  {
    key: "delayIncidentExport",
    label: "Delay incident export",
    description: "Make review the default before sharing an incident record.",
  },
  {
    key: "hideAdvancedTechnicalDetails",
    label: "Hide advanced technical details",
    description: "Reduce potentially sensitive on-screen diagnostics.",
  },
  {
    key: "reduceDiagnosticFrequency",
    label: "Reduce diagnostic frequency",
    description: "Favor fewer local checks when uncertainty is acceptable.",
  },
  {
    key: "emergencyPause",
    label: "Emergency pause",
    description: "Stop sending new mock messages until resumed.",
  },
];

export function SafetyModePanel({ controls, onControlsChange }: SafetyModePanelProps) {
  function updateControl(key: SafetyToggleKey, value: boolean): void {
    onControlsChange({
      ...controls,
      [key]: value,
    });
  }

  return (
    <section className="panel-card" aria-labelledby="safety-mode-title">
      <div className="panel-title-row">
        <div>
          <h2 id="safety-mode-title">Safety Mode</h2>
          <p>Gorz prioritizes user safety. Diagnostics are minimized, local-first, and never automatically uploaded in this PoC.</p>
        </div>
        <ShieldCheck aria-hidden="true" size={22} />
      </div>

      <label className="toggle-row primary-toggle">
        <span>
          <strong>Safety mode enabled</strong>
          <small>Recommended for the prototype.</small>
        </span>
        <input
          checked={controls.safetyModeEnabled}
          onChange={(event) => updateControl("safetyModeEnabled", event.target.checked)}
          type="checkbox"
        />
      </label>

      <div className="toggle-list">
        {toggleRows.map((row) => (
          <label className="toggle-row" key={row.key}>
            <span>
              <strong>
                {row.key === "emergencyPause" ? <PauseCircle aria-hidden="true" size={15} /> : null}
                {row.label}
              </strong>
              <small>{row.description}</small>
            </span>
            <input
              checked={Boolean(controls[row.key])}
              onChange={(event) => updateControl(row.key, event.target.checked)}
              type="checkbox"
            />
          </label>
        ))}
      </div>
    </section>
  );
}
