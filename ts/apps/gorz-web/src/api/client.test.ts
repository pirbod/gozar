import { isDeliveryClassification } from "./types";

describe("API type guards", () => {
  it("accepts known delivery classifications", () => {
    expect(isDeliveryClassification("delivered_confirmed")).toBe(true);
    expect(isDeliveryClassification("not_delivered_or_no_proof")).toBe(true);
    expect(isDeliveryClassification("sent")).toBe(false);
  });
});

