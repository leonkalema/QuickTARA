---
name: performance-and-optimization
description: Profiles and optimizes latency, throughput, memory, and cost; sets budgets; introduces safe caching, indexing, batching, and concurrency. Use when reducing p95/p99, diagnosing slow endpoints/queries, planning capacity, or preventing regressions.
license: Complete terms in LICENSE.txt
---

# Performance and Optimization

## Objectives
- Hit explicit latency and throughput SLOs with predictable tail behavior.
- Reduce cost/footprint without harming correctness or reliability.
- Prevent regressions with budgets and CI checks.

## Principles
- Measure first; optimize the critical path only (Amdahl’s Law).
- Set budgets (p50/p95/p99, CPU, memory, I/O) and enforce.
- Prefer algorithmic/data design fixes before micro-optimizations.
- Optimize safely: feature flags, canary, rollback plan.

## Instructions

### Step 1: Define SLIs/SLOs and budgets
- Choose SLIs per capability: request latency (p50/p95/p99), throughput (req/s), error rate.
- Define budgets: CPU %, RSS/heap MB, open FDs, DB connections, queue depth.
- Separate cold vs. warm path goals.

### Step 2: Baseline and profile
- Add tracing spans around handlers, DB calls, cache, external I/O.
- Capture flamegraphs (CPU) and heap profiles (memory) in staging under load.
- For DB: run EXPLAIN/ANALYZE, capture timings and row estimates.
- Identify top 3 bottlenecks; ignore the rest until those are fixed.

### Step 3: Database performance
- Eliminate N+1 with joins or prefetch; use covering indexes.
- Check selectivity; avoid functions on indexed columns in predicates.
- Prefer keyset (cursor) pagination for large, frequently updated sets.
- Tune pool size; prevent pool exhaustion and long queue times.

### Step 4: Application-level optimization
- Caching:
  - Request cache: respect Cache-Control, ETag/If-None-Match.
  - Application cache: read-through/write-through with explicit TTLs.
  - Avoid stampedes: request coalescing and jittered TTLs.
- Batching and bulk ops: aggregate small calls; use set-based DB ops.
- Async I/O: offload long work to background jobs with back-pressure.
- Streaming: chunk large responses; prefer HTTP compression where applicable.

### Step 5: Concurrency, queues, and back-pressure
- Use bounded queues; drop/slow non-critical work when saturated.
- Rate limiters (token bucket/leaky bucket) per principal and route.
- Timeouts everywhere; exponential backoff with jitter for retries.

### Step 6: Load and stress testing
- Define scenarios (baseline, burst, soak); warm caches; seed realistic data.
- Tooling (examples): k6, Locust, Artillery. Capture traces and metrics.
- Record p50/p95/p99, error rates, saturation signals; compare to budgets.

### Step 7: Rollout and guardrails
- Ship behind a flag; run a canary (e.g., 5%) with automated rollback on SLO breach.
- Add alerts for p95/p99, queue depth, pool saturation, GC pauses.

## Checklists

### Query optimization checklist
- Predicates match indexes; no leading wildcard LIKE.
- Joins on indexed keys; small-to-large join order where relevant.
- Avoid SELECT * in hot paths; fetch only needed columns.
- Verify with EXPLAIN/ANALYZE before and after.

### Caching checklist
- Clear ownership of cache keys and invalidation rules.
- TTLs include jitter; protection against stampede (coalescing).
- Metrics: hit ratio, evictions, stale-while-revalidate where safe.

### HTTP performance checklist
- Proper Cache-Control and ETag; gzip/br compression.
- Keep-Alive enabled; connection pooling tuned.
- Paginated endpoints; streaming for large payloads.

## Patterns
- Request coalescing: single-flight per key to avoid duplicate upstream calls.
- Read-through cache + background refresh for expensive reads.
- Token bucket rate limiter with leaky bucket smoothing.
- Circuit breaker to fail fast on unhealthy dependencies.

## Troubleshooting
- Tail spikes (p99): check GC pauses, lock contention, thundering herds.
- Cache stampede: add coalescing and jitter; consider stale-if-error.
- Pool exhaustion: reduce concurrency, increase pool, fix slow queries.
- Memory leaks: heap profiles; check unbounded caches and long-lived refs.
