import { PauseCircle, PlayCircle } from "lucide-react";

import { AuditTrailPanel } from "../components/AuditTrailPanel";
import { PrototypeLimitationsPanel } from "../components/PrototypeLimitationsPanel";

interface SafetyPageProps {
  safety: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["safety"];
  audit: ReturnType<typeof import("../state/useGorzApi").useGorzApi>["audit"];
  onPause: () => void;
  onResume: () => void;
}

export function SafetyPage({ safety, audit, onPause, onResume }: SafetyPageProps) {
  return (
    <div className="page-grid">
      <section className="panel safety-actions" aria-labelledby="safety-actions-title">
        <div className="section-title">
          <h2 id="safety-actions-title">Safety Controls</h2>
        </div>
        <p>
          Emergency pause blocks new local demo sends while keeping identity, conversation, evidence, and audit views
          available.
        </p>
        <div className="button-row">
          <button
            className="secondary-button danger-button"
            disabled={Boolean(safety?.pause_enabled)}
            onClick={onPause}
            type="button"
          >
            <PauseCircle aria-hidden="true" size={17} />
            Enable pause
          </button>
          <button
            className="secondary-button"
            disabled={!safety?.pause_enabled}
            onClick={onResume}
            type="button"
          >
            <PlayCircle aria-hidden="true" size={17} />
            Resume demo sends
          </button>
        </div>
      </section>
      <PrototypeLimitationsPanel safety={safety} />
      <AuditTrailPanel events={audit} />
    </div>
  );
}

