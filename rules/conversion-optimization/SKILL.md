---
name: conversion-optimization
description: Improves conversion rates via research-driven UX, analytics, and disciplined experimentation. Use when auditing funnels, reducing friction in forms/checkout, crafting value props and CTAs, designing A/B tests, and measuring impact. Produces hypotheses, prioritized opportunity backlogs, test plans, and guardrails to prevent bad lifts.
license: Complete terms in LICENSE.txt
---

# Conversion Optimization (CRO)

## Principles
- Users first; clarity beats cleverness; reduce cognitive load and risk.
- Evidence-driven: combine quant (analytics) + qual (research) + heuristics.
- Ethics: no dark patterns; comply with privacy/consent laws.
- Experimentation discipline: proper power, no peeking, guardrails.

## Instructions

### Step 1: Define goals and measurement
- Primary conversions (macro): purchase, signup, lead.
- Secondary (micro): add-to-cart, email click, scroll depth, demo request.
- Instrument events with clear schema (name, props, user/session IDs) and verify.
- Baseline funnel: impressions → clicks → land → engage → convert by device/geo.

### Step 2: Research and diagnosis
- Quant: funnel drop-off, cohorts, pathing, top exit pages, device/browser splits.
- CWV and performance checks (LCP/CLS/INP) for landing and checkout.
- Heatmaps/session replay (mask PII); form analytics (field-level abandonment).
- Qual: interviews, on-site polls, support tickets, reviews; message mining.
- Heuristics (LIFT): Value prop, Relevance, Clarity, Anxiety, Distraction, Urgency.

### Step 3: Hypothesis backlog and prioritization
- Write hypotheses: Observation → Hypothesis → Expected Impact → Metric → Risk.
- Score with ICE or PXL; prioritize quick wins and high-signal tests.
- Define north-star metric and guardrails (bounce, AOV, churn, refund rate).

### Step 4: Solution design
- Copy: problem→agitate→solve; features→benefits; address objections.
- IA/Layouts: focused hierarchy, one primary CTA, supportive social proof.
- Forms: minimize fields, progressive profiling, inline validation, autofill.
- Trust: guarantees, payment logos, policies; real testimonials with attribution.
- Mobile: sticky primary CTA, thumb zones, large tap targets.

### Step 5: Experiment design
- Choose test: A/B for discrete changes; MVT for UI micro-interactions; bandits for low-risk.
- Compute sample size and MDE; set duration min. 1–2 business cycles.
- Randomization and bucketing: consistent assignment; exclude bots/employees.
- Tag events with experiment and variant IDs.

### Step 6: QA and launch
- Cross-browser/device QA; accessibility and performance budgets.
- Ensure SEO-friendly: avoid duplicate content; block index of test-only routes if needed.
- Launch behind flags; start canary; monitor guardrails.

### Step 7: Analyze and decide
- Check data quality; use appropriate statistical test.
- Segment carefully (new vs returning, mobile vs desktop) without p-hacking.
- Decide: ship/iterate/kill; document learnings in a knowledge base.

### Step 8: Institutionalize wins
- Roll out winners; update design system, templates, and playbooks.
- Add regression tests and tracking dashboards; plan follow-up tests.

## Checklists

### Landing/offer page
- Clear who/what/value above the fold; one primary CTA.
- Scannable benefits; objection-handling near CTAs; authentic social proof.
- Fast LCP; stable layout; accessible colors and focus states.

### Forms/checkout
- Only necessary fields; inline validation; descriptive errors.
- Proper input types; autofill/autocomplete; mobile-friendly.
- Trust signals; shipping/fees clarity; guest checkout option (if applicable).

### Experiment hygiene
- Hypothesis documented; sample size/MDE set; guardrails defined.
- Unique experiment key; event schema verified; QA checklist passed.
- No mid-test design changes; predetermined stop rules.

## Patterns
- Progressive disclosure in multi-step forms.
- Exit-intent or scroll-triggered offers used sparingly and respectfully.
- Anchoring and tiered pricing tables with a recommended plan.
- Personalization by segment (new/returning, geo) within consent and privacy bounds.

## Troubleshooting
- No significance: increase power (longer/pooled traffic), adjust MDE, check variance.
- Lift evaporates post-rollout: novelty/seasonality; verify randomization; re-test.
- Conflicting with SEO: preserve intent keywords and headings; avoid render-blocking scripts; keep CWV healthy.
- Dirty data: bot traffic, ad blockers, missing experiment IDs; validate instrumentation.

## Privacy and ethics
- Obtain consent where required; honor Do Not Track and regional laws.
- Mask PII in replays; store minimal data; provide clear opt-outs.
