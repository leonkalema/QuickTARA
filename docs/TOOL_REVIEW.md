# QuickTARA — Honest Tool Review

> Reviewed: February 2026
> Reviewer: AI pair programmer (after full codebase audit)
> Status: Prototype / Early MVP

---

## What's Genuinely Good

### 1. Correct TARA Workflow
The tool models the full TARA pipeline: **Scoping → Assets → Damage Scenarios → Threat Scenarios → Risk Assessment → Risk Treatment**. This maps correctly to ISO/SAE 21434's work product flow. Most competing tools get this wrong or skip steps.

### 2. Feasibility Ratings Use the Right Parameters
The attack path feasibility rating uses: elapsed time, specialist expertise, knowledge of target, window of opportunity, and equipment. This follows the **attack potential approach from ISO/SAE 21434 Annex G**. Non-trivial to get right.

### 3. Damage Scenarios and Threat Scenarios Are Separate Entities
This is correct per 21434. Many tools conflate damage scenarios with threat scenarios, but QuickTARA properly separates them — damage scenarios describe what can go wrong (impact), threat scenarios describe how (attack).

### 4. Self-Hosted Architecture
OEMs and Tier 1 suppliers won't put TARA data on third-party cloud infrastructure. Self-hosted (local, LAN, or on-prem VPS) is the right architecture for this domain. Docker support and the office-deploy script reinforce this.

### 5. RBAC with Org/Department Scoping
Multi-tenant role-based access control with organizations (departments), products, and role hierarchy (Tool Admin, Org Admin, Risk Manager, Analyst, Viewer) makes sense for team use across multiple product lines.

### 6. Comprehensive Data Model
The database schema covers: components, vulnerabilities with CWE/CVE mappings, attack paths, review decisions, risk frameworks, damage scenarios, threat scenarios, and risk treatment. The relational model is solid and extensible.

---

## Where It Needs Work

### 1. The Analysis Engine Is Keyword Matching, Not Real Analysis

**File:** `core/quicktara.py` — `match_threats_to_component()`, `core/threat_analysis.py` — `analyze_impact_categories()`

The threat matching does `string.lower() in name.lower()` substring matching. Impact scoring counts keyword hits in descriptions and normalizes to a 1-5 scale. This is fragile:
- Will miss real threats that don't use expected keywords
- Will flag irrelevant threats based on coincidental word overlap
- No automotive security engineer would trust these outputs without manually verifying every result

**Recommendation:** Replace keyword matching with structured threat-to-component mapping using a proper ontology (component type + interface type + trust zone → applicable threats). Consider integrating MITRE ATT&CK for ICS or building an automotive-specific threat knowledge base.

### 2. Only 5 Hardcoded Automotive Threats

**File:** `core/threat_analysis.py` — `AUTOMOTIVE_THREATS`

The built-in automotive threat catalog contains only:
- CAN Injection
- ECU Firmware Tampering
- Sensor Data Manipulation
- Diagnostic Interface Exploit
- Gateway Compromise

Real automotive TARA needs coverage of: V2X communications, OTA update compromise, telematics unit attacks, ADAS/AD sensor spoofing (LiDAR, radar, camera), key fob relay attacks, infotainment system compromise, cellular modem exploits, HSM bypass, supply chain compromise, charging infrastructure (for EVs), etc.

CAPEC CSV loading helps but CAPEC is generic IT threat data — not automotive-specific.

**Recommendation:** Build an automotive threat catalog with 50-100+ entries organized by attack surface (in-vehicle network, external interfaces, sensors, telematics, V2X, diagnostics, OTA). Map each to STRIDE categories, relevant component types, and applicable standards.

### 3. Risk Calculations Are Oversimplified

**File:** `core/risk_acceptance.py` — `calculate_risk_severity()`

Current approach: `risk_score = max_impact × likelihood`, mapped to severity thresholds.

Real ISO/SAE 21434 risk assessment uses:
- **Separate SFOP impact dimensions** (Safety, Financial, Operational, Privacy) with independent ratings
- **Attack feasibility** based on attack potential (the feasibility rating in the UI is good, but isn't integrated into the core risk calculation)
- A **risk matrix** combining impact and feasibility into risk levels

The frontend risk-assessment page has the feasibility piece, but the impact side is flattened to a single max value.

**Recommendation:** Implement proper SFOP impact rating per damage scenario, combine with attack feasibility per threat scenario to produce per-dimension risk values. Support configurable risk matrices.

### 4. Compliance Mappings Are Shallow

**Files:** `core/compliance_mappings.py`

ISO 26262 and UN R155 references are one-line clause descriptions (e.g., "Part 4-7: Hardware-software interface specification and verification"). This is a reference card, not a compliance engine.

Missing:
- Full requirement text and context
- Evidence templates for each requirement
- Gap analysis (what's covered vs what's not)
- Traceability from threats → requirements → controls → evidence
- **ISO/SAE 21434 is THE automotive cybersecurity standard and is not explicitly mapped** — the concepts exist in the tool but the standard's clause structure isn't surfaced to users

**Recommendation:** Add ISO/SAE 21434 clause mapping as a first-class feature. Provide traceability matrices and evidence checklists per clause.

### 5. No Auto-Generation in the Web UI

This is the **single biggest UX gap**. After defining a product and its assets, there's no "Generate Threats" button that auto-creates damage scenarios and threat scenarios based on asset properties (type, interfaces, trust zone, CIA requirements).

Users must manually create every damage scenario and every threat scenario. For a tool called "Quick" TARA, this is the single biggest miss.

**Recommendation:**
- Add "Auto-Generate Damage Scenarios" from asset CIA properties
- Add "Auto-Generate Threat Scenarios" from damage scenarios + component attributes
- Allow users to review, edit, accept, or reject auto-generated items
- This is where the "Quick" comes in — scaffolding the TARA, not doing it from scratch

### 6. No Audit Trail or Approval Workflow

For a security tool used in automotive type approval / homologation, you need:
- Change history on all artifacts
- Versioned snapshots of the complete TARA
- Approval chains with sign-off tracking
- Evidence attachments (test reports, pen test results, etc.)
- Export for auditors

The `ReviewDecision` model exists in `db/base.py` but it's basic — no workflow state machine, no multi-level sign-off, no versioning.

**Recommendation:** Add versioned TARA snapshots, approval workflow states (Draft → Review → Approved → Released), and evidence attachment support.

### 7. Frontend Code Quality

- `any[]` typed data scattered throughout (e.g., `let productScopes: any[] = []`, `let assets: any[] = []`)
- Several page components are 400-500+ lines
- Raw `fetch()` calls mixed with API client usage on the same pages
- Some inconsistency between Svelte 4 reactive patterns (`$:`) and Svelte 5 conventions

**Recommendation:** Type all data with proper interfaces, break large page components into smaller feature components, standardize all API calls through the API client layer, and settle on one Svelte version's patterns throughout.

---

## Priority Roadmap

| Priority | Item | Status | Impact |
|----------|------|--------|--------|
| ~~**P0**~~ | ~~Auto-generate damage/threat scenarios from assets~~ | **Done** | Core value prop ("Quick") |
| ~~**P1**~~ | ~~Expand automotive threat catalog to 50+ entries~~ | **Done** (126 entries) | Analysis quality |
| ~~**P1**~~ | ~~ISO/SAE 21434 clause mapping per artifact~~ | **Done** | Compliance credibility |
| ~~**P2**~~ | ~~SFOP impact dimensions in risk calculation~~ | **Done** | Risk accuracy |
| ~~**P2**~~ | ~~Wire feasibility ratings into risk matrix properly~~ | **Done** | Risk accuracy |
| ~~**P3**~~ | ~~Add audit trail and approval workflows~~ | **Done** | Enterprise readiness |
| ~~**P3**~~ | ~~Deep compliance traceability and evidence mgmt~~ | **Done** | Audit readiness |
| **P4** | Frontend refactor (types, component size, patterns) | Open | Maintainability |

---

## Bottom Line

**QuickTARA correctly models the TARA workflow and has a solid data model.** The self-hosted architecture, RBAC, feasibility ratings, and separation of damage/threat scenarios are all done right.

The main gap is that it's currently a **structured database for TARA artifacts** rather than an **analysis engine**. Users do all the thinking; the tool stores what they type. Closing that gap — especially auto-generation of scenarios — would transform it from a form-filling tool into an actual accelerator for automotive cybersecurity engineers.

The bones are good. The intelligence layer is what's missing.
