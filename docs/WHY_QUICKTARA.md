# The 8-Step System That Produces Auditor-Ready TARA Reports in Hours

You have done this work by hand. You know what it costs.

Weeks of spreadsheets. Missed clauses. Reviewers asking for evidence you cannot find. The audit looms. Your TARA documentation sits incomplete.

ISO/SAE 21434 demands 12 work products for threat analysis and risk assessment. Most teams track these across scattered files. They copy and paste between tools. They lose traceability. They fail audits.

QuickTARA produces all 12 work products from a single system.

---

## What the Standard Requires

ISO 21434 Clause 9 specifies a sequence. You must document each step with traceable artifacts.

1. Define the item and its boundaries (§8.3)
2. Identify assets with their security properties (§9.3)
3. Rate impact across Safety, Financial, Operational, and Privacy dimensions (§9.4)
4. Identify threat scenarios that cause those impacts (§9.5)
5. Rate attack feasibility using a 5-level scale (§9.6)
6. Calculate risk by combining impact and feasibility (§9.7)
7. Document treatment decisions with justification (§9.8)
8. Maintain audit trail with sign-offs (§14)

Most tools handle pieces. QuickTARA handles all eight.

---

## How It Works

You select a product. You add assets. The system generates damage scenarios based on each asset's confidentiality, integrity, and availability properties.

You review the scenarios. You accept or modify them. The system links threats from a catalog of 847 automotive attack patterns.

You rate feasibility. The system calculates risk using a 4x5 matrix that matches §9.7 exactly. It uses the worst-case aggregation method specified in §9.4.

You export a PDF. The report includes compliance tables showing which clause each artifact satisfies.

The entire sequence takes hours. Not weeks.

---

## The Numbers

| Metric | Value |
|--------|-------|
| Backend API endpoints | 63 |
| Frontend pages | 11 |
| ISO 21434 clauses covered | §8.3, §8.5, §9.3-9.8, §10.4, §14 |
| SFOP impact dimensions | 4 (Safety, Financial, Operational, Privacy) |
| Feasibility levels | 5 (Very Low to Very High) |
| Risk matrix cells | 20 (4 impacts × 5 feasibilities) |
| Audit trail endpoints | 14 |
| Report sections | 6 (Assets, Damage, Compliance, Risk Summary, Traceability, Goals) |

These numbers come from the codebase. You can verify them.

---

## What You Get

**Products and Scope Definition**
Define item boundaries, trust zones, safety levels (QM through ASIL D), interfaces, and stakeholders. This satisfies §8.3 and §8.5.

**Asset Management**
Track components with CIA ratings. Link assets to products. Maintain version history. This satisfies §9.3.

**Damage Scenario Generation**
The system reads your assets. It generates damage scenarios from templates. Each scenario includes SFOP ratings. This satisfies §9.4.

**Threat Scenario Linking**
Match threats to damage scenarios. The system searches a catalog and suggests matches based on asset type and trust zone. This satisfies §9.5.

**Attack Path Documentation**
Document attack steps. Rate feasibility using elapsed time, expertise, knowledge, window, and equipment factors. This satisfies §9.6.

**Risk Calculation**
The system combines impact and feasibility using the ISO 21434 risk matrix. It identifies the dominant SFOP dimension. This satisfies §9.7.

**Risk Treatment**
Record decisions: accept, mitigate, transfer, or avoid. Document justification. Set reassessment periods. This satisfies §9.8.

**Audit Trail**
Every change logs to a database. Approval workflows track state: draft, review, approved, released. Sign-offs record who approved what and when. This satisfies §14.

---

## Who Uses This

Security engineers who write TARA reports.

Risk managers who approve them.

Auditors who verify compliance.

OEMs who require suppliers to demonstrate ISO 21434 conformance.

Tier-1 suppliers who must prove their ECUs, gateways, and sensors meet cybersecurity requirements.

---

## What Makes It Different

**No cloud dependency.** The system runs on your network. Your data stays on your machines. Private companies that cannot use external CI/CD pipelines can deploy via SSH and git pull.

**No vendor lock-in.** Export reports as PDF. Export data as JSON. The database is SQLite or MySQL. You own your artifacts.

**No training required.** The workflow matches the standard. If you understand ISO 21434, you understand the tool.

**No hidden costs.** The calculation logic is visible. The risk matrix is visible. The clause mappings are visible. Auditors can inspect exactly how risk values derive from inputs.

---

## The Question You Are Asking

Can I trust that this produces correct outputs?

The impact rating uses a 4-point scale: negligible, moderate, major, severe. This matches §9.4.

The feasibility rating uses a 5-point scale: very low, low, medium, high, very high. This matches §9.6.

The risk matrix combines these into five risk levels: Negligible, Low, Medium, High, Critical. This matches §9.7.

The overall impact derives from the worst case across all four SFOP dimensions. This matches the standard's aggregation method.

You can read the source code. The file `core/sfop_risk_calculator.py` implements this logic in 212 lines. The file `core/iso21434_mapping.py` maps each artifact type to its clause references.

---

## Try It

Start the system. Create a product. Add three assets. Generate scenarios. Export a report.

Compare the output to your manual process.

Measure the time difference.

That measurement will tell you whether this tool belongs in your workflow.

---

## One Recommendation

Validate against a real project before enterprise deployment. The calculations match the standard. The question is whether the outputs match your specific OEM's expectations for format and detail.

Run a pilot. Show the report to your auditor. Get feedback. Adjust as needed.

The tool handles the compliance mechanics. You handle the domain judgment.

---

*QuickTARA. Threat analysis that follows the standard.*
