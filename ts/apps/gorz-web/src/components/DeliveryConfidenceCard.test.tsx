import { render, screen } from "@testing-library/react";

import { DeliveryConfidenceCard } from "./DeliveryConfidenceCard";

describe("DeliveryConfidenceCard", () => {
  it("displays the backend confidence state", () => {
    render(
      <DeliveryConfidenceCard
        diagnostic={{
          scenario: "blocked",
          label: "Blocked simulation",
          dns_score: 0.2,
          transport_score: 0.1,
          tls_or_quic_score: 0.1,
          app_delivery_score: 0.05,
          path_diversity_score: 0.1,
          source_independence_score: 0.4,
          risk_penalty: 0.05,
          confidence: 0.12,
          classification: "not_delivered_or_no_proof",
          mandatory_score: 0.1,
          support_score: 0.32,
          explanation: {
            top_positive_factors: ["encrypted envelope was created locally"],
            top_negative_factors: ["app-level receipt evidence"],
            human_summary: "The local prototype does not have enough evidence to prove delivery.",
            recommended_user_message: "No reliable proof of delivery in this simulation.",
          },
        }}
        message={null}
      />,
    );

    expect(screen.getByText("not delivered or no proof")).toBeTruthy();
    expect(screen.getByText("12%")).toBeTruthy();
  });
});

