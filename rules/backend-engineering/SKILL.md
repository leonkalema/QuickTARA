---
name: backend-engineering
description: Designs and implements backend services and APIs (REST/GraphQL) with secure, testable, and maintainable patterns. Use when the user asks to build or review endpoints, services, data access layers, background jobs, or to refactor backend code. Produces contracts, layered architecture, error taxonomy, pagination/rate limits, authn/z, caching, observability, and rollout plans.
license: Complete terms in LICENSE.txt
---

# Backend Engineering

## Intent
Ship backend features end-to-end with strong correctness, reliability, and developer experience.

## Principles
- Keep functions small and single-purpose with early returns.
- Strong typing and DTOs at boundaries; prefer immutability.
- Layered architecture: handlers → services → repositories → integrations.
- Fail fast with explicit errors; avoid silent fallbacks.
- Prefer Postgres + ACID; use queues for async/long-running work.

## Instructions

### Step 1: Clarify scope and constraints
- Inputs: business goal, SLAs/SLOs, data sensitivity (PII), traffic estimates, latency/throughput targets.
- Outputs: API surface (resources, verbs), acceptance criteria, non-functional requirements.

### Step 2: Design the API contract
- Prefer REST; use GraphQL for client-driven aggregation or complex querying.
- Define resource names, IDs, and URL shapes.
- Status codes and error schema (`application/problem+json`).
- Idempotency: require `Idempotency-Key` for unsafe POST/PUT.
- Pagination: prefer cursor-based with opaque cursors; set `MAX_LIMIT` constant.
- Versioning: additive changes; deprecations with `Sunset` header; document timelines.

Example error body:
```json
{
  "type": "https://errors.example.com/resource-not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "User 123 does not exist",
  "instance": "/v1/users/123",
  "code": "USR_404"
}
```

### Step 3: Model domain and data
- Identify entities, invariants, and boundaries.
- Choose storage (default Postgres). Design schema with PKs, FKs, uniques, CHECKs.
- Indexing: create selective indexes; validate with EXPLAIN/ANALYZE.
- Migration plan: forward-only steps with safe rollbacks and backfills.

### Step 4: Architecture and layers
- Handlers/controllers (HTTP) validate/parse and translate to DTOs.
- Services hold business rules; repository/DAO isolates data access.
- Integrations encapsulate external APIs with retries/backoff and circuit breakers.
- Use RO-RO: receive object, return object.

### Step 5: Implement safely
- Boundary validation with schema validators.
- Transactions for multi-row invariants; keep scopes small.
- Retries with jitter for transient errors; never inside transactions.
- Timeouts everywhere; no unbounded waits.

### Step 6: Authentication and authorization
- Verify tokens (exp, iss, aud, kid) or sessions; short-lived access, refresh rotation.
- Enforce RBAC/ABAC in the service layer; deny-by-default.
- Rate limits per principal and route; emit `X-RateLimit-*` headers.

### Step 7: Observability
- Structured JSON logs with request IDs and user/tenant (non-PII).
- Metrics: RED (Rate, Errors, Duration) per endpoint; business KPIs.
- Distributed tracing with correlation/trace IDs propagated end-to-end.

### Step 8: Performance and caching
- Profile before optimizing; focus on p95/p99.
- Eliminate N+1 queries; add covering indexes.
- Apply caching (request/application/db) with explicit invalidation rules.

### Step 9: Docs and release
- OpenAPI/GraphQL schema with examples and error catalog.
- Feature flags for risky changes; canary + fast rollback plan.
- Post-deploy verification checklist.

## Checklists

### Endpoint quality checklist
- Consistent resource names and HTTP verbs.
- Correct `Content-Type`, `Accept`, caching headers.
- 2xx/4xx/5xx mapped; `problem+json` error shape.
- Pagination cursors are opaque; deterministic ordering.
- Idempotency enforced for unsafe operations.

### Data layer checklist
- PKs/FKs/uniques/CHECKs defined; not just app-level validation.
- Indexes measured for selectivity; avoid over-indexing.
- Migrations backward-compatible; online-safe; rollback plan.
- Seed/default data is idempotent.

### Reliability checklist
- Timeouts and retries with exponential backoff and jitter.
- Circuit breakers and bulkheads for dependencies.
- DLQ for async jobs; retries are idempotent.

## Patterns
- Idempotency store: persist `idempotency_key → result/status` for POST to prevent duplicates.
- Outbox pattern for reliable event delivery.
- Saga orchestration for cross-service workflows.
- Job processing: at-least-once semantics with dedupe keys and visibility timeouts.

## Troubleshooting
- 500s from dependency: add timeouts/circuit breaker; provide fallback; surface error codes.
- Deadlocks: shrink transaction scope; stable locking order; retry on specific codes.
- Hot endpoints: profile, cache read-mostly paths, batch/stream large results.
