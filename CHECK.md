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

- [ ] Derive **Cybersecurity Goals** from safety goals & assets.  
  Use QuickTARA *Cybersecurity Goal* module (`core/cybersecurity_goals.py`).
- [ ] Map each CSG to: confidentiality / integrity / availability / authenticity.

---

## 3. System Decomposition (SD)

- [ ] Model **Components** (ECUs, sensors, gateways) with interfaces, trust zones, ASIL levels.  
  Use *Components* API or CSV import.
- [ ] Model **Connections** (`connected_to` field) to create attack graph.
- [ ] Assign **Trust Zones** (`trust_zone` attr) and physical locations.

---

## 4. Threat & Vulnerability Identification (TVI)

| Task | QuickTARA Support |
|------|------------------|
| Apply STRIDE or HEAVENS to each component/interface | `core/stride_analysis.py` |
| Import known CVE/CWE vulnerabilities | `db/threat_catalog.py` + Vuln services |
| Record Assumptions & Constraints | Attack Path form → `assumptions`, `constraints` fields |

---

## 5. Attack Path Analysis (APA)

1. **Select Component Set** in UI or via API.  
2. **Run** `POST /api/attack-paths` with optional depth/entry/target parameters.  
3. **Review Results**:  
   - Entry points, targets, paths, chains, high-risk flags.  
   - Export JSON or visualise in *AttackPathVisualizer*.
4. **Iterate** with additional scenarios or constraints until coverage is adequate.

---

## 6. Risk Assessment (RA)

- [ ] Use QuickTARA risk model (`core/risk_review.py`) to score likelihood × impact.
- [ ] Document **Residual Risk** and justification.
- [ ] Decide **Risk Treatment**: accept, mitigate, transfer.

---

## 7. Verification & Validation (VV)

- [ ] Trace TARA outputs to **requirements** and **test cases**.
- [ ] Plan **Penetration Testing** or code reviews.

---

## 8. Documentation & Release (DR)

- [ ] Export **TARA Report** (`api/reports`, `ReportService`).
- [ ] Archive evidence in BOM.
- [ ] Obtain stakeholder approval.

---

## References (in `data/`)

- ISO/SAE 21434:2021  
- UNECE R155 / R156  
- ISO 26262-6:2018

---

> **Note**: Update this checklist as QuickTARA features grow (e.g., automated TVI, CWE mapping, compliance dashboards).
