"""
ISO/SAE 21434 Clause Mapping for TARA Artifacts

Maps each QuickTARA artifact type to its relevant ISO/SAE 21434 clauses,
work products, and requirements. Provides dynamic per-artifact traceability.

Reference: ISO/SAE 21434:2021 — Road vehicles — Cybersecurity engineering
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional


class ArtifactType(str, Enum):
    """TARA artifact types in QuickTARA."""
    PRODUCT_SCOPE = "product_scope"
    ASSET = "asset"
    DAMAGE_SCENARIO = "damage_scenario"
    THREAT_SCENARIO = "threat_scenario"
    ATTACK_PATH = "attack_path"
    RISK_ASSESSMENT = "risk_assessment"
    RISK_TREATMENT = "risk_treatment"
    CYBERSECURITY_GOAL = "cybersecurity_goal"


@dataclass(frozen=True)
class ClauseReference:
    """A single ISO/SAE 21434 clause reference."""
    clause_id: str
    clause_title: str
    work_product: str
    requirement_summary: str
    section: str  # e.g. "Clause 9 — Threat analysis and risk assessment"


# ── Complete clause mapping registry ──────────────────────────────────────
CLAUSE_REGISTRY: Dict[ArtifactType, List[ClauseReference]] = {
    ArtifactType.PRODUCT_SCOPE: [
        ClauseReference(
            clause_id="8.3",
            clause_title="Item definition",
            work_product="WP-08-01",
            requirement_summary="Define the item including boundaries, functions, "
                                "preliminary architecture, and operational environment.",
            section="Clause 8 — Threat analysis and risk assessment methods",
        ),
        ClauseReference(
            clause_id="8.5",
            clause_title="Cybersecurity relevance identification",
            work_product="WP-08-02",
            requirement_summary="Determine whether the item is cybersecurity-relevant "
                                "based on its connectivity and operational context.",
            section="Clause 8 — Threat analysis and risk assessment methods",
        ),
    ],
    ArtifactType.ASSET: [
        ClauseReference(
            clause_id="9.3",
            clause_title="Asset identification",
            work_product="WP-09-01",
            requirement_summary="Identify cybersecurity-relevant assets including "
                                "data, functions, and components with their CIA properties.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
    ],
    ArtifactType.DAMAGE_SCENARIO: [
        ClauseReference(
            clause_id="9.4",
            clause_title="Impact rating",
            work_product="WP-09-02",
            requirement_summary="Determine damage scenarios and rate their impact "
                                "on safety, financial, operational, and privacy dimensions.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.4.1",
            clause_title="Impact rating — Safety",
            work_product="WP-09-02",
            requirement_summary="Rate safety impact considering potential harm to "
                                "road users per ISO 26262 severity levels.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.4.2",
            clause_title="Impact rating — Financial",
            work_product="WP-09-02",
            requirement_summary="Rate financial impact considering direct and "
                                "indirect monetary consequences.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.4.3",
            clause_title="Impact rating — Operational",
            work_product="WP-09-02",
            requirement_summary="Rate operational impact on vehicle functions "
                                "and user experience.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.4.4",
            clause_title="Impact rating — Privacy",
            work_product="WP-09-02",
            requirement_summary="Rate privacy impact considering personal data "
                                "exposure and regulatory consequences.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
    ],
    ArtifactType.THREAT_SCENARIO: [
        ClauseReference(
            clause_id="9.5",
            clause_title="Threat scenario identification",
            work_product="WP-09-03",
            requirement_summary="Identify threat scenarios that could lead to the "
                                "identified damage scenarios, including attack vectors.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.6",
            clause_title="Attack feasibility rating",
            work_product="WP-09-04",
            requirement_summary="Rate the feasibility of each threat scenario "
                                "using an attack-potential-based or CVSS approach.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
    ],
    ArtifactType.ATTACK_PATH: [
        ClauseReference(
            clause_id="9.5",
            clause_title="Attack path analysis",
            work_product="WP-09-03",
            requirement_summary="Identify and document attack paths showing how "
                                "threat scenarios can be realized through the architecture.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.6",
            clause_title="Attack feasibility rating",
            work_product="WP-09-04",
            requirement_summary="Assess attack feasibility considering elapsed time, "
                                "specialist expertise, knowledge, window of opportunity, "
                                "and equipment.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
    ],
    ArtifactType.RISK_ASSESSMENT: [
        ClauseReference(
            clause_id="9.7",
            clause_title="Risk value determination",
            work_product="WP-09-05",
            requirement_summary="Determine risk values by combining impact rating "
                                "and attack feasibility for each threat scenario.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="9.8",
            clause_title="Risk treatment decision",
            work_product="WP-09-05",
            requirement_summary="Decide on risk treatment option: avoiding, reducing, "
                                "sharing, or retaining each identified risk.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
    ],
    ArtifactType.RISK_TREATMENT: [
        ClauseReference(
            clause_id="9.8",
            clause_title="Risk treatment decision",
            work_product="WP-09-06",
            requirement_summary="Document the selected risk treatment strategy and "
                                "justification for each risk.",
            section="Clause 9 — Threat analysis and risk assessment",
        ),
        ClauseReference(
            clause_id="14",
            clause_title="Risk acceptance",
            work_product="WP-14-01",
            requirement_summary="Formally accept residual risks with documented "
                                "criteria, justification, and stakeholder approval.",
            section="Clause 14 — Cybersecurity risk management",
        ),
    ],
    ArtifactType.CYBERSECURITY_GOAL: [
        ClauseReference(
            clause_id="10.4",
            clause_title="Cybersecurity goals",
            work_product="WP-10-01",
            requirement_summary="Define cybersecurity goals derived from threat "
                                "scenarios with associated CALs.",
            section="Clause 10 — Concept phase",
        ),
        ClauseReference(
            clause_id="10.4.1",
            clause_title="Cybersecurity claims",
            work_product="WP-10-01",
            requirement_summary="Establish cybersecurity claims that support each "
                                "cybersecurity goal.",
            section="Clause 10 — Concept phase",
        ),
    ],
}


def get_clauses_for_artifact(artifact_type: ArtifactType) -> List[ClauseReference]:
    """Return all ISO 21434 clauses mapped to the given artifact type."""
    return CLAUSE_REGISTRY.get(artifact_type, [])


def get_clause_ids_for_artifact(artifact_type: ArtifactType) -> List[str]:
    """Return just the clause IDs (e.g. ['9.4', '9.4.1']) for an artifact type."""
    return [c.clause_id for c in get_clauses_for_artifact(artifact_type)]


def get_work_products_for_artifact(artifact_type: ArtifactType) -> FrozenSet[str]:
    """Return unique work product IDs for an artifact type."""
    return frozenset(c.work_product for c in get_clauses_for_artifact(artifact_type))


def get_all_mappings() -> Dict[str, List[Dict[str, str]]]:
    """Return the full mapping as a serializable dict for API responses."""
    result: Dict[str, List[Dict[str, str]]] = {}
    for artifact_type, clauses in CLAUSE_REGISTRY.items():
        result[artifact_type.value] = [
            {
                "clause_id": c.clause_id,
                "clause_title": c.clause_title,
                "work_product": c.work_product,
                "requirement_summary": c.requirement_summary,
                "section": c.section,
            }
            for c in clauses
        ]
    return result


def format_clause_badge(clause: ClauseReference) -> str:
    """Format a clause reference as a short badge string for UI display."""
    return f"§{clause.clause_id} ({clause.work_product})"


def format_artifact_compliance_summary(artifact_type: ArtifactType) -> str:
    """Return a human-readable compliance summary for an artifact type."""
    clauses = get_clauses_for_artifact(artifact_type)
    if not clauses:
        return "No ISO/SAE 21434 clause mapping defined."
    lines = [f"ISO/SAE 21434 Compliance — {artifact_type.value}:"]
    for c in clauses:
        lines.append(f"  • §{c.clause_id} {c.clause_title} [{c.work_product}]")
        lines.append(f"    {c.requirement_summary}")
    return "\n".join(lines)
