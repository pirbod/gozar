# Production Gap Analysis

This repository has alpha-readiness guardrails, but it is not production secure and not a public routing product.

| Gap | Current State | Required Before Production |
| --- | --- | --- |
| Android hardware-backed keystore gap | Demo settings and local keys can use SharedPreferences-backed abstractions. | Replace demo storage with Android Keystore-backed encrypted storage and migration tests. |
| Real cryptographic profile envelope gap | Profile envelopes demonstrate signing and Android local demo encryption. | Complete production crypto design, independent review, key rotation, and device-bound key handling. |
| Backend auth and tenant model gap | Local admin token and local demo users are sufficient for lab flows. | Add tenant model, user identity, scoped authorization, session controls, and audit accountability. |
| Admin token hardening gap | Static local demo token protects admin endpoints. | Replace with managed secrets, rotation, least privilege, and audit of admin actions. |
| CI/emulator gap | Unit checks and safety scanners exist; emulator smoke can be manual/nightly. | Establish stable Android emulator CI and make it a release blocker. |
| Privacy policy gap | Prototype privacy behavior is documented. | Produce reviewed privacy policy, data map, retention policy, and user-facing notices. |
| Release signing gap | Android debug builds are demo artifacts. | Configure release signing, key custody, reproducible build evidence, and artifact approval. |
| Observability gap | Local logs and audit exports exist. | Add production-grade metrics, alerting, redaction validation, and log retention controls. |
| Threat model validation gap | Threat models exist as internal docs. | Run independent review and update controls from findings. |
| Independent audit gap | No external audit has been completed. | Complete security, privacy, and abuse-prevention review before production claims. |
| Legal review gap | Repo is positioned for lawful controlled evaluation. | Complete jurisdiction-specific legal review and pilot agreements. |
| Abuse-prevention gap | Safety language and scanners reduce misuse risk. | Add abuse monitoring, reporting, eligibility, rate limits, and enforcement process. |
| Data retention policy gap | Local runtime data can be cleared manually. | Define retention schedules, deletion workflows, and audit retention requirements. |
| Evidence export misuse gap | Evidence export is redacted and user initiated, but sharing is operator controlled. | Add reviewer policy, approval workflow, and retention controls. |
| Screenshot leakage gap | Screenshots are manual or emulator artifacts and may show local state. | Add screenshot review, storage policy, and sharing approval. |
| Release artifact misuse gap | Debug artifacts can be generated for controlled review. | Add signing, artifact custody, provenance, and distribution controls. |
| Route guard regression gap | Phase 4 tests and scanners check known unsafe route scopes. | Add broader property tests and independent route review. |
| Platform operations gap | Terraform and Kubernetes are controlled demo assets. | Add cloud-specific architecture, secret management, policy-as-code, admission control, and reviewed runbooks. |
| Observability operations gap | Metrics, alerts, and dashboards are modeled assets. | Add real scrape endpoints, alert routing, retention, access control, and SLO ownership. |
| Detection operations gap | Local SIEM-style rules and deterministic summaries exist. | Integrate with reviewed SOC workflow and external SIEM only after privacy and security approval. |
