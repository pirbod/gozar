import { Send } from "lucide-react";
import { FormEvent, useState } from "react";

import type { ScenarioId, ScenarioInfo } from "../api/types";

interface MessageComposerProps {
  disabled: boolean;
  disabledReason?: string;
  scenarios: ScenarioInfo[];
  selectedScenario: ScenarioId;
  onScenarioChange: (scenario: ScenarioId) => void;
  onSendMessage: (body: string) => void;
}

export function MessageComposer({
  disabled,
  disabledReason,
  scenarios,
  selectedScenario,
  onScenarioChange,
  onSendMessage,
}: MessageComposerProps) {
  const [body, setBody] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const trimmed = body.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSendMessage(trimmed);
    setBody("");
  }

  return (
    <form className="message-composer" onSubmit={handleSubmit}>
      <div className="composer-grid">
        <label>
          <span>Scenario</span>
          <select
            disabled={disabled}
            onChange={(event) => onScenarioChange(event.target.value as ScenarioId)}
            value={selectedScenario}
          >
            {scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.label}
              </option>
            ))}
          </select>
        </label>
        <label className="message-field">
          <span>Message</span>
          <textarea
            disabled={disabled}
            onChange={(event) => setBody(event.target.value)}
            placeholder={disabled ? disabledReason : "Write a local demo message"}
            rows={3}
            value={body}
          />
        </label>
      </div>
      <button className="primary-button" disabled={disabled || !body.trim()} type="submit">
        <Send aria-hidden="true" size={18} />
        Send
      </button>
    </form>
  );
}

