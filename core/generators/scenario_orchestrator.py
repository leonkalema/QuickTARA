"""
Scenario orchestrator for QuickTARA.
Coordinates the full auto-generation pipeline: assets → damage scenarios → threat scenarios.

Purpose: Single entry point for generating all scenarios for a product's assets
Depends on: core/generators/damage_scenario_generator.py, core/generators/threat_scenario_generator.py
Used by: api/routes/analysis.py (or dedicated generation endpoint)
"""
import logging
from datetime import datetime
from typing import Dict, List, Any

from sqlalchemy.orm import Session

from db.product_asset_models import (
    Asset as DBAsset,
    DamageScenario as DBDamageScenario,
    ProductScope as DBProductScope,
)
from core.generators.damage_scenario_generator import (
    generate_for_asset,
    load_templates,
)
from core.generators.threat_scenario_generator import (
    find_matching_catalog_threats,
    generate_threat_scenarios,
)

logger = logging.getLogger(__name__)


def generate_scenarios_for_product(
    db: Session,
    scope_id: str,
) -> Dict[str, Any]:
    """
    Auto-generate damage scenarios and threat scenarios for all assets in a product.
    Returns a summary of what was generated.
    """
    product = _get_product(db, scope_id)
    if not product:
        return {"error": f"Product '{scope_id}' not found"}

    assets = _get_assets(db, scope_id)
    if not assets:
        return {"error": "No assets found for this product", "scope_id": scope_id}

    templates = load_templates()
    product_name = product.name
    trust_zone = product.trust_zone

    all_damage: List[Dict[str, Any]] = []
    all_threats: List[Dict[str, Any]] = []

    for asset in assets:
        asset_dict = _asset_to_dict(asset)

        damage_scenarios = generate_for_asset(asset_dict, product_name, templates)
        all_damage.extend(damage_scenarios)

        matched_threats = find_matching_catalog_threats(db, asset_dict, trust_zone)
        threat_scenarios = generate_threat_scenarios(
            matched_threats, damage_scenarios, asset_dict, scope_id,
        )
        all_threats.extend(threat_scenarios)

    damage_saved = _save_damage_scenarios(db, all_damage, scope_id)
    threat_saved = _save_threat_scenarios(db, all_threats)

    logger.info(
        "Auto-generated %d damage + %d threat scenarios for product '%s'",
        damage_saved, threat_saved, scope_id,
    )

    return {
        "scope_id": scope_id,
        "product_name": product_name,
        "assets_processed": len(assets),
        "damage_scenarios_created": damage_saved,
        "threat_scenarios_created": threat_saved,
        "damage_scenarios": all_damage,
        "threat_scenarios": all_threats,
    }


def _get_product(db: Session, scope_id: str):
    """Fetch the current product scope."""
    return (
        db.query(DBProductScope)
        .filter(DBProductScope.scope_id == scope_id, DBProductScope.is_current == True)
        .first()
    )


def _get_assets(db: Session, scope_id: str) -> List[DBAsset]:
    """Fetch all current assets for a product."""
    return (
        db.query(DBAsset)
        .filter(DBAsset.scope_id == scope_id, DBAsset.is_current == True)
        .all()
    )


def _asset_to_dict(asset: DBAsset) -> Dict[str, Any]:
    """Convert a DB asset to a dict for the generators."""
    return {
        "asset_id": asset.asset_id,
        "name": asset.name,
        "description": asset.description,
        "asset_type": asset.asset_type,
        "scope_id": asset.scope_id,
        "confidentiality": asset.confidentiality,
        "integrity": asset.integrity,
        "availability": asset.availability,
    }


def _save_damage_scenarios(
    db: Session,
    scenarios: List[Dict[str, Any]],
    scope_id: str,
) -> int:
    """Persist auto-generated damage scenarios to the database."""
    saved = 0
    for s in scenarios:
        db_scenario = DBDamageScenario(
            scenario_id=s["scenario_id"],
            name=s["name"],
            description=s["description"],
            damage_category=s["damage_category"],
            impact_type=s["impact_type"],
            severity=s["severity"],
            confidentiality_impact=s["confidentiality_impact"],
            integrity_impact=s["integrity_impact"],
            availability_impact=s["availability_impact"],
            safety_impact=s.get("safety_impact", "negligible"),
            financial_impact=s.get("financial_impact", "negligible"),
            operational_impact=s.get("operational_impact", "negligible"),
            privacy_impact=s.get("privacy_impact", "negligible"),
            scope_id=scope_id,
            primary_component_id=s.get("primary_component_id"),
            violated_properties=_build_violated_properties(s),
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(db_scenario)
        saved += 1

    db.flush()
    return saved


def _save_threat_scenarios(
    db: Session,
    scenarios: List[Dict[str, Any]],
) -> int:
    """Persist auto-generated threat scenarios to the database."""
    from db.threat_scenario import ThreatScenario as DBThreatScenario
    from sqlalchemy import text

    saved = 0
    for s in scenarios:
        db_scenario = DBThreatScenario(
            threat_scenario_id=s["threat_scenario_id"],
            name=s["name"],
            description=s["description"],
            attack_vector=s.get("attack_vector", ""),
            scope_id=s["scope_id"],
            scope_version=s.get("scope_version", 1),
            damage_scenario_id=s["damage_scenario_id"],
        )
        db.add(db_scenario)
        saved += 1

        # Link to additional damage scenarios via junction table
        for ds_id in s.get("damage_scenario_ids", [])[1:]:
            db.execute(
                text(
                    "INSERT OR IGNORE INTO threat_damage_links "
                    "(threat_scenario_id, damage_scenario_id) VALUES (:tid, :did)"
                ),
                {"tid": s["threat_scenario_id"], "did": ds_id},
            )

    db.commit()
    return saved


def _build_violated_properties(scenario: Dict[str, Any]) -> List[str]:
    """Build the violated_properties JSON list from CIA flags."""
    props: List[str] = []
    if scenario.get("confidentiality_impact"):
        props.append("Confidentiality")
    if scenario.get("integrity_impact"):
        props.append("Integrity")
    if scenario.get("availability_impact"):
        props.append("Availability")
    return props
