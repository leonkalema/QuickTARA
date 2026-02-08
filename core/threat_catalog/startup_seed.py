"""
Startup auto-seeder for the threat catalog.
Seeds from automotive_mappings.json directly — no STIX bundle required.
This runs on app startup if the catalog is empty.

Purpose: Ensure prod deployments ship with a pre-populated threat catalog
Depends on: core/threat_catalog/catalog_seeder.py, data/threat_catalogs/automotive_mappings.json
Used by: api/app.py (startup event)
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from db.threat_catalog import ThreatCatalog
from core.threat_catalog.automotive_mapping import load_mapping_config, get_stride_for_tactic
from core.threat_catalog.catalog_seeder import seed_from_enriched

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "threat_catalogs"
DEFAULT_MAPPING_FILE = DATA_DIR / "automotive_mappings.json"


def should_auto_seed(db: Session) -> bool:
    """Check if the catalog needs seeding (empty or no MITRE entries)."""
    mitre_count = db.query(ThreatCatalog).filter(
        ThreatCatalog.source == "mitre_attack_ics"
    ).count()
    return mitre_count == 0


def auto_seed_catalog(db: Session) -> Dict[str, int]:
    """
    Auto-seed the threat catalog from automotive_mappings.json on startup.
    Only runs if no MITRE entries exist. No internet access needed.
    """
    if not should_auto_seed(db):
        logger.info("Threat catalog already seeded, skipping auto-seed")
        return {"created": 0, "updated": 0, "skipped": 0}

    config = load_mapping_config(DEFAULT_MAPPING_FILE)
    if not config.get("mappings"):
        logger.warning("No automotive mappings found at %s", DEFAULT_MAPPING_FILE)
        return {"created": 0, "updated": 0, "skipped": 0}

    enriched = _build_threats_from_mappings(config)
    result = seed_from_enriched(db, enriched)
    logger.info(
        "Auto-seed complete: %d threats created, %d updated",
        result["created"],
        result["updated"],
    )
    return result


def _build_threats_from_mappings(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build enriched threat dicts directly from automotive_mappings.json."""
    attack_version = config.get("attack_version", "")
    threats: List[Dict[str, Any]] = []

    for technique_id, mapping in config.get("mappings", {}).items():
        primary_vector = mapping.get("attack_vectors", [""])[0] if mapping.get("attack_vectors") else ""
        stride_category = _infer_stride_from_mapping(mapping, primary_vector)

        threats.append({
            "mitre_technique_id": technique_id,
            "title": f"ATT&CK ICS {technique_id}",
            "description": mapping.get("automotive_context", ""),
            "stride_category": stride_category,
            "mitre_tactic": "",
            "source": "mitre_attack_ics",
            "source_version": attack_version,
            "automotive_relevance": mapping.get("automotive_relevance", 3),
            "automotive_context": mapping.get("automotive_context", ""),
            "applicable_component_types": mapping.get("component_types", []),
            "applicable_trust_zones": mapping.get("trust_zones", []),
            "attack_vectors": mapping.get("attack_vectors", []),
            "typical_likelihood": mapping.get("typical_likelihood", 3),
            "typical_severity": mapping.get("typical_severity", 3),
            "mitigation_strategies": [],
            "cwe_ids": mapping.get("cwe_ids", []),
            "capec_ids": mapping.get("capec_ids", []),
            "examples": mapping.get("examples", []),
        })

    return threats


def _infer_stride_from_mapping(mapping: Dict[str, Any], primary_vector: str) -> str:
    """Infer STRIDE category from the mapping's severity/vector context."""
    severity = mapping.get("typical_severity", 3)
    vectors = mapping.get("attack_vectors", [])
    trust_zones = mapping.get("trust_zones", [])

    if severity >= 5 and "can_bus" in vectors:
        return "tampering"
    if "external" in trust_zones or "network" in vectors:
        return "spoofing"
    if severity <= 3 and any(v in vectors for v in ["wifi", "bluetooth"]):
        return "info_disclosure"
    return "tampering"
