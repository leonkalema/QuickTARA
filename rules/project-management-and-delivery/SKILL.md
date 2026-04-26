---
name: project-management-and-delivery
description: Orchestrates execution to deliver outcomes on time and with quality. Use when creating delivery plans, estimating and sequencing work, running sprints/kanban, managing risks/dependencies, reporting status, and preparing releases. Produces delivery roadmap, RAID log, RACI, sprint boards, metrics dashboards, and release plans.
license: Complete terms in LICENSE.txt
---

# Project Management and Delivery

## Principles
- Outcomes over output; predictability over heroics; transparency over surprises.
- Small batches, visible flow, explicit WIP limits; continuous improvement.
- One owner per decision (RACI); single source of truth for plans and status.

## Instructions

### Step 1: Intake and scoping
- Capture requests in a single backlog with problem, value, and definition of done (DoD).
- Triage: size (t-shirt), urgency, dependencies, risks, required teams.

### Step 2: Plan the work
- Break into Epics → Stories → Tasks; define acceptance criteria.
- Estimation: story points or time-range estimates with confidence.
- Capacity plan per team (holidays, meetings, interrupts); set WIP limits.
- Build a delivery roadmap (Now/Next/Later) aligned to OKRs.

### Step 3: Governance and ownership
- Create a RACI for key decisions/areas.
- Maintain a RAID log (Risks, Assumptions, Issues, Dependencies) with owners and due dates.

### Step 4: Execution model
- Scrum: Sprint Planning → Daily Standup → Review → Retrospective.
- Kanban: continuous flow with classes of service and explicit policies.
- Definition of Ready (DoR) and DoD enforced at board transitions.

### Step 5: Tracking and reporting
- Boards reflect reality (no side work off the board).
- Burnup/burndown for sprints; cumulative flow for kanban.
- Status reports: risks, blockers, scope changes, percent complete by milestone.
- Publish a single weekly update with decisions and impact.

### Step 6: Risk and dependency management
- Identify critical path; add buffers; monitor slack.
- For external deps, define SLAs and escalation paths.
- Run pre-mortems for major launches; convert to mitigations.

### Step 7: Quality and release readiness
- Entry/exit criteria per stage: reviews, tests, security checks, a11y, performance budgets.
- Release plan: feature flags, canary, rollback; comms to stakeholders/support.

### Step 8: Metrics and improvement
- Track: lead time, cycle time, throughput, WIP, predictability (commit vs. complete), escaped defects, change fail rate, MTTR.
- Hold retros; turn findings into explicit policy changes.

## Checklists

### Sprint/iteration readiness
- Stories meet DoR; acceptance criteria clear; test strategy known.
- Dependencies resolved or tracked; capacity confirmed; WIP limits set.

### Release readiness
- All gates passed (tests, security/privacy, performance, a11y).
- Rollback plan tested; runbooks updated; monitoring/alerts configured.
- Stakeholder and customer comms prepared; support trained.

### Status hygiene
- RAID log up to date; owners and dates current.
- Board reflects actual state; no stale “in progress” items.
- Risks listed with probability×impact and mitigations.

## Patterns
- Dual-track agile (discovery and delivery in parallel with handoffs).
- WSJF (weighted shortest job first) for sequencing by cost of delay.
- Program increments/quarterly planning for multi-team coordination.
- Trunk-based development with short-lived PRs and feature flags.

## Troubleshooting
- Scope creep: enforce change control; re-baseline and communicate impact.
- Missed deadlines: inspect plan assumptions; reduce WIP; increase slice size clarity.
- Chronic blockers: escalate via RACI; create service-level working agreements.
- Poor predictability: lower WIP, improve DoR/DoD, stabilize estimation with ranges.
