import { Gauge } from "lucide-react";

import type { DiagnosticResponse, MessageResponse } from "../api/types";
import { formatPercent, formatStatus, statusTone } from "../utils/formatting";

interface DeliveryConfidenceCardProps {
  message: MessageResponse | null;
  diagnostic: DiagnosticResponse | null;
}

export function DeliveryConfidenceCard({ message, diagnostic }: DeliveryConfidenceCardProps) {
  const status = message?.delivery_status ?? diagnostic?.classification ?? "not_delivered_or_no_proof";
  const confidence = message?.confidence ?? diagnostic?.confidence ?? 0;
  const summary =
    message?.evidence.diagnostic?.explanation.human_summary ??
    diagnostic?.explanation.human_summary ??
    "Select a message or scenario to inspect confidence evidence.";

  return (
    <section className="panel confidence-panel" aria-labelledby="delivery-confidence-title">
      <div className="section-title">
        <h2 id="delivery-confidence-title">Delivery Confidence</h2>
        <Gauge aria-hidden="true" size={18} />
      </div>
      <div className="confidence-meter">
        <span>{formatPercent(confidence)}</span>
        <div className="meter-track" aria-hidden="true">
          <div style={{ width: formatPercent(confidence) }} />
        </div>
      </div>
      <span className={`pill ${statusTone(status)}`}>{formatStatus(status)}</span>
      <p>{summary}</p>
      <div className="score-grid">
        <div>
          <span>Mandatory</span>
          <strong>{formatPercent(diagnostic?.mandatory_score ?? message?.evidence.diagnostic?.mandatory_score)}</strong>
        </div>
        <div>
          <span>Support</span>
          <strong>{formatPercent(diagnostic?.support_score ?? message?.evidence.diagnostic?.support_score)}</strong>
        </div>
      </div>
    </section>
  );
}

