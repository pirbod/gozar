import { Clipboard, Download, FileJson } from "lucide-react";
import { useMemo, useState } from "react";

import { serializeIncidentRecord } from "../connectivity/incidentRecord";
import type { IncidentRecord } from "../types/incident";
import { formatDeliveryState, formatPercent } from "../utils/format";

interface IncidentRecordPanelProps {
  record: IncidentRecord;
}

export function IncidentRecordPanel({ record }: IncidentRecordPanelProps) {
  const [copyState, setCopyState] = useState("Copy JSON");
  const json = useMemo(() => serializeIncidentRecord(record), [record]);

  function handleCopy(): void {
    void navigator.clipboard
      .writeText(json)
      .then(() => setCopyState("Copied"))
      .catch(() => setCopyState("Copy unavailable"));
  }

  function handleDownload(): void {
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `gorz-incident-${record.incidentId}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="panel-card" aria-labelledby="incident-record-title">
      <div className="panel-title-row">
        <div>
          <h2 id="incident-record-title">Incident Record</h2>
          <p>Redacted simulated evidence for review and export.</p>
        </div>
        <FileJson aria-hidden="true" size={22} />
      </div>

      <div className="incident-summary">
        <div>
          <span>Classification</span>
          <strong>{record.classification.replaceAll("_", " ")}</strong>
        </div>
        <div>
          <span>Confidence</span>
          <strong>{formatPercent(record.confidenceScore)}</strong>
        </div>
        <div>
          <span>Delivery</span>
          <strong>{formatDeliveryState(record.messageDeliveryState)}</strong>
        </div>
      </div>

      <div className="redaction-box">
        <h3>Redacted by default</h3>
        <ul>
          {record.redactions.map((redaction) => (
            <li key={redaction}>{redaction}</li>
          ))}
        </ul>
      </div>

      <p className="warning-copy">This is simulated PoC data. It must be reviewed before sharing.</p>

      <div className="button-row">
        <button className="secondary-action" onClick={handleCopy} type="button">
          <Clipboard aria-hidden="true" size={16} />
          <span>{copyState}</span>
        </button>
        <button className="secondary-action" onClick={handleDownload} type="button">
          <Download aria-hidden="true" size={16} />
          <span>Download JSON</span>
        </button>
      </div>

      <details className="json-details">
        <summary>JSON view</summary>
        <pre>{json}</pre>
      </details>
    </section>
  );
}
