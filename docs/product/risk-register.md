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
