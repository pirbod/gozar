import { render, screen } from "@testing-library/react";

import { IncidentExportPanel } from "./IncidentExportPanel";

describe("IncidentExportPanel", () => {
  it("renders redacted incident records without plaintext", () => {
    render(
      <IncidentExportPanel
        incidents={[
          {
            incident_id: "inc_1",
            created_at: "2026-05-18T12:30:00Z",
            record: {
              classification: "not_delivered_or_no_proof",
              confidence: 0.2,
              redactions: ["Plaintext message body withheld."],
              evidence: { envelope_hash: "sha256:abc" },
            },
          },
        ]}
      />,
    );

    expect(screen.getByText("Plaintext message body withheld.")).toBeTruthy();
    expect(screen.queryByText("secret plaintext")).toBeNull();
    expect(screen.getByText("Download JSON")).toBeTruthy();
  });
});

