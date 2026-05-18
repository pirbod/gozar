import { fireEvent, render, screen } from "@testing-library/react";

import { SafetyPage } from "./SafetyPage";

describe("SafetyPage", () => {
  it("shows limitations and pause controls", () => {
    const onPause = vi.fn();
    const onResume = vi.fn();
    render(
      <SafetyPage
        audit={[]}
        onPause={onPause}
        onResume={onResume}
        safety={{
          safety_mode: "local-demo",
          pause_enabled: false,
          limitations: ["Local demo only.", "Not production secure."],
          updated_at: "2026-05-18T12:00:00Z",
        }}
      />,
    );

    expect(screen.getByText("Local demo only.")).toBeTruthy();
    fireEvent.click(screen.getByText("Enable pause"));
    expect(onPause).toHaveBeenCalledTimes(1);
  });
});

