# Terraform

The Terraform layer under `infra/terraform/` models a controlled local lab architecture. It prepares namespace names, deployment values, observability placeholders, security operations placeholders, storage paths, environment variables, and local secret placeholders.

## Module Structure

- `gozar-local-lab`: app namespace and internal deployment values.
- `observability`: Prometheus and Grafana placeholder configuration.
- `security-ops`: detection and incident-summary placeholder configuration.

## Commands

```bash
make terraform-fmt
make terraform-validate
make terraform-check
```

`terraform-validate` runs `terraform init -backend=false` and `terraform validate` when Terraform is installed.

## Provisioned Shape

The layer defines values for internal Kubernetes services, local storage paths, observability config, and security operations config. It does not create public networking resources by default.

## Intentionally Not Provisioned

No public ingress, no public gateway service, no public relay registry, no traffic forwarding resource, and no real secrets are provisioned.

## Production Gaps

Cloud account layout, IAM, secret management, remote state, policy-as-code, workload identity, and reviewed network design remain future production expansion work.

## Safety Boundaries

Defaults are local/dev only and keep `enable_public_entrypoints = false`.
