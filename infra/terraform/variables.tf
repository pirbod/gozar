variable "environment" {
  type        = string
  description = "Controlled environment name."
  default     = "local"
}

variable "namespace_prefix" {
  type        = string
  description = "Prefix for local Kubernetes namespaces."
  default     = "gozar"
}

variable "storage_root" {
  type        = string
  description = "Local storage root for generated lab config."
  default     = "runtime/platform"
}

variable "profile_api_image" {
  type        = string
  description = "Profile API image reference for local manifests."
  default     = "gozar-profile-api:latest"
}

variable "gorz_api_image" {
  type        = string
  description = "Gorz API image reference for local manifests."
  default     = "gozar-gorz-api:latest"
}

variable "enable_public_entrypoints" {
  type        = bool
  description = "Must remain false for controlled release candidate defaults."
  default     = false

  validation {
    condition     = var.enable_public_entrypoints == false
    error_message = "Controlled release candidate defaults must not enable public entrypoints."
  }
}
