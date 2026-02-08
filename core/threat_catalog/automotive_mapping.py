"""
Automotive mapping layer for MITRE ATT&CK ICS techniques.
Maps ICS techniques to automotive component types, trust zones, STRIDE categories,
and assigns automotive-specific relevance and context.

Purpose: Load automotive_mappings.json and enrich parsed STIX techniques
Depends on: data/threat_catalogs/automotive_mappings.json
Used by: core/threat_catalog/catalog_seeder.py
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "threat_catalogs"
DEFAULT_MAPPING_FILE = DATA_DIR / "automotive_mappings.json"

# ATT&CK ICS tactic → STRIDE category mapping
TACTIC_TO_STRIDE: Dict[str, str] = {
    "initial-access": "spoofing",
    "execution": "tampering",
    "persistence": "tampering",
    "evasion": "repudiation",
    "discovery": "info_disclosure",
    "lateral-movement": "elevation_of_privilege",
    "collection": "info_disclosure",
    "command-and-control": "spoofing",
    "inhibit-response-function": "denial_of_service",
    "impair-process-control": "tampering",
    "impact": "denial_of_service",
}


def load_mapping_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the automotive mapping configuration from JSON."""
    config_path = path or DEFAULT_MAPPING_FILE
    if not config_path.exists():
        logger.warning("Mapping config not found at %s", config_path)
        return {"version": "0.0", "attack_version": "", "mappings": {}}
    with open(config_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def get_stride_for_tactic(tactic_name: str) -> str:
    """Map an ATT&CK ICS tactic phase-name to a STRIDE category."""
    return TACTIC_TO_STRIDE.get(tactic_name, "tampering")


def enrich_technique(
    technique: Dict[str, Any],
    mapping_config: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Enrich a parsed STIX technique with automotive mapping data.
    Returns None if the technique has no automotive mapping (not relevant).
    """
    technique_id = technique.get("mitre_technique_id", "")
    mappings = mapping_config.get("mappings", {})
    mapping = mappings.get(technique_id)
    if mapping is None:
        return None

    tactic_names = technique.get("tactic_names", [])
    primary_tactic = tactic_names[0] if tactic_names else ""
    stride_category = get_stride_for_tactic(primary_tactic)

    mitigations = _build_mitigation_list(technique.get("mitigations", []))

    return {
        "mitre_technique_id": technique_id,
        "title": technique.get("name", ""),
        "description": technique.get("description", ""),
        "stride_category": stride_category,
        "mitre_tactic": primary_tactic,
        "source": "mitre_attack_ics",
        "source_version": mapping_config.get("attack_version", ""),
        "automotive_relevance": mapping.get("automotive_relevance", 3),
        "automotive_context": mapping.get("automotive_context", ""),
        "applicable_component_types": mapping.get("component_types", []),
        "applicable_trust_zones": mapping.get("trust_zones", []),
        "attack_vectors": mapping.get("attack_vectors", []),
        "typical_likelihood": mapping.get("typical_likelihood", 3),
        "typical_severity": mapping.get("typical_severity", 3),
        "mitigation_strategies": mitigations,
        "cwe_ids": mapping.get("cwe_ids", []),
        "capec_ids": mapping.get("capec_ids", []),
        "examples": mapping.get("examples", []),
    }


def enrich_all_techniques(
    techniques: List[Dict[str, Any]],
    mapping_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Enrich a list of parsed STIX techniques, keeping only those
    with an automotive mapping entry.
    """
    if mapping_config is None:
        mapping_config = load_mapping_config()

    enriched: List[Dict[str, Any]] = []
    for tech in techniques:
        result = enrich_technique(tech, mapping_config)
        if result is not None:
            enriched.append(result)

    skipped = len(techniques) - len(enriched)
    logger.info(
        "Enriched %d automotive-relevant techniques (skipped %d)",
        len(enriched),
        skipped,
    )
    return enriched


def _build_mitigation_list(
    raw_mitigations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert parsed STIX mitigations into the ThreatCatalog mitigation format."""
    result: List[Dict[str, Any]] = []
    for mit in raw_mitigations:
        result.append({
            "title": mit.get("name", ""),
            "description": mit.get("description", ""),
            "effectiveness": 3,
            "implementation_complexity": 3,
            "references": [],
        })
    return result
