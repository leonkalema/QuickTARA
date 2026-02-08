"""
STIX 2.1 parser for MITRE ATT&CK ICS bundles.
Extracts techniques, tactics, mitigations, and their relationships.

Purpose: Parse raw STIX JSON → normalized Python dicts
Depends on: None (stdlib only)
Used by: core/threat_catalog/catalog_seeder.py
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# STIX object type constants
ATTACK_PATTERN = "attack-pattern"
COURSE_OF_ACTION = "course-of-action"
RELATIONSHIP = "relationship"
X_MITRE_TACTIC = "x-mitre-tactic"


def load_stix_bundle(bundle_path: Path) -> Dict[str, Any]:
    """Load a STIX 2.1 JSON bundle from disk."""
    with open(bundle_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_techniques(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract attack-pattern objects (techniques) from a STIX bundle."""
    techniques: List[Dict[str, Any]] = []
    for obj in bundle.get("objects", []):
        if obj.get("type") != ATTACK_PATTERN:
            continue
        if obj.get("revoked", False) or obj.get("x_mitre_deprecated", False):
            continue
        techniques.append(_normalize_technique(obj))
    logger.info("Extracted %d techniques from STIX bundle", len(techniques))
    return techniques


def extract_mitigations(bundle: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract course-of-action objects (mitigations) keyed by STIX id."""
    mitigations: Dict[str, Dict[str, Any]] = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != COURSE_OF_ACTION:
            continue
        if obj.get("revoked", False) or obj.get("x_mitre_deprecated", False):
            continue
        mitigations[obj["id"]] = _normalize_mitigation(obj)
    logger.info("Extracted %d mitigations from STIX bundle", len(mitigations))
    return mitigations


def extract_tactics(bundle: Dict[str, Any]) -> Dict[str, str]:
    """Extract tactic short-names keyed by STIX id."""
    tactics: Dict[str, str] = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != X_MITRE_TACTIC:
            continue
        tactics[obj["id"]] = obj.get("x_mitre_shortname", obj.get("name", ""))
    return tactics


def build_technique_mitigation_map(
    bundle: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Build technique_stix_id → [mitigation_stix_id] mapping from relationships."""
    tech_to_mits: Dict[str, List[str]] = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != RELATIONSHIP:
            continue
        if obj.get("relationship_type") != "mitigates":
            continue
        target_id = obj.get("target_ref", "")
        source_id = obj.get("source_ref", "")
        tech_to_mits.setdefault(target_id, []).append(source_id)
    return tech_to_mits


def parse_full_bundle(bundle_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a STIX bundle and return enriched technique dicts
    with their mitigations and tactic names resolved.
    """
    bundle = load_stix_bundle(bundle_path)
    techniques = extract_techniques(bundle)
    mitigations = extract_mitigations(bundle)
    tactics = extract_tactics(bundle)
    tech_mit_map = build_technique_mitigation_map(bundle)

    enriched: List[Dict[str, Any]] = []
    for tech in techniques:
        stix_id = tech["stix_id"]
        # Resolve tactic names from kill_chain_phases
        tech["tactic_names"] = _resolve_tactics(tech.get("kill_chain_phases", []))
        # Attach mitigations
        mit_ids = tech_mit_map.get(stix_id, [])
        tech["mitigations"] = [
            mitigations[mid] for mid in mit_ids if mid in mitigations
        ]
        enriched.append(tech)

    logger.info("Parsed %d enriched techniques from %s", len(enriched), bundle_path)
    return enriched


def _normalize_technique(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a STIX attack-pattern into a flat dict."""
    external_id = _get_external_id(obj)
    return {
        "stix_id": obj["id"],
        "mitre_technique_id": external_id,
        "name": obj.get("name", ""),
        "description": _clean_description(obj.get("description", "")),
        "kill_chain_phases": obj.get("kill_chain_phases", []),
        "x_mitre_platforms": obj.get("x_mitre_platforms", []),
        "x_mitre_data_sources": obj.get("x_mitre_data_sources", []),
    }


def _normalize_mitigation(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a STIX course-of-action into a flat dict."""
    external_id = _get_external_id(obj)
    return {
        "stix_id": obj["id"],
        "mitre_id": external_id,
        "name": obj.get("name", ""),
        "description": _clean_description(obj.get("description", "")),
    }


def _get_external_id(obj: Dict[str, Any]) -> Optional[str]:
    """Extract the MITRE external ID (e.g. T0800) from external_references."""
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def _clean_description(raw: str) -> str:
    """Strip markdown citations and excessive whitespace from STIX descriptions."""
    cleaned = raw.replace("\n", " ").strip()
    # Remove STIX citation markers like (Citation: ...)
    import re
    cleaned = re.sub(r"\(Citation:[^)]*\)", "", cleaned)
    return " ".join(cleaned.split())


def _resolve_tactics(kill_chain_phases: List[Dict[str, str]]) -> List[str]:
    """Extract tactic phase-names from kill_chain_phases entries."""
    return [
        phase.get("phase_name", "")
        for phase in kill_chain_phases
        if phase.get("kill_chain_name") == "mitre-ics-attack"
    ]
