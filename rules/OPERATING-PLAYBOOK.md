# Operating Playbook — Skills Orchestration and Non‑Skippable Gates

This playbook shows who starts, the end‑to‑end flow, and how we enforce that coding never skips the skills.

## Roles and Core Artifacts
- Product Owner: Vision/OKRs, discovery, PRDs, roadmap
- Project Manager: Plan, RACI, RAID, delivery cadence
- Tech Lead/Architect: System design, ADRs, capacity/cost
- Engineers: Backend/Frontend, tests, security, perf
- DevOps/SRE: CI/CD, infra, observability, DR

Artifacts: Opportunity backlog, PRDs, ADRs, C4 diagrams, delivery roadmap, RACI/RAID, test plans, budgets, runbooks, dashboards.

## Dual‑Track Agile Flow (continuous)

Discovery Track (problem/solution discovery)
- Intake opportunities with evidence and JTBD — use: product-ownership-and-roadmapping
- Research, interviews, problem framing, write PRD v0 (lightweight)
- Spikes/prototypes (minimal gates), user tests, refine scope and metrics
- Outputs: validated problems, PRD vN, experiment plan, updated opportunity backlog

Delivery Track (solution delivery)
- Plan epics/stories/tasks, RACI/RAID, Now/Next/Later — use: project-management-and-delivery
- Iterative architecture and ADRs — use: system-design-architecture (C4, capacity/cost)
- Implement slices — use: backend-engineering, frontend-design, accessibility-and-ux-quality, documentation-and-developer-experience
- Per‑PR gates (non‑skippable) — use: security-and-privacy, testing-and-quality, performance-and-optimization, search-engine-optimization, devops-and-cicd
- Deploy with canary/rollback and observe — use: devops-and-cicd (+ observability-and-reliability if present)
- Measure outcomes and feed back into Discovery — use: product-ownership-and-roadmapping

Notes
- Tracks run in parallel; PRDs and ADRs are living documents that evolve per slice.
- Ship thin vertical slices; each PR must satisfy all applicable gates before merge.

## Enforcements (Make It Impossible to Skip)
1) PR Template (Per‑PR Definition of Done)
- Checklist sections that mirror skills: Security, Tests/Coverage, Perf budgets, A11y, SEO/Schema, Docs/ADRs updated, Rollback plan.

2) Branch Protection + Required Checks (examples)
- check-security, check-tests, check-coverage, check-perf-budgets, check-a11y, check-seo-schema, check-lint-types, check-build

3) CODEOWNERS (examples)
- SECURITY.md, auth/** → @security-owners
- db/**, migrations/** → @data-owners
- ui/** → @ux-owners
- .github/**, ops/** → @devops-owners

4) Pre-commit Hooks
- Lint, type-check, secrets scan, conventional commits.

5) CI Gates
- SAST/SCA, unit/integration/E2E, coverage thresholds, Lighthouse/axe audits, performance budgets, schema/SEO validation, image/license scans.

6) Release Gates
- Canary success, error budget not breached, dashboards/alerts live, rollback tested.

7) Discovery Spikes (minimal gates)
- Allowed only for time‑boxed discovery. Required: secrets scan, basic security/privacy hygiene, documentation of learnings. Delivery PRs must pass full gates.

## Definition of Ready (DoR)
- PRD v0 approved (problem, users, success metrics) and evolves as we learn
- Initial architecture sketch (C4 + ADR stubs); acceptance criteria; test plan

## Definition of Done (DoD)
- All CI checks green; coverage + perf/a11y/SEO gates pass
- Docs updated (README/API/ADRs/changelog); dashboards + alerts live
- Rollout and rollback plan executed or staged

## LLM Kickoff Prompt (paste at the start of any AI coding task)
"Load and strictly follow these skills: backend-engineering, testing-and-quality, security-and-privacy, performance-and-optimization, system-design-architecture, accessibility-and-ux-quality, documentation-and-developer-experience, devops-and-cicd, search-engine-optimization, conversion-optimization, product-ownership-and-roadmapping, project-management-and-delivery. For every change: 1) cite which skill sections you applied, 2) block if any gate/checklist would fail, 3) propose the smallest change to satisfy the gate, 4) produce PR-ready code that passes all checks. PRDs and ADRs are iterative (v0 acceptable) but must be updated. Refuse to proceed if required artifacts are missing—ask for them first."

## Next Steps to Automate
- Confirm platform (GitHub/GitLab/Bitbucket) and I will:
  - Add PR template + CODEOWNERS
  - Add CI workflows implementing the required checks above
  - Configure branch protections and status checks
