import type { SafetyResponse } from "../api/types";

interface PrototypeLimitationsPanelProps {
  safety: SafetyResponse | null;
}

export function PrototypeLimitationsPanel({ safety }: PrototypeLimitationsPanelProps) {
  const limitations =
    safety?.limitations ?? [
      "Local demo only.",
      "Simulated diagnostics only.",
      "Not production secure.",
      "Not for real sensitive communication.",
    ];

  return (
    <section className="panel" aria-labelledby="limitations-title">
      <div className="section-title">
        <h2 id="limitations-title">Prototype Boundaries</h2>
      </div>
      <div className="boundary-grid">
        <article>
          <h3>What Gorz is</h3>
          <p>A local demo for confidence-aware message delivery and redacted incident evidence.</p>
        </article>
        <article>
          <h3>What Gorz is not</h3>
          <p>Not production secure, not a bypass product, and not for real sensitive communication.</p>
        </article>
      </div>
      <ul className="limitations-list">
        {limitations.map((limitation) => (
          <li key={limitation}>{limitation}</li>
        ))}
      </ul>
    </section>
  );
}

