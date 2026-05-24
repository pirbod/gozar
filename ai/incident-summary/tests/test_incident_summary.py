import json
from pathlib import Path

from importlib.machinery import SourceFileLoader


module = SourceFileLoader(
    "incident_summary",
    "ai/incident-summary/incident_summary.py",
).load_module()


def test_deterministic_summary_redacted() -> None:
    event = json.loads(Path("ai/incident-summary/sample_input/route_policy_violation.json").read_text())
    summary = module.deterministic_summary(event, Path("sample.json"))
    assert "Route Policy Violation" in summary
    assert "raw_device_id" not in summary
    assert "private_key" not in summary
