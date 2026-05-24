from pathlib import Path

from scripts.security.run_detection_tests import load_rules


def test_rules_load() -> None:
    rules = load_rules(Path("security/detection/rules"))
    assert len(rules) >= 8
    assert all(rule["id"] for rule in rules)
