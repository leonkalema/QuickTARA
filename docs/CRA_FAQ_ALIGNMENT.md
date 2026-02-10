# CRA FAQ Alignment — Issues & Fixes

**Source:** FAQs on the CRA v1.2 (EU Commission, Jan 2026, Regulation (EU) 2024/2847)
**Date:** 10 Feb 2026
**Purpose:** Ensure QuickTARA provides accurate, legally aligned CRA compliance guidance.

---

## 1. Classification Logic — WRONG

**Current:** 6-question scoring quiz in `core/cra_classifier.py` assigns Default/Class I/Class II/Critical based on yes-count thresholds.

**FAQs say (Section 3):** Classification depends on the product's **core functionality** matching categories in **Implementing Regulation (EU) 2025/2392**. Not a point-based questionnaire.

> "a manufacturer should look at the core functionality of its product with digital elements to determine whether that product is an important or critical product"

**Key rules:**
- Integrating an important/critical component does NOT make the host product important/critical.
- Multi-function products classified by CORE functionality, not ancillary functions.
- SOAR with SIEM capabilities ≠ SIEM. Smartphone with OS ≠ operating system.

**Fix:** Replace scoring quiz with a category lookup against actual product categories from the Implementing Regulation. Users select their product's core functionality from a list.

---

## 2. Conformity Assessment Module Mapping — WRONG

**Current output from classifier:**
- Critical → "EUCC certification required"
- Class I deadline → 2026-08-30
- Class II deadline → 2026-10-30

**FAQs say (Section 6):**
- Critical → Module B+C or H mandatory (EUCC only if specifically mandated in future — hasn't happened)
- ALL essential requirements apply from **11 December 2027** for ALL categories
- Only reporting (Article 14) from **11 September 2026**

**Correct conformity assessment rules:**

| Classification | Module A (self-assessment) | Module B+C or H (notified body) |
|---|---|---|
| Default | ✅ Always available | Optional |
| Class I + harmonised standard applied | ✅ Available | Optional |
| Class I without harmonised standard | ❌ | **Mandatory** |
| Class II | ❌ | **Mandatory** |
| Critical | ❌ | **Mandatory** |
| Class I/II free open-source (public tech docs) | ✅ Available | Optional |

**Fix:** Correct the conformity assessment output. Fix all deadlines to 11 Dec 2027. Add Module A/B+C/H recommendation based on classification + standards.

---

## 3. Gap Analysis: Part I vs Part II Distinction — MISSING

**Current:** All 18 requirements shown identically in gap analysis.

**FAQs say (Sections 4.1.3 and 4.3):**
- **Part I** (product properties, CRA-01 to CRA-09): Risk-based. Manufacturer determines which are relevant via risk assessment. Non-applicable ones need justification in technical documentation.
- **Part II** (vulnerability handling, CRA-10 to CRA-14): ALL mandatory throughout support period. No exceptions.
- **Documentation** (CRA-15 to CRA-18): Required for conformity assessment.

**Fix:** Add `annex_part` and `obligation_type` fields to requirement data. Show badges in gap analysis: "Risk-Based" for Part I, "Mandatory" for Part II, "Required" for Documentation.

---

## 4. Support Period — NOT VALIDATED

**Current:** No support period field or validation in assessment setup.

**FAQs say (Section 4.5):**
- Minimum **5 years** support period.
- Less than 5 years ONLY if product expected to be in use less than 5 years.
- If expected use > 5 years, support period must reflect that (hardware, industrial, automotive often much longer).
- Support period determination must be documented in technical documentation.

**Fix:** Add `support_period_years` field to CraAssessment. Validate minimum 5 years with option for shorter with justification. Show warning in UI if < 5 years.

---

## 5. CRA-01 Guidance: Tailor-Made Exception — MISSING

**Current:** No mention of tailor-made exception.

**FAQs say (Section 4.2.5):**
- Manufacturers CAN deviate from secure-by-default for **tailor-made products** fitted to a particular purpose for a particular business user with explicit contractual terms.
- Minor customizations of standard products do NOT qualify.
- Must be documented in technical documentation.

**Fix:** Add tailor-made exception note to CRA-01 guidance explanation and sub-requirements.

---

## 6. CRA-11 Guidance: Proportional Remediation — INCOMPLETE

**Current:** Implies all vulnerabilities need patches with SLAs.

**FAQs say (Section 4.3.1):**
- CRA does NOT require patching ALL vulnerabilities.
- Manufacturer assesses risk, then remediates proportionally.
- Remedies include: immediate patches, advisories on workarounds, software updates, user manual updates, configuration guidance to disable affected features.
- Example: buffer overflow in unused library — document it, remove in next regular release, no dedicated patch needed.

**Fix:** Update CRA-11 guidance to reflect proportional remediation approach.

---

## 7. CRA-09 Guidance: Exploitable Vulnerability Definition — INCOMPLETE

**Current:** Doesn't clarify what "exploitable" means.

**FAQs say (Section 4.2.2):**
- "No known exploitable vulnerabilities" does NOT mean free from ALL vulnerabilities.
- "Exploitable" = can be effectively used by adversary under practical operational conditions.
- Theoretical/lab-only exploits don't count if not exploitable in product's actual environment.
- Case-by-case assessment considering: extent vulnerable code is invoked, access level required, whether compensating controls exist.

**Fix:** Update CRA-09 guidance explanation and sub-requirements.

---

## Timeline Reference (from FAQs Section 7)

| Date | What Applies |
|---|---|
| 10 Dec 2024 | CRA enters into force |
| 11 Jun 2026 | Notified body designation provisions (Articles 35-51) |
| **11 Sep 2026** | **Reporting obligations (Article 14) — FIRST hard deadline** |
| **11 Dec 2027** | **Full application — all essential requirements, market surveillance, enforcement** |
| 11 Jun 2028 | EU-type examination certificates from other legislation expire |
