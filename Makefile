PYTHON ?= python3
EVAL_RUNNER := eval/scripts/eval_runner.py
GORZ_COMPOSE := docker compose -f docker-compose.gorz.yml
PROFILE_COMPOSE := docker compose -f docker-compose.profile.yml
ANDROID_DIR := android/gorz

.PHONY: eval eval-clean eval-baseline eval-adaptive eval-smoke eval-scenario gorz-install gorz-dev gorz-demo gorz-test gorz-lint gorz-validate gorz-clean gorz-cli-test gorz-homebrew-check gorz-release-check profile-install profile-dev profile-demo profile-test profile-lint profile-validate profile-clean profile-audit-export profile-safety-check safety-wording-check profile-syntax-check profile-compose-check profile-release-check profile-full-check android-check android-test android-build android-clean android-safety-check android-emulator-smoke android-emulator-smoke-report backend-safety-check docs-check safety-check production-readiness-check local-health-report phase2-check phase3-check phase4-docs-check phase4-safety-check phase4-screenshots phase4-screenshot-report release-candidate-manifest terraform-fmt terraform-validate terraform-check k8s-lint k8s-validate k8s-check observability-check detection-check incident-summary-demo platform-screenshots demo-video-assets platform-check phase4-check

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
	$(PYTHON) scripts/check_android_manifest_permissions.py
	$(PYTHON) scripts/check_android_route_safety.py

android-emulator-smoke:
	cd $(ANDROID_DIR) && ./gradlew pixel2api30DebugAndroidTest

android-emulator-smoke-report:
	$(PYTHON) scripts/android/run_emulator_smoke_report.py

terraform-fmt:
	@if command -v terraform >/dev/null 2>&1; then cd infra/terraform && terraform fmt -recursive; else $(PYTHON) scripts/platform/run_terraform_check.py; fi

terraform-validate:
	$(PYTHON) scripts/platform/run_terraform_check.py

terraform-check:
	$(MAKE) terraform-fmt
	$(MAKE) terraform-validate

k8s-lint:
	$(PYTHON) scripts/platform/run_k8s_check.py

k8s-validate:
	$(PYTHON) scripts/platform/run_k8s_check.py

k8s-check:
	$(PYTHON) scripts/platform/run_k8s_check.py

observability-check:
	$(PYTHON) scripts/platform/check_observability_assets.py

detection-check:
	$(PYTHON) scripts/security/run_detection_tests.py

incident-summary-demo:
	$(PYTHON) ai/incident-summary/incident_summary.py --input security/detection/sample-events/route_policy_violation.json --output runtime/reports/incident-summary.md --mode deterministic

platform-screenshots:
	$(PYTHON) scripts/platform/capture_platform_screenshots.py

demo-video-assets:
	@echo "See docs/demo/demo-video-script.md and docs/demo/demo-video-shot-list.md"

platform-check:
	$(MAKE) terraform-check
	$(MAKE) k8s-check
	$(MAKE) observability-check
	$(MAKE) detection-check
	$(MAKE) incident-summary-demo
	$(MAKE) platform-screenshots

backend-safety-check:
	$(PYTHON) scripts/check_backend_safety.py

docs-check:
	@test -f docs/product/one-page-overview.md || (echo "docs/product/one-page-overview.md is missing" >&2; exit 1)
	@test -f docs/product/system-map.md || (echo "docs/product/system-map.md is missing" >&2; exit 1)
	@test -f docs/product/production-gap-analysis.md || (echo "docs/product/production-gap-analysis.md is missing" >&2; exit 1)
	@test -f docs/product/release-blocker-checklist.md || (echo "docs/product/release-blocker-checklist.md is missing" >&2; exit 1)
	@test -f docs/product/risk-register.md || (echo "docs/product/risk-register.md is missing" >&2; exit 1)
	@test -f SECURITY.md || (echo "SECURITY.md is missing" >&2; exit 1)
	@test -f PRIVACY.md || (echo "PRIVACY.md is missing" >&2; exit 1)

safety-check:
	$(MAKE) safety-wording-check
	$(MAKE) android-safety-check
	$(MAKE) backend-safety-check
	@if test -f scripts/check_phase3_safety.py; then $(PYTHON) scripts/check_phase3_safety.py; fi

production-readiness-check:
	$(PYTHON) scripts/production_readiness_check.py

local-health-report:
	$(PYTHON) scripts/local_health_report.py

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

phase4-docs-check:
	@test -f docs/product/four-phase-roadmap.md || (echo "docs/product/four-phase-roadmap.md is missing" >&2; exit 1)
	@test -f docs/vpn-product/confidence-model.md || (echo "docs/vpn-product/confidence-model.md is missing" >&2; exit 1)
	@test -f docs/vpn-product/evidence-package-v2.md || (echo "docs/vpn-product/evidence-package-v2.md is missing" >&2; exit 1)
	@test -f docs/vpn-product/local-diagnostics.md || (echo "docs/vpn-product/local-diagnostics.md is missing" >&2; exit 1)
	@test -f docs/vpn-product/phase-4-screenshot-guide.md || (echo "docs/vpn-product/phase-4-screenshot-guide.md is missing" >&2; exit 1)
	@test -f docs/security/android-phase-4-threat-model.md || (echo "docs/security/android-phase-4-threat-model.md is missing" >&2; exit 1)
	@test -f docs/privacy/android-phase-4-privacy-review.md || (echo "docs/privacy/android-phase-4-privacy-review.md is missing" >&2; exit 1)
	@test -f docs/backend/android-phase-4-backend-contract.md || (echo "docs/backend/android-phase-4-backend-contract.md is missing" >&2; exit 1)
	@test -f docs/release/phase-4-controlled-release-process.md || (echo "docs/release/phase-4-controlled-release-process.md is missing" >&2; exit 1)
	@test -f docs/release/phase-4-release-notes.md || (echo "docs/release/phase-4-release-notes.md is missing" >&2; exit 1)
	@test -f docs/vpn-product/phase-4-final-validation-report.md || (echo "docs/vpn-product/phase-4-final-validation-report.md is missing" >&2; exit 1)

phase4-safety-check:
	$(MAKE) safety-check
	$(PYTHON) scripts/check_android_manifest_permissions.py
	$(PYTHON) scripts/check_android_route_safety.py

phase4-screenshots:
	$(PYTHON) scripts/android/capture_phase4_screenshots.py

phase4-screenshot-report:
	$(PYTHON) scripts/android/capture_phase4_screenshots.py --report-only
	$(PYTHON) scripts/platform/capture_platform_screenshots.py

release-candidate-manifest:
	$(PYTHON) scripts/android/generate_release_candidate_manifest.py

phase4-check:
	$(MAKE) docs-check
	$(MAKE) phase4-docs-check
	$(MAKE) android-safety-check
	$(MAKE) backend-safety-check
	$(MAKE) phase3-check
	@if command -v gradle >/dev/null 2>&1 && (cd $(ANDROID_DIR) && ./gradlew -v >/dev/null 2>&1); then \
		$(MAKE) android-test; \
		$(MAKE) android-build; \
	else \
		echo "Warning: Gradle or Android SDK not available; skipped Android unit tests and build." >&2; \
	fi
	$(MAKE) platform-check
	$(MAKE) production-readiness-check
	$(MAKE) android-emulator-smoke-report
	$(MAKE) phase4-screenshot-report
	$(MAKE) release-candidate-manifest

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
