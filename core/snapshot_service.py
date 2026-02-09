"""
TARA Snapshot service — creates versioned point-in-time snapshots of a complete TARA.

A snapshot captures all artifacts (assets, damage scenarios, threat scenarios,
attack paths, risk treatments) for a product scope at a given moment.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.audit_models import TaraSnapshot
from core.audit_service import log_change


def create_snapshot(
    db: Session,
    scope_id: str,
    created_by: str,
    version_label: Optional[str] = None,
    notes: Optional[str] = None,
) -> TaraSnapshot:
    """Capture a full snapshot of the TARA for a product scope."""
    snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
    # Determine next version number
    max_ver = db.execute(
        text("SELECT COALESCE(MAX(version), 0) FROM tara_snapshots WHERE scope_id = :sid"),
        {"sid": scope_id},
    ).scalar()
    next_version = (max_ver or 0) + 1
    # Collect all artifacts
    data = _collect_artifacts(db, scope_id)
    snapshot = TaraSnapshot(
        snapshot_id=snapshot_id,
        scope_id=scope_id,
        version=next_version,
        version_label=version_label or f"v{next_version}",
        asset_count=len(data.get("assets", [])),
        damage_scenario_count=len(data.get("damage_scenarios", [])),
        threat_scenario_count=len(data.get("threat_scenarios", [])),
        attack_path_count=len(data.get("attack_paths", [])),
        risk_treatment_count=len(data.get("risk_treatments", [])),
        snapshot_data=data,
        created_by=created_by,
        notes=notes,
    )
    db.add(snapshot)
    db.flush()
    log_change(
        db, "tara_snapshot", snapshot_id, "create",
        performed_by=created_by, scope_id=scope_id,
        change_summary=f"TARA snapshot {version_label or f'v{next_version}'} created",
    )
    return snapshot


def get_snapshot(db: Session, snapshot_id: str) -> Optional[TaraSnapshot]:
    """Get a single snapshot by ID."""
    return db.query(TaraSnapshot).filter(TaraSnapshot.snapshot_id == snapshot_id).first()


def list_snapshots(
    db: Session, scope_id: str, limit: int = 50,
) -> List[TaraSnapshot]:
    """List all snapshots for a product scope, newest first."""
    return (
        db.query(TaraSnapshot)
        .filter(TaraSnapshot.scope_id == scope_id)
        .order_by(TaraSnapshot.version.desc())
        .limit(limit)
        .all()
    )


def _collect_artifacts(db: Session, scope_id: str) -> Dict[str, Any]:
    """Gather all TARA artifacts for a scope into a serializable dict."""
    result: Dict[str, Any] = {"scope_id": scope_id, "captured_at": datetime.utcnow().isoformat()}
    # Assets
    rows = db.execute(
        text("SELECT asset_id, name, asset_type, confidentiality, integrity, availability "
             "FROM assets WHERE scope_id = :sid AND is_current = 1"),
        {"sid": scope_id},
    ).fetchall()
    result["assets"] = [
        {"asset_id": r[0], "name": r[1], "asset_type": r[2],
         "confidentiality": r[3], "integrity": r[4], "availability": r[5]}
        for r in rows
    ]
    # Damage scenarios
    rows = db.execute(
        text("SELECT scenario_id, name, damage_category, severity, status, "
             "safety_impact, financial_impact, operational_impact, privacy_impact "
             "FROM damage_scenarios WHERE scope_id = :sid AND is_deleted = 0"),
        {"sid": scope_id},
    ).fetchall()
    result["damage_scenarios"] = [
        {"scenario_id": r[0], "name": r[1], "damage_category": r[2],
         "severity": r[3], "status": r[4], "safety_impact": r[5],
         "financial_impact": r[6], "operational_impact": r[7], "privacy_impact": r[8]}
        for r in rows
    ]
    # Threat scenarios
    rows = db.execute(
        text("SELECT threat_scenario_id, name, attack_vector, status "
             "FROM threat_scenarios WHERE scope_id = :sid AND is_deleted = 0"),
        {"sid": scope_id},
    ).fetchall()
    result["threat_scenarios"] = [
        {"threat_scenario_id": r[0], "name": r[1], "attack_vector": r[2], "status": r[3]}
        for r in rows
    ]
    # Attack paths (via threat scenarios)
    rows = db.execute(
        text("SELECT ap.attack_path_id, ap.threat_scenario_id, ap.name, "
             "ap.overall_rating, ap.elapsed_time, ap.specialist_expertise, "
             "ap.knowledge_of_target, ap.window_of_opportunity, ap.equipment "
             "FROM attack_paths ap "
             "JOIN threat_scenarios ts ON ap.threat_scenario_id = ts.threat_scenario_id "
             "WHERE ts.scope_id = :sid"),
        {"sid": scope_id},
    ).fetchall()
    result["attack_paths"] = [
        {"attack_path_id": r[0], "threat_scenario_id": r[1], "name": r[2],
         "overall_rating": r[3], "elapsed_time": r[4], "specialist_expertise": r[5],
         "knowledge_of_target": r[6], "window_of_opportunity": r[7], "equipment": r[8]}
        for r in rows
    ]
    # Risk treatments
    rows = db.execute(
        text("SELECT risk_treatment_id, damage_scenario_id, attack_path_id, "
             "impact_level, feasibility_level, risk_level, suggested_treatment, "
             "selected_treatment, treatment_status "
             "FROM risk_treatments WHERE scope_id = :sid"),
        {"sid": scope_id},
    ).fetchall()
    result["risk_treatments"] = [
        {"risk_treatment_id": r[0], "damage_scenario_id": r[1], "attack_path_id": r[2],
         "impact_level": r[3], "feasibility_level": r[4], "risk_level": r[5],
         "suggested_treatment": r[6], "selected_treatment": r[7], "treatment_status": r[8]}
        for r in rows
    ]
    return result
