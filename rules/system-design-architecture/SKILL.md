---
name: system-design-architecture
description: Produces scalable, reliable architectures with explicit trade-offs, diagrams, capacity estimates, and migration plans. Use when designing new systems, evolving monoliths, planning multi-region, or assessing scale/failure modes.
license: Complete terms in LICENSE.txt
---

# System Design and Architecture

## Outcomes
- Clear architecture doc with requirements, constraints, choices, and trade-offs.
- C4 diagrams (Context/Container/Component) + sequence/data-flow.
- Back-of-envelope capacity and cost estimates.
- Migration/evolution plan with risks and mitigations.

## Method

### Step 1: Requirements and constraints
- Functional scope and core user journeys.
- Non-functional: SLA/SLOs, availability, consistency, latency budgets.
- Compliance: data residency, PII handling, auditability.
- Constraints: team size, timeline, cloud/provider, legacy deps.

### Step 2: Workload modeling
- Traffic shape: req/s, burstiness, growth curve.
- Data profile: read/write mix, object sizes, retention, hotspots.
- External integrations and their SLAs/limits.

### Step 3: Architecture choices
- Monolith vs. services (team topology, deploy cadence, boundaries).
- Sync (HTTP/gRPC) vs. async (queues/streams) per interaction.
- Storage: relational vs. KV/document/search/time-series; justify picks.
- Caching layers: client/CDN/app/DB; invalidation strategy.

### Step 4: Data modeling and consistency
- Transactions and invariants; schema with FKs/uniques/checks.
- Partitioning/sharding strategy; rebalancing plan and keys.
- Consistency model: strong vs. eventual; read-your-writes needs.
- Multi-region: leader-follower vs. active-active; failover policy.

### Step 5: Reliability and resilience
- SLOs and error budgets; graceful degradation under partial outages.
- Back-pressure, timeouts, retries with jitter, circuit breakers.
- Idempotency for unsafe operations; dedupe keys.

### Step 6: Observability and security (cross-cutting)
- Structured logs, metrics (RED/USE), distributed tracing.
- Authn/z strategy; secrets; audit logs; least privilege.

### Step 7: Diagrams and documentation
- C4: Context → Container → Component.
- Sequence diagrams for critical flows (e.g., checkout, signup).
- Data flow and lifecycle: creation → transformations → retention/deletion.

### Step 8: Capacity and cost
- Estimate QPS, storage growth, cache sizes, queue depths.
- Instance sizing; throughput per instance; bottleneck projections.
- Cost model: compute, storage, network egress; headroom policy.

### Step 9: Evolution plan
- Start simple; identify clear service boundaries for future extraction.
- Strangler-fig migrations; outbox for event propagation.
- Feature flags, canary deploys, rollback criteria.
- Capture decisions in ADRs with rationale and consequences.

## Checklists
- Requirements captured, constraints explicit, risks listed.
- Single-writer vs. multi-writer decided with consistency rationale.
- Back-pressure and failure modes documented per dependency.
- Security and privacy addressed; data residency considered.
- Diagrams present; capacity numbers back assumptions.

## Patterns
- CQRS for divergent read/write workloads; Event Sourcing where auditability is critical.
- Outbox + change data capture for reliable events.
- API Gateway/BFF to tailor APIs to clients.
- Strangler pattern for legacy replacement.

## Troubleshooting
- Unclear boundaries: use Domain-Driven Design to define bounded contexts.
- Over-engineering: begin with modular monolith; extract later.
- Data hotspots: introduce sharding or cache; reconsider access patterns.
