locals {
  app_namespace           = "${var.namespace_prefix}-${var.environment}"
  observability_namespace = "${var.namespace_prefix}-${var.environment}-observability"
  security_ops_namespace  = "${var.namespace_prefix}-${var.environment}-security-ops"
  deployment_values = {
    profile_api_image = var.profile_api_image
    gorz_api_image    = var.gorz_api_image
    service_type      = "ClusterIP"
    public_ingress    = false
    storage_root      = var.storage_root
  }
}
