import { UserPlus } from "lucide-react";
import { FormEvent, useState } from "react";

import type { IdentityResponse } from "../api/types";

interface IdentityPanelProps {
  identities: IdentityResponse[];
  activeIdentityId: string;
  onSelectIdentity: (identityId: string) => void;
  onCreateIdentity: (displayName: string, deviceLabel: string) => void;
}

export function IdentityPanel({
  identities,
  activeIdentityId,
  onSelectIdentity,
  onCreateIdentity,
}: IdentityPanelProps) {
  const [displayName, setDisplayName] = useState("");
  const [deviceLabel, setDeviceLabel] = useState("Local device");

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const trimmed = displayName.trim();
    if (!trimmed) {
      return;
    }
    onCreateIdentity(trimmed, deviceLabel.trim() || "Local device");
    setDisplayName("");
  }

  return (
    <section className="panel compact-panel" aria-labelledby="identity-panel-title">
      <div className="section-title">
        <h2 id="identity-panel-title">Demo Identity</h2>
        <UserPlus aria-hidden="true" size={18} />
      </div>
      <form className="stacked-form" onSubmit={handleSubmit}>
        <label htmlFor="display-name">Display name</label>
        <input
          id="display-name"
          onChange={(event) => setDisplayName(event.target.value)}
          placeholder="Ari Local"
          value={displayName}
        />
        <label htmlFor="device-label">Device label</label>
        <input
          id="device-label"
          onChange={(event) => setDeviceLabel(event.target.value)}
          value={deviceLabel}
        />
        <button className="secondary-button" type="submit">
          Create identity
        </button>
      </form>

      <div className="list-stack">
        {identities.length === 0 ? (
          <p className="empty-state">No identities yet.</p>
        ) : (
          identities.map((identity) => (
            <button
              aria-current={identity.identity_id === activeIdentityId ? "page" : undefined}
              className="list-row"
              key={identity.identity_id}
              onClick={() => onSelectIdentity(identity.identity_id)}
              type="button"
            >
              <strong>{identity.display_name}</strong>
              <span>{identity.device_label ?? "Local device"}</span>
              <small>Demo key only</small>
            </button>
          ))
        )}
      </div>
    </section>
  );
}

