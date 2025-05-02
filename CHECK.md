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

## 1. Scope Definition (ID)

| Step | Action | Tool / Artefact | Depends On | Status |
|------|--------|-----------------|------------|--------|
| 1.1 | Define **Item** (vehicle function) | Component Manager UI | Preparation | [ ] |
| 1.2 | List **Operational Scenarios** | Use-case docs, CSV import | 1.1 | [ ] |
| 1.3 | Identify **Assets & Stakeholders** | Asset list | 1.1 | [ ] |

---

## 2. Component Modelling (SD)

| Step | Action | QuickTARA Feature | Depends On | Status |
|------|--------|------------------|------------|--------|
| 2.1 | Create / import **Components** | `POST /api/components` or CSV | 1.x | [ ] |
| 2.2 | Add **Interfaces & Protocols** | Component `interfaces` | 2.1 | [ ] |
| 2.3 | Define **Trust Zones & Location** | Component attrs | 2.1 | [ ] |
| 2.4 | Link **Connections** | `connected_to` graph | 2.1 | [ ] |
| 2.5 | Validate graph integrity | `ComponentService.validate_graph()` | 2.4 | [ ] |

---

## 3. Threat Analysis (STRIDE / HEAVENS)

| Step | Action | Module | Depends On | Status |
|------|--------|--------|------------|--------|
| 3.1 | Run **STRIDE** per component/interface | `core/stride_analysis.py` | 2.x | [ ] |
| 3.2 | Review generated **Threat Scenarios** | Threat dashboard | 3.1 | [ ] |
| 3.3 | Capture **Assumptions & Constraints** | Attack Path form fields | 3.2 | [ ] |

---

## 4. Vulnerability Analysis

| Step | Action | Tooling | Depends On | Status |
|------|--------|---------|------------|--------|
| 4.1 | Import **Known CVE/CWE** data | `db/threat_catalog.py` | 2.x | [ ] |
| 4.2 | Run **Automated Scans** (SAST/DAST) | `vulnerability_service.scan()` | 2.1 | [ ] |
| 4.3 | Map vulns to components & interfaces | Vulnerability relations | 4.1/4.2 | [ ] |
| 4.4 | Deduplicate & triage vulnerabilities | Vuln dashboard | 4.3 | [ ] |

---

## 5. Attack Path Analysis (APA)

| Step | Action | Endpoint / UI | Depends On | Status |
|------|--------|--------------|------------|--------|
| 5.1 | Select **Component Set** / Scenario | Attack Path Manager UI | 2.x, 3.x, 4.x | [ ] |
| 5.2 | Configure **Depth / Entry / Target** | Form inputs | 5.1 | [ ] |
| 5.3 | Submit **POST /api/attack-paths** | `AttackPathService.generate()` | 5.2 | [ ] |
| 5.4 | Review **Paths & Chains** | Visualizer | 5.3 | [ ] |
| 5.5 | Iterate with constraints / updated vulns | Repeat cycle | 5.4 | [ ] |

---

## 6. Risk Assessment (RA)

| Step | Action | Module | Depends On | Status |
|------|--------|--------|------------|--------|
| 6.1 | Calculate **Likelihood** | `risk_service.calculate_likelihood()` | 5.4 | [ ] |
| 6.2 | Calculate **Impact** | `risk_service` | 5.4 | [ ] |
| 6.3 | Determine **Risk Level** | matrix | 6.1/6.2 | [ ] |
| 6.4 | Decide **Treatment** | Risk record | 6.3 | [ ] |
| 6.5 | Document **Residual Risk** | CHECK.md | 6.4 | [ ] |

---

## 7. Verification & Validation (VV)

| Step | Action | Artefact | Depends On | Status |
|------|--------|----------|------------|--------|
| 7.1 | Map CSG → Requirements → Tests | Traceability | 6.x | [ ] |
| 7.2 | Plan **Pen-Tests / Fuzzing** | Test plan | 6.x | [ ] |
| 7.3 | Execute tests & collect evidence | Test reports | 7.2 | [ ] |
| 7.4 | Verify mitigations effective | Re-run RA | 7.3 | [ ] |

---

## 8. Documentation & Release (DR)

| Step | Action | Evidence | Depends On | Status |
|------|--------|----------|------------|--------|
| 8.1 | Generate **TARA Report** | `ReportService.export()` | 6.x | [ ] |
| 8.2 | Store artefacts in BOM | Repo / SharePoint | 8.1 | [ ] |
| 8.3 | Obtain **Stakeholder Sign-off** | Signed minutes | 8.2 | [ ] |
| 8.4 | Release & handover | Release checklist | 8.3 | [ ] |

---

## References (in `data/`)

- ISO/SAE 21434:2021  
- UNECE R155 / R156  
- ISO 26262-6:2018

---

> **Note**: tick the boxes as you progress and expand with project-specific details.
