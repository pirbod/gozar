PYTHON ?= python3
EVAL_RUNNER := eval/scripts/eval_runner.py
GORZ_COMPOSE := docker compose -f docker-compose.gorz.yml

.PHONY: eval eval-clean eval-baseline eval-adaptive eval-smoke eval-scenario gorz-install gorz-dev gorz-demo gorz-test gorz-lint gorz-validate gorz-clean

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

gorz-install:
	@if $(PYTHON) -m pip --version >/dev/null 2>&1; then \
		$(PYTHON) -m pip install -e "python/gorz_api[dev]"; \
	else \
		echo "Host Python pip is unavailable; Docker demo images will install backend dependencies."; \
	fi
	npm install

gorz-dev:
	@echo "Gorz Web: http://localhost:5174"
	@echo "Gorz API: http://localhost:8090/api/gorz/health"
	@echo "API Docs: http://localhost:8090/docs"
	$(GORZ_COMPOSE) up --build

gorz-demo:
	@echo "Gorz Web: http://localhost:5174"
	@echo "Gorz API: http://localhost:8090/api/gorz/health"
	@echo "API Docs: http://localhost:8090/docs"
	$(GORZ_COMPOSE) up --build

gorz-test:
	@if $(PYTHON) -m pytest --version >/dev/null 2>&1; then \
		cd python/gorz_api && $(PYTHON) -m pytest; \
	else \
		$(GORZ_COMPOSE) build gorz-api; \
		docker run --rm gozar-gorz-api sh -lc 'python -m pip install -e "/workspace/python/gorz_api[dev]" >/tmp/gorz-pip.log && cd /workspace/python/gorz_api && pytest'; \
	fi
	npm run test --workspace gorz-web

gorz-lint:
	@if $(PYTHON) -m ruff --version >/dev/null 2>&1; then \
		cd python/gorz_api && $(PYTHON) -m ruff check .; \
	else \
		$(GORZ_COMPOSE) build gorz-api; \
		docker run --rm gozar-gorz-api sh -lc 'python -m pip install -e "/workspace/python/gorz_api[dev]" >/tmp/gorz-pip.log && cd /workspace/python/gorz_api && ruff check .'; \
	fi
	npm run typecheck --workspace gorz-web

gorz-validate:
	@if $(PYTHON) -c "import httpx" >/dev/null 2>&1; then \
		$(PYTHON) scripts/gorz/validate_gorz.py; \
	else \
		docker run --rm --network gozar_default -v "$(CURDIR)/scripts/gorz:/scripts/gorz:ro" gozar-gorz-api python /scripts/gorz/validate_gorz.py --api http://gorz-api:8090; \
	fi

gorz-clean:
	$(GORZ_COMPOSE) down -v
	rm -rf runtime/gorz
