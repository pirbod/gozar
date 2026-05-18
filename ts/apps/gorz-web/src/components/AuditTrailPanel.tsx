import type { AuditResponse } from "../api/types";
import { formatTimestamp } from "../utils/formatting";

interface AuditTrailPanelProps {
  events: AuditResponse[];
}

export function AuditTrailPanel({ events }: AuditTrailPanelProps) {
  return (
    <section className="panel" aria-labelledby="audit-title">
      <div className="section-title">
        <h2 id="audit-title">Audit Trail</h2>
      </div>
      <div className="audit-list">
        {events.length === 0 ? (
          <p className="empty-state">No audit events yet.</p>
        ) : (
          events.map((event) => (
            <article key={event.event_id}>
              <strong>{event.event_type}</strong>
              <span>{event.summary}</span>
              <small>{formatTimestamp(event.created_at)}</small>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

