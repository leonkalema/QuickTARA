"""
CRA Requirement Guidance — Part II (Vulnerability Handling) and Documentation

Continues from cra_requirement_guidance.py with CRA-10 through CRA-18.
Based on EU 2024/2847 Annex I Part II, Articles 13-14, Annex V, VII.
"""
from core.cra_requirement_guidance import (
    RequirementGuidance, SubRequirement, RemediationAction, GUIDANCE_MAP,
)


# ── Part II: Vulnerability handling requirements ──────────────────

_CRA_10 = RequirementGuidance(
    requirement_id="CRA-10",
    annex_section="Part II",
    cra_article="Art. 13(6) / Annex I Part II §1",
    priority="Critical",
    deadline_note="SBOM required for conformity assessment. Operational by Q3 2026 recommended.",
    explanation=(
        "Manufacturers must identify and document all components in the product "
        "by creating a Software Bill of Materials (SBOM) in a machine-readable "
        "format covering at minimum the top-level dependencies. The SBOM must "
        "be maintained throughout the product lifecycle and available to "
        "regulators on request. "
        "Per FAQs Section 4.4: manufacturers MUST exercise due diligence when "
        "integrating third-party components (including free/open-source). The "
        "level of diligence depends on the component's cybersecurity risk. "
        "Due diligence actions include: checking CE marking, verifying security "
        "update history, checking vulnerability databases, carrying out security "
        "tests (fuzz, pentest, SCA), reviewing the component's SBOM, and "
        "assessing the component manufacturer's security posture. Components "
        "WITHOUT CE marking (including pre-CRA and open-source) CAN be "
        "integrated — you don't need to bring them into CRA compliance, but "
        "you must ensure your own product meets CRA overall."
    ),
    regulatory_text=(
        "Manufacturers shall identify and document vulnerabilities and "
        "components contained in the product, including by drawing up a "
        "software bill of materials in a commonly used and machine-readable "
        "format covering at minimum the top-level dependencies of the product."
    ),
    sub_requirements=[
        SubRequirement(
            "SBOM exists in machine-readable format (CycloneDX or SPDX)",
            "Generated SBOM file in JSON/XML format with spec version noted",
            "No SBOM exists at all",
        ),
        SubRequirement(
            "All top-level components listed with name, version, supplier",
            "SBOM content review: every component has name, version, supplier fields",
            "SBOM is a manual spreadsheet that is never updated",
        ),
        SubRequirement(
            "SBOM integrated into build pipeline",
            "CI/CD config showing SBOM generation step per release",
            "SBOM generated manually and goes stale",
        ),
        SubRequirement(
            "Vulnerability monitoring tied to SBOM components",
            "Dependency-Track or equivalent tool showing CVE matching against SBOM",
            "No link between SBOM and vulnerability scanning",
        ),
        SubRequirement(
            "SBOM retention for 10 years or support period",
            "Archive policy and storage location for historical SBOMs",
            "SBOMs overwritten on each release with no history",
        ),
    ],
    evidence_checklist=[
        "SBOM file in CycloneDX JSON or SPDX format",
        "Component inventory: name, version, supplier, type, license per component",
        "Build pipeline config showing automated SBOM generation",
        "Vulnerability monitoring dashboard (Dependency-Track or equivalent)",
        "SBOM maintenance process document",
        "Supplier SBOM request records",
        "SBOM archive with retention policy (10 years minimum)",
    ],
    investigation_prompts=[
        "Do you have a current list of every software component? RTOS, HAL, drivers, libraries?",
        "Is the SBOM generated automatically in the build pipeline, or manually?",
        "Which format: CycloneDX or SPDX? BSI recommends CycloneDX for security focus.",
        "Are known CVEs tracked against these components? What tool do you use?",
        "For embedded: have you inventoried components not auto-detectable (BSP, vendor HAL)?",
        "Have you requested SBOMs from your component suppliers?",
    ],
    common_gaps=[
        "No SBOM exists at all — this is the #1 gap across industry",
        "SBOM is a manual spreadsheet that goes stale after first release",
        "Transitive dependencies (deps of deps) missing",
        "Embedded-specific components (RTOS, HAL, BSP) not included",
        "No vulnerability monitoring linked to SBOM (CVEs not tracked)",
        "No supplier SBOM collection process",
    ],
    remediation_actions=[
        RemediationAction("Select SBOM format — CycloneDX recommended for security focus", "Security", 1),
        RemediationAction("Inventory all software components (manual for embedded)", "Engineering", 5),
        RemediationAction("Integrate SBOM generation into CI/CD build pipeline", "DevOps", 5),
        RemediationAction("Set up Dependency-Track or equivalent for CVE monitoring", "DevOps", 3),
        RemediationAction("Request SBOMs from all component suppliers", "Procurement", 2),
        RemediationAction("Define SBOM maintenance and archive process", "Quality", 2),
    ],
    effort_estimate="15-20 days total. Critical path item — start early.",
    mapped_controls=[],
    mapped_standards=["CycloneDX 1.5+", "SPDX ISO/IEC 5962:2021", "NTIA SBOM Minimum Elements"],
    tara_link="Not directly from TARA. Requires separate SBOM generation tool/process.",
)

_CRA_11 = RequirementGuidance(
    requirement_id="CRA-11",
    annex_section="Part II",
    cra_article="Art. 14(1-3) / Annex I Part II §2",
    priority="High",
    deadline_note="Process must be operational by Aug 2026 (vulnerability reporting deadline).",
    explanation=(
        "You must have a documented process for receiving, triaging, and "
        "remediating vulnerabilities — both internally discovered and "
        "externally reported. CRA does NOT require patching ALL "
        "vulnerabilities. Remediation is PROPORTIONAL to risk. Acceptable "
        "remedies include: immediate patches, advisories on workarounds, "
        "configuration guidance to disable affected features, user manual "
        "updates, or removing unused vulnerable code in next regular release. "
        "Define severity classification (CVSS) and response SLAs by severity. "
        "For integrated components: if the component manufacturer handles "
        "vulnerability management (CRA-compliant component), you can rely on "
        "their process. If not, you must address it yourself."
    ),
    regulatory_text=(
        "In relation to the risks posed to the products with digital "
        "elements, manufacturers shall address and remediate "
        "vulnerabilities without delay, including by providing security "
        "updates."
    ),
    sub_requirements=[
        SubRequirement(
            "Formal vulnerability handling process documented",
            "Written procedure: intake → triage → classify → remediate → verify → disclose",
            "Informal or ad-hoc handling with no written procedure",
        ),
        SubRequirement(
            "CVSS-based severity classification",
            "Severity matrix: Critical (9.0+), High (7.0-8.9), Medium (4.0-6.9), Low (<4.0)",
            "No severity classification — everything treated the same",
        ),
        SubRequirement(
            "Remediation SLAs defined per severity",
            "SLA document: Critical 24h response/72h patch, High 48h/7d, Medium 1w/30d, Low 2w/90d",
            "No defined timeline for fix delivery",
        ),
        SubRequirement(
            "Vulnerability tracking system operational",
            "Jira/GitLab board with vulnerability tickets, severity labels, SLA tracking",
            "Vulnerabilities tracked in email or not tracked at all",
        ),
    ],
    evidence_checklist=[
        "Vulnerability handling process document",
        "Severity classification matrix (CVSS-based)",
        "Remediation SLA targets per severity level",
        "Vulnerability tracking system (Jira, GitLab, etc.)",
        "Public contact point for external reports (e.g. security@ or security.txt)",
        "Sample vulnerability records showing full lifecycle",
    ],
    investigation_prompts=[
        "Is there a written procedure for handling reported vulnerabilities?",
        "Who triages incoming reports? What criteria do they use?",
        "What are your target fix times? Critical: 72h? High: 7 days?",
        "How do external researchers report vulnerabilities to you?",
        "Do you have a security.txt file on your website?",
    ],
    common_gaps=[
        "No written vulnerability handling procedure",
        "No public contact point for security researchers",
        "No defined SLA for patch delivery by severity",
        "Triage done ad-hoc with no documented criteria",
        "No tracking system — vulnerabilities lost in email",
    ],
    remediation_actions=[
        RemediationAction("Write vulnerability handling process document", "Security", 3),
        RemediationAction("Define CVSS-based severity classification matrix", "Security", 1),
        RemediationAction("Establish remediation SLAs per severity level", "Management", 1),
        RemediationAction("Set up vulnerability tracking in Jira/GitLab", "DevOps", 2),
        RemediationAction("Create public security contact (security.txt)", "Security", 1),
    ],
    effort_estimate="10 days. Must be done before Aug 2026 reporting deadline.",
    mapped_controls=[],
    mapped_standards=["ISO 21434 §8 (Vulnerability management)", "ISO 30111", "ISO 29147"],
    tara_link="TARA damage scenarios define impact levels for vulnerability triage.",
)

_CRA_12 = RequirementGuidance(
    requirement_id="CRA-12",
    annex_section="Part II",
    cra_article="Art. 13(5) / Annex I Part II §3",
    priority="Medium",
    deadline_note="Schedule annual penetration testing. Full compliance by Dec 2027.",
    explanation=(
        "Manufacturers must apply effective and regular tests and reviews "
        "of the product security throughout its development and operational "
        "life. This includes static analysis, penetration testing, fuzz "
        "testing, and regression testing for previously found vulnerabilities. "
        "Per FAQs Section 6: CRA does NOT mandate a specific evaluation "
        "methodology. Harmonised standards are voluntary but give a "
        "presumption of conformity. You may choose any technically sound "
        "testing approach appropriate to your product's risk profile."
    ),
    regulatory_text=(
        "Manufacturers shall apply effective and regular tests and reviews "
        "of the security of the product with digital elements."
    ),
    sub_requirements=[
        SubRequirement(
            "Security testing in development (SAST, DAST)",
            "Static analysis tool config and recent scan results with findings addressed",
            "Static analysis runs but nobody reviews the findings",
        ),
        SubRequirement(
            "Penetration testing on regular schedule",
            "Annual pentest report from qualified tester (internal or third-party)",
            "No penetration testing at all",
        ),
        SubRequirement(
            "Regular security reviews",
            "Security review checkpoints in development process",
            "Reviews done ad-hoc or not at all",
        ),
        SubRequirement(
            "Regression testing for past vulnerabilities",
            "Test suite covering previously found and fixed CVEs",
            "No regression tests — past bugs can reappear",
        ),
    ],
    evidence_checklist=[
        "Security testing plan (what, how often, by whom)",
        "Static analysis tool configuration and scan results",
        "Penetration test report (annual minimum)",
        "Fuzz testing setup and coverage metrics (for protocol parsers)",
        "Regression test suite for previously found vulnerabilities",
        "Security review checkpoints in development process",
    ],
    investigation_prompts=[
        "What security testing runs before each release?",
        "When was the last penetration test? Who did it? Budget €15-25K annually.",
        "Do you fuzz-test network interfaces and file/protocol parsers?",
        "Do you re-test for previously fixed vulnerabilities in each release?",
        "Are security review checkpoints defined in your development process?",
    ],
    common_gaps=[
        "No penetration testing at all — budget not allocated",
        "Static analysis runs but findings not reviewed or addressed",
        "Fuzz testing not performed on protocol parsers or interfaces",
        "No regression tests for past CVEs — they can reappear",
        "No security review checkpoints in development lifecycle",
    ],
    remediation_actions=[
        RemediationAction("Schedule annual penetration testing (budget €15-25K)", "Management", 2),
        RemediationAction("Define security review checkpoints in development process", "Security", 2),
        RemediationAction("Document testing methodology and coverage", "Quality", 2),
        RemediationAction("Set up regression test suite for past CVEs", "Engineering", 3),
    ],
    effort_estimate="5 days for process + external pentest cost (€15-25K/year)",
    mapped_controls=[],
    mapped_standards=["ISO 21434 §10 (Verification)", "OWASP Testing Guide", "IEC 62443-4-1 SVV"],
    tara_link="Threat scenarios identify attack vectors. Test plans should cover each one.",
)

_CRA_13 = RequirementGuidance(
    requirement_id="CRA-13",
    annex_section="Part II",
    cra_article="Art. 14(1) / Annex I Part II §4",
    priority="High",
    deadline_note="Disclosure policy should be published by Q1 2026.",
    explanation=(
        "You must have a coordinated vulnerability disclosure policy, "
        "published publicly. When a vulnerability is fixed, publish a "
        "security advisory with CVE ID, affected versions, severity, "
        "impact, and remediation guidance. "
        "Per FAQs Section 5: 'actively exploited vulnerability' means "
        "reliable evidence that a malicious actor exploited it without "
        "authorization. Vulnerabilities found by ethical hackers, bug "
        "bounties, or security researchers WITHOUT evidence of malicious "
        "exploitation are NOT 'actively exploited' and do NOT trigger "
        "mandatory reporting — but should still be handled through your "
        "normal vulnerability management process."
    ),
    regulatory_text=(
        "Once a security update has been made available, the manufacturer "
        "shall publicly disclose information about fixed vulnerabilities, "
        "including a description, information allowing users to identify "
        "the product, the impacts, severity, and remediation."
    ),
    sub_requirements=[
        SubRequirement(
            "Public vulnerability disclosure policy on company website",
            "URL to published policy page with reporting instructions",
            "No public disclosure policy exists",
        ),
        SubRequirement(
            "Security advisory template and publication channel",
            "Template with: CVE, affected versions, CVSS, impact, fix, timeline",
            "Vulnerabilities fixed silently with no advisory",
        ),
        SubRequirement(
            "CVE assignment process",
            "CNA registration or partnership with MITRE/CERT for CVE assignment",
            "No CVE IDs assigned to disclosed vulnerabilities",
        ),
        SubRequirement(
            "Coordinated disclosure with reporters",
            "Process doc: acknowledge within 48h, coordinate timeline, credit researcher",
            "No coordination with reporter before public disclosure",
        ),
    ],
    evidence_checklist=[
        "Public vulnerability disclosure policy (URL)",
        "Security advisory template (CVE, CVSS, affected versions, fix)",
        "CVE assignment process (CNA or partner)",
        "Publication channel (website, mailing list, security bulletin)",
        "security.txt file on company website",
        "Past advisories as examples (if any)",
    ],
    investigation_prompts=[
        "Is there a public page describing how to report vulnerabilities?",
        "Do you publish security advisories when you fix issues?",
        "Do you request CVE IDs for disclosed vulnerabilities?",
        "Do you have a security.txt file? (RFC 9116)",
        "Do you coordinate with the reporter before public disclosure?",
    ],
    common_gaps=[
        "No public disclosure policy at all",
        "Vulnerabilities fixed silently in release notes with no advisory",
        "No CVE assignment — vulnerabilities have no trackable identifier",
        "No coordination with researchers — creates reputation risk",
    ],
    remediation_actions=[
        RemediationAction("Draft and publish vulnerability disclosure policy", "Security + Legal", 3),
        RemediationAction("Create security advisory template", "Security", 1),
        RemediationAction("Establish CVE assignment process (register as CNA or partner)", "Security", 3),
        RemediationAction("Set up publication channel (website section, mailing list)", "Marketing", 2),
        RemediationAction("Create security.txt file per RFC 9116", "Security", 1),
    ],
    effort_estimate="10 days. Low effort, high visibility — do this early.",
    mapped_controls=[],
    mapped_standards=["ISO 29147 (Vulnerability disclosure)", "RFC 9116 (security.txt)"],
    tara_link="Process-level. Not directly mapped from TARA artifacts.",
)

_CRA_14 = RequirementGuidance(
    requirement_id="CRA-14",
    annex_section="Part II",
    cra_article="Art. 14(4-8)",
    priority="Critical",
    deadline_note="MANDATORY from 11 Sep 2026. Internal readiness by Mar 2026 recommended.",
    explanation=(
        "Actively exploited vulnerabilities and severe security incidents "
        "must be reported to ENISA and the national CSIRT within 24 hours. "
        "A full report follows within 72 hours. This requires a 24/7 "
        "response capability, internal escalation chain, and pre-registration "
        "on the ENISA reporting platform. "
        "Per FAQs Section 5: reporting obligations apply from 11 September "
        "2026 — the FIRST CRA hard deadline. They apply to ALL in-scope "
        "products, including those placed on market BEFORE 11 Dec 2027. "
        "Zero-day vulnerabilities are reportable ONLY if there is evidence "
        "of malicious exploitation. If a vulnerability is in a third-party "
        "component: BOTH the product manufacturer AND the component "
        "manufacturer (if the component was placed on market) must report. "
        "If the vulnerability in a component CANNOT be exploited in your "
        "product, it is NOT 'actively exploited' and no mandatory report "
        "is needed — but you should notify the component maintainer per "
        "Article 13(6)."
    ),
    regulatory_text=(
        "The manufacturer shall, without undue delay and in any event "
        "within 24 hours of becoming aware of it, notify ENISA of any "
        "actively exploited vulnerability contained in the product."
    ),
    sub_requirements=[
        SubRequirement(
            "24-hour reporting capability to ENISA and national CSIRT",
            "Tested reporting process with ENISA portal access and CSIRT contact info",
            "No process exists — nobody knows how to report to ENISA",
        ),
        SubRequirement(
            "Internal escalation chain defined",
            "Escalation doc: who discovers → who decides → who reports (names, roles, contacts)",
            "No escalation chain — decisions delayed by hierarchy",
        ),
        SubRequirement(
            "On-call rotation for 24/7 coverage",
            "On-call schedule covering weekends and holidays",
            "No on-call — incidents discovered Friday aren't handled until Monday",
        ),
        SubRequirement(
            "ENISA platform registration",
            "Screenshot or confirmation of registration on ENISA single reporting platform",
            "Not registered — can't submit reports when needed",
        ),
        SubRequirement(
            "Reporting runbook and templates",
            "Step-by-step runbook with report templates for 24h and 72h reports",
            "No templates — first report written under pressure during incident",
        ),
    ],
    evidence_checklist=[
        "Incident response procedure with 24h ENISA reporting step",
        "ENISA single reporting platform registration",
        "National CSIRT contact details and relationship",
        "Internal escalation chain document (names, roles, contact info)",
        "On-call rotation schedule (24/7 coverage)",
        "Reporting runbook with 24h and 72h report templates",
        "Tabletop exercise report (dry-run of reporting process)",
        "User notification templates for affected customers",
    ],
    investigation_prompts=[
        "Do you have an incident response plan that includes 24h ENISA reporting?",
        "Who in the company is authorized to submit a report to ENISA?",
        "Is there an on-call rotation covering weekends and holidays?",
        "Have you registered on the ENISA single reporting platform?",
        "Have you identified your national CSIRT contact?",
        "Have you run a tabletop exercise to test the 24h reporting process?",
    ],
    common_gaps=[
        "No incident response plan exists at all",
        "Nobody knows who ENISA is or how to report",
        "No on-call process — incidents on weekends are missed",
        "24-hour deadline not reflected in internal SLAs",
        "No tabletop exercise — first real test is a real incident",
        "Not registered on ENISA platform",
    ],
    remediation_actions=[
        RemediationAction("Identify national CSIRT and establish contact", "Legal", 2),
        RemediationAction("Register on ENISA single reporting platform", "Legal", 1),
        RemediationAction("Define internal escalation workflow and on-call rotation", "PSIRT", 3),
        RemediationAction("Create 24h and 72h reporting templates and runbook", "PSIRT", 3),
        RemediationAction("Train response team on reporting obligations", "PSIRT", 2),
        RemediationAction("Conduct tabletop exercise (dry-run)", "PSIRT", 2),
    ],
    effort_estimate="15 days. CRITICAL — regulatory deadline Sep 2026, be ready by Mar 2026.",
    mapped_controls=[],
    mapped_standards=["NIS2 Directive (reporting alignment)", "ISO 21434 §8.6"],
    tara_link="TARA damage scenarios define what counts as a reportable incident.",
)


# ── Documentation requirements ────────────────────────────────────

_CRA_15 = RequirementGuidance(
    requirement_id="CRA-15",
    annex_section="Documentation",
    cra_article="Art. 31 / Annex VII",
    priority="Medium",
    deadline_note="Required for conformity assessment. Compile by Q3 2026.",
    explanation=(
        "You must produce a Technical File per Annex VII containing: "
        "product description, security architecture, risk assessment (TARA), "
        "Annex I compliance evidence, test results, and SBOM reference. "
        "This is the core document package for conformity assessment. "
        "Per FAQs Section 6: technical documentation must be available at "
        "the time of market placement and must be comprehensive enough for "
        "market surveillance authorities to verify compliance. It must "
        "contain ALL elements from Annex VII. CRA does not mandate a "
        "specific format — organize it to be auditable and complete."
    ),
    regulatory_text=(
        "The technical documentation shall contain all relevant data or "
        "details of the means used by the manufacturer to ensure that "
        "the product complies with the essential requirements."
    ),
    sub_requirements=[
        SubRequirement(
            "Product description and intended use",
            "Document: product name, type, version, intended use, architecture overview",
            "No single product description document exists",
        ),
        SubRequirement(
            "Security architecture documentation",
            "Architecture doc showing security controls, trust boundaries, data flows",
            "Security architecture not documented (even if implemented)",
        ),
        SubRequirement(
            "Risk assessment (TARA)",
            "TARA report covering all digital elements, threat scenarios, and controls",
            "TARA doesn't cover CRA-specific requirements or is incomplete",
        ),
        SubRequirement(
            "Annex I compliance evidence consolidated",
            "Compliance matrix: each Annex I requirement → evidence location → status",
            "Evidence scattered across teams with no central index",
        ),
        SubRequirement(
            "Test results organized",
            "Test report index: pentest, static analysis, fuzz testing, regression",
            "Test results exist but not organized for audit",
        ),
    ],
    evidence_checklist=[
        "Product description (name, type, version, intended use)",
        "Security architecture and design documentation",
        "TARA report (risk assessment per ISO 21434)",
        "Compliance evidence matrix (Annex I requirement → evidence → status)",
        "SBOM reference",
        "Test reports index (pentest, SAST, fuzz, regression)",
        "List of harmonised standards applied",
        "Conformity assessment results (if completed)",
    ],
    investigation_prompts=[
        "Is there a single document describing the product and its security architecture?",
        "Does the TARA report cover all digital elements of the product?",
        "Can you produce a compliance evidence matrix showing each requirement's status?",
        "Can you produce this documentation for a market surveillance authority on request?",
        "Which harmonised standards have you applied? (EN standards when available)",
    ],
    common_gaps=[
        "Documentation scattered across teams with no central index",
        "TARA doesn't cover CRA-specific requirements",
        "No compliance evidence matrix",
        "No reference to harmonised standards",
        "Test results not organized for external audit",
    ],
    remediation_actions=[
        RemediationAction("Create compliance evidence matrix (requirement → evidence → status)", "Quality", 3),
        RemediationAction("Consolidate security architecture documentation", "Security", 3),
        RemediationAction("Organize test results into indexed package", "Quality", 2),
        RemediationAction("Review Annex VII requirements and create document index", "Quality", 2),
    ],
    effort_estimate="10 days to compile. Depends on having other gaps closed first.",
    mapped_controls=[],
    mapped_standards=["ISO 21434 (full)", "IEC 62443-4-1 (development process)"],
    tara_link="Your TARA product scope and asset inventory feed directly into this file.",
)

_CRA_16 = RequirementGuidance(
    requirement_id="CRA-16",
    annex_section="Documentation",
    cra_article="Art. 28 / Annex V",
    priority="Medium",
    deadline_note="Required after conformity assessment. Target Q4 2027.",
    explanation=(
        "You must draft an EU Declaration of Conformity (DoC) per Annex V "
        "stating that the product meets all applicable CRA essential requirements. "
        "It must be signed by an authorized representative and kept for 10 years. "
        "For Class II products, a notified body must be engaged. "
        "Per FAQs Section 6: you may use either the FULL DoC (Annex V template) "
        "or a SIMPLIFIED DoC (Annex VI) that includes a URL to the full version. "
        "The simplified form is acceptable if users can easily access the full "
        "version online. CE marking is required — visible, legible, indelible, "
        "≥5mm. For software-only products: the CE marking must appear on the "
        "EU Declaration of Conformity OR on the product website."
    ),
    regulatory_text=(
        "The EU declaration of conformity shall state that the fulfilment "
        "of the applicable essential requirements has been demonstrated."
    ),
    sub_requirements=[
        SubRequirement(
            "EU Declaration of Conformity drafted per Annex V",
            "DoC document with all Annex V required fields",
            "No DoC exists",
        ),
        SubRequirement(
            "Correct regulation reference (EU 2024/2847)",
            "DoC references CRA regulation number and applicable articles",
            "DoC references wrong regulation or outdated standards",
        ),
        SubRequirement(
            "Authorized signatory identified",
            "Named person with authority to sign on behalf of manufacturer",
            "No authorized signatory identified",
        ),
        SubRequirement(
            "Conformity assessment completed (notified body for Class II)",
            "Certificate from notified body (Class II) or self-assessment record (Default/Class I)",
            "Conformity assessment not started",
        ),
    ],
    evidence_checklist=[
        "EU Declaration of Conformity document (Annex V format)",
        "Manufacturer name and address",
        "Product identification (name, type, batch/serial number)",
        "List of harmonised standards or technical specifications applied",
        "Signature of authorized representative",
        "Notified body certificate (if Class II)",
        "Languages for target EU markets",
    ],
    investigation_prompts=[
        "Has anyone drafted a Declaration of Conformity for this product?",
        "Who in the company is authorized to sign the DoC?",
        "What is the product classification? (Default, Class I, Class II, Critical)",
        "For Class II: have you engaged a notified body? Budget €20-50K.",
        "Is the DoC available in the languages of your target EU markets?",
    ],
    common_gaps=[
        "No DoC exists at all",
        "DoC references wrong regulation or outdated standards",
        "No authorized signatory identified",
        "Notified body not engaged (Class II products)",
        "Budget not allocated for third-party assessment (€20-50K)",
    ],
    remediation_actions=[
        RemediationAction("Confirm product classification (Default/Class I/Class II/Critical)", "Quality", 2),
        RemediationAction("Identify and engage notified body (for Class II)", "Quality", 5),
        RemediationAction("Draft DoC per Annex V template", "Quality", 2),
        RemediationAction("Legal review of DoC", "Legal", 2),
        RemediationAction("Obtain executive sign-off", "Management", 1),
    ],
    effort_estimate="5 days for DoC. Notified body assessment: 3-6 months, €20-50K.",
    mapped_controls=[],
    mapped_standards=["EU 2024/2847 Annex V"],
    tara_link="TARA results support the claims in the DoC.",
)

_CRA_17 = RequirementGuidance(
    requirement_id="CRA-17",
    annex_section="Documentation",
    cra_article="Art. 13(19-20)",
    priority="Medium",
    deadline_note="Full compliance by Dec 2027. Support period declaration needed early.",
    explanation=(
        "You must provide clear instructions to users on secure installation, "
        "configuration, operation, and disposal. This includes the declared "
        "support period, contact details for security issues, and update "
        "instructions. "
        "Per FAQs Section 4.5: the MINIMUM support period is 5 years. Less "
        "than 5 years is only acceptable if the product is expected to be in "
        "use for less than 5 years (e.g. pandemic contact tracing app, "
        "subscription-only software that becomes unavailable after subscription). "
        "If the product is expected to be in use LONGER than 5 years, the "
        "support period must reflect that (hardware, network devices, OS, ICS "
        "often need much longer). Factors to consider: reasonable user "
        "expectations, product nature/intended purpose, other EU law on product "
        "lifetime, support periods of similar products, availability of the "
        "operating environment, and ADCO guidance."
    ),
    regulatory_text=(
        "The manufacturer shall provide users with instructions and "
        "information on the secure use and maintenance of the product, "
        "including the expected product lifetime and support period."
    ),
    sub_requirements=[
        SubRequirement(
            "Security instructions in user documentation",
            "User manual section covering secure installation, configuration, and operation",
            "User manual has no security section at all",
        ),
        SubRequirement(
            "Support period publicly declared",
            "Published support period per product (e.g. '10 years from SOP')",
            "No public commitment on support duration",
        ),
        SubRequirement(
            "Update instructions provided",
            "Documentation explaining how to apply security updates (OTA, USB, workshop)",
            "No update instructions — users don't know how to patch",
        ),
        SubRequirement(
            "Security contact information published",
            "Contact for reporting security issues (security@, security.txt)",
            "No security contact in user-facing documentation",
        ),
    ],
    evidence_checklist=[
        "User manual with security instructions section",
        "Secure installation and configuration guide",
        "Instructions for applying security updates",
        "Published support period declaration per product",
        "Security issue reporting contact (security@, security.txt)",
        "End-of-life and secure disposal instructions",
    ],
    investigation_prompts=[
        "Does the user manual explain how to configure the product securely?",
        "Are there instructions for applying firmware/security updates?",
        "Does the manual tell the user how to report a security issue?",
        "Is the support period declared? (e.g. 7 years, 10 years from SOP)",
        "Is there guidance on secure disposal or decommissioning?",
    ],
    common_gaps=[
        "User manual has no security section",
        "No instructions for applying updates",
        "No vulnerability reporting contact in user-facing docs",
        "Support period not declared publicly",
    ],
    remediation_actions=[
        RemediationAction("Define and publish support periods per product line", "Product Management", 2),
        RemediationAction("Add security instructions section to user manual", "Technical Writing", 3),
        RemediationAction("Add security contact and update instructions", "Technical Writing", 1),
    ],
    effort_estimate="5 days. Support period is a business decision — escalate early.",
    mapped_controls=[],
    mapped_standards=["ISO 21434 §6 (Information sharing)"],
    tara_link="Informed by TARA asset inventory and threat model.",
)

_CRA_18 = RequirementGuidance(
    requirement_id="CRA-18",
    annex_section="Documentation",
    cra_article="Art. 30",
    priority="Low",
    deadline_note="Applied after conformity assessment. Final step before market placement.",
    explanation=(
        "Products that meet CRA requirements must carry the CE marking. "
        "The marking must be visible, legible (≥5mm), and affixed before "
        "placing on the EU market. For software-only products, the CE "
        "marking must appear in the digital documentation. "
        "Per FAQs Section 7: the full compliance deadline is 11 December "
        "2027. Products placed on market BEFORE this date do NOT need "
        "CRA compliance unless substantially modified after that date. "
        "Products manufactured to a non-compliant type CANNOT be placed "
        "on market on or after 11 Dec 2027, even if the original type "
        "was placed before. EU-type examination certificates from other "
        "legislation (e.g. RED Delegated Regulation) expire 11 June 2028."
    ),
    regulatory_text=(
        "The CE marking shall be affixed visibly, legibly and indelibly "
        "to the product with digital elements or to its data plate. "
        "Where that is not possible, it shall be affixed to the packaging "
        "or to the accompanying documents."
    ),
    sub_requirements=[
        SubRequirement(
            "CE marking applied to product, packaging, or documentation",
            "Photo or drawing showing CE marking placement and dimensions",
            "CE marking not applied or applied incorrectly",
        ),
        SubRequirement(
            "Conformity assessment completed before CE marking",
            "Completed conformity assessment record or notified body certificate",
            "CE marking applied before conformity assessment is done",
        ),
        SubRequirement(
            "Marking meets physical requirements (≥5mm, legible, indelible)",
            "Specification showing marking size, material, and placement",
            "Marking too small, illegible, or removable",
        ),
    ],
    evidence_checklist=[
        "CE marking applied to product or packaging (photo evidence)",
        "Marking dimensions verification (≥5mm height)",
        "Declaration of Conformity on file (supports the CE marking)",
        "Confirmation that conformity assessment completed before marking",
        "Labeling update records",
    ],
    investigation_prompts=[
        "Is the CE marking visible on the product or its packaging?",
        "Has the conformity assessment been completed before affixing CE?",
        "Is the marking legible and at least 5mm in height?",
        "Are there other EU directives that also require CE marking? (Machinery, EMC, etc.)",
        "For software-only: where does the CE marking appear?",
    ],
    common_gaps=[
        "CE marking applied before conformity assessment is done",
        "Marking not visible, too small, or illegible",
        "CE mark placement for software-only products not considered",
        "Other EU directive CE markings not aligned",
    ],
    remediation_actions=[
        RemediationAction("Update CE marking to include CRA reference", "Engineering", 1),
        RemediationAction("Update product labeling and documentation", "Operations", 1),
    ],
    effort_estimate="2 days. Final step — do only after all other requirements met.",
    mapped_controls=[],
    mapped_standards=["EU 2024/2847 Art. 30", "Regulation (EC) No 765/2008"],
    tara_link="Final step. CE marking is the last action after all requirements are met.",
)


# Register Part II + Documentation guidance into the shared map
for _g in [_CRA_10, _CRA_11, _CRA_12, _CRA_13, _CRA_14,
           _CRA_15, _CRA_16, _CRA_17, _CRA_18]:
    GUIDANCE_MAP[_g.requirement_id] = _g
