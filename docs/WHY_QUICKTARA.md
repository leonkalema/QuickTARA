# How QuickTARA Covers ISO 21434 and the EU Cyber Resilience Act

You do this work by hand. You know what it costs.

Weeks of spreadsheets. Missed clauses. Reviewers asking for evidence you cannot find. The audit date approaches. Your TARA documentation sits incomplete.

ISO/SAE 21434 specifies 12 work products for threat analysis and risk assessment. The EU Cyber Resilience Act (Regulation (EU) 2024/2847) adds 18 mandatory requirements, a conformity workflow, and three reporting deadlines. Most teams track these across separate files. They copy between tools. They lose traceability. They fail audits.

QuickTARA produces all of it from one system.

---

## ISO 21434 Coverage

ISO 21434 Clause 9 defines a sequence. Each step requires traceable artifacts.

1. Define the item and its boundaries (§8.3)
2. Identify assets and their security properties (§9.3)
3. Rate impact across Safety, Financial, Operational, and Privacy dimensions (§9.4)
4. Identify threat scenarios that cause those impacts (§9.5)
5. Rate attack feasibility using a 5-level scale (§9.6)
6. Calculate risk by combining impact and feasibility (§9.7)
7. Document treatment decisions with justification (§9.8)
8. Maintain an audit trail with sign-offs (§14)

Most tools handle some of these steps. QuickTARA handles all eight.

---

## EU Cyber Resilience Act Coverage

The CRA applies to products with digital elements placed on the EU market after 11 December 2027. It sets technical requirements, conformity obligations, and incident reporting rules.

QuickTARA maps to the CRA as follows.

**Product classification.** The wizard determines whether your product is Default, Class I, Class II, Critical, or an Art. 24 open-source steward. Each classification maps to a conformity module: A, B+C, H, or security attestation. The automotive exclusion under Art. 2(2)(c) is flagged when it applies.

**18 CRA requirements.** All requirements cite exact Annex I section numbers per Regulation (EU) 2024/2847. The system auto-maps your existing TARA artefacts to each requirement and shows per-requirement status, evidence, owner, and gap severity.

**Conformity workflow (Art. 13).** A 7-step checklist tracks the procedural compliance acts: conformity assessment, Declaration of Conformity, CE marking, EU central database registration (Art. 31), 10-year documentation retention (Art. 23(1)), post-market surveillance plan, and EOSS publication.

**SBOM ingestion (Art. 13(6)).** Upload CycloneDX or SPDX files. The system parses components, versions, licenses, and hashes, then maps them to CRA-10.

**Incident reporting (Art. 14).** Three deadline clocks track the 24-hour early warning, 72-hour incident report, and 14-day final report. Export is formatted for the ENISA Single Reporting Platform.

**Annex II checklist.** All 9 mandatory user-information items are tracked. The support-period item auto-derives from your stored EOSS date.

**Annex VII technical documentation.** Seven-section technical documentation assembles from live TARA data. Export as Markdown for Pandoc conversion to PDF or DOCX.

---

## The Numbers

| Metric | Value |
|--------|-------|
| ISO 21434 clauses covered | §8.3, §8.5, §9.3-9.8, §10.4, §14 |
| CRA requirements | 18 (9 Annex I Part I, 5 Part II, 4 documentation) |
| SFOP impact dimensions | 4 (Safety, Financial, Operational, Privacy) |
| Feasibility levels | 5 (Very Low to Very High) |
| Risk matrix cells | 20 (4 impacts x 5 feasibilities) |
| CRA conformity checklist steps | 7 |
| Annex II user-information items | 9 |
| Incident reporting deadlines | 3 (24h, 72h, 14d) |

---

## Who Uses This

Security engineers who write TARA reports.

Risk managers who approve them.

Auditors who verify compliance.

OEMs who require suppliers to demonstrate ISO 21434 conformance.

Tier-1 suppliers whose ECUs, gateways, and sensors must meet both ISO 21434 and CRA requirements.

---

## What Makes It Different

**No cloud dependency.** The system runs on your network. Your data stays on your machines.

**No vendor lock-in.** Export reports as PDF. Export data as JSON. The database is SQLite, MySQL, or PostgreSQL. You own your artifacts.

**No training required.** The workflow matches the standard. If you understand ISO 21434, you understand the tool.

**Auditable calculations.** The risk matrix is visible. The clause mappings are visible. Auditors can inspect exactly how risk values derive from inputs.

---

## Can You Trust the Outputs?

The impact rating uses a 4-point scale: Negligible, Moderate, Major, Severe. This matches §9.4.

The feasibility rating uses a 5-point scale: Very Low, Low, Medium, High, Very High. This matches §9.6.

The risk matrix combines these into five risk levels: Negligible, Low, Medium, High, Critical. This matches §9.7.

The overall impact derives from the worst case across all four SFOP dimensions. This matches the standard's aggregation method.

You can read the source code. The file `core/sfop_risk_calculator.py` implements this logic. The file `core/iso21434_mapping.py` maps each artifact type to its clause references.

---

## One Recommendation

Validate against a real project before deploying across a team. The calculations match the standard. The question is whether the outputs match your specific OEM's expectations for format and detail.

Run a pilot. Show the report to your auditor. Get feedback. Adjust as needed.

The tool handles the compliance mechanics. You handle the domain judgment.
