import { AlertTriangle, ShieldCheck } from "lucide-react";

import type { HealthResponse, SafetyResponse } from "../api/types";

interface SafetyBannerProps {
  health: HealthResponse | null;
  safety: SafetyResponse | null;
  error: string | null;
}

export function SafetyBanner({ health, safety, error }: SafetyBannerProps) {
  return (
    <header className="top-bar">
      <div className="brand">
        <div className="brand-mark">G</div>
        <div>
          <h1>Gorz</h1>
          <p>Local-first confidence-aware messaging prototype</p>
        </div>
      </div>
      <div className="banner-status">
        <span className="pill good">
          <ShieldCheck aria-hidden="true" size={15} />
          {health?.status === "ok" ? "API online" : "API pending"}
        </span>
        <span className={`pill ${safety?.pause_enabled ? "bad" : "good"}`}>
          {safety?.pause_enabled ? "Emergency pause" : "Safety mode"}
        </span>
        {error ? (
          <span className="pill bad">
            <AlertTriangle aria-hidden="true" size={15} />
            {error}
          </span>
        ) : null}
      </div>
    </header>
  );
}

