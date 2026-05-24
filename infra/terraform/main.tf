module "gozar_local_lab" {
  source = "./modules/gozar-local-lab"

  environment       = var.environment
  namespace_prefix  = var.namespace_prefix
  profile_api_image = var.profile_api_image
  gorz_api_image    = var.gorz_api_image
  storage_root      = var.storage_root
}

module "observability" {
  source = "./modules/observability"

  environment      = var.environment
  namespace        = module.gozar_local_lab.observability_namespace
  storage_root     = var.storage_root
  prometheus_rules = "observability/prometheus/rules"
  grafana_path     = "observability/grafana/dashboards"
}

module "security_ops" {
  source = "./modules/security-ops"

  environment          = var.environment
  namespace            = module.gozar_local_lab.security_ops_namespace
  detection_rules_path = "security/detection/rules"
  incident_summary_dir = "ai/incident-summary"
}
