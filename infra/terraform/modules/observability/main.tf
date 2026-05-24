locals {
  observability_config = {
    namespace        = var.namespace
    prometheus_rules = var.prometheus_rules
    grafana_path     = var.grafana_path
    storage_root     = "${var.storage_root}/observability"
    external_uploads = false
  }
}
