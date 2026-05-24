# Gozar/Gorz Terraform

This Terraform layer models a production-shaped controlled local lab. It prepares names, Kubernetes values, observability placeholders, security operations placeholders, storage paths, environment variables, and local secret placeholders.

Default mode is local/dev only. It does not create public routing resources, public gateway services, relay registries, or traffic forwarding resources.

## Commands

```bash
terraform fmt -recursive
terraform init -backend=false
terraform validate
```

Use `example.tfvars` as a safe placeholder input file.
