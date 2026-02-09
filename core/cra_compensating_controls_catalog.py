"""
Pre-approved Compensating Controls Catalog for Legacy Products

Sourced from: docs/CRA/compensating-controls-catalog.md
Used by: api/routes/cra.py (frontend populates from this list)
"""
from typing import List, Dict, Optional


COMPENSATING_CONTROLS_CATALOG: List[Dict] = [
    {
        "control_id": "CC-DIAG-001",
        "name": "Diagnostic Interface Restriction",
        "category": "Diagnostic Interface",
        "description": (
            "Restrict UDS/OBD access to authenticated diagnostic tools only. "
            "Disable or filter security-sensitive services (e.g., 0x27, 0x2E, 0x31) "
            "when accessed outside authorized maintenance sessions."
        ),
        "applicability": "All legacy ECUs with diagnostic ports",
        "limitations": "Does not protect against physical hardware attacks",
        "applicable_requirements": ["CRA-02", "CRA-04", "CRA-07"],
    },
    {
        "control_id": "CC-DIAG-002",
        "name": "Session Timeout Enforcement",
        "category": "Diagnostic Interface",
        "description": (
            "Enforce automatic timeout of diagnostic sessions after configurable "
            "inactivity period. Re-authentication required after timeout."
        ),
        "applicability": "ECUs supporting extended diagnostic sessions",
        "limitations": "Timeout window still vulnerable during active session",
        "applicable_requirements": ["CRA-02", "CRA-07"],
    },
    {
        "control_id": "CC-NET-001",
        "name": "CAN Gateway Filtering",
        "category": "Network Containment",
        "description": (
            "Deploy or configure CAN gateway to filter, rate-limit, and validate "
            "messages to/from the legacy ECU. Block unexpected CAN IDs and enforce "
            "message frequency limits."
        ),
        "applicability": "Legacy ECUs on CAN bus networks",
        "limitations": "Requires gateway hardware; does not protect intra-segment traffic",
        "applicable_requirements": ["CRA-04", "CRA-06", "CRA-07"],
    },
    {
        "control_id": "CC-NET-002",
        "name": "Network Segmentation",
        "category": "Network Containment",
        "description": (
            "Isolate legacy ECU onto a dedicated network segment with controlled "
            "ingress/egress points. Minimize direct connectivity to external-facing "
            "interfaces."
        ),
        "applicability": "Vehicle architectures supporting domain separation",
        "limitations": "May require hardware changes; functional dependencies may limit isolation",
        "applicable_requirements": ["CRA-03", "CRA-06", "CRA-07"],
    },
    {
        "control_id": "CC-NET-003",
        "name": "Rate Limiting and Anomaly Detection",
        "category": "Network Containment",
        "description": (
            "Implement message rate limiting at the gateway level and deploy "
            "anomaly detection for unexpected traffic patterns targeting the legacy ECU."
        ),
        "applicability": "Networks with gateway or IDS capability",
        "limitations": "Detection-only; does not prevent initial attack attempts",
        "applicable_requirements": ["CRA-06", "CRA-07", "CRA-08"],
    },
    {
        "control_id": "CC-MON-001",
        "name": "External Monitoring Agent",
        "category": "Monitoring",
        "description": (
            "Deploy an external monitoring agent (separate ECU or gateway function) "
            "that observes the legacy ECU's communication patterns and flags deviations "
            "from expected behavior."
        ),
        "applicability": "Any legacy ECU with observable network traffic",
        "limitations": "Cannot detect internal firmware compromise without external symptoms",
        "applicable_requirements": ["CRA-08", "CRA-06"],
    },
    {
        "control_id": "CC-MON-002",
        "name": "Periodic Integrity Verification",
        "category": "Monitoring",
        "description": (
            "Implement periodic challenge-response or checksum verification of the "
            "legacy ECU's firmware integrity from an external trusted entity."
        ),
        "applicability": "ECUs supporting basic diagnostic read commands",
        "limitations": "Verification frequency limited; sophisticated rootkits may evade",
        "applicable_requirements": ["CRA-04", "CRA-08"],
    },
    {
        "control_id": "CC-ACC-001",
        "name": "Physical Access Restriction",
        "category": "Access Control",
        "description": (
            "Document and enforce physical access restrictions to the legacy ECU. "
            "Tamper-evident seals, locked enclosures, or restricted service bay access."
        ),
        "applicability": "All legacy ECUs",
        "limitations": "Organizational control; depends on enforcement discipline",
        "applicable_requirements": ["CRA-02", "CRA-04"],
    },
    {
        "control_id": "CC-ACC-002",
        "name": "Service Tool Authentication",
        "category": "Access Control",
        "description": (
            "Require authenticated service tools for any interaction with the legacy ECU. "
            "Implement tool certificate validation at the gateway level."
        ),
        "applicability": "Service environments with controlled tool deployment",
        "limitations": "Does not protect against compromised authorized tools",
        "applicable_requirements": ["CRA-02", "CRA-07"],
    },
    {
        "control_id": "CC-DOC-001",
        "name": "Technical Justification Memo",
        "category": "Documentation",
        "description": (
            "Formal documented justification under CRA Art. 5(3) explaining why the "
            "legacy product cannot meet specific requirements, what compensating controls "
            "are in place, and the residual risk assessment."
        ),
        "applicability": "All Bucket C legacy products",
        "limitations": "Documentation only; does not reduce technical risk",
        "applicable_requirements": ["CRA-15", "CRA-16"],
    },
    {
        "control_id": "CC-DOC-002",
        "name": "End-of-Security-Support Declaration",
        "category": "Documentation",
        "description": (
            "Formal declaration of the End-of-Security-Support (EoSS) date for the "
            "legacy product, communicated to customers with migration path guidance."
        ),
        "applicability": "All legacy products approaching end of support",
        "limitations": "Relies on customer action to migrate",
        "applicable_requirements": ["CRA-09", "CRA-11", "CRA-17"],
    },
    {
        "control_id": "CC-SUP-001",
        "name": "Supply Chain Notification",
        "category": "Supply Chain",
        "description": (
            "Notify downstream OEMs/integrators of known vulnerabilities in the legacy "
            "component and provide recommended compensating controls for their integration."
        ),
        "applicability": "Tier-1/Tier-2 suppliers with legacy components in active vehicles",
        "limitations": "OEM must implement recommendations; no enforcement mechanism",
        "applicable_requirements": ["CRA-11", "CRA-13", "CRA-14"],
    },
    {
        "control_id": "CC-SBOM-001",
        "name": "Manual SBOM Generation",
        "category": "Documentation",
        "description": (
            "Generate a Software Bill of Materials for the legacy component through "
            "manual analysis of firmware, libraries, and dependencies. Document known "
            "components and their versions."
        ),
        "applicability": "All legacy products with software components",
        "limitations": "May be incomplete for deeply embedded or obfuscated code",
        "applicable_requirements": ["CRA-10"],
    },
    {
        "control_id": "CC-VULN-001",
        "name": "Vulnerability Monitoring Service",
        "category": "Process",
        "description": (
            "Subscribe to vulnerability feeds (NVD, CERT, vendor advisories) and "
            "maintain active monitoring for CVEs affecting the legacy component's "
            "known software dependencies."
        ),
        "applicability": "All legacy products with known SBOM",
        "limitations": "Dependent on SBOM completeness; zero-days not covered",
        "applicable_requirements": ["CRA-11", "CRA-13", "CRA-14"],
    },
]


def get_catalog() -> List[Dict[str, str]]:
    """Return the full compensating controls catalog."""
    return COMPENSATING_CONTROLS_CATALOG


def get_control_by_id(control_id: str) -> Optional[Dict[str, str]]:
    """Look up a control by its catalog ID."""
    for ctrl in COMPENSATING_CONTROLS_CATALOG:
        if ctrl["control_id"] == control_id:
            return ctrl
    return None


def get_controls_by_category(category: str) -> List[Dict[str, str]]:
    """Get all controls in a given category."""
    return [c for c in COMPENSATING_CONTROLS_CATALOG if c["category"] == category]
