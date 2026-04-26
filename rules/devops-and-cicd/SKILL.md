---
name: devops-and-cicd
description: Establishes CI/CD pipelines, artifact management, environment promotion, infrastructure-as-code, rollout/rollback strategies, and secret management. Use when automating build/test/deploy or improving release reliability and speed.
license: Complete terms in LICENSE.txt
---

# DevOps and CI/CD

## Principles
- Build once, promote everywhere; immutable artifacts.
- Least privilege and secure-by-default pipelines.
- Observability for changes; fast rollback paths.

## Instructions

### Step 1: Pipeline design
- Stages: lint → type-check → unit → integration → build/package → scan → deploy.
- Parallelize and cache dependencies; deterministic builds.

### Step 2: Artifacts and versioning
- Produce SBOM; sign images/artifacts; store in registry.
- Semantic versions; provenance metadata; reproducible builds.

### Step 3: Environments and configuration
- Dev/stage/prod with environment parity.
- Config via env vars or provider secrets; never commit secrets.
- Feature flags for risky changes and experiments.

### Step 4: Deployment strategies
- Blue/green, rolling, or canary with health checks.
- Automated rollback on SLO/error regression; deploy timeouts.
- Database migrations: expand→migrate→contract pattern.

### Step 5: Infrastructure as Code
- Terraform/Pulumi modules; PR-reviewed changes; state protection.
- Drift detection and periodic reconciliation.

### Step 6: Security in CI
- SAST, SCA, DAST gates; container/image scanning; policy as code.
- Short-lived credentials via OIDC; minimal runner permissions.
- Secrets scanning on push and in PRs.

### Step 7: Observability and change management
- Deployment markers in tracing/logging; release dashboards.
- Change feed with author, artifact, commit, ticket.
- Post-deploy verification checklist.

### Step 8: Disaster recovery and resilience
- Backups with retention; periodic restore drills.
- RTO/RPO documented; simulate region/service failures.

## Checklists
- Pipeline is deterministic, parallel, and cached.
- Artifacts signed; SBOM generated; stored in registry.
- Secrets managed outside VCS; least privilege enforced.
- Canary + auto-rollback configured; DB migrations safe.
- IaC changes PR-reviewed; drift checks scheduled.

## Patterns
- GitOps (ArgoCD/Flux) for declarative deploys.
- Preview environments per PR.
- ChatOps for safe, audited deploy triggers.

## Troubleshooting
- Flaky pipeline: isolate stages, add retries only for infra flake, improve caching.
- Cache poisoning: scope and key caches precisely; verify checksums.
- Failed rollback: ensure immutable artifacts and database back-compat.
