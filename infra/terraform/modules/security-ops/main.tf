locals {
  security_ops_config = {
    namespace            = var.namespace
    detection_rules_path = var.detection_rules_path
    incident_summary_dir = var.incident_summary_dir
    external_siem        = false
    external_llm_api     = false
  }
}
