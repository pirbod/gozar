# Phase 4 Demo Video Script

Target length: 5 to 7 minutes.

## 1. Project Intro

Gozar/Gorz is a controlled local-first prototype release candidate for demonstrating Android UX, local profile lifecycle, platform engineering, observability, detection logic, and offline incident summaries.

## 2. Safety Boundary

State that the demo uses local lifecycle validation, local diagnostics, redacted evidence, and controlled platform assets. It is not a production VPN, not a public routing product, and not suitable for sensitive communication.

## 3. Four-Phase Roadmap

Show the roadmap closure: Phase 1 local profile lifecycle, Phase 2 Android VpnService prototype, Phase 3 clickable Android product experience, Phase 4 controlled release readiness.

## 4. Android App Home

Open the emulator and show the Home screen.

## 5. Offline Demo Connect Flow

Show offline mode and staged connect flow.

## 6. Confidence Screen

Show deterministic score, status, and explanations.

## 7. Route Policy Screen

Show applied local route `10.77.0.0/24` and blocked full-device route labels.

## 8. Evidence Package V2

Generate evidence, show redaction summary and checksum.

## 9. Safety Pause

Enable pause, show that new sessions are blocked, then resume.

## 10. Terraform And Kubernetes Overview

Show the Terraform directory, Kubernetes overlays, ClusterIP service shape, and NetworkPolicy.

## 11. Prometheus/Grafana View

Show Prometheus alerts or Grafana dashboard assets.

## 12. SIEM Detection Report

Show `runtime/reports/siem-detection-report.md`.

## 13. Deterministic Incident Summary

Show `runtime/reports/incident-summary.md`.

## 14. GitHub Actions

Show CI workflow files and explain artifact reports.

## 15. Production Readiness Report

Show production readiness report with `Production readiness report: READY` and `Production-ready for real use: NO`.

## 16. Final Positioning

Close with controlled prototype release candidate scope and remaining production gaps before any real production use.
