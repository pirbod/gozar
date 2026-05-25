# CI Evidence

GitHub Actions provide repeatable checks and artifact references for the controlled prototype release candidate. This page documents what each workflow is intended to prove; it does not claim a workflow passed unless `docs/ci/workflow-status.md` has been manually updated from a verified run.

| Workflow | Purpose | Trigger | Required | Artifacts | Expected failure behavior |
| --- | --- | --- | --- | --- | --- |
| `ci.yml` | Rust, TypeScript, e2e, and eval smoke coverage. | Push, pull request | Required for core repo health | Evaluation results | Fails on format, lint, test, build, e2e, or eval smoke errors. |
| `android.yml` | Android unit tests, debug APK build, and Android safety checks. | Push, pull request, manual | Required for Android review | Debug APK, Android build reports, runtime reports when generated | Fails on unit test, build, or safety check errors. |
| `android-emulator-smoke.yml` | Optional managed-device emulator smoke run. | Manual, nightly | Optional until emulator stability is verified | Emulator reports, APK, screenshot reports | Reports `SKIPPED` when GitHub runner emulator setup fails; CI fails when app smoke tests fail after emulator execution starts. |
| `production-readiness.yml` | Platform, screenshot, emulator report, release manifest, and production readiness reports. | Push, pull request, manual | Required for Phase 4 evidence | `runtime/reports` | Fails on critical safety or report generation errors. |
| `terraform.yml` | Terraform formatting and validation through the report script. | Push, pull request, manual | Required for platform evidence | Terraform check report | Fails when Terraform validation fails. |
| `kubernetes.yml` | Kubernetes overlay rendering and client-side validation. | Push, pull request, manual | Required for platform evidence | Rendered manifests and Kubernetes check report | Returns `PARTIAL` when no cluster is available after render succeeds. |
| `detection-and-ai.yml` | SIEM-style detection report and deterministic incident summary. | Push, pull request, manual | Required for detection evidence | Detection report and incident summary | Fails when expected sample detections do not match. |
| `release-candidate.yml` | Android release candidate package and manifest. | Manual | Optional release packaging | APK and `runtime/reports` | Fails on safety checks or APK build errors. |

## Artifact Policy

Reports are uploaded from `runtime/reports` where possible. APK artifacts are uploaded only from local debug build outputs and are not release signed. Screenshot reports distinguish real captures from placeholders.

## Status Tracking

Manual status notes live in `docs/ci/workflow-status.md`. Do not mark a workflow as passing unless its run has been verified in GitHub Actions.
