import { LockKeyhole, ShieldCheck } from "lucide-react";

import type { NetworkStatusChip } from "../types/connectivity";
import { formatPercent, formatStatusChip } from "../utils/format";

interface HeaderProps {
  statusChip: NetworkStatusChip;
  confidenceScore: number;
  classificationLabel: string;
  safetyModeEnabled: boolean;
}

export function Header({
  statusChip,
  confidenceScore,
  classificationLabel,
  safetyModeEnabled,
}: HeaderProps) {
  return (
    <header className="app-header">
      <div className="brand-lockup" aria-label="Gorz">
        <div className="brand-mark">
          <LockKeyhole aria-hidden="true" size={22} />
        </div>
        <div>
          <h1>Gorz</h1>
          <p>Private messaging with network confidence awareness</p>
        </div>
      </div>

      <div className="header-status" aria-label="Current network confidence">
        <span className={`status-chip status-${statusChip}`}>{formatStatusChip(statusChip)}</span>
        <span className="score-pill">{formatPercent(confidenceScore)}</span>
        <span className="desktop-header-copy">{classificationLabel}</span>
        {safetyModeEnabled ? (
          <span className="safety-pill">
            <ShieldCheck aria-hidden="true" size={14} />
            Safety mode
          </span>
        ) : null}
      </div>
    </header>
  );
}
