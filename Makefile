PYTHON ?= python3
EVAL_RUNNER := eval/scripts/eval_runner.py
GORZ_COMPOSE := docker compose -f docker-compose.gorz.yml
PROFILE_COMPOSE := docker compose -f docker-compose.profile.yml
ANDROID_DIR := android/gorz

.PHONY: eval eval-clean eval-baseline eval-adaptive eval-smoke eval-scenario gorz-install gorz-dev gorz-demo gorz-test gorz-lint gorz-validate gorz-clean gorz-cli-test gorz-homebrew-check gorz-release-check profile-install profile-dev profile-demo profile-test profile-lint profile-validate profile-clean profile-audit-export profile-safety-check safety-wording-check profile-syntax-check profile-compose-check profile-release-check profile-full-check android-check android-test android-build android-clean android-safety-check phase2-check phase3-check

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

gorz-cli-test:
	tests/gorz_cli_test.sh

gorz-homebrew-check:
	@test -x bin/gorz || (echo "bin/gorz must exist and be executable" >&2; exit 1)
	@test -f packaging/homebrew/Formula/gorz.rb || (echo "packaging/homebrew/Formula/gorz.rb is missing" >&2; exit 1)
	@if command -v ruby >/dev/null 2>&1; then ruby -c packaging/homebrew/Formula/gorz.rb >/dev/null; fi
	@output="$$(bin/gorz help; bin/gorz version; bin/gorz path)"; \
	if printf '%s\n' "$$output" | grep -Eiq 'relay discovery|discover relays|public network scan|external network scan|scrape endpoints|scanner|production secure messenger'; then \
		echo "Unsafe operational wording found in CLI output" >&2; \
		exit 1; \
	fi

gorz-release-check:
	@test -x bin/gorz || (echo "bin/gorz must exist and be executable" >&2; exit 1)
	@test -f docker-compose.gorz.yml || (echo "docker-compose.gorz.yml is missing" >&2; exit 1)
	@test -f Dockerfile.gorz-api || (echo "Dockerfile.gorz-api is missing" >&2; exit 1)
	@test -f Dockerfile.gorz-web || (echo "Dockerfile.gorz-web is missing" >&2; exit 1)
	@test -f python/gorz_api/pyproject.toml || (echo "python/gorz_api/pyproject.toml is missing" >&2; exit 1)
	@test -f scripts/gorz/validate_gorz.py || (echo "scripts/gorz/validate_gorz.py is missing" >&2; exit 1)
	@test -f scripts/gorz/prepare_homebrew_release.py || (echo "scripts/gorz/prepare_homebrew_release.py is missing" >&2; exit 1)
	@grep -q "brew install pirbod/tap/gorz" README.md || (echo "README.md is missing Homebrew install instructions" >&2; exit 1)
	@test -f docs/gorz/homebrew-install.md || (echo "docs/gorz/homebrew-install.md is missing" >&2; exit 1)

profile-install:
	$(PYTHON) -m pip install -e "python/profile_api[dev]"

profile-dev:
	uvicorn profile_api.main:app --reload --host 0.0.0.0 --port 8095

profile-demo:
	$(PROFILE_COMPOSE) up --build

profile-test:
	@if $(PYTHON) -m pytest --version >/dev/null 2>&1; then \
		cd python/profile_api && $(PYTHON) -m pytest; \
	else \
		$(PROFILE_COMPOSE) build profile-api; \
		docker run --rm -v "$(CURDIR)/python/profile_api:/workspace/python/profile_api" gozar-profile-api sh -lc 'python -m pip install -e "/workspace/python/profile_api[dev]" >/tmp/profile-pip.log && cd /workspace/python/profile_api && pytest'; \
	fi

profile-lint:
	@if $(PYTHON) -m ruff --version >/dev/null 2>&1; then \
		cd python/profile_api && $(PYTHON) -m ruff check .; \
	else \
		$(PROFILE_COMPOSE) build profile-api; \
		docker run --rm -v "$(CURDIR)/python/profile_api:/workspace/python/profile_api" gozar-profile-api sh -lc 'python -m pip install -e "/workspace/python/profile_api[dev]" >/tmp/profile-pip.log && cd /workspace/python/profile_api && ruff check .'; \
	fi

profile-syntax-check:
	python3 -m py_compile python/profile_api/profile_api/*.py
	python3 -m py_compile scripts/profile/*.py
	python3 -m py_compile python/profile_api/tests/*.py

profile-validate:
	@if $(PYTHON) -c "import httpx" >/dev/null 2>&1; then \
		$(PYTHON) scripts/profile/validate_profile_lifecycle.py; \
	else \
		docker run --rm --network gozar_default -v "$(CURDIR):/workspace" -w /workspace gozar-profile-api python scripts/profile/validate_profile_lifecycle.py --api http://profile-api:8095; \
	fi

profile-audit-export:
	$(PYTHON) scripts/profile/export_demo_profile_audit.py

profile-safety-check:
	$(PYTHON) scripts/profile/check_safety_wording.py

safety-wording-check:
	$(PYTHON) scripts/check_safety_wording.py

profile-compose-check:
	$(PROFILE_COMPOSE) config

profile-full-check:
	$(MAKE) profile-lint
	$(MAKE) profile-test
	$(PROFILE_COMPOSE) config
	$(PROFILE_COMPOSE) up -d --build
	@if $(PYTHON) -c "import httpx" >/dev/null 2>&1; then \
		$(PYTHON) scripts/profile/validate_profile_lifecycle.py --api http://127.0.0.1:8095; \
	else \
		docker run --rm --network gozar_default -v "$(CURDIR):/workspace" -w /workspace gozar-profile-api python scripts/profile/validate_profile_lifecycle.py --api http://profile-api:8095; \
	fi
	$(PROFILE_COMPOSE) down -v
	$(MAKE) safety-wording-check

android-check:
	bash scripts/android/validate_android_project.sh

android-test:
	cd $(ANDROID_DIR) && ./gradlew test

android-build:
	cd $(ANDROID_DIR) && ./gradlew assembleDebug

android-clean:
	cd $(ANDROID_DIR) && ./gradlew clean

android-safety-check:
	$(PYTHON) scripts/android/check_android_safety_wording.py

phase2-check:
	$(MAKE) profile-full-check
	$(MAKE) android-check
	$(MAKE) android-safety-check

phase3-check:
	@if command -v gradle >/dev/null 2>&1 && (cd $(ANDROID_DIR) && ./gradlew -v >/dev/null 2>&1); then \
		cd $(ANDROID_DIR) && ./gradlew test; \
	else \
		echo "Warning: Gradle or Android SDK not available; skipped Android Gradle unit tests." >&2; \
	fi
	$(MAKE) android-check
	$(MAKE) phase2-check
	$(PYTHON) scripts/check_phase3_safety.py

profile-release-check:
	@test -f Dockerfile.profile-api || (echo "Dockerfile.profile-api is missing" >&2; exit 1)
	@test -f docker-compose.profile.yml || (echo "docker-compose.profile.yml is missing" >&2; exit 1)
	@test -f python/profile_api/pyproject.toml || (echo "python/profile_api/pyproject.toml is missing" >&2; exit 1)
	@test -f python/profile_api/profile_api/main.py || (echo "profile API app is missing" >&2; exit 1)
	@test -f scripts/profile/validate_profile_lifecycle.py || (echo "profile validator is missing" >&2; exit 1)
	@test -f scripts/profile/run_profile_lifecycle_demo.py || (echo "profile lifecycle demo is missing" >&2; exit 1)
	@test -f scripts/profile/export_demo_profile_audit.py || (echo "profile audit exporter is missing" >&2; exit 1)
	@test -f docs/vpn-product/phase-1-local-profile-lifecycle.md || (echo "Phase 1 docs are missing" >&2; exit 1)
	$(MAKE) profile-syntax-check
	$(MAKE) profile-safety-check
	$(MAKE) profile-test
	$(MAKE) profile-compose-check

profile-clean:
	$(PROFILE_COMPOSE) down -v
	rm -rf runtime/profile
