# Report Module Redesign — Design Spec

Status: Draft for review
Scope: TARA report generation (`api/services/reporting/*`, `tara-web/src/routes/reports/+page.svelte`)

## 1. Goal

Let the user shape a TARA report at generation time based on:

1. **Who consumes it** — internal vs external audience.
2. **What it contains** — per-section include/exclude.
3. **ISO/SAE 21434 alignment** — each section traced to its work product, plus a proper document-control block.

## 2. Current State (baseline)

- `build_complete_report(scope_id, db)` in `api/services/reporting/report_builder.py` assembles a **fixed** section list in a fixed order: Compliance → CRA → Risk Summary → Assets → Damage Scenarios → Goals.
- Existing section builders (already modular, reusable as-is):
  - `compliance_section.py` — ISO 21434 clause matrix
  - `cra_compliance_section.py` — EU CRA compliance
  - `risk_summary_section.py` — risk register (WP-08/09)
  - `assets_section.py` — asset inventory
  - `damage_section.py` — damage scenarios
  - `goals_section.py` — cybersecurity goals
  - `traceability_section.py` — built but **not currently wired in**
- Frontend exposes **format only** (PDF/Excel/JSON/text). No content control.
- PDF header always stamps the same ISO 21434 statement (`pdf_renderer.py:build_document_header`).

## 3. Proposed Model: `ReportConfig`

A single config object flows frontend → API → builder.

```jsonc
{
  "audience": "internal" | "external",
  "detail_level": "full" | "summary",
  "classification": "Public" | "Internal" | "Confidential",
  "sections": {
    "executive_summary": true,
    "document_control": true,
    "iso_compliance": true,
    "cra_compliance": false,
    "asset_inventory": true,
    "damage_scenarios": true,
    "threat_scenarios": true,
    "attack_paths": true,
    "risk_register": true,
    "treatment_plan": true,
    "cybersecurity_goals": true,
    "traceability": false
  },
  "metadata": {
    "author": "string|null",
    "approver": "string|null",
    "reference": "string|null"
  }
}
```

Notes:
- `sections` keys map 1:1 to section builders. Adding a section later = add a key + builder.
- `audience` and `detail_level` only set **defaults**; the user can still override individual toggles.

## 4. Audience Profiles (default presets)

| Section | Internal (default) | External (default) | Rationale |
|---|---|---|---|
| Document control | on | on | Auditors expect version/author/approver |
| Executive summary | on | on | Both audiences |
| ISO 21434 compliance matrix | on | on | Core deliverable |
| CRA compliance | on | optional | Only if CRA assessment exists |
| Asset inventory | on (component-level) | on (summary) | Hide internal component IDs externally |
| Damage scenarios | full | full | Both |
| Threat scenarios | on | on | Both |
| Attack paths | on (with feasibility scores) | summary (ratings only) | Hide raw feasibility internals externally |
| Risk register | all states | approved/final only | Don't expose drafts externally |
| Treatment plan | all (incl. draft) | approved only | WIP stays internal |
| Cybersecurity goals | on | on | Key external claim |
| Traceability matrix | on | optional | Heavy; auditor-driven |
| Analyst notes / open gaps | on | off | Internal only |

`detail_level: summary` trims tables to ratings/final values and drops internal IDs and raw scores.

## 5. ISO/SAE 21434 Work-Product Mapping

Each included section declares its work product so the compliance matrix is generated from what's actually in the document (not a static list).

| Section | ISO 21434 Work Product / Clause |
|---|---|
| Asset inventory + damage scenarios | WP-04 — Item definition / damage scenarios (§15.3) |
| Threat scenarios | WP-05 — Threat scenario identification (§15.4) |
| Attack paths | WP-06/07 — Attack path analysis + feasibility (§15.5–15.6) |
| Risk register | WP-08 — Risk value determination (§15.7) |
| Treatment plan | WP-09 — Risk treatment decision (§15.8) |
| Cybersecurity goals | WP-15 — Cybersecurity goals/claims (§9.x) |
| Document control | §6 — Project-dependent CS management / documentation |

## 6. Document Control Block (new)

Added to PDF header for audit-readiness:
- Document title + product name
- Classification label (from config)
- Version
- Author, Approver (from `metadata`)
- Generated date, tool name + version
- Reference / document ID

## 7. API Changes

- New endpoint: `POST /reports/{scope_id}/pdf` accepting `ReportConfig` body (keep existing `GET` for backward compatibility = internal/full default).
- `build_complete_report(scope_id, db, config: ReportConfig)` conditionally assembles sections from `config.sections`, ordered canonically.
- Export endpoints (`/export/{format}`) accept the same config for JSON/Excel/text parity.

## 8. Frontend Changes (`reports/+page.svelte`)

- **Audience toggle** (Internal / External) — sets section defaults.
- **Section checklist** — grouped, pre-filled from audience, user-overridable.
- **Classification dropdown** + optional author/approver/reference fields.
- Keep format selector.
- "Readiness" checklist stays; warn if an included section has no data.

## 8b. Reusable Report Templates (decided: reusable)

A **template** is a saved, named `ReportConfig` the user can reapply.

Perfect-world design:
- **Built-in presets** (read-only, always available): `Internal — Full`, `External — Customer/OEM`, `Auditor / Regulator`. These ship with the tool and seed the audience defaults from §4.
- **Org templates**: a `tool_admin` can save/edit org-wide templates (e.g. "Acme External Standard") so every report looks consistent across the org.
- **Product override**: a product can pin a default template; the reports page preselects it but the user can still tweak before generating.
- Resolution order when opening the reports page: product default → org default → built-in `Internal — Full`.

Minimal persistence (new table `report_templates`):

| Column | Notes |
|---|---|
| `template_id` | PK |
| `organization_id` | FK, nullable for built-ins |
| `name` | unique per org |
| `is_builtin` | read-only presets |
| `config_json` | serialized `ReportConfig` |
| `created_by`, `created_at`, `updated_at` | audit |

This keeps v1 lean: the generator only ever consumes a `ReportConfig`; templates are just a way to store and reuse one.

## 9. Backward Compatibility

- Existing `GET /reports/{scope_id}/pdf` keeps working (defaults to internal/full).
- The generator is config-only; the single additive schema change is the `report_templates` table (§8b). Reports themselves are not persisted.
- A product's pinned default template is an optional nullable column/reference; absence falls back to org/built-in defaults.

## 10. Out of Scope (v1)

- Digital signing / cryptographic signature on the document.
- Multi-step approval **workflow** (author submits → approver signs off in-app). See §6 note.
- Multi-language reports.

## 11. Decisions (resolved)

1. **Reusable templates** — yes. Design in §8b: built-in presets + org templates + per-product default, generator always consumes a plain `ReportConfig`.
2. **External redaction** — soft. Audience sets defaults; user can override. No server-enforced redaction in v1.
3. **CRA compliance** — conditional. Include the CRA section **only if a `CraAssessment` exists for the product** (this is how CRA-in-scope is already represented in the DB — `CraAssessment.product_id`). If no assessment, the section is omitted entirely rather than printing a "no assessment" placeholder.
4. **Approval signature block** — the **document-control block** (author / approver names + date + version, §6) ships in **v1** because ISO/SAE 21434 expects identified authors, approvers, and dates in the deliverable. The interactive **approval workflow** (in-app sign-off) is deferred (§10).

