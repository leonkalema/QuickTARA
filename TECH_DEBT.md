# QuickTARA — Technical Debt Register

A short, honest list of structural shortcuts in the codebase that work today
but will become expensive if left alone. Each entry has a one-line summary,
where it bites, the impact, and a suggested remediation.

Update this file whenever you discover or pay down debt. **Do not let it get
longer than ~10 entries** — if it does, schedule a debt sprint.

---

## 1. Two `declarative_base()` instances with overlapping table names

**Where:** `db/base.py` declares `Base` for the legacy model family
(`SystemScope`, `DamageScenario`, `Component`, ...). `db/product_asset_models.py`
declares its **own** `Base` for the product-asset family (`ProductScope`,
`Asset`, a *second* `DamageScenario`, ...).

**Symptom:** Both Bases register a table named `damage_scenarios` with
**different schemas**. Whichever `create_all` runs first wins; the second is
silently skipped (SQLAlchemy treats `create_all` as idempotent per-table-name).
Caught by integration tests in `tests/api/conftest.py:52-58`, which now
explicitly runs the product-asset metadata first as a workaround.

**Impact:** Latent runtime error if a query targets `db.product_asset_models.DamageScenario`
columns (e.g. `violated_properties`) but the legacy schema is in the DB.
Schema migrations cannot reason about a single source of truth.

**Remediation:** Unify under a single `Base`. The product-asset family is the
newer, richer schema and should win. Move legacy models to use it; rename or
delete the duplicate `DamageScenario` in `db/damage_scenario.py`.

**Effort:** Medium (1–2 days; touches imports across `db/` and several routes).

---

## 2. Alembic migrations do not cover all SQLAlchemy tables

**Where:** `db/migrations/versions/` contains migrations for SBOM
(`a1c2d3e4f5g6`), incidents (`b2d3e4f5g6h7`), and a small initial set, but
**most production tables are created by `Base.metadata.create_all()`** in
`db/session.py:142-145` as a fallback when migrations don't bring the schema
to the expected shape.

**Impact:**
- Fresh dev environments rely on app startup to fill the schema; running
  alembic alone produces an incomplete DB.
- Schema changes outside the SBOM/incident path are not version-controlled —
  rollback is impossible, drift between environments is undetectable.
- The app cannot run on a strict "migrations only" Postgres deployment.

**Remediation:** Generate alembic migrations for every existing table (use
`alembic revision --autogenerate` against a fresh DB built from `create_all`).
Lock down `init_db` to migrations-only after that. Add a CI check that
forbids `create_all` outside tests.

**Effort:** Medium (one focused day to autogenerate, review, and verify).

---

## 3. Pydantic v1 ↔ v2 mixed validators

**Where:** `api/models/component.py` (and possibly siblings) still uses the
v1-era `@validator` decorator. The rest of the codebase is on v2
(`@field_validator`, `ConfigDict(from_attributes=True)`).

**Symptom:** Pydantic deprecation warnings on every test run. More
importantly: three latent serialization bugs were caught during the
integration-test backfill (April 2026) where SQLAlchemy column types
(comma-separated `Text`, JSON-encoded `Text`) did not coerce into the
declared schema types — patched ad-hoc with `field_validator(mode="before")`
in `api/models/cra_sbom.py` and `api/models/cra_incident.py`.

**Impact:** Future Pydantic releases will drop v1 compatibility entirely;
the warning gradient hides real validation failures behind noise.

**Remediation:** Sweep all `api/models/` for `@validator`, port to
`@field_validator`. Add a CI rule that fails on Pydantic deprecation
warnings.

**Effort:** Small (half a day).

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
