# CRA Compliance Module — Design Document

**Date:** 2026-02-09
**Status:** Design Phase

---

## 1. What This Module Does

A company selects a product in QuickTARA. They run a CRA assessment. The system:

1. Classifies the product (Default / Class I / Class II / Critical)
2. Detects whether TARA work already exists for that product
3. Maps existing TARA artifacts to CRA requirements (auto-fill)
4. Shows all 18 CRA requirements with gap status
5. Tracks remediation per requirement (owner, date, evidence)
6. Handles legacy products that have no TARA
7. Generates a CRA compliance report section

---

## 2. Two Paths: Products With TARA vs Without

### Path A — Product Has TARA (Current Product)

The product already has assets, damage scenarios, threat scenarios, risk ratings, and audit trail in QuickTARA. The system auto-maps these to CRA requirements.

**Auto-filled CRA requirements from existing TARA:**

| CRA Requirement | Auto-Mapped From | Article |
|-----------------|------------------|---------|
| Risk assessment | Product scope + damage/threat scenarios exist | Art. 13 |
| Confidentiality protection | Assets with CIA ratings (C dimension) | Art. 13 |
| Integrity protection | Assets with CIA ratings (I dimension) | Art. 13 |
| Availability protection | Assets with CIA ratings (A dimension) | Art. 13 |
| Attack surface documentation | Attack paths documented | Art. 13 |
| Security monitoring | Audit trail exists | Art. 13 |
| Vulnerability remediation capability | Risk treatment decisions exist | Art. 13 |
| Cybersecurity risk assessment | TARA report generated | Annex VII |

**Remaining gaps the user must fill manually:**

| CRA Requirement | Why Not Auto-Filled | Article |
|-----------------|---------------------|---------|
| SBOM | Build-time artifact, not TARA | Art. 13(6) |
| Secure default configuration | Product-specific evidence | Art. 13 |
| Data minimization | Privacy assessment | Art. 13 |
| 24h vulnerability reporting | Organizational process | Art. 14(4) |
| Public disclosure policy | Organizational process | Art. 14 |
| Vulnerability handling process | Organizational process | Art. 14 |
| Security testing program | Organizational process | Art. 14 |
| Support period declaration | Business decision | Art. 13(8) |
| EU Declaration of Conformity | Legal document | Annex V |
| CE marking | Physical marking | Art. 28 |

### Path B — Product Has No TARA (Legacy Product)

The product is old. No assets, no scenarios, no risk ratings in QuickTARA. Maybe no source code. The system handles this differently.

**Legacy product classification (Buckets):**

| Bucket | Description | CRA Strategy |
|--------|-------------|--------------|
| A — Maintainable | Source available, can patch | Full compliance path |
| B — Partial | Some artifacts, limited patch | Retrofitted compliance + compensating controls |
| C — Orphaned | No source, no patch path | Art. 5(3) compensating controls or EoSS |

**What the system does for legacy products:**

1. Asks bucket classification questions (source available? build system? patch path?)
2. Assigns bucket A/B/C
3. For Bucket A: recommends creating a lightweight TARA in QuickTARA (item def + top 10 threats)
4. For Bucket B: tracks reconstructed SBOM, compensating controls, partial TARA
5. For Bucket C: tracks EoSS date, migration path, compensating control specifications, Technical Justification Memo (Art. 5(3))

**Legacy-specific CRA requirements:**

| Requirement | Bucket A | Bucket B | Bucket C |
|-------------|----------|----------|----------|
| TARA | Create lightweight | Create minimal | Risk acceptance only |
| SBOM | Generate from source | Reconstruct via binary analysis | Reconstruct via binary analysis |
| Patching | Standard updates | Where feasible | Compensating controls (Art. 5(3)) |
| Support period | Declare | Declare | Publish EoSS date |
| Vulnerability handling | Full PSIRT | Full PSIRT | PSIRT + compensating control specs |
| Conformity assessment | Standard | Standard | Art. 5(3) documentation |

---

## 3. CRA Classification Questionnaire

Based on CRA Annex III and the product-classification.md decision matrix.

**Questions (6 total):**

1. Does the product contain a microcontroller or microprocessor?
2. Does the product perform security-related functions (crypto, auth, secure boot)?
3. Is the product designed to be tamper-resistant?
4. Is the product intended for industrial or automotive use?
5. Does the product contain an HSM or secure cryptoprocessor?
6. Could the product be marketed independently (not only vehicle-integrated)?

**Scoring:**

| Yes Count | Classification |
|-----------|---------------|
| 0-1 | Default |
| 2-3 | Important Class I |
| 4-5 | Important Class II |
| 6 (with HSM) | Critical |

**Automotive exception check:**

If the product is exclusively integrated into type-approved vehicles by a single OEM under UN R155, CRA may not apply (lex specialis). The questionnaire includes this check:

- Is this product sold exclusively to one OEM for vehicle type-approval?
- If yes: flag as "potentially excluded under lex specialis" but recommend compliance anyway

**Classification output includes:**

- CRA category (Default / Class I / Class II / Critical)
- Conformity assessment type (self-assessment / internal + standards / third-party / EUCC)
- Compliance deadline (Aug 2026 for Class I, Oct 2026 for Class II, Dec 2027 for Default)
- Estimated assessment cost range

---

## 4. Master Requirement List

18 requirements derived from CRA Annex I Parts I and II, plus documentation.

### Part I — Product Security (9 requirements)

| ID | Requirement | Article | Category |
|----|-------------|---------|----------|
| CRA-01 | Secure by default configuration | Art. 13 | Technical |
| CRA-02 | Access control and authentication | Art. 13 | Technical |
| CRA-03 | Data confidentiality (encryption) | Art. 13 | Technical |
| CRA-04 | Data integrity protection | Art. 13 | Technical |
| CRA-05 | Data minimization | Art. 13 | Technical |
| CRA-06 | Availability and resilience | Art. 13 | Technical |
| CRA-07 | Attack surface limitation | Art. 13 | Technical |
| CRA-08 | Security monitoring and logging | Art. 13 | Technical |
| CRA-09 | Vulnerability remediation capability | Art. 13 | Technical |

### Part II — Vulnerability Handling (5 requirements)

| ID | Requirement | Article | Category |
|----|-------------|---------|----------|
| CRA-10 | Software Bill of Materials (SBOM) | Art. 13(6) | Process |
| CRA-11 | Vulnerability handling process | Art. 14 | Process |
| CRA-12 | Security testing program | Art. 14 | Process |
| CRA-13 | Public vulnerability disclosure | Art. 14 | Process |
| CRA-14 | 24-hour vulnerability reporting | Art. 14(4) | Process |

### Documentation (4 requirements)

| ID | Requirement | Article | Category |
|----|-------------|---------|----------|
| CRA-15 | Technical documentation (Annex VII) | Art. 28 | Documentation |
| CRA-16 | EU Declaration of Conformity | Annex V | Documentation |
| CRA-17 | User information and instructions | Art. 13 | Documentation |
| CRA-18 | CE marking | Art. 28 | Documentation |

---

## 5. Data Model

### Table: `cra_assessments`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | FK to product_scopes |
| classification | ENUM | default, class_i, class_ii, critical |
| classification_answers | JSON | Questionnaire answers |
| product_type | ENUM | current, legacy_a, legacy_b, legacy_c |
| compliance_deadline | DATE | Based on classification |
| assessment_date | TIMESTAMP | When assessment was created |
| assessor_id | UUID | FK to users |
| status | ENUM | draft, in_progress, complete |
| overall_compliance_pct | INTEGER | Calculated from requirement statuses |
| support_period_end | DATE | Declared support end date |
| eoss_date | DATE | End of security support (legacy) |
| notes | TEXT | General notes |

### Table: `cra_requirement_statuses`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| assessment_id | UUID | FK to cra_assessments |
| requirement_id | VARCHAR | CRA-01 through CRA-18 |
| status | ENUM | not_started, partial, compliant, not_applicable |
| auto_mapped | BOOLEAN | True if filled from existing TARA |
| mapped_artifact_type | VARCHAR | e.g., "damage_scenario", "asset", "attack_path" |
| mapped_artifact_count | INTEGER | Number of linked artifacts |
| owner | VARCHAR | Person responsible |
| target_date | DATE | Target completion |
| evidence_notes | TEXT | Description of evidence |
| evidence_links | JSON | Links to documents/artifacts |
| gap_description | TEXT | What is missing |
| remediation_plan | TEXT | How to close the gap |

### Table: `cra_compensating_controls` (Legacy products only)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| assessment_id | UUID | FK to cra_assessments |
| control_id | VARCHAR | CC-DIAG-001, CC-NET-001, etc. |
| name | VARCHAR | Control name |
| description | TEXT | What it does |
| implementation_status | ENUM | planned, implemented, verified |
| supplier_actions | TEXT | What supplier does |
| oem_actions | TEXT | What OEM must do |
| residual_risk | TEXT | What risk remains |

---

## 6. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/cra/assessments` | Create assessment for a product |
| GET | `/cra/assessments/{id}` | Get assessment with all requirement statuses |
| GET | `/cra/assessments/product/{product_id}` | Get assessment by product |
| PUT | `/cra/assessments/{id}` | Update assessment |
| DELETE | `/cra/assessments/{id}` | Delete assessment |
| POST | `/cra/assessments/{id}/classify` | Run classification questionnaire |
| POST | `/cra/assessments/{id}/auto-map` | Auto-map existing TARA to CRA requirements |
| GET | `/cra/requirements` | Get master requirement list |
| PUT | `/cra/requirements/{status_id}` | Update single requirement status |
| GET | `/cra/compensating-controls/{assessment_id}` | Get compensating controls (legacy) |
| POST | `/cra/compensating-controls` | Add compensating control |
| PUT | `/cra/compensating-controls/{id}` | Update compensating control |

---

## 7. Frontend Pages

### `/cra` — Assessment List

- Shows all products with CRA assessment status
- Card per product: name, classification badge, compliance %, last updated
- Button to create new assessment
- Filter by classification, status, product type

### `/cra/[id]` — Assessment Detail

Two tabs:

**Tab 1: Overview**
- Product name and classification badge (color-coded)
- Compliance deadline with countdown
- Overall compliance percentage bar
- Product type (current / legacy bucket)
- Questionnaire answers summary
- Auto-mapped TARA artifact summary

**Tab 2: Requirements**
- Table of 18 requirements
- Each row: ID, name, status badge, auto-mapped indicator, owner, target date
- Click row to expand: evidence notes, gap description, remediation plan, linked artifacts
- Inline edit for status, owner, date, notes

**Tab 3: Compensating Controls (legacy only)**
- Visible only for legacy_b and legacy_c products
- Table of applied compensating controls
- Add/edit controls with supplier and OEM actions

### `/cra/[id]/classify` — Classification Wizard

- Step-by-step questionnaire (6 questions)
- Each question is a yes/no card
- After answering all: shows classification result with explanation
- Button to confirm and save

---

## 8. Report Section

New file: `api/services/reporting/sections/cra_compliance_section.py`

Adds to PDF report:
- CRA classification and rationale
- Compliance deadline
- Requirements table with status (18 rows)
- Auto-mapped TARA artifacts summary
- Gap summary (what is not yet compliant)
- Compensating controls (if legacy)
- Support period / EoSS declaration

---

## 9. RBAC

| Role | CRA Permissions |
|------|----------------|
| TOOL_ADMIN | Full access |
| ORG_ADMIN | Create/edit assessments for org products |
| ANALYST | Create/edit assessments, update requirement statuses |
| RISK_MANAGER | Approve assessments, edit all fields |
| AUDITOR | Read-only access to all CRA data |
| VIEWER | Read-only access to assigned products |

---

## 10. What We Do NOT Build

- SBOM generation (use Syft, CycloneDX CLI, or binary analysis tools)
- ENISA reporting workflow (organizational process, not a tool feature)
- PSIRT ticketing (use Jira or existing tools)
- CE marking management (physical process)
- Notified body engagement tracking (project management, not TARA)

The module tracks whether these things are done. It does not do them.

---

## 11. Knowledge Base Source

All CRA requirement definitions, classification logic, gap analysis templates, legacy product strategies, and compensating control catalogs are derived from:

| Source File | Used For |
|-------------|----------|
| `CRA/product-classification.md` | Classification questionnaire and scoring |
| `CRA/gap-analysis.md` | 18 requirements with sub-requirements |
| `CRA/technical-requirements.md` | Annex I Part I mapping |
| `CRA/sbom-requirements.md` | SBOM requirement details |
| `CRA/timeline.md` | Compliance deadlines per classification |
| `CRA/legacy-vs-new-products.md` | Path A vs Path B logic |
| `CRA/legacy-product-security-program.md` | Bucket A/B/C classification |
| `CRA/legacy-security-dossier-template.md` | Legacy assessment structure |
| `CRA/compensating-controls-catalog.md` | Pre-approved controls for legacy |
| `eu-compliance/internal/compliance-tracker.md` | Internal gap tracking structure |
| `eu-compliance/internal/legacy-cra-survival-playbook.md` | Legacy compliance strategies (Art. 5(3)) |
| `eu-compliance/external/customer-roadmap.md` | Customer-facing output format |
| `CRA-GAP-ANALYSIS.md` | Article-level requirement mapping |
| `CRA-COMPLIANCE-ROADMAP.md` | Phased roadmap template |
| `EU-COMPLIANCE-MASTER-ANALYSIS.md` | Multi-regulation overview |
| `MachineryRegulation/overview.md` | Machinery Reg overlap (future scope) |
| `DataAct/overview.md` | Data Act overlap (future scope) |

---

## 12. Effort Estimate

| Phase | Work | Days |
|-------|------|------|
| 1. Database tables + migration | 3 tables, indexes, seed data | 1 |
| 2. Classification logic (Python) | Questionnaire scoring, deadline calc | 1 |
| 3. Auto-mapping logic (Python) | Check existing TARA artifacts per product | 1 |
| 4. API routes | 12 endpoints | 2 |
| 5. Frontend: assessment list page | Cards, filters, create button | 1 |
| 6. Frontend: assessment detail page | 3 tabs, inline editing, status badges | 2 |
| 7. Frontend: classification wizard | Step form, result display | 1 |
| 8. Report section | PDF table for CRA status | 1 |
| 9. Testing and integration | End-to-end flow | 1 |
| **Total** | | **11 days** |

---

## 13. Future Scope (Not in v1)

- EU Machinery Regulation module (2023/1230) — similar structure, different requirements
- EU Data Act module (2023/2854) — data access and sharing requirements
- Multi-regulation dashboard — single view across CRA + Machinery + Data Act
- SBOM upload and parsing — accept CycloneDX/SPDX files, link to assessment
- VEX integration — track vulnerability exploitability per SBOM component
- Supplier compliance tracking — track supplier CRA status per component
