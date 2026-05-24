# Risk Register

| Risk ID | Description | Impact | Likelihood | Control | Residual Risk | Owner | Review Cadence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Misinterpreted as real VPN product. | High | Medium | README, UI labels, demo positioning. | Medium | TBD | Every release |
| RISK-002 | Demo crypto mistaken for production crypto. | High | Medium | Gap analysis, hardening docs, `PRODUCTION_GAP` comments. | Medium | TBD | Every release |
| RISK-003 | Unsafe routing accidentally introduced. | High | Low | Android route checker and CI gate. | Low | TBD | Every PR |
| RISK-004 | Public probing accidentally introduced. | High | Low | Safety wording and backend safety scanners. | Low | TBD | Every PR |
| RISK-005 | Sensitive diagnostics collection. | High | Medium | Privacy docs, local diagnostics model, evidence redaction. | Medium | TBD | Monthly |
| RISK-006 | Weak admin token handling. | Medium | High | Admin endpoint tests and documented hardening gap. | High | TBD | Every milestone |
| RISK-007 | Android permission creep. | High | Low | Manifest permission checker. | Low | TBD | Every PR |
| RISK-008 | CI does not cover Android emulator. | Medium | Medium | Managed-device config, smoke docs, manual/nightly workflow. | Medium | TBD | Every milestone |
| RISK-009 | Overclaiming research results. | High | Medium | Demo positioning and docs review. | Medium | TBD | Every release |
| RISK-010 | Supply-chain dependency risk. | High | Medium | Dependency audit workflow and release checklist. | Medium | TBD | Every release |
| RISK-011 | Android storage downgrade risk. | High | Medium | Demo warning, storage mode UI, Keystore gap documentation. | Medium | TBD | Every release |
| RISK-012 | Evidence export misuse risk. | Medium | Medium | User-initiated export, redaction tests, evidence docs. | Medium | TBD | Every release |
| RISK-013 | Screenshot leakage risk. | Medium | Medium | Screenshot guide and validation report warnings. | Medium | TBD | Every release |
| RISK-014 | Emulator-only validation risk. | Medium | Medium | Manual checklist, skipped reports, CI artifacts. | Medium | TBD | Every milestone |
| RISK-015 | Demo interpreted as production risk. | High | Medium | README, UI labels, release notes, final validation report. | Medium | TBD | Every release |
| RISK-016 | Route guard regression risk. | High | Low | RoutePolicyGuard tests and Android route checker. | Low | TBD | Every PR |
| RISK-017 | Admin token leakage risk. | High | Medium | Redaction tests and admin token hardening gap. | Medium | TBD | Every release |
| RISK-018 | Release artifact misuse risk. | Medium | Medium | RC manifest, release notes, no signing unless configured. | Medium | TBD | Every release |
| RISK-019 | Platform manifests interpreted as production deployment. | High | Medium | README, platform docs, ClusterIP defaults, Terraform local defaults. | Medium | TBD | Every release |
| RISK-020 | Detection summaries treated as completed security review. | Medium | Medium | Docs state summaries are reviewer aids only. | Medium | TBD | Every release |
