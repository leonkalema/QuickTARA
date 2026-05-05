# QuickTARA — Technical Debt Register

A short, honest list of structural shortcuts in the codebase that work today
but will become expensive if left alone. Each entry has a one-line summary,
where it bites, the impact, and a suggested remediation.

Update this file whenever you discover or pay down debt. **Do not let it get
longer than ~10 entries** — if it does, schedule a debt sprint.

---


## 4. No PDF golden-file tests for reports

**Where:** `api/services/reporting/` produces ReportLab PDFs (audit trace,
customer compliance summary). There are no regression tests that assert
section presence, page count, or reproducible byte output.

**Impact:** Any change to the reporting pipeline can silently break a
deliverable customers see. Reports are the product; they should be locked.

**Remediation:** For each report, save a known-good PDF (or a normalised
text extraction) under `tests/reports/golden/` and assert equality on
regeneration. Re-bless intentionally with a script.

**Effort:** Small per report (~2 hours each).

---

## 5. No E2E (Playwright) coverage for CRA flows

**Where:** `tara-web/` has no end-to-end test runner wired up.

**Impact:** Frontend-backend integration regressions go uncaught until a
human clicks the UI. The CRA module — classification wizard → requirements
table → Annex VII export — is exactly the multi-step workflow that benefits
most from E2E.

**Partial progress (May 2026):** Component tests exist for
`CraClassificationWizard` (15 tests) and `CraAnnexVii` (27 tests) using
`@testing-library/svelte` with Playwright as the browser runtime. These test
each component in isolation with the API mocked — they are **not** E2E.
A real E2E test would spin up the FastAPI backend and drive a real browser
through the full flow with no mocks.

**Remediation:** Add Playwright with one happy-path test per shipped CRA
sub-feature (SBOM upload, incident create + submit, Annex VII download).
Run on PR.

**Effort:** Medium (one day for setup + first three tests).

---

## How to use this file

- Reference an entry by number in commit messages and PRs (e.g. *"works
  around debt #1"*) so the connection survives.
- When you fix one, **delete the entry** rather than marking it done — the
  git history is the audit trail.
- New debt: add to the bottom with the same structure.
