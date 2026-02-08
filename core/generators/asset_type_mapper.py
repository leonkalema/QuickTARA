"""
Maps between QuickTARA asset/product enums and threat catalog enums.

Purpose: Bridge AssetType→ComponentType and TrustZone→catalog trust zones
Depends on: None (pure mapping logic)
Used by: core/generators/damage_scenario_generator.py, core/generators/threat_scenario_generator.py
"""
from typing import List

# AssetType (DB) → ComponentType (threat catalog) mapping
ASSET_TYPE_TO_COMPONENT: dict[str, List[str]] = {
    "Firmware": ["controller", "gateway", "processing_unit"],
    "Software": ["controller", "processing_unit", "hmi"],
    "Configuration": ["controller", "gateway"],
    "Calibration": ["controller", "sensor"],
    "Data": ["storage", "processing_unit"],
    "Diagnostic": ["interface", "controller"],
    "Communication": ["communication", "gateway", "interface"],
    "Hardware": ["controller", "sensor", "actuator"],
    "Interface": ["interface", "gateway", "external_service"],
    "Other": ["other"],
}

# ProductScope.trust_zone → catalog trust zones
TRUST_ZONE_TO_CATALOG: dict[str, List[str]] = {
    "Critical": ["secure", "trusted"],
    "Boundary": ["trusted", "untrusted"],
    "Standard": ["trusted", "untrusted"],
    "Untrusted": ["untrusted", "external"],
}

# CIA level → severity mapping for damage scenarios
CIA_TO_SEVERITY: dict[str, str] = {
    "High": "Critical",
    "Medium": "High",
    "Low": "Medium",
    "N/A": "Low",
}

# CIA level → SFOP impact level mapping
CIA_TO_IMPACT: dict[str, str] = {
    "High": "severe",
    "Medium": "major",
    "Low": "moderate",
    "N/A": "negligible",
}


def get_component_types(asset_type: str) -> List[str]:
    """Map an AssetType to matching ComponentType values."""
    return ASSET_TYPE_TO_COMPONENT.get(asset_type, ["other"])


def get_catalog_trust_zones(trust_zone: str) -> List[str]:
    """Map a ProductScope trust zone to catalog trust zone values."""
    return TRUST_ZONE_TO_CATALOG.get(trust_zone, ["untrusted"])


def get_severity(cia_level: str) -> str:
    """Map a CIA security level to a damage scenario severity."""
    return CIA_TO_SEVERITY.get(cia_level, "Medium")


def get_impact_level(cia_level: str) -> str:
    """Map a CIA security level to an SFOP impact level."""
    return CIA_TO_IMPACT.get(cia_level, "negligible")
