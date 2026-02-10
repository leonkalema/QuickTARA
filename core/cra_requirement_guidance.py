"""
CRA Requirement Guidance Knowledge Base

Provides per-requirement coaching for users with no CRA experience.
Each entry includes sub-requirements, remediation actions, effort
estimates, priorities, and links to TARA artifacts and controls.

Source: EU Regulation 2024/2847 (Cyber Resilience Act), Annex I
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubRequirement:
    """One checkable sub-item within a CRA requirement."""
    description: str
    check_evidence: str
    typical_gap: str


@dataclass(frozen=True)
class RemediationAction:
    """One concrete step to close a gap."""
    action: str
    owner_hint: str
    effort_days: int


@dataclass(frozen=True)
class RequirementGuidance:
    """Full coaching data for a single CRA requirement."""
    requirement_id: str
    annex_section: str
    cra_article: str
    priority: str
    deadline_note: str
    explanation: str
    regulatory_text: str
    sub_requirements: List[SubRequirement]
    evidence_checklist: List[str]
    investigation_prompts: List[str]
    common_gaps: List[str]
    remediation_actions: List[RemediationAction]
    effort_estimate: str
    mapped_controls: List[str]
    mapped_standards: List[str]
    tara_link: str


def get_guidance(requirement_id: str) -> Optional[RequirementGuidance]:
    """Look up guidance by requirement ID (e.g. 'CRA-01')."""
    return GUIDANCE_MAP.get(requirement_id)


def get_all_guidance() -> Dict[str, RequirementGuidance]:
    """Return the full guidance map."""
    return GUIDANCE_MAP


# ── Part I: Security requirements for design and development ──────

_CRA_01 = RequirementGuidance(
    requirement_id="CRA-01",
    annex_section="Part I",
    cra_article="Annex I, Part I, §1",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must be delivered with a secure-by-default configuration, "
        "including the ability to reset the product to its original state. "
        "The user should not need to harden the product after installation. "
        "EXCEPTION: Tailor-made products fitted to a particular purpose for "
        "a specific business user may deviate from secure-by-default IF "
        "explicitly agreed in contractual terms. Minor customizations of "
        "standard products do NOT qualify as tailor-made."
    ),
    regulatory_text=(
        "Products with digital elements shall be designed, developed and "
        "produced to ensure a secure by default configuration, including "
        "the possibility to reset the product to its original state."
    ),
    sub_requirements=[
        SubRequirement(
            "Secure default configuration in production mode",
            "Config review doc showing debug disabled, security enabled",
            "Debug interfaces left enabled in production firmware",
        ),
        SubRequirement(
            "Factory reset capability that preserves security",
            "Test report: factory reset does not expose credentials or disable security",
            "Reset doesn't re-lock debug ports or reverts to insecure state",
        ),
        SubRequirement(
            "No default or shared credentials",
            "Scan report confirming zero hardcoded passwords or shared keys",
            "Shared API keys or default passwords baked into binary",
        ),
    ],
    evidence_checklist=[
        "Default configuration review document",
        "Production build config vs. development diff",
        "Factory reset security test report",
        "Credential scan report (no hardcoded secrets)",
        "Hardening guide or secure deployment instructions",
    ],
    investigation_prompts=[
        "Does the product ship with any default passwords or shared keys?",
        "Which network ports and debug interfaces are active on first boot?",
        "What happens after a factory reset — does security stay enabled?",
        "Is the production build provably different from dev/debug builds?",
    ],
    common_gaps=[
        "Debug interfaces (JTAG, SWD, serial) left enabled in production",
        "Shared API keys or test credentials baked into the binary",
        "Factory reset reverts to insecure state",
    ],
    remediation_actions=[
        RemediationAction("Document factory reset security behavior", "Engineering", 1),
        RemediationAction("Verify reset doesn't expose credentials or disable security", "QA", 1),
        RemediationAction("Run credential scan on production binary", "Security", 1),
    ],
    effort_estimate="2-3 days (documentation + verification)",
    mapped_controls=["Secure Boot", "Access Control"],
    mapped_standards=["ISO 21434 §9 (Concept)", "IEC 62443-4-2 CR 7.6"],
    tara_link="Assets with 'authorization_required' flag. Check asset list for items exposed at boot.",
)

_CRA_02 = RequirementGuidance(
    requirement_id="CRA-02",
    annex_section="Part I",
    cra_article="Annex I, Part I, §2",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must ensure protection from unauthorized access through "
        "appropriate control mechanisms, including authentication, identity "
        "management, and access management systems."
    ),
    regulatory_text=(
        "Products shall implement appropriate control mechanisms for "
        "authentication, identity management, and access control to "
        "protect from unauthorized access."
    ),
    sub_requirements=[
        SubRequirement(
            "Authentication mechanisms for all access paths",
            "Architecture doc listing auth method per interface (e.g. UDS SecurityAccess, API keys, TLS client certs)",
            "API endpoints or diagnostic services accessible without authentication",
        ),
        SubRequirement(
            "Multi-level identity and access management",
            "Role/privilege matrix showing separate privileges per role (read-only, calibration, admin, service)",
            "Single shared admin account with no role separation",
        ),
        SubRequirement(
            "Unauthorized access logging",
            "Audit log samples showing failed auth attempts with timestamps",
            "No logging of failed login attempts",
        ),
        SubRequirement(
            "Brute-force and rate-limit protection",
            "Test report showing lockout after N failed attempts",
            "Unlimited retry on authentication interfaces",
        ),
    ],
    evidence_checklist=[
        "Authentication mechanism description per interface",
        "Role and privilege matrix (who can do what)",
        "Session timeout and lockout policy document",
        "Brute-force protection test report",
        "Audit log samples showing failed access attempts",
    ],
    investigation_prompts=[
        "How does the product authenticate users, systems, and diagnostic tools?",
        "Are there separate privilege levels? Document each role.",
        "What happens after repeated failed login attempts?",
        "Do sessions expire after inactivity? What's the timeout?",
    ],
    common_gaps=[
        "No brute-force or rate-limit protection on login interfaces",
        "Single shared admin account with no role separation",
        "Diagnostic services accessible without authentication",
    ],
    remediation_actions=[
        RemediationAction("Document authentication method per interface", "Security", 2),
        RemediationAction("Create role and privilege matrix", "Security", 1),
        RemediationAction("Implement and test lockout policy", "Engineering", 3),
    ],
    effort_estimate="3-5 days if controls exist; 15-20 days if building from scratch",
    mapped_controls=["Identity Authentication", "Access Control"],
    mapped_standards=["ISO 21434 §15 (Cybersecurity specifications)", "IEC 62443-4-2 CR 1.1-1.7"],
    tara_link="Assets flagged with 'authorization_required = True' in your TARA.",
)

_CRA_03 = RequirementGuidance(
    requirement_id="CRA-03",
    annex_section="Part I",
    cra_article="Annex I, Part I, §3",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must protect the confidentiality of stored, transmitted, "
        "or processed data using state-of-the-art encryption mechanisms "
        "for data at rest and in transit."
    ),
    regulatory_text=(
        "Products shall protect the confidentiality of data, including "
        "at rest and in transit, using state of the art encryption."
    ),
    sub_requirements=[
        SubRequirement(
            "Data at rest encryption",
            "Doc showing what's encrypted in flash/NVM (firmware, config, credentials, calibration)",
            "Credentials or sensitive config stored in plaintext",
        ),
        SubRequirement(
            "Data in transit encryption",
            "TLS/DTLS config document. For CAN: document SecOC or rationale for accepted limitation",
            "Unencrypted network communications (or no documented rationale)",
        ),
        SubRequirement(
            "Encryption key management (HSM or equivalent)",
            "Key lifecycle doc: generation, storage, rotation, destruction",
            "Keys stored in firmware without hardware protection",
        ),
    ],
    evidence_checklist=[
        "Data inventory: what is stored and where",
        "Encryption algorithms and key lengths per data type",
        "Key management procedure (generation, storage, rotation, destruction)",
        "TLS/DTLS configuration for network communications",
        "Rationale document for any accepted crypto limitations (e.g. CAN bus)",
    ],
    investigation_prompts=[
        "What sensitive data does the product store locally? Is each item encrypted?",
        "Is all network traffic encrypted? Which protocol and cipher suite?",
        "Where are cryptographic keys stored? Hardware (HSM/TPM) or software?",
        "For automotive: is CAN bus encryption used, or SecOC? Document the rationale.",
    ],
    common_gaps=[
        "Plaintext storage of credentials or calibration parameters",
        "Outdated TLS versions (1.0, 1.1) still supported",
        "Keys stored in firmware without hardware protection (no HSM)",
        "CAN bus security not documented (missing rationale for no encryption)",
    ],
    remediation_actions=[
        RemediationAction("Inventory all stored and transmitted data", "Security", 2),
        RemediationAction("Document encryption per data type with algorithms", "Security", 2),
        RemediationAction("Document key management lifecycle", "Security", 2),
        RemediationAction("Write rationale for any crypto limitations (e.g. CAN)", "Security", 1),
    ],
    effort_estimate="3-5 days (documentation); 15-30 days if implementing new encryption",
    mapped_controls=["Encryption", "Secure Key Management"],
    mapped_standards=["ISO 21434 §15", "IEC 62443-4-2 CR 4.1", "ISO 11898 (CAN)"],
    tara_link="Assets rated High confidentiality in your TARA.",
)

_CRA_04 = RequirementGuidance(
    requirement_id="CRA-04",
    annex_section="Part I",
    cra_article="Annex I, Part I, §4",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must protect the integrity of data, commands, programs, "
        "and configurations against unauthorized manipulation, and report "
        "on any corruptions detected."
    ),
    regulatory_text=(
        "Products shall protect the integrity of stored, transmitted, or "
        "processed data, commands, programs, and configuration against "
        "manipulation or modification, and shall report corruptions."
    ),
    sub_requirements=[
        SubRequirement(
            "Firmware integrity verification at boot",
            "Secure boot chain doc: SHA-256/RSA validation, HSM root of trust",
            "No secure boot — firmware runs unsigned",
        ),
        SubRequirement(
            "Configuration and calibration integrity",
            "CRC/checksum validation docs for NVM parameters",
            "Configuration files modifiable without detection",
        ),
        SubRequirement(
            "Command and data integrity on interfaces",
            "CAN CRC validation, message authentication (SecOC)",
            "Commands accepted without integrity check",
        ),
        SubRequirement(
            "Corruption reporting and logging",
            "Audit log or DTC generation on integrity failure",
            "Integrity failures silently ignored",
        ),
    ],
    evidence_checklist=[
        "Secure boot chain documentation (root of trust, verification algorithm)",
        "Firmware signing process and key management",
        "Integrity check mechanisms for config and calibration data",
        "Command/data integrity on all communication interfaces",
        "Corruption reporting mechanism (audit log, DTC)",
    ],
    investigation_prompts=[
        "Is firmware signed before deployment? What algorithm? Who holds the key?",
        "Does the product verify firmware integrity at every boot?",
        "Are calibration parameters and config validated with checksums?",
        "What happens when an integrity violation is detected? Is it logged?",
    ],
    common_gaps=[
        "No secure boot — firmware runs unsigned",
        "Configuration files modifiable via file system access with no integrity check",
        "No integrity verification after OTA updates complete",
        "Integrity failures not logged or reported",
    ],
    remediation_actions=[
        RemediationAction("Document full secure boot chain", "Engineering", 2),
        RemediationAction("Document integrity checks for all data types", "Engineering", 2),
        RemediationAction("Verify corruption reporting mechanism works", "QA", 1),
    ],
    effort_estimate="2-3 days (documentation); 30+ days if implementing secure boot",
    mapped_controls=["Cryptographic Validation", "Runtime Integrity", "Secure Boot"],
    mapped_standards=["ISO 21434 §15", "IEC 62443-4-2 CR 3.4"],
    tara_link="Assets rated High integrity in your TARA.",
)

_CRA_05 = RequirementGuidance(
    requirement_id="CRA-05",
    annex_section="Part I",
    cra_article="Annex I, Part I, §5",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products should process only data that is adequate, relevant, and "
        "limited to what is necessary. Document what you collect, why, "
        "and how long you keep it."
    ),
    regulatory_text=(
        "Products shall only process data that is adequate, relevant, and "
        "limited to what is necessary in relation to the intended purpose "
        "of the product (data minimisation)."
    ),
    sub_requirements=[
        SubRequirement(
            "Data collection scope documented and justified",
            "Data flow diagram listing every data field collected and its purpose",
            "No documented justification for data fields collected",
        ),
        SubRequirement(
            "Data retention policy defined",
            "Policy document: retention periods for diagnostic, operational, and log data",
            "Data retained indefinitely with no deletion policy",
        ),
        SubRequirement(
            "Telemetry opt-out if applicable",
            "Telemetry configuration showing opt-in or user control",
            "Telemetry enabled by default with no opt-out",
        ),
    ],
    evidence_checklist=[
        "Data flow diagram: what data is collected, where it goes, why",
        "Data retention and deletion policy",
        "Privacy impact assessment (if personal data involved)",
        "Telemetry opt-in/opt-out documentation (if applicable)",
    ],
    investigation_prompts=[
        "What data does the product collect? Is each field necessary?",
        "How long is diagnostic data retained? Is there automatic deletion?",
        "Does the product send telemetry? Can the user opt out?",
        "Is any personal data processed? If no, document that explicitly.",
    ],
    common_gaps=[
        "Verbose logging that captures more data than needed",
        "No documented retention policy for diagnostic data",
        "No explicit statement that no personal data is processed",
    ],
    remediation_actions=[
        RemediationAction("Document data collection scope and justification", "Security", 1),
        RemediationAction("Define diagnostic data retention policy", "Engineering", 1),
        RemediationAction("Write explicit statement on personal data handling", "Legal", 1),
    ],
    effort_estimate="2-3 days (documentation only)",
    mapped_controls=[],
    mapped_standards=["GDPR Art. 5(1)(c)", "ISO 21434 §15"],
    tara_link="Review asset inventory for data stores and communication channels.",
)

_CRA_06 = RequirementGuidance(
    requirement_id="CRA-06",
    annex_section="Part I",
    cra_article="Annex I, Part I, §6",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must protect the availability of essential functions, "
        "including resilience against denial-of-service attacks. This "
        "covers rate limiting, watchdogs, safe-state transitions, and recovery."
    ),
    regulatory_text=(
        "Products shall protect the availability of essential and basic "
        "functions, including resilience and mitigation against "
        "denial-of-service attacks."
    ),
    sub_requirements=[
        SubRequirement(
            "DoS protection on all network interfaces",
            "Rate limiting config, intrusion detection rules",
            "No rate limiting — device crashes under traffic flood",
        ),
        SubRequirement(
            "Recovery from failures (bus-off, watchdog)",
            "Watchdog config, bus-off recovery test report (e.g. ≤100ms)",
            "Crash on malformed input with no automatic recovery",
        ),
        SubRequirement(
            "Degraded/safe-state operation",
            "Safe-state transition documentation, priority-based processing",
            "No defined safe state on failure",
        ),
    ],
    evidence_checklist=[
        "DoS/DDoS mitigation measures per interface",
        "Watchdog and recovery mechanism documentation",
        "Safe-state or graceful degradation behavior",
        "Priority-based processing (safety-critical commands first)",
        "Bus-off recovery test report (if CAN/automotive)",
    ],
    investigation_prompts=[
        "What happens if the product receives excessive or malformed traffic?",
        "Is there a watchdog that restarts crashed services?",
        "What is the defined safe state? How fast is the transition?",
        "Are safety-critical commands prioritized over diagnostic traffic?",
    ],
    common_gaps=[
        "No rate limiting on network interfaces",
        "No watchdog or automatic recovery mechanism",
        "No documented safe state or degraded operation mode",
    ],
    remediation_actions=[
        RemediationAction("Document DoS protection per interface", "Engineering", 1),
        RemediationAction("Document recovery mechanisms and test results", "QA", 2),
        RemediationAction("Document safe-state transitions", "Engineering", 1),
    ],
    effort_estimate="2-3 days (documentation); 10+ days if implementing new protections",
    mapped_controls=["Network Management", "Communication Protection"],
    mapped_standards=["ISO 21434 §15", "IEC 62443-4-2 CR 7.1"],
    tara_link="Assets rated High availability in your TARA.",
)

_CRA_07 = RequirementGuidance(
    requirement_id="CRA-07",
    annex_section="Part I",
    cra_article="Annex I, Part I, §7",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must be designed to limit attack surfaces, including "
        "external interfaces. Reduce impact of incidents using "
        "appropriate exploitation mitigation mechanisms."
    ),
    regulatory_text=(
        "Products shall be designed to reduce attack surfaces, including "
        "external interfaces, and to reduce the impact of incidents "
        "using appropriate exploitation mitigation mechanisms."
    ),
    sub_requirements=[
        SubRequirement(
            "Debug interfaces disabled in production",
            "Build config showing JTAG/SWD disabled, RDP Level 2 set",
            "JTAG, SWD, or serial console accessible in production",
        ),
        SubRequirement(
            "Read-out protection enabled",
            "MCU config doc showing read-out protection level",
            "Firmware can be extracted from flash",
        ),
        SubRequirement(
            "Interface minimization — only necessary interfaces exposed",
            "Interface inventory with justification for each",
            "Unnecessary services (SSH, Telnet, unused USB) left enabled",
        ),
        SubRequirement(
            "Exploitation mitigation techniques documented",
            "Doc listing: stack canaries, ASLR, MPU config, memory protection",
            "No exploitation mitigations documented or implemented",
        ),
    ],
    evidence_checklist=[
        "Interface inventory (network, physical, debug) with justification",
        "Debug disable verification (JTAG/SWD/serial production state)",
        "Read-out protection configuration",
        "Exploitation mitigation document (stack protection, ASLR, MPU)",
        "Port scan results on production build",
    ],
    investigation_prompts=[
        "Which interfaces are active in production? Is each one necessary?",
        "Is JTAG/SWD disabled? Is read-out protection at maximum level?",
        "Has anyone done a port scan on the production build?",
        "What exploitation mitigations are active (stack canaries, ASLR, MPU)?",
    ],
    common_gaps=[
        "Debug interfaces still accessible in production builds",
        "No read-out protection on MCU",
        "Exploitation mitigations not documented (even if they exist)",
        "Unnecessary services or USB ports left enabled",
    ],
    remediation_actions=[
        RemediationAction("Verify and document debug interface disable state", "Engineering", 1),
        RemediationAction("Document exploitation mitigations", "Security", 1),
        RemediationAction("Run port scan on production build", "Security", 1),
    ],
    effort_estimate="1-3 days (documentation + verification)",
    mapped_controls=["Secure Enclosure"],
    mapped_standards=["ISO 21434 §15", "IEC 62443-4-2 CR 7.4-7.7"],
    tara_link="Threat scenarios that target exposed interfaces.",
)

_CRA_08 = RequirementGuidance(
    requirement_id="CRA-08",
    annex_section="Part I",
    cra_article="Annex I, Part I, §8",
    priority="Low",
    deadline_note="Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must provide security-related information by recording "
        "and monitoring relevant internal activity, including access to "
        "or modification of data, services, or functions."
    ),
    regulatory_text=(
        "Products shall record and/or monitor relevant internal activity "
        "to provide security-related information, including access or "
        "modification of data, services, or functions."
    ),
    sub_requirements=[
        SubRequirement(
            "Authentication attempts logged (success and failure)",
            "Audit log samples showing login attempts with timestamps",
            "No logging of failed login attempts",
        ),
        SubRequirement(
            "Configuration and calibration changes logged",
            "Audit log showing parameter change events",
            "Silent configuration changes with no audit trail",
        ),
        SubRequirement(
            "Security events logged (tamper, integrity failure, boot)",
            "Log samples showing tamper detection, integrity violation, firmware update events",
            "Security events silently discarded",
        ),
        SubRequirement(
            "Log integrity protection",
            "Immutable/append-only log mechanism, chain-hash, or remote syslog",
            "Logs stored in modifiable local storage with no protection",
        ),
    ],
    evidence_checklist=[
        "List of all security events that are logged",
        "Audit log format and samples",
        "Log integrity protection mechanism (chain-hash, append-only, remote)",
        "Log retention period and rotation policy",
        "Export capability (SIEM, syslog)",
    ],
    investigation_prompts=[
        "Does the product log failed authentication attempts?",
        "Are firmware updates, config changes, and reboots logged?",
        "Can logs be exported to a central SIEM or syslog server?",
        "Are logs protected from deletion or modification?",
    ],
    common_gaps=[
        "No logging of failed login attempts",
        "Logs stored locally with no tamper protection",
        "No log rotation — device runs out of storage",
        "Security events not captured at all",
    ],
    remediation_actions=[
        RemediationAction("Document all logged security events", "Security", 1),
        RemediationAction("Export log samples as evidence", "Engineering", 1),
        RemediationAction("Verify log integrity protection works", "QA", 1),
    ],
    effort_estimate="2-3 days (documentation); 10+ days if implementing logging",
    mapped_controls=["Audit Logging"],
    mapped_standards=["ISO 21434 §15", "IEC 62443-4-2 CR 6.1-6.2"],
    tara_link="Logging supports detection of attack paths in your TARA threat scenarios.",
)

_CRA_09 = RequirementGuidance(
    requirement_id="CRA-09",
    annex_section="Part I",
    cra_article="Annex I, Part I, §9",
    priority="High",
    deadline_note="Support period declaration needed early. Full compliance by 11 Dec 2027.",
    explanation=(
        "Products must be placed on the market with no known EXPLOITABLE "
        "vulnerabilities. 'Exploitable' means effectively usable by an "
        "adversary under practical operational conditions — NOT theoretical "
        "or lab-only exploits. Assessment is case-by-case considering: "
        "extent vulnerable code is invoked, access level required, whether "
        "compensating controls exist. Products must ensure vulnerabilities "
        "can be addressed through security updates, with authentication, "
        "rollback protection, and notification of available updates. "
        "Security updates should be provided SEPARATELY from functionality "
        "updates where technically feasible. Support period: minimum 5 years."
    ),
    regulatory_text=(
        "Products shall ensure that vulnerabilities can be addressed "
        "through security updates, including automatic updates where "
        "applicable, with notification to users."
    ),
    sub_requirements=[
        SubRequirement(
            "Security update mechanism exists",
            "Secure update architecture doc (OTA, USB, or workshop-based)",
            "No update capability at all — device must be replaced",
        ),
        SubRequirement(
            "Update authentication (signature verification)",
            "Doc showing RSA/ECDSA signature verification of update packages",
            "Updates not signed — malicious firmware can be injected",
        ),
        SubRequirement(
            "Rollback protection",
            "Anti-rollback mechanism doc and test report",
            "No rollback protection — downgrade attacks possible",
        ),
        SubRequirement(
            "Support period publicly declared",
            "Published support period per product (e.g. 10 years from SOP)",
            "No public commitment on how long updates will be provided",
        ),
    ],
    evidence_checklist=[
        "Secure update mechanism architecture document",
        "Update signature verification (algorithm, key management)",
        "Anti-rollback mechanism description and test report",
        "Published support period declaration per product",
        "User notification process for available updates",
    ],
    investigation_prompts=[
        "Can the product receive security patches? OTA or manual?",
        "Are updates signed and verified before installation? What algorithm?",
        "What happens if an update fails mid-install? Is there rollback?",
        "How long will the manufacturer provide security updates?",
        "For automotive: is update OEM-dependent? Document OEM responsibility.",
    ],
    common_gaps=[
        "No OTA capability — requires physical access to patch",
        "Updates not signed, allowing malicious firmware injection",
        "No rollback mechanism if an update bricks the device",
        "No published support period commitment",
    ],
    remediation_actions=[
        RemediationAction("Define and publish support periods per product", "Product Management", 2),
        RemediationAction("Document update mechanism with signature verification", "Engineering", 3),
        RemediationAction("Test and document rollback protection", "QA", 2),
        RemediationAction("Document OEM responsibility for update notification (if applicable)", "Security", 1),
    ],
    effort_estimate="5-8 days (documentation); support period is a business decision",
    mapped_controls=["Secure Update"],
    mapped_standards=["ISO 21434 §13", "UN R156 (SUMS)", "IEC 62443-4-2 CR 7.5"],
    tara_link="Damage and threat scenarios related to update mechanisms.",
)


GUIDANCE_MAP: Dict[str, RequirementGuidance] = {
    g.requirement_id: g for g in [
        _CRA_01, _CRA_02, _CRA_03, _CRA_04, _CRA_05,
        _CRA_06, _CRA_07, _CRA_08, _CRA_09,
    ]
}
