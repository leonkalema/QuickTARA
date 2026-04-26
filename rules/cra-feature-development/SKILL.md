---
name: cra-feature-development
description: How to design, build, test, and ship the next CRA Compliance features in QuickTARA. Use this skill whenever the task involves the CRA module — SBOM ingestion, ENISA 24-hour reporting, Annex VII technical documentation generation, PSIRT / vulnerability disclosure, NVD feed integration, or any change to `core/cra_*` and `api/routes/cra.py`. Encodes regulatory accuracy requirements, the canonical priority order, file boundaries, testing discipline, and security/privacy invariants for this codebase.
license: Internal
---

# CRA Feature Development

## Objectives
Ship CRA features that are **regulation-correct first, ergonomic second, and never both at the cost of the other**. Each new feature must move a customer measurably closer to a defensible Module A self-assessment, Module B+C notified body submission, or Article 14 incident report — not just add a checkbox.

## Non-negotiable principles
- **Cite the law.** Every new requirement, deadline, classification rule, or workflow step gets an inline source comment naming the article (e.g. `# CRA Art. 14(2)`, `# Annex VII §3`, `# Implementing Regulation 2025/2392`). Untraceable claims do not ship.
- **Risk-based vs mandatory must remain distinguishable.** Part I (risk-based) and Part II (mandatory) requirements behave differently in the UI, in reports, and in gap severity defaults. Do not collapse them.
- **Auto-mapping is the moat.** Every new artifact (SBOM, CVE, incident, technical doc) must register a mapping to one or more `CRA_REQUIREMENTS` entries. A feature that only adds storage without auto-mapping is incomplete.
- **No published default credentials, secrets, or shortcut bypasses.** Bootstrap data goes to `0600` files, never into source. JWT secret, admin password, TLS keys: all generated per-install (already established — keep it that way).
- **Reports are evidence, not decoration.** Every PDF section that claims compliance must show its source data, the article reference, and the timestamp. A reviewer must be able to walk from "claim" → "evidence" → "raw artifact" in three clicks max.

## Canonical priority order (do not reshuffle)
Build in this order. Each feature unlocks the next; skipping ahead creates rework.

1. **SBOM ingestion** (CycloneDX 1.5 + SPDX 2.3) — required for CRA-10, prerequisite for #4 and #5.
2. **ENISA 24-hour reporting workflow** — covers CRA-14, the most time-critical regulatory obligation. Includes structured incident form, countdown clock from discovery, and ENISA Single Reporting Platform export.
3. **Annex VII technical documentation generator** — covers CRA-15. Generates from existing `ProductScope` + `Asset` + TARA artifacts. PDF output with section-by-section citations to the underlying records.
4. **PSIRT inbox + CVE-to-product linkage** — covers CRA-09, CRA-11, CRA-13. Provides the ongoing workflow.
5. **NVD feed integration** — auto-flags new CVEs against SBOM-listed components. Depends on #1.

Anything outside this list (supplier registry, CE marking generator, Module B+C submission packager) waits until 1–5 are shipped.

## File and module boundaries

When adding a CRA feature, the change set should fit this layout:

```
core/cra_<feature>.py                    # pure logic, no I/O, no DB, no FastAPI
core/cra_<feature>_catalog.py            # static reference data (regulation-derived)
db/cra_models.py                         # new SQLAlchemy tables (one entity per feature)
db/migrations/versions/<rev>_<feature>.py # alembic migration; idempotent
api/models/cra.py                        # Pydantic request/response schemas
api/routes/cra.py                        # FastAPI endpoints; thin layer
api/services/reporting/sections/cra_<feature>_section.py  # report builder
tara-web/src/features/cra/components/    # Svelte UI
tara-web/src/lib/api/craApi.ts           # frontend API client
tests/api/test_cra_<feature>.py          # backend tests
tests/cra/test_cra_<feature>_<unit>.py   # core logic tests
```

Rules:
- **`core/` is pure.** No SQLAlchemy, no FastAPI, no `requests`, no file I/O outside reading bundled regulation data. Pure functions enable fast unit tests against regulation fixtures.
- **`db/` defines persistence only.** Business logic stays in `core/`. The `db/` layer should be reasonably easy to swap for Postgres later (no SQLite-specific SQL).
- **`api/routes/cra.py` is thin.** Endpoints validate the request, call a single `core/` or `service/` function, and return a Pydantic model. No business logic in routes.
- **One file ≤ 400 lines.** When a `core/cra_*` file approaches this limit, split by concern (e.g. `cra_sbom_parser.py`, `cra_sbom_validator.py`, `cra_sbom_mapper.py`).

## Testing discipline (mandatory)

**Test before shipping. No exceptions for "small" CRA changes — regulatory bugs cost customers a notified body resubmission.**

### What must have tests
- Every regulation-derived rule (deadlines, classification thresholds, conformity-module derivation, support-period minimums).
- Every auto-mapping function (`auto_map_*`, `analyze_gaps`, `derive_severity_*`).
- Every parser that ingests external data (SBOM, CVE feed, incident form).
- Every PDF report section that makes a compliance claim.

### Test categories
- **Regulation fixtures** — JSON/CSV under `tests/cra/fixtures/` containing official examples (e.g. a real CycloneDX SBOM, a real ENISA incident template, an Annex III category list). Tests assert behaviour against these, not against synthetic data.
- **Golden classification cases** — `tests/cra/test_cra_classifier.py` already contains some. Extend to cover every Annex III/IV category, the open-source exception, the harmonised standard exception, and the automotive lex specialis.
- **Auto-mapping invariants** — for each `CRA-XX`, a test that creates the relevant TARA artifact and asserts that the mapping appears with correct `status`, `evidence_notes`, and `gap_severity`.
- **Migration round-trip** — every new alembic migration must have an upgrade + downgrade test under `tests/db/`.
- **Report determinism** — generating the same product's CRA report twice produces byte-identical PDFs (modulo timestamps, which are isolated in one section).

### Naming
`test_<function>_<scenario>_<expected>` — e.g. `test_classify_product_class_ii_with_open_source_returns_module_a`. One behaviour per test.

### Runtime
- Unit tests on `core/cra_*`: target < 5s for the full file.
- Integration tests with DB: ephemeral SQLite per test, transaction rollback.
- Never call NVD / ENISA / external services in tests; use recorded responses under `tests/cra/fixtures/external/`.

## Coding conventions for this module

- **Type hints everywhere.** Pydantic v2 models for I/O, dataclasses (`frozen=True`) for value objects, SQLAlchemy mapped types for persistence. No `Any` unless the boundary is genuinely opaque (e.g. parsed JSON from a third-party feed before validation).
- **Article references in docstrings.** Every public function in `core/cra_*` starts its docstring with the article it implements: `"""CRA Art. 14(4) — 24-hour early warning to ENISA."""`.
- **Enums for status fields.** No magic strings. `CraRequirementStatus.PARTIAL`, not `"partial"`.
- **Frozen dataclasses for catalog entries.** All `CONTROLS_CATALOG`, `REQUIREMENTS`, `CATEGORIES` lists hold immutable records. Mutability bugs in regulatory data are silent disasters.
- **No `print` statements.** Use `logging.getLogger(__name__)`. Migrations are the one exception.
- **Errors are explicit.** Raise `HTTPException` with the precise status code and a stable `detail`. Customers integrating the API parse those.

## Bug-fixing discipline

When a regulation update or a customer report exposes an error:

1. **Reproduce with a test first.** The fix isn't real until a test would have caught it.
2. **Find the upstream cause.** A symptom in the report layer is almost always a bug in `core/cra_auto_mapper.py` or a catalog entry. Fix the source, not the symptom.
3. **Prefer the smallest correct change.** Single-line fixes are normal. Refactoring "while we're here" is not — open a separate PR.
4. **Cite the source of the correction.** Commit message: `fix(cra): CRA-XX deadline corrected per Implementing Reg 2025/2392 §X`. The trail must survive the fix.
5. **Never weaken a test to make it pass.** If a test now disagrees with the regulation, the regulation interpretation is what changed — update the test with a comment citing why.

## Security and privacy invariants

- **SBOMs may contain proprietary component lists.** Treat them as confidential. Do not log SBOM contents. Storage requires the same access control as TARA artifacts.
- **Incident reports may name unfixed vulnerabilities.** Same handling as SBOMs. Disclosure timestamps matter — do not let internal users export an incident before the public-disclosure date encoded in the record.
- **Every external integration (NVD, ENISA, supplier portals) is opt-in and configurable per-org.** No automatic outbound calls without explicit `Organization`-level configuration.
- **Audit log everything.** Classification changes, status transitions, control assignments, report exports. The audit log is itself evidence under CRA Art. 28.

## Definition of done (per feature)

A CRA feature is shippable only when **all** of the following hold:

- [ ] Article references in code, in tests, in user-facing UI tooltips, in PDF report sections.
- [ ] Auto-mapping registered (or explicit comment justifying why none applies).
- [ ] Unit tests for every regulation-derived rule, integration tests for the API surface, golden file for the report section.
- [ ] Alembic migration with passing upgrade + downgrade test.
- [ ] One paragraph in `README.md` under the CRA module section, with article reference.
- [ ] No file in the change set exceeds 400 lines.
- [ ] No new hardcoded secrets, default passwords, or wildcard CORS additions.
- [ ] Manually verified end-to-end against a fixture product (`tests/cra/fixtures/products/<product>.json`).

## What not to build (yet)

- Multi-tenant SaaS architecture — wait until #1–5 ship.
- A custom report renderer — `reportlab` via `api/services/reporting/` is sufficient through 2027.
- Real-time collaboration on assessments — single-editor pessimistic locking is fine.
- An ML-based threat suggester — regulatory tools sell on traceability, not novelty.
