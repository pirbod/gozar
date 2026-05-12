PYTHON ?= python3
EVAL_RUNNER := eval/scripts/eval_runner.py

.PHONY: eval eval-clean eval-baseline eval-adaptive eval-smoke eval-scenario

eval:
	$(PYTHON) $(EVAL_RUNNER) run-all

eval-clean:
	$(PYTHON) $(EVAL_RUNNER) clean

eval-baseline:
	$(PYTHON) $(EVAL_RUNNER) run-baseline

eval-adaptive:
	$(PYTHON) $(EVAL_RUNNER) run-adaptive

eval-smoke:
	$(PYTHON) $(EVAL_RUNNER) smoke

# Run one scenario by passing SCENARIO=eval/scenarios/name.yaml.
eval-scenario:
	@test -n "$(SCENARIO)" || (echo "Set SCENARIO=eval/scenarios/<name>.yaml" >&2; exit 2)
	$(PYTHON) $(EVAL_RUNNER) run-scenario "$(SCENARIO)"
