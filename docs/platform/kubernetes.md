# Kubernetes

The Kubernetes layer deploys a local controlled demo shape for the Profile API, Gorz API, observability configuration, SIEM-style detection rules, and deterministic incident summary job.

## Architecture

All services use `ClusterIP` by default. There is no public ingress and no `LoadBalancer` service. A NetworkPolicy limits traffic to namespace-local workloads and DNS.

## Namespaces

Base manifests use `gozar-controlled-demo`. Overlays append local or demo labels and suffixes.

## Deployments And Services

`profile-api` listens on port 8095 and `gorz-api` listens on 8090. Both include readiness probes, liveness probes, resource requests, limits, and non-privileged security context settings.

## Validation

```bash
make k8s-lint
make k8s-validate
make k8s-check
```

If `kubectl` is missing, checks write SKIPPED reports rather than claiming success.

## Production Gaps

Image provenance, secret management, service mesh policy, admission controls, runtime security, and cloud-specific networking are not complete.

## Safety Boundaries

No public ingress, no default `LoadBalancer`, no public routing services, no privileged containers, no `hostNetwork`, and no real secrets.
