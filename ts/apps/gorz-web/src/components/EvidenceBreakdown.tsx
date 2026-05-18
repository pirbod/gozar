import { ListChecks } from "lucide-react";

import type { DiagnosticResponse, MessageResponse } from "../api/types";
import { formatPercent } from "../utils/formatting";

interface EvidenceBreakdownProps {
  message: MessageResponse | null;
  diagnostic: DiagnosticResponse | null;
}

export function EvidenceBreakdown({ message, diagnostic }: EvidenceBreakdownProps) {
  const activeDiagnostic = message?.evidence.diagnostic ?? diagnostic;
  const positives = activeDiagnostic?.explanation.top_positive_factors ?? [];
  const negatives = activeDiagnostic?.explanation.top_negative_factors ?? [];

  return (
    <section className="panel" aria-labelledby="evidence-breakdown-title">
      <div className="section-title">
        <h2 id="evidence-breakdown-title">Evidence</h2>
        <ListChecks aria-hidden="true" size={18} />
      </div>
      <div className="score-grid">
        <Score label="DNS or baseline" value={activeDiagnostic?.dns_score} />
        <Score label="Transport" value={activeDiagnostic?.transport_score} />
        <Score label="TLS or QUIC" value={activeDiagnostic?.tls_or_quic_score} />
        <Score label="App delivery" value={activeDiagnostic?.app_delivery_score} />
        <Score label="Path diversity" value={activeDiagnostic?.path_diversity_score} />
        <Score label="Source independence" value={activeDiagnostic?.source_independence_score} />
      </div>
      <div className="two-column-list">
        <div>
          <h3>Helpful evidence</h3>
          <ul>
            {positives.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Bottlenecks</h3>
          <ul>
            {negatives.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        </div>
      </div>
      {message ? (
        <p className="muted-copy">Envelope hash: {message.envelope_hash}</p>
      ) : (
        <p className="muted-copy">No message selected.</p>
      )}
    </section>
  );
}

function Score({ label, value }: { label: string; value: number | undefined }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{formatPercent(value)}</strong>
    </div>
  );
}

