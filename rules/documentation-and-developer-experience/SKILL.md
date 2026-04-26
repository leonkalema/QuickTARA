---
name: documentation-and-developer-experience
description: Produces clear READMEs, API docs, ADRs, onboarding guides, examples, and changelogs; standardizes style and automates docs CI. Use when shipping features/libraries or improving team onboarding and DX.
license: Complete terms in LICENSE.txt
---

# Documentation and Developer Experience

## Principles
- Docs are a product: accurate, concise, example-first.
- Single source of truth; automate generation where possible.
- Make the first 10 minutes delightful: quickstart that works.

## Instructions

### Step 1: Repository scaffolding
- README: purpose, features, prerequisites, quickstart, FAQs, support.
- CONTRIBUTING: branching, commit style, PR checklist, code style.
- CODE_OF_CONDUCT and LICENSE present.

### Step 2: API documentation
- Generate OpenAPI/GraphQL SDL; publish browsable docs.
- Include request/response examples and error taxonomy.
- Document pagination, rate limits, idempotency, and versioning.

### Step 3: ADRs (Architecture Decision Records)
- Use a short template: Context → Decision → Consequences.
- One ADR per significant decision; link PRs/issues.
- Status: proposed/accepted/deprecated/superseded.

### Step 4: Onboarding
- Scripts to set up environment and seed data.
- Access to staging, secrets guidance, troubleshooting FAQ.
- Onboarding checklist: tools, accounts, repos, run tests, open first PR.

### Step 5: Examples and cookbooks
- Minimal runnable examples for common tasks.
- Showcase good patterns and anti-patterns.

### Step 6: Releases and changelogs
- Conventional Commits; semantic versioning.
- CHANGELOG with migration notes; link to releases.
- Deprecation policy and timelines.

### Step 7: Docs CI and ownership
- Link checker, spell checker, and doc build in CI.
- Preview docs on PR; assign owners and review SLAs.

## Checklists
- README quickstart runs as written.
- API docs complete with examples and error codes.
- ADRs up to date; decisions searchable.
- Onboarding script works on clean machine.
- Changelog entries for user-visible changes.
- CI checks for links/spelling/build enabled.

## Patterns
- MkDocs/Docusaurus site with versioned docs.
- Auto-generate API clients from OpenAPI.
- Example verification tests to prevent doc drift.

## Troubleshooting
- Stale docs: add owners and review cadence; use doc coverage reports.
- Conflicting sources: consolidate to single source; delete outdated pages.
