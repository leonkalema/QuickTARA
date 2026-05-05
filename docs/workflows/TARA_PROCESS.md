# The TARA Process in QuickTARA

This guide covers all 15 steps of a complete Threat Analysis and Risk Assessment (TARA). The process follows ISO/SAE 21434 Clause 9 and satisfies UNECE R155 requirements. Each step lists what you need before you start and what you produce when you finish.

---

## Step 1: Item Definition

**What you need:** A system description, stakeholder requirements, and the vehicle architecture.

**What you produce:** A written item description with clear boundaries, a component list, and the interfaces between them.

**Next:** Step 2

---

## Step 2: Asset Identification

**What you need:** The item definition from Step 1 and supporting system documentation.

**What you produce:** An asset inventory. Each asset has rated security properties: Confidentiality, Integrity, Availability, Authenticity, Authorization, and Non-repudiation.

**Next:** Step 3

---

## Step 3: Damage Scenario Identification

**What you need:** The asset list with security properties from Step 2.

**What you produce:** A set of damage scenarios. Each one describes what could happen if a security property is violated.

**Next:** Step 4

---

## Step 4: Impact Rating

**What you need:** The damage scenarios and any system safety requirements.

**What you produce:** An impact rating for each damage scenario across four dimensions: Safety, Financial, Operational, and Privacy (SFOP). Each dimension is rated Negligible, Moderate, Major, or Severe.

**Next:** Step 5

---

## Step 5: Threat Scenario Identification

**What you need:** The asset list, damage scenarios, and access to the threat catalog.

**What you produce:** Specific threat scenarios. Each one describes how an attacker could cause a damage scenario.

**Next:** Step 6

---

## Step 6: Attack Path Analysis

**What you need:** The threat scenarios and the system architecture, including entry points.

**What you produce:** Attack paths. Each path shows the step-by-step route an attacker takes through the system.

**Next:** Step 7

---

## Step 7: Attack Feasibility Rating

**What you need:** Attack paths, known vulnerability information, and attacker profile assumptions.

**What you produce:** A feasibility rating for each attack path. QuickTARA uses five factors: elapsed time, expertise, system knowledge, window of opportunity, and equipment.

**Next:** Step 8

---

## Step 8: Risk Determination

**What you need:** Impact ratings from Step 4 and feasibility ratings from Step 7.

**What you produce:** A risk value for each threat scenario. QuickTARA uses the ISO 21434 4x5 risk matrix with worst-case SFOP aggregation.

**Next:** Step 9

---

## Step 9: Risk Treatment Decision

**What you need:** Risk values and your organisation's risk acceptance criteria.

**What you produce:** A treatment decision for each unacceptable risk: Mitigate, Accept, Avoid, or Transfer. Each decision requires a written justification.

**Next:** Step 10

---

## Step 10: Cybersecurity Goals Definition

**What you need:** Treatment decisions and the linked damage scenarios.

**What you produce:** Specific cybersecurity goals, each mapped to one or more risks that require mitigation.

**Next:** Step 11

---

## Step 11: Cybersecurity Claims

**What you need:** The cybersecurity goals from Step 10.

**What you produce:** Claims and arguments showing how you will verify each security goal.

**Next:** Step 12

---

## Step 12: Cybersecurity Concept Development

**What you need:** Goals, claims, and the system architecture.

**What you produce:** Security requirements allocated to specific system elements.

**Next:** Step 13

---

## Step 13: Documentation and Residual Risk Acceptance

**What you need:** All outputs from Steps 1 through 12, plus remaining risk information.

**What you produce:** A complete TARA report with formal acceptance of residual risks.

**Next:** Step 14

---

## Step 14: Review and Validation

**What you need:** The complete TARA documentation.

**What you produce:** A verified, approved TARA report with stakeholder sign-offs.

**Next:** Step 15

---

## Step 15: Continuous Monitoring

**What you need:** The approved TARA and a change management process.

**What you produce:** A process for triggering TARA updates when the product changes, plus a schedule for periodic reassessment.

---

Each step builds on the last. The full chain runs from item definition to continuous monitoring, with a traceable record at every stage.
