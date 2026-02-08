"""
Threat scenario generator for QuickTARA.
Matches threat catalog entries to assets and links them to damage scenarios.

Purpose: For each asset, find matching threats from the catalog and create threat scenarios
Depends on: core/generators/asset_type_mapper.py, db/threat_catalog.py
Used by: core/generators/scenario_orchestrator.py
"""
import logging
import uuid
from typing import Dict, List, Any

from sqlalchemy.orm import Session

from db.threat_catalog import ThreatCatalog
from core.generators.asset_type_mapper import (
    get_component_types,
    get_catalog_trust_zones,
)

logger = logging.getLogger(__name__)

MIN_RELEVANCE_SCORE = 2  # minimum automotive_relevance to include


def find_matching_catalog_threats(
    db: Session,
    asset: Dict[str, Any],
    product_trust_zone: str,
) -> List[ThreatCatalog]:
    """
    Query the threat catalog for entries matching the asset's type and trust zone.
    Returns ordered by automotive_relevance descending.
    """
    component_types = get_component_types(asset.get("asset_type", "Other"))
    catalog_zones = get_catalog_trust_zones(product_trust_zone)

    all_threats: List[ThreatCatalog] = (
        db.query(ThreatCatalog)
        .filter(ThreatCatalog.automotive_relevance >= MIN_RELEVANCE_SCORE)
        .order_by(ThreatCatalog.automotive_relevance.desc())
        .all()
    )

    matched: List[ThreatCatalog] = []
    for threat in all_threats:
        if _matches_asset(threat, component_types, catalog_zones):
            matched.append(threat)

    logger.debug(
        "Matched %d catalog threats for asset '%s' (types=%s, zones=%s)",
        len(matched), asset.get("name"), component_types, catalog_zones,
    )
    return matched


def generate_threat_scenarios(
    matched_threats: List[ThreatCatalog],
    damage_scenarios: List[Dict[str, Any]],
    asset: Dict[str, Any],
    scope_id: str,
) -> List[Dict[str, Any]]:
    """
    Create threat scenario dicts from matched catalog threats.
    Links each threat to the most relevant damage scenario(s) based on STRIDE↔CIA mapping.
    """
    threat_scenarios: List[Dict[str, Any]] = []

    for catalog_threat in matched_threats:
        linked_damage_ids = _find_linked_damage_scenarios(
            catalog_threat, damage_scenarios,
        )
        if not linked_damage_ids:
            continue

        scenario = _build_threat_scenario(
            catalog_threat, linked_damage_ids, asset, scope_id,
        )
        threat_scenarios.append(scenario)

    logger.debug(
        "Generated %d threat scenarios for asset '%s'",
        len(threat_scenarios), asset.get("name"),
    )
    return threat_scenarios


def _matches_asset(
    threat: ThreatCatalog,
    component_types: List[str],
    catalog_zones: List[str],
) -> bool:
    """Check if a catalog threat matches the asset's component types or trust zones."""
    threat_types = threat.applicable_component_types or []
    threat_zones = threat.applicable_trust_zones or []

    type_match = not threat_types or any(ct in threat_types for ct in component_types)
    zone_match = not threat_zones or any(tz in threat_zones for tz in catalog_zones)

    return type_match and zone_match


def _find_linked_damage_scenarios(
    catalog_threat: ThreatCatalog,
    damage_scenarios: List[Dict[str, Any]],
) -> List[str]:
    """
    Map a catalog threat to damage scenarios using STRIDE→CIA correspondence:
    - Spoofing, Information Disclosure → confidentiality
    - Tampering, Repudiation → integrity
    - Denial of Service → availability
    - Elevation of Privilege → integrity + confidentiality
    """
    stride = str(catalog_threat.stride_category).lower().replace(" ", "_")
    cia_dims = STRIDE_TO_CIA.get(stride, [])

    linked_ids: List[str] = []
    for ds in damage_scenarios:
        ds_dim = ds.get("cia_dimension", "")
        if ds_dim in cia_dims:
            linked_ids.append(ds["scenario_id"])

    return linked_ids


def _build_threat_scenario(
    catalog_threat: ThreatCatalog,
    damage_scenario_ids: List[str],
    asset: Dict[str, Any],
    scope_id: str,
) -> Dict[str, Any]:
    """Build a threat scenario dict from a catalog entry."""
    technique_id = catalog_threat.mitre_technique_id or ""
    title = catalog_threat.title
    name = f"[{technique_id}] {title}" if technique_id else title

    attack_vectors = catalog_threat.attack_vectors or []
    description = catalog_threat.automotive_context or catalog_threat.description or ""

    return {
        "threat_scenario_id": f"TS-AUTO-{uuid.uuid4().hex[:8]}",
        "name": name,
        "description": f"{description} (Target: {asset.get('name', 'Unknown')})",
        "attack_vector": ", ".join(attack_vectors),
        "scope_id": scope_id,
        "scope_version": 1,
        "damage_scenario_id": damage_scenario_ids[0],
        "damage_scenario_ids": damage_scenario_ids,
        "catalog_threat_id": catalog_threat.id,
        "mitre_technique_id": technique_id,
        "stride_category": str(catalog_threat.stride_category),
        "auto_generated": True,
    }


# STRIDE category → CIA dimension mapping
STRIDE_TO_CIA: Dict[str, List[str]] = {
    "spoofing": ["confidentiality", "integrity"],
    "tampering": ["integrity"],
    "repudiation": ["integrity"],
    "information_disclosure": ["confidentiality"],
    "denial_of_service": ["availability"],
    "elevation_of_privilege": ["integrity", "confidentiality"],
}
