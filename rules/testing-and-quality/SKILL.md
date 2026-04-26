---
name: testing-and-quality
description: Establishes a comprehensive testing strategy (unit, integration, E2E), conventions, fixtures, coverage targets, and CI gates. Use when adding tests, preventing regressions, or hardening quality for a service or library. Provides test pyramid, naming standards, flake control, test data management, and review checklists.
license: Complete terms in LICENSE.txt
---

# Testing and Quality

## Objectives
Fast feedback, high confidence, and reproducibility with minimal flakiness.

## Principles
- Test behavior, not implementation details.
- Prefer pure functions and small units; isolate side effects.
- Deterministic fixtures; one reason to fail per test.
- Keep tests readable; arrange–act–assert.

## Instructions

### Step 1: Define risk and scope
- Identify critical paths, SLAs, and data sensitivity.
- Set quality goals: coverage targets, allowed flake rate, max runtime.

### Step 2: Test pyramid and targets
- Unit tests (majority): fast, isolated, cover happy/sad paths and edges.
- Integration tests: service + DB/external via containers or test doubles; contract tests for APIs.
- E2E: key user journeys; smoke + a smaller regression suite.
- Coverage: global threshold and higher thresholds for critical modules.

### Step 3: Conventions
- Naming: `test_<unit>_does_<behavior>`; one behavior per test.
- Keep helper functions small; prefer builders over large fixtures.
- Tagging/markers to group slow, integration, or e2e tests.

### Step 4: Fixtures and data
- Factory/builders for entities with sensible defaults.
- DB isolation: transaction per test or ephemeral DB; auto-rollback.
- No real third-party calls; use stubs/VCR/snapshots.

### Step 5: Mocking and contracts
- Mock only at seam boundaries; prefer real infra in integration tests.
- Provider/consumer contract tests for external APIs.

### Step 6: CI gates
- Lint and type-check mandatory.
- Unit suite shard in parallel; cache dependencies.
- Integration suite with ephemeral database/containers.
- E2E smoke on preview; full E2E nightly or pre-release.
- Enforce coverage thresholds; fail on growth of flaky tests.

### Step 7: Reporting and flake control
- Export JUnit/HTML and coverage (LCOV) artifacts.
- Retries allowed only for known flaky e2e, with quarantine list and auto-ticket.
- Track p95 test durations; deflake or skip long-tail offenders.

## Checklists

### Unit test checklist
- Covers normal, boundary, and error cases.
- No I/O or network; deterministic.
- Asserts on outputs and error types/messages.

### Integration test checklist
- Real schema/migrations applied.
- Timeouts and realistic network conditions (where feasible).
- Contract tests for external providers.

### E2E checklist
- Critical user journeys automated.
- Accessibility checks and basic performance budgets.
- Screenshots/videos for failures; artifacts stored.

## Patterns
- Property-based tests for parsers/normalizers.
- Golden files for stable format outputs (with deliberate update workflow).
- Snapshot tests for UI or API payload shape (review diffs carefully).
- Mutation testing to harden critical logic.

## Troubleshooting
- Flaky E2E: add explicit wait-for conditions; stabilize data; use test IDs.
- Slow suite: parallelize, shard by cost, profile hot tests; remove redundant E2E in favor of integration tests.
- Brittle mocks: move logic behind interfaces; favor contract tests.
