# Local Development Matrix

| Area | Commands |
| --- | --- |
| Rust | `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` |
| TypeScript | `npm install`, `npm run typecheck:ts`, `npm run test:ts`, `npm run build:ts` |
| Python Profile API | `make profile-lint`, `make profile-test`, `make profile-validate` |
| Python Gorz API | `make gorz-lint`, `make gorz-test`, `make gorz-validate` |
| Android | `make android-check`, `make android-build`, `make android-test`, `make android-emulator-smoke` |
| Docker | `make gorz-demo`, `make profile-demo`, `make gorz-clean`, `make profile-clean` |
| Evaluation | `make eval-smoke`, `make eval`, `make eval-clean` |
| Production readiness | `make production-readiness-check`, `make safety-check`, `make docs-check`, `make local-health-report` |
