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

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.product_asset_models import (
    Asset as DBAsset,
    DamageScenario as DBDamageScenario,
    ProductScope as DBProductScope,
    asset_damage_scenario,
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

AUTO_PREFIX_DAMAGE = "DS-AUTO-"
AUTO_PREFIX_THREAT = "TS-AUTO-"


def preview_damage_generation(
    db: Session,
    scope_id: str,
) -> Dict[str, Any]:
    """Preview how many damage scenarios would be generated (no DB writes)."""
    product = _get_product(db, scope_id)
    if not product:
        return {"error": f"Product '{scope_id}' not found"}
    assets = _get_assets(db, scope_id)
    if not assets:
        return {"error": "No assets found for this product"}
    templates = load_templates()
    count = 0
    for asset in assets:
        count += len(generate_for_asset(_asset_to_dict(asset), product.name, templates))
    existing_drafts = _count_auto_damage_drafts(db, scope_id)
    return {
        "scope_id": scope_id,
        "product_name": product.name,
        "assets_count": len(assets),
        "scenarios_to_generate": count,
        "existing_drafts": existing_drafts,
    }


def generate_damage_scenarios_for_product(
    db: Session,
    scope_id: str,
) -> Dict[str, Any]:
    """
    Step 1: Generate damage scenarios from assets based on CIA properties.
    Deletes previous auto-generated drafts first to avoid duplicates.
    All-or-nothing: rolls back on any failure.
    """
    product = _get_product(db, scope_id)
    if not product:
        return {"error": f"Product '{scope_id}' not found"}
    assets = _get_assets(db, scope_id)
    if not assets:
        return {"error": "No assets found for this product", "scope_id": scope_id}
    templates = load_templates()
    all_damage: List[Dict[str, Any]] = []
    for asset in assets:
        asset_dict = _asset_to_dict(asset)
        damage_scenarios = generate_for_asset(asset_dict, product.name, templates)
        all_damage.extend(damage_scenarios)
    try:
        drafts_removed = _remove_auto_damage_drafts(db, scope_id)
        damage_saved = _save_damage_scenarios(db, all_damage, scope_id)
        db.commit()
    except Exception:
        db.rollback()
        raise
    logger.info(
        "Auto-generated %d damage scenarios for product '%s' (removed %d old drafts)",
        damage_saved, scope_id, drafts_removed,
    )
    return {
        "scope_id": scope_id,
        "product_name": product.name,
        "assets_processed": len(assets),
        "damage_scenarios_created": damage_saved,
        "drafts_replaced": drafts_removed,
    }


def generate_threat_scenarios_for_product(
    db: Session,
    scope_id: str,
) -> Dict[str, Any]:
    """
    Step 2: Generate threat scenarios from existing damage scenarios
    by matching the threat catalog. Deletes previous auto-generated drafts first.
    All-or-nothing: rolls back on any failure.
    """
    product = _get_product(db, scope_id)
    if not product:
        return {"error": f"Product '{scope_id}' not found"}
    assets = _get_assets(db, scope_id)
    if not assets:
        return {"error": "No assets found for this product", "scope_id": scope_id}
    existing_damage = _get_existing_damage_scenarios(db, scope_id)
    if not existing_damage:
        return {"error": "No damage scenarios found. Generate damage scenarios first.", "scope_id": scope_id}
    all_threats: List[Dict[str, Any]] = []
    for asset in assets:
        asset_dict = _asset_to_dict(asset)
        asset_damage = _filter_damage_for_asset(existing_damage, asset_dict["asset_id"])
        if not asset_damage:
            continue
        matched_threats = find_matching_catalog_threats(db, asset_dict, product.trust_zone)
        threat_scenarios = generate_threat_scenarios(
            matched_threats, asset_damage, asset_dict, scope_id,
        )
        all_threats.extend(threat_scenarios)
    try:
        drafts_removed = _remove_auto_threat_drafts(db, scope_id)
        threat_saved = _save_threat_scenarios(db, all_threats)
        db.commit()
    except Exception:
        db.rollback()
        raise
    logger.info(
        "Auto-generated %d threat scenarios for product '%s' (removed %d old drafts)",
        threat_saved, scope_id, drafts_removed,
    )
    return {
        "scope_id": scope_id,
        "product_name": product.name,
        "assets_processed": len(assets),
        "damage_scenarios_used": len(existing_damage),
        "threat_scenarios_created": threat_saved,
        "drafts_replaced": drafts_removed,
    }


def generate_scenarios_for_product(
    db: Session,
    scope_id: str,
) -> Dict[str, Any]:
    """Convenience: run both steps in sequence."""
    damage_result = generate_damage_scenarios_for_product(db, scope_id)
    if damage_result.get("error"):
        return damage_result
    threat_result = generate_threat_scenarios_for_product(db, scope_id)
    return {
        "scope_id": scope_id,
        "product_name": damage_result.get("product_name", ""),
        "assets_processed": damage_result.get("assets_processed", 0),
        "damage_scenarios_created": damage_result.get("damage_scenarios_created", 0),
        "threat_scenarios_created": threat_result.get("threat_scenarios_created", 0),
    }


def _count_auto_damage_drafts(db: Session, scope_id: str) -> int:
    """Count existing auto-generated damage drafts for a product."""
    return (
        db.query(DBDamageScenario)
        .filter(
            DBDamageScenario.scope_id == scope_id,
            DBDamageScenario.scenario_id.like(f"{AUTO_PREFIX_DAMAGE}%"),
            DBDamageScenario.status == "draft",
        )
        .count()
    )


def _remove_auto_damage_drafts(db: Session, scope_id: str) -> int:
    """Delete previous auto-generated damage drafts (not accepted ones).
    Uses raw SQL to avoid ORM relationship cascade issues."""
    params = {"sid": scope_id, "prefix": f"{AUTO_PREFIX_DAMAGE}%"}
    count_row = db.execute(
        text(
            "SELECT COUNT(*) FROM damage_scenarios "
            "WHERE scope_id = :sid AND scenario_id LIKE :prefix AND status = 'draft'"
        ),
        params,
    ).scalar() or 0
    # Remove M2M links first
    db.execute(
        text(
            "DELETE FROM asset_damage_scenario WHERE scenario_id IN "
            "(SELECT scenario_id FROM damage_scenarios "
            " WHERE scope_id = :sid AND scenario_id LIKE :prefix AND status = 'draft')"
        ),
        params,
    )
    # Remove the damage scenario rows
    db.execute(
        text(
            "DELETE FROM damage_scenarios "
            "WHERE scope_id = :sid AND scenario_id LIKE :prefix AND status = 'draft'"
        ),
        params,
    )
    return int(count_row)


def _remove_auto_threat_drafts(db: Session, scope_id: str) -> int:
    """Delete previous auto-generated threat drafts (not accepted ones).
    Uses raw SQL to avoid ORM relationship cascade issues."""
    params = {"sid": scope_id, "prefix": f"{AUTO_PREFIX_THREAT}%"}
    count_row = db.execute(
        text(
            "SELECT COUNT(*) FROM threat_scenarios "
            "WHERE scope_id = :sid AND threat_scenario_id LIKE :prefix AND status = 'draft'"
        ),
        params,
    ).scalar() or 0
    # Remove junction table links first
    db.execute(
        text(
            "DELETE FROM threat_damage_links WHERE threat_scenario_id IN "
            "(SELECT threat_scenario_id FROM threat_scenarios "
            " WHERE scope_id = :sid AND threat_scenario_id LIKE :prefix AND status = 'draft')"
        ),
        params,
    )
    # Remove the threat scenario rows
    db.execute(
        text(
            "DELETE FROM threat_scenarios "
            "WHERE scope_id = :sid AND threat_scenario_id LIKE :prefix AND status = 'draft'"
        ),
        params,
    )
    return int(count_row)


def _get_existing_damage_scenarios(
    db: Session, scope_id: str,
) -> List[Dict[str, Any]]:
    """Fetch existing damage scenarios for a product and convert to dicts."""
    rows = (
        db.query(DBDamageScenario)
        .filter(DBDamageScenario.scope_id == scope_id)
        .all()
    )
    result: List[Dict[str, Any]] = []
    for ds in rows:
        cia_dimension = "integrity"
        if ds.confidentiality_impact:
            cia_dimension = "confidentiality"
        elif ds.availability_impact:
            cia_dimension = "availability"
        result.append({
            "scenario_id": ds.scenario_id,
            "name": ds.name,
            "cia_dimension": cia_dimension,
            "primary_component_id": ds.primary_component_id,
        })
    return result


def _filter_damage_for_asset(
    damage_scenarios: List[Dict[str, Any]],
    asset_id: str,
) -> List[Dict[str, Any]]:
    """Filter damage scenarios linked to a specific asset."""
    return [
        ds for ds in damage_scenarios
        if ds.get("primary_component_id") == asset_id
    ]


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
    """Persist auto-generated damage scenarios and link to assets via M2M."""
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
            status="draft",
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(db_scenario)
        db.flush()
        # Link to asset via M2M (affected_assets relationship)
        asset_id = s.get("primary_component_id")
        if asset_id:
            db.execute(
                asset_damage_scenario.insert().values(
                    asset_id=asset_id,
                    scenario_id=s["scenario_id"],
                )
            )
        saved += 1
    return saved


def _save_threat_scenarios(
    db: Session,
    scenarios: List[Dict[str, Any]],
) -> int:
    """Persist auto-generated threat scenarios and link ALL damage scenarios."""
    from db.threat_scenario import ThreatScenario as DBThreatScenario
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
            status="draft",
        )
        db.add(db_scenario)
        db.flush()
        # Link ALL damage scenarios via junction table (not skipping first)
        for ds_id in s.get("damage_scenario_ids", []):
            db.execute(
                text(
                    "INSERT OR IGNORE INTO threat_damage_links "
                    "(threat_scenario_id, damage_scenario_id) VALUES (:tid, :did)"
                ),
                {"tid": s["threat_scenario_id"], "did": ds_id},
            )
        saved += 1
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
