# Gozar/Gorz Kubernetes Manifests

These manifests deploy the controlled local lab shape. Services default to `ClusterIP`, no public ingress is defined, and the NetworkPolicy limits app traffic to same-namespace workloads.

Use overlays:

```bash
kubectl kustomize deploy/kubernetes/overlays/local
kubectl apply --dry-run=client -k deploy/kubernetes/overlays/local
```
