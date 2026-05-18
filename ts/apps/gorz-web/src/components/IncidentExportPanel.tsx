import { Download } from "lucide-react";
import { useMemo, useState } from "react";

import { incidentDownloadUrl } from "../api/client";
import type { IncidentResponse } from "../api/types";
import { formatPercent, formatStatus, formatTimestamp, statusTone } from "../utils/formatting";

interface IncidentExportPanelProps {
  incidents: IncidentResponse[];
}

export function IncidentExportPanel({ incidents }: IncidentExportPanelProps) {
  const [selectedIncidentId, setSelectedIncidentId] = useState("");
  const selected = useMemo(
    () => incidents.find((incident) => incident.incident_id === selectedIncidentId) ?? incidents[0] ?? null,
    [incidents, selectedIncidentId],
  );
  const json = selected ? JSON.stringify(selected.record, null, 2) : "";

  return (
    <section className="panel incident-panel" aria-labelledby="incident-export-title">
      <div className="section-title">
        <h2 id="incident-export-title">Incident Evidence</h2>
      </div>
      {incidents.length === 0 ? (
        <p className="empty-state">Generate an incident from a message to preview redacted evidence.</p>
      ) : (
        <div className="incident-layout">
          <div className="list-stack">
            {incidents.map((incident) => (
              <button
                aria-current={incident.incident_id === selected?.incident_id ? "page" : undefined}
                className="list-row"
                key={incident.incident_id}
                onClick={() => setSelectedIncidentId(incident.incident_id)}
                type="button"
              >
                <strong>{incident.incident_id}</strong>
                <span>{formatStatus(String(incident.record.classification ?? "not_delivered_or_no_proof"))}</span>
                <small>{formatTimestamp(incident.created_at)}</small>
              </button>
            ))}
          </div>
          {selected ? (
            <div className="incident-preview">
              <div className="incident-summary">
                <span className={`pill ${statusTone(String(selected.record.classification ?? ""))}`}>
                  {formatStatus(String(selected.record.classification ?? ""))}
                </span>
                <strong>{formatPercent(Number(selected.record.confidence ?? 0))}</strong>
                <a className="secondary-button" href={incidentDownloadUrl(selected.incident_id)}>
                  <Download aria-hidden="true" size={16} />
                  Download JSON
                </a>
              </div>
              <div className="redaction-box">
                <h3>Redaction summary</h3>
                <ul>
                  {(selected.record.redactions ?? []).map((redaction) => (
                    <li key={redaction}>{redaction}</li>
                  ))}
                </ul>
              </div>
              <pre className="json-preview">{json}</pre>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

