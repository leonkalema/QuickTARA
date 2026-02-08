"""
Damage scenario generator for QuickTARA.
Generates CIA-based damage scenarios from assets using templates.

Purpose: For each asset, generate damage scenarios based on its CIA properties
Depends on: data/templates/damage_templates.json, core/generators/asset_type_mapper.py
Used by: core/generators/scenario_orchestrator.py
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.generators.asset_type_mapper import get_severity, get_impact_level

logger = logging.getLogger(__name__)

TEMPLATES_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data" / "templates" / "damage_templates.json"
)


def load_templates(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load damage scenario templates from JSON."""
    template_path = path or TEMPLATES_PATH
    if not template_path.exists():
        logger.warning("Damage templates not found at %s", template_path)
        return {"templates": {}}
    with open(template_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def generate_for_asset(
    asset: Dict[str, Any],
    product_name: str,
    templates: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate damage scenarios for a single asset based on its CIA properties.
    Only generates scenarios for CIA dimensions rated Medium or High.
    """
    if templates is None:
        templates = load_templates()

    template_map = templates.get("templates", {})
    scenarios: List[Dict[str, Any]] = []
    asset_name = asset.get("name", "Unknown Asset")
    asset_type = asset.get("asset_type", "Other")
    scope_id = asset.get("scope_id", "")
    asset_id = asset.get("asset_id", "")

    cia_dimensions = _get_active_cia_dimensions(asset)

    for dimension, level in cia_dimensions.items():
        dimension_templates = template_map.get(dimension, [])
        for tmpl in dimension_templates:
            scenario = _build_scenario(
                tmpl, asset_name, asset_type, product_name,
                scope_id, asset_id, dimension, level,
            )
            scenarios.append(scenario)

    logger.debug(
        "Generated %d damage scenarios for asset '%s'",
        len(scenarios), asset_name,
    )
    return scenarios


def _get_active_cia_dimensions(asset: Dict[str, Any]) -> Dict[str, str]:
    """Return CIA dimensions that are Medium or High (worth generating scenarios for)."""
    active: Dict[str, str] = {}
    for dimension, key in [
        ("confidentiality", "confidentiality"),
        ("integrity", "integrity"),
        ("availability", "availability"),
    ]:
        level = asset.get(key, "Low")
        if level in ("High", "Medium"):
            active[dimension] = level
    return active


def _build_scenario(
    template: Dict[str, Any],
    asset_name: str,
    asset_type: str,
    product_name: str,
    scope_id: str,
    asset_id: str,
    cia_dimension: str,
    cia_level: str,
) -> Dict[str, Any]:
    """Build a single damage scenario dict from a template."""
    fmt_vars = {
        "asset_name": asset_name,
        "asset_type": asset_type,
        "product_name": product_name,
    }
    scenario_id = f"DS-AUTO-{uuid.uuid4().hex[:8]}"
    severity = get_severity(cia_level)
    impact = get_impact_level(cia_level)

    return {
        "scenario_id": scenario_id,
        "name": template["name_template"].format(**fmt_vars),
        "description": template["description_template"].format(**fmt_vars),
        "damage_category": template.get("damage_category", "Operational"),
        "impact_type": template.get("impact_type", "Direct"),
        "severity": severity,
        "confidentiality_impact": cia_dimension == "confidentiality",
        "integrity_impact": cia_dimension == "integrity",
        "availability_impact": cia_dimension == "availability",
        "safety_impact": _scale_impact(template.get("safety_impact", "negligible"), impact),
        "financial_impact": _scale_impact(template.get("financial_impact", "negligible"), impact),
        "operational_impact": _scale_impact(template.get("operational_impact", "negligible"), impact),
        "privacy_impact": _scale_impact(template.get("privacy_impact", "negligible"), impact),
        "scope_id": scope_id,
        "primary_component_id": asset_id,
        "affected_component_ids": [asset_id],
        "cia_dimension": cia_dimension,
        "cia_level": cia_level,
        "auto_generated": True,
    }


def _scale_impact(template_impact: str, asset_impact: str) -> str:
    """Scale template impact based on asset CIA level. Never exceed template's base."""
    rank = {"negligible": 0, "moderate": 1, "major": 2, "severe": 3}
    template_rank = rank.get(template_impact, 0)
    asset_rank = rank.get(asset_impact, 0)
    # Take the lower of template suggestion and asset-derived impact
    final_rank = min(template_rank, asset_rank) if template_rank > 0 else 0
    reverse = {v: k for k, v in rank.items()}
    return reverse.get(final_rank, "negligible")
