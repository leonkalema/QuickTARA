"""
CRA Auto-Mapping Logic

Checks existing TARA artifacts for a product and auto-maps them
to CRA requirements. Returns which requirements have evidence
from existing work.

Enhanced to:
1. Auto-detect gaps (requirements without TARA coverage)
2. Auto-derive gap severity from damage scenario impact ratings
3. Suggest applicable compensating controls for gaps
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from sqlalchemy import text
from db.product_asset_models import (
    ProductScope, Asset, DamageScenario,
)


@dataclass
class MappedRequirement:
    """A single CRA requirement that was auto-mapped from TARA artifacts."""
    requirement_id: str
    status: str
    artifact_type: str
    artifact_count: int
    evidence_notes: str


@dataclass
class GapAnalysisResult:
    """Result of automated gap analysis for a CRA requirement."""
    requirement_id: str
    requirement_name: str
    has_coverage: bool
    gap_severity: str  # none, low, medium, high, critical
    severity_rationale: str
    suggested_controls: List[str]  # control_ids from catalog
    linked_artifacts: List[Dict]  # TARA artifacts providing evidence


# Map TARA impact ratings to CRA gap severity
IMPACT_TO_SEVERITY: Dict[str, str] = {
    "Negligible": "low",
    "Moderate": "medium",
    "Major": "high",
    "Severe": "critical",
}

# Map CRA requirements to what TARA artifacts can provide evidence
REQUIREMENT_EVIDENCE_MAP: Dict[str, Dict] = {
    "CRA-01": {"needs": ["asset"], "cia": None, "desc": "Secure default config"},
    "CRA-02": {"needs": ["asset"], "cia": None, "check": "authorization_required", "desc": "Access control"},
    "CRA-03": {"needs": ["asset"], "cia": "confidentiality", "desc": "Data confidentiality"},
    "CRA-04": {"needs": ["asset"], "cia": "integrity", "desc": "Data integrity"},
    "CRA-05": {"needs": ["asset"], "cia": None, "desc": "Data minimization"},
    "CRA-06": {"needs": ["asset"], "cia": "availability", "desc": "Availability"},
    "CRA-07": {"needs": ["threat_scenario"], "cia": None, "desc": "Attack surface"},
    "CRA-08": {"needs": ["asset"], "cia": None, "desc": "Security monitoring"},
    "CRA-09": {"needs": ["damage_scenario", "threat_scenario"], "cia": None, "desc": "Vuln remediation"},
    "CRA-10": {"needs": ["sbom"], "cia": None, "desc": "SBOM"},  # Usually not in TARA
    "CRA-11": {"needs": ["process"], "cia": None, "desc": "Vuln handling"},  # Process
    "CRA-12": {"needs": ["process"], "cia": None, "desc": "Security testing"},  # Process
    "CRA-13": {"needs": ["process"], "cia": None, "desc": "Disclosure"},  # Process
    "CRA-14": {"needs": ["process"], "cia": None, "desc": "24h reporting"},  # Process
    "CRA-15": {"needs": ["product_scope", "asset"], "cia": None, "desc": "Tech docs"},
    "CRA-16": {"needs": ["declaration"], "cia": None, "desc": "DoC"},  # Manual
    "CRA-17": {"needs": ["documentation"], "cia": None, "desc": "User info"},  # Manual
    "CRA-18": {"needs": ["declaration"], "cia": None, "desc": "CE marking"},  # Manual
}

# Map CRA requirements to applicable compensating controls
REQUIREMENT_TO_CONTROLS: Dict[str, List[str]] = {
    "CRA-02": ["CC-NET-001", "CC-GW-001"],  # Access control → network seg, gateway
    "CRA-03": ["CC-NET-001"],  # Confidentiality → network seg
    "CRA-04": ["CC-GW-001", "CC-IDS-001"],  # Integrity → gateway, IDS
    "CRA-06": ["CC-NET-001", "CC-IDS-001"],  # Availability → network seg, IDS
    "CRA-07": ["CC-GW-001", "CC-NET-001"],  # Attack surface → gateway, network
    "CRA-08": ["CC-MON-001", "CC-IDS-001"],  # Monitoring → monitoring, IDS
    "CRA-09": ["CC-VULN-001"],  # Vuln remediation → vuln monitoring
    "CRA-10": ["CC-SBOM-001"],  # SBOM → manual SBOM
    "CRA-11": ["CC-VULN-001", "CC-DISC-001"],  # Vuln handling → monitoring, disclosure
    "CRA-14": ["CC-DISC-001"],  # 24h reporting → disclosure
}


# Master list of 18 CRA requirements — sourced from EU 2024/2847
#
# annex_part mapping:
#   "Part I"             = Annex I Part I: product security properties (risk-based, §1-10)
#   "Part II"            = Annex I Part II: vulnerability handling capabilities (mandatory, §1-8)
#   "Art. 14 Obligation" = Art. 14 procedural reporting obligations (NOT in Annex I)
#   "Documentation"      = conformity assessment, technical docs, CE marking
#
# Annex I Part I coverage:  §1(no known exploitable vulns)+§10(update capability) → CRA-09
#                            §2(secure default) → CRA-01, §3(access ctrl) → CRA-02
#                            §4(confidentiality) → CRA-03, §5(integrity) → CRA-04
#                            §6(data minimisation) → CRA-05, §7(availability) → CRA-06
#                            §8(attack surface) → CRA-07, §9(monitoring) → CRA-08
# Annex I Part II coverage: §1(SBOM+3rd-party) → CRA-10, §2(remediation) → CRA-11
#                            §3(testing) → CRA-12, §4+§5+§6(disclosure+CVD+contact) → CRA-13
#                            §7+§8(update distrib+auto patch) → CRA-09 sub-requirements
#
# obligation_type: "risk_based" = manufacturer applies based on risk assessment
#                  "mandatory"  = applies regardless of risk assessment
CRA_REQUIREMENTS: List[Dict[str, str]] = [
    {"id": "CRA-01", "name": "Secure by default configuration",        "article": "Annex I Part I §2",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-02", "name": "Access control and authentication",      "article": "Annex I Part I §3",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-03", "name": "Data confidentiality (encryption)",      "article": "Annex I Part I §4",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-04", "name": "Data integrity protection",              "article": "Annex I Part I §5",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-05", "name": "Data minimization",                      "article": "Annex I Part I §6",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-06", "name": "Availability and resilience",            "article": "Annex I Part I §7",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-07", "name": "Attack surface limitation",              "article": "Annex I Part I §8",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-08", "name": "Security monitoring and logging",        "article": "Annex I Part I §9",       "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-09", "name": "Vulnerability remediation capability",   "article": "Annex I Part I §1 & §10", "category": "technical",      "annex_part": "Part I",             "obligation_type": "risk_based"},
    {"id": "CRA-10", "name": "Software Bill of Materials (SBOM)",      "article": "Annex I Part II §1",      "category": "process",        "annex_part": "Part II",            "obligation_type": "mandatory"},
    {"id": "CRA-11", "name": "Vulnerability handling process",         "article": "Annex I Part II §2",      "category": "process",        "annex_part": "Part II",            "obligation_type": "mandatory"},
    {"id": "CRA-12", "name": "Security testing program",               "article": "Annex I Part II §3",      "category": "process",        "annex_part": "Part II",            "obligation_type": "mandatory"},
    {"id": "CRA-13", "name": "Public vulnerability disclosure",        "article": "Annex I Part II §4-6",    "category": "process",        "annex_part": "Part II",            "obligation_type": "mandatory"},
    {"id": "CRA-14", "name": "24-hour vulnerability reporting",        "article": "Art. 14(4-8)",            "category": "process",        "annex_part": "Art. 14 Obligation", "obligation_type": "mandatory"},
    {"id": "CRA-15", "name": "Technical documentation (Annex VII)",    "article": "Art. 28 / Annex VII",     "category": "documentation",  "annex_part": "Documentation",      "obligation_type": "mandatory"},
    {"id": "CRA-16", "name": "EU Declaration of Conformity",           "article": "Art. 28 / Annex V",       "category": "documentation",  "annex_part": "Documentation",      "obligation_type": "mandatory"},
    {"id": "CRA-17", "name": "User information and instructions",      "article": "Art. 13 / Annex II",      "category": "documentation",  "annex_part": "Documentation",      "obligation_type": "mandatory"},
    {"id": "CRA-18", "name": "CE marking",                             "article": "Art. 28-30",              "category": "documentation",  "annex_part": "Documentation",      "obligation_type": "mandatory"},
]


def get_requirement_by_id(requirement_id: str) -> Optional[Dict[str, str]]:
    """Look up a CRA requirement by its ID."""
    for req in CRA_REQUIREMENTS:
        if req["id"] == requirement_id:
            return req
    return None


def auto_map_tara_to_cra(
    db: Session,
    product_id: str,
) -> List[MappedRequirement]:
    """
    Inspect existing TARA artifacts for a product and return
    auto-mapped CRA requirement statuses.

    Only maps requirements where real evidence exists.
    Requirements without evidence are left as not_started.
    """
    mappings: List[MappedRequirement] = []

    product = db.query(ProductScope).filter(
        ProductScope.scope_id == product_id
    ).first()
    if not product:
        return mappings

    asset_count = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
    ).count()

    damage_count = db.query(DamageScenario).filter(
        DamageScenario.scope_id == product_id,
    ).count()

    threat_result = db.execute(text(
        "SELECT COUNT(*) FROM threat_scenarios ts "
        "JOIN damage_scenarios ds ON ts.damage_scenario_id = ds.scenario_id "
        "WHERE ds.scope_id = :pid"
    ), {"pid": product_id})
    threat_count = threat_result.scalar() or 0

    # Check CIA coverage from assets
    assets_with_high_c = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
        Asset.confidentiality == "High",
    ).count()

    assets_with_high_i = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
        Asset.integrity == "High",
    ).count()

    assets_with_high_a = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
        Asset.availability == "High",
    ).count()

    # CRA-02: Access control — if assets have authorization_required
    auth_assets = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
        Asset.authorization_required == True,
    ).count()
    if auth_assets > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-02",
            status="partial",
            artifact_type="asset",
            artifact_count=auth_assets,
            evidence_notes=(
                f"{auth_assets} asset(s) require authorization — "
                "access control requirements documented"
            ),
        ))

    # CRA-03: Confidentiality — assets with High confidentiality
    if assets_with_high_c > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-03",
            status="partial",
            artifact_type="asset",
            artifact_count=assets_with_high_c,
            evidence_notes=(
                f"{assets_with_high_c} asset(s) rated High confidentiality "
                "— encryption requirements identified"
            ),
        ))

    # CRA-04: Integrity — assets with High integrity
    if assets_with_high_i > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-04",
            status="partial",
            artifact_type="asset",
            artifact_count=assets_with_high_i,
            evidence_notes=(
                f"{assets_with_high_i} asset(s) rated High integrity "
                "— integrity protection requirements identified"
            ),
        ))

    # CRA-06: Availability — assets with High availability
    if assets_with_high_a > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-06",
            status="partial",
            artifact_type="asset",
            artifact_count=assets_with_high_a,
            evidence_notes=(
                f"{assets_with_high_a} asset(s) rated High availability "
                "— resilience requirements identified"
            ),
        ))

    # CRA-07: Attack surface — if threat scenarios exist
    if threat_count > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-07",
            status="partial",
            artifact_type="threat_scenario",
            artifact_count=threat_count,
            evidence_notes=(
                f"{threat_count} threat scenario(s) documented "
                "— attack surface analyzed"
            ),
        ))

    # CRA-09: Vulnerability remediation — if damage + threat exist
    if damage_count > 0 and threat_count > 0:
        mappings.append(MappedRequirement(
            requirement_id="CRA-09",
            status="partial",
            artifact_type="damage_scenario",
            artifact_count=damage_count,
            evidence_notes=(
                f"{damage_count} damage and {threat_count} threat "
                "scenario(s) — risk treatment context available"
            ),
        ))

    # CRA-15: Technical documentation — product scope exists
    mappings.append(MappedRequirement(
        requirement_id="CRA-15",
        status="partial",
        artifact_type="product_scope",
        artifact_count=1,
        evidence_notes=(
            f"Product scope defined with {asset_count} asset(s), "
            f"{damage_count} damage scenario(s) — "
            "TARA documentation exists"
        ),
    ))

    return mappings


def get_max_impact_from_damage_scenarios(
    db: Session,
    product_id: str,
) -> Tuple[str, str]:
    """
    Get the maximum impact rating from damage scenarios for a product.
    Returns (impact_level, rationale).
    """
    scenarios = db.query(DamageScenario).filter(
        DamageScenario.scope_id == product_id,
    ).all()
    
    if not scenarios:
        return ("medium", "No damage scenarios defined - defaulting to medium")
    
    impact_order = ["Severe", "Major", "Moderate", "Negligible"]
    max_impact = "Negligible"
    max_scenario = None
    
    for scenario in scenarios:
        impact = getattr(scenario, 'safety_impact', None) or \
                 getattr(scenario, 'financial_impact', None) or \
                 getattr(scenario, 'operational_impact', None) or "Negligible"
        
        if impact in impact_order:
            if impact_order.index(impact) < impact_order.index(max_impact):
                max_impact = impact
                max_scenario = scenario
    
    severity = IMPACT_TO_SEVERITY.get(max_impact, "medium")
    rationale = f"Derived from damage scenario: {max_scenario.name if max_scenario else 'N/A'} (Impact: {max_impact})"
    
    return (severity, rationale)


def analyze_gaps(
    db: Session,
    product_id: str,
) -> List[GapAnalysisResult]:
    """
    Perform automated gap analysis for all CRA requirements.
    
    For each requirement:
    1. Check if TARA artifacts provide evidence
    2. If no evidence → flag as gap
    3. Derive gap severity from damage scenario impact ratings
    4. Suggest applicable compensating controls
    """
    results: List[GapAnalysisResult] = []
    
    mappings = auto_map_tara_to_cra(db, product_id)
    mapped_req_ids = {m.requirement_id for m in mappings}
    
    base_severity, severity_rationale = get_max_impact_from_damage_scenarios(db, product_id)
    
    asset_count = db.query(Asset).filter(
        Asset.scope_id == product_id,
        Asset.is_current == True,
    ).count()
    
    for req in CRA_REQUIREMENTS:
        req_id = req["id"]
        has_coverage = req_id in mapped_req_ids
        
        linked_artifacts = []
        mapping = next((m for m in mappings if m.requirement_id == req_id), None)
        if mapping:
            linked_artifacts.append({
                "type": mapping.artifact_type,
                "count": mapping.artifact_count,
                "notes": mapping.evidence_notes,
            })
        
        if has_coverage:
            gap_severity = "none"
            rationale = "Covered by TARA artifacts"
        else:
            evidence_info = REQUIREMENT_EVIDENCE_MAP.get(req_id, {})
            needs = evidence_info.get("needs", [])
            
            if any(n in ["process", "declaration", "documentation", "sbom"] for n in needs):
                gap_severity = "medium"
                rationale = "Process/documentation gap - requires organizational action"
            else:
                gap_severity = base_severity
                rationale = severity_rationale
        
        suggested_controls = REQUIREMENT_TO_CONTROLS.get(req_id, [])
        
        results.append(GapAnalysisResult(
            requirement_id=req_id,
            requirement_name=req["name"],
            has_coverage=has_coverage,
            gap_severity=gap_severity,
            severity_rationale=rationale,
            suggested_controls=suggested_controls,
            linked_artifacts=linked_artifacts,
        ))
    
    return results
