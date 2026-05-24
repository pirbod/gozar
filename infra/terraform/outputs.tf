output "platform_summary" {
  description = "Safe local platform summary."
  value = {
    environment             = var.environment
    app_namespace           = module.gozar_local_lab.app_namespace
    observability_namespace = module.gozar_local_lab.observability_namespace
    security_ops_namespace  = module.gozar_local_lab.security_ops_namespace
    public_entrypoints      = false
    storage_root            = var.storage_root
  }
}
