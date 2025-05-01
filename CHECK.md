# QuickTARA – Automotive TARA Checklist

This checklist walks through a **complete Threat Analysis & Risk Assessment (TARA)** process compliant with ISO/SAE 21434 and aligned with UNECE R155.

> Treat this file as a living document. Tick off items (`[x]`) as you complete them or add notes under each step.

---

## 0. Preparation

- [ ] **Define Scope & Objectives**  
  Identify vehicle platform, subsystems, features, and lifecycle phases in scope.
- [ ] **Gather Standards & References**  
  - ISO/SAE 21434:2021 (see `data/ISO_SAE_21434_2021_EN.pdf`)  
  - UNECE R155 & R156 regs (see `data/R155e.pdf`, `data/R156e.pdf`)  
  - ISO 26262-6 (functional safety interface; see `data/ISO-26262-6-2018.pdf`)
- [ ] **Set Up Tooling**  
  QuickTARA backend (FastAPI) + frontend (Svelte) running locally.  
  DB seeded with system components, connections, and safety attributes.

---

## 1. Item Definition (ID)

| Task | QuickTARA Support | Status |
|------|------------------|--------|
| Define the **Item** (vehicle feature/function) | `components` API + Component Manager UI | [ ] |
| List **Operational Scenarios & Use Cases** | Free-text notes or import CSV | [ ] |
| Identify **Assets & Stakeholders** | Asset model TBD | [ ] |

---

## 2. Cybersecurity Goals (CSG)

| Step | Action | Responsible Artefact / Module | Status |
|------|--------|-------------------------------|--------|
| 2.1 | Import **Safety Goals** (from ISO-26262 HARA) | Attach PDF excerpts or CSV to `data/` | [ ] |
| 2.2 | Map Safety Goals → **Assets** | Asset list (TBD) | [ ] |
| 2.3 | Derive **Cybersecurity Goals** (CSG) | `core/cybersecurity_goals.py` | [ ] |
| 2.4 | Assign **CIAA properties** (Conf., Integ., Avail., Auth.) | CSG model fields | [ ] |
| 2.5 | Review & Approve CSGs with stakeholders | Meeting minutes | [ ] |

---

## 3. System Decomposition (SD)

| Step | Action | QuickTARA Feature | Status |
|------|--------|------------------|--------|
| 3.1 | Create / import **Components** | `POST /api/components` or CSV import | [ ] |
| 3.2 | Specify **Interfaces** & **Protocols** | Component `interfaces` field | [ ] |
| 3.3 | Define **Trust Zones** & physical **Location** | Component attributes | [ ] |
| 3.4 | Link **Connections** (`connected_to`) | Component graph builder | [ ] |
| 3.5 | Validate graph integrity (no orphans / loops) | `ComponentService.validate_graph()` | [ ] |

---

## 4. Threat & Vulnerability Identification (TVI)

| Step | Action | QuickTARA Tooling | Status |
|------|--------|------------------|--------|
| 4.1 | Run **STRIDE** analysis per component | `core/stride_analysis.py` | [ ] |
| 4.2 | Document **Assumptions** & **Constraints** | Attack Path form fields | [ ] |
| 4.3 | Import **Known Vulnerabilities** (CVE/CWE) | `db/threat_catalog.py`; Vuln service | [ ] |
| 4.4 | Perform **Automated Scan** (optional) | `vulnerability_service.scan()` | [ ] |
| 4.5 | Map findings to Components & Interfaces | Vulnerability model relations | [ ] |
| 4.6 | Review & deduplicate threats | Threat dashboard | [ ] |

---

## 5. Attack Path Analysis (APA)

| Step | Action | Endpoint / UI | Status |
|------|--------|--------------|--------|
| 5.1 | Select **Analysis Scenario** (component set) | Attack Path Manager UI | [ ] |
| 5.2 | Configure **Depth**, **Entry / Target IDs** (if needed) | Form inputs | [ ] |
| 5.3 | Submit **POST /api/attack-paths** | `AttackPathService.generate()` | [ ] |
| 5.4 | Inspect **Paths & Chains** list | AttackPathList + Visualization | [ ] |
| 5.5 | Flag **High-Risk** paths (>= threshold) | Service auto-label | [ ] |
| 5.6 | Iterate with new constraints until satisfied | Repeat 5.1-5.5 | [ ] |

---

## 6. Risk Assessment (RA)

| Step | Action | Module | Status |
|------|--------|--------|--------|
| 6.1 | Quantify **Likelihood** per threat | `risk_service.calculate_likelihood()` | [ ] |
| 6.2 | Quantify **Impact** (safety, financial, privacy) | Same service | [ ] |
| 6.3 | Compute **Risk Level** (matrix) | `risk_service.risk_matrix()` | [ ] |
| 6.4 | Decide **Treatment** (mitigate, transfer, accept) | Risk record field | [ ] |
| 6.5 | Document **Residual Risk** justification | CHECK.md updates | [ ] |

---

## 7. Verification & Validation (VV)

| Step | Action | Artefact | Status |
|------|--------|----------|--------|
| 7.1 | Trace CSG → Requirements → Tests | Traceability matrix | [ ] |
| 7.2 | Plan **Pen-Test / Fuzzing** | Security test plan | [ ] |
| 7.3 | Execute tests & record findings | Test reports | [ ] |
| 7.4 | Verify risk mitigations effective | Re-run Risk Assessment | [ ] |

---

## 8. Documentation & Release (DR)

| Step | Action | Tool / Evidence | Status |
|------|--------|-----------------|--------|
| 8.1 | Generate **TARA Report** PDF/JSON | `ReportService.export()` | [ ] |
| 8.2 | Store artefacts in **BOM / evidence repo** | External repo | [ ] |
| 8.3 | Obtain **Stakeholder Sign-off** | Signed minutes | [ ] |
| 8.4 | Release to production & handover | Release checklist | [ ] |

---

## References (in `data/`)

- ISO/SAE 21434:2021  
- UNECE R155 / R156  
- ISO 26262-6:2018

---

> **Note**: tick the boxes as you progress and expand with project-specific details.
