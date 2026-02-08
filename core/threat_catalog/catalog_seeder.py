"""
Catalog seeder for QuickTARA threat catalog.
Orchestrates: STIX parse → automotive mapping → DB insert/update.

Purpose: Populate or refresh the threat_catalog table from MITRE ATT&CK ICS data
Depends on: core/threat_catalog/stix_parser.py, core/threat_catalog/automotive_mapping.py
Used by: API admin endpoint, startup seeder, CLI script
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from db.threat_catalog import ThreatCatalog
from core.threat_catalog.stix_parser import parse_full_bundle
from core.threat_catalog.automotive_mapping import (
    load_mapping_config,
    enrich_all_techniques,
)

logger = logging.getLogger(__name__)

STIX_BUNDLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "threat_catalogs"
DEFAULT_STIX_FILE = STIX_BUNDLE_DIR / "ics-attack.json"


def seed_from_stix(
    db: Session,
    stix_path: Optional[Path] = None,
    mapping_path: Optional[Path] = None,
    force_update: bool = False,
) -> Dict[str, int]:
    """
    Parse STIX bundle, apply automotive mappings, and upsert into DB.
    Returns counts: {"created": N, "updated": N, "skipped": N}
    """
    bundle_path = stix_path or DEFAULT_STIX_FILE
    if not bundle_path.exists():
        logger.error("STIX bundle not found at %s", bundle_path)
        return {"created": 0, "updated": 0, "skipped": 0, "error": "stix_not_found"}

    mapping_config = load_mapping_config(mapping_path)
    techniques = parse_full_bundle(bundle_path)
    enriched = enrich_all_techniques(techniques, mapping_config)

    return _upsert_threats(db, enriched, force_update)


def seed_from_enriched(
    db: Session,
    enriched_threats: List[Dict[str, Any]],
    force_update: bool = False,
) -> Dict[str, int]:
    """Seed the DB from pre-enriched threat dicts (for testing or direct use)."""
    return _upsert_threats(db, enriched_threats, force_update)


def get_catalog_stats(db: Session) -> Dict[str, Any]:
    """Return summary stats about the current threat catalog."""
    total = db.query(ThreatCatalog).count()
    mitre_count = db.query(ThreatCatalog).filter(
        ThreatCatalog.source == "mitre_attack_ics"
    ).count()
    custom_count = db.query(ThreatCatalog).filter(
        ThreatCatalog.source == "custom"
    ).count()
    user_modified = db.query(ThreatCatalog).filter(
        ThreatCatalog.is_user_modified == True  # noqa: E712
    ).count()

    return {
        "total": total,
        "mitre_attack_ics": mitre_count,
        "custom": custom_count,
        "user_modified": user_modified,
    }


def _upsert_threats(
    db: Session,
    threats: List[Dict[str, Any]],
    force_update: bool,
) -> Dict[str, int]:
    """Insert new threats or update existing ones (by mitre_technique_id)."""
    created = 0
    updated = 0
    skipped = 0

    for threat_data in threats:
        technique_id = threat_data.get("mitre_technique_id", "")
        if not technique_id:
            skipped += 1
            continue

        existing = db.query(ThreatCatalog).filter(
            ThreatCatalog.mitre_technique_id == technique_id
        ).first()

        if existing is None:
            _create_threat(db, threat_data)
            created += 1
        elif force_update or not existing.is_user_modified:
            _update_threat(db, existing, threat_data)
            updated += 1
        else:
            skipped += 1

    db.commit()
    logger.info("Seed complete: created=%d, updated=%d, skipped=%d", created, updated, skipped)
    return {"created": created, "updated": updated, "skipped": skipped}


def _create_threat(db: Session, data: Dict[str, Any]) -> ThreatCatalog:
    """Create a new ThreatCatalog row from enriched threat data."""
    threat_id = f"MITRE-{data['mitre_technique_id']}"
    db_threat = ThreatCatalog(
        id=threat_id,
        title=data["title"],
        description=data.get("description", ""),
        stride_category=data.get("stride_category", "tampering"),
        applicable_component_types=data.get("applicable_component_types", []),
        applicable_trust_zones=data.get("applicable_trust_zones", []),
        attack_vectors=data.get("attack_vectors", []),
        prerequisites=[],
        typical_likelihood=data.get("typical_likelihood", 3),
        typical_severity=data.get("typical_severity", 3),
        mitigation_strategies=data.get("mitigation_strategies", []),
        cwe_ids=data.get("cwe_ids", []),
        capec_ids=data.get("capec_ids", []),
        examples=data.get("examples", []),
        source=data.get("source", "mitre_attack_ics"),
        source_version=data.get("source_version", ""),
        mitre_technique_id=data.get("mitre_technique_id", ""),
        mitre_tactic=data.get("mitre_tactic", ""),
        automotive_relevance=data.get("automotive_relevance", 3),
        automotive_context=data.get("automotive_context", ""),
        is_user_modified=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(db_threat)
    return db_threat


def _update_threat(
    db: Session,
    existing: ThreatCatalog,
    data: Dict[str, Any],
) -> None:
    """Update an existing ThreatCatalog row, preserving user modifications flag."""
    existing.title = data.get("title", existing.title)
    existing.description = data.get("description", existing.description)
    existing.stride_category = data.get("stride_category", existing.stride_category)
    existing.applicable_component_types = data.get("applicable_component_types", existing.applicable_component_types)
    existing.applicable_trust_zones = data.get("applicable_trust_zones", existing.applicable_trust_zones)
    existing.attack_vectors = data.get("attack_vectors", existing.attack_vectors)
    existing.typical_likelihood = data.get("typical_likelihood", existing.typical_likelihood)
    existing.typical_severity = data.get("typical_severity", existing.typical_severity)
    existing.mitigation_strategies = data.get("mitigation_strategies", existing.mitigation_strategies)
    existing.cwe_ids = data.get("cwe_ids", existing.cwe_ids)
    existing.capec_ids = data.get("capec_ids", existing.capec_ids)
    existing.examples = data.get("examples", existing.examples)
    existing.source_version = data.get("source_version", existing.source_version)
    existing.mitre_tactic = data.get("mitre_tactic", existing.mitre_tactic)
    existing.automotive_relevance = data.get("automotive_relevance", existing.automotive_relevance)
    existing.automotive_context = data.get("automotive_context", existing.automotive_context)
    existing.updated_at = datetime.now()
