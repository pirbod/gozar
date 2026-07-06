# Production Deployment Templates

This directory contains inert production-oriented templates for Gozar Core. They
are not wired into the current local demo, and they are not a production claim.

Use these files as starting points after the production design decisions are
made:

- `docker/Dockerfile.rust`: locked Rust service image for `desktop-client`,
  `relay`, `gateway`, or `echo-service`.
- `docker/Dockerfile.control-plane`: locked TypeScript control-plane image.
- `kubernetes/base`: example Kubernetes base for control-plane, relay, gateway,
  services, and namespace-local network policy.

Before deploying from these templates:

1. Replace images with digest-pinned, signed images from your registry.
2. Provide secrets through a managed secret store or external secret sync.
3. Replace demo HMAC secrets with the production identity and signing model.
4. Replace process-local replay protection with durable replay storage.
5. Replace local JSON state with production storage.
6. Add environment-specific ingress, service mesh, certificate, and policy
   controls.
7. Run manifest validation, image scanning, SBOM generation, and release
   approval.
