"""
Clean data access layer for report generation.
All database queries return structured dictionaries with explicit column names.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from db.product_asset_models import ProductScope
from api.models.user import Organization


def get_scope_info(scope_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get product scope information."""
    scope = db.query(ProductScope).filter(ProductScope.scope_id == scope_id).first()
    if not scope:
        return None
    
    # Best-effort fetch of organization name (first org) until scopes are org-linked
    org_name = None
    try:
        org = db.query(Organization).first()
        if org:
            org_name = org.name
    except Exception:
        org_name = None

    return {
        "scope_id": scope.scope_id,
        "name": scope.name,
        "product_type": scope.product_type,
        "safety_level": scope.safety_level,
        "version": scope.version,
        "description": scope.description,
        "organization_name": org_name
    }


def get_damage_scenarios(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get damage scenarios with explicit column mapping."""
    result = db.execute(text("""
        SELECT 
            ds.scenario_id,
            ds.name,
            ds.description,
            ds.severity,
            ds.safety_impact,
            ds.financial_impact,
            ds.operational_impact,
            ds.privacy_impact,
            ds.confidentiality_impact,
            ds.integrity_impact,
            ds.availability_impact,
            ds.primary_component_id
        FROM damage_scenarios ds
        WHERE ds.scope_id = :scope_id
        ORDER BY ds.scenario_id
    """), {"scope_id": scope_id})
    
    scenarios = []
    for row in result.fetchall():
        m = row._mapping
        scenarios.append({
            "scenario_id": m.get("scenario_id"),
            "name": m.get("name"),
            "description": m.get("description"),
            "severity": m.get("severity"),
            "safety_impact": m.get("safety_impact"),
            "financial_impact": m.get("financial_impact"),
            "operational_impact": m.get("operational_impact"),
            "privacy_impact": m.get("privacy_impact"),
            "confidentiality_impact": m.get("confidentiality_impact"),
            "integrity_impact": m.get("integrity_impact"),
            "availability_impact": m.get("availability_impact"),
            "primary_component_id": m.get("primary_component_id")
        })
    
    return scenarios


def get_risk_treatments(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get risk treatment data with explicit column mapping."""
    result = db.execute(text("""
        SELECT 
            rt.risk_treatment_id,
            rt.damage_scenario_id,
            rt.attack_path_id,
            rt.impact_level,
            rt.feasibility_level,
            rt.risk_level,
            rt.feasibility_score,
            rt.suggested_treatment,
            rt.selected_treatment,
            rt.treatment_goal,
            rt.treatment_status
        FROM risk_treatments rt
        WHERE rt.scope_id = :scope_id
        ORDER BY rt.damage_scenario_id
    """), {"scope_id": scope_id})
    
    treatments = []
    for row in result.fetchall():
        m = row._mapping
        treatments.append({
            "risk_treatment_id": m.get("risk_treatment_id"),
            "damage_scenario_id": m.get("damage_scenario_id"),
            "attack_path_id": m.get("attack_path_id"),
            "impact_level": m.get("impact_level"),
            "feasibility_level": m.get("feasibility_level"),
            "risk_level": m.get("risk_level"),
            "feasibility_score": m.get("feasibility_score"),
            "suggested_treatment": m.get("suggested_treatment"),
            "selected_treatment": m.get("selected_treatment"),
            "treatment_goal": m.get("treatment_goal"),
            "treatment_status": m.get("treatment_status")
        })
    
    return treatments


def get_threat_scenarios(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get threat scenarios with explicit column mapping."""
    result = db.execute(text("""
        SELECT 
            ts.threat_scenario_id,
            ts.name,
            ts.description,
            ts.scope_id
        FROM threat_scenarios ts
        WHERE ts.scope_id = :scope_id
        ORDER BY ts.threat_scenario_id
    """), {"scope_id": scope_id})
    
    threats = []
    for row in result.fetchall():
        m = row._mapping
        threats.append({
            "threat_scenario_id": m.get("threat_scenario_id"),
            "name": m.get("name"),
            "description": m.get("description"),
            "scope_id": m.get("scope_id")
        })
    
    return threats


def get_assets(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get assets with explicit column mapping. Only select columns that exist in DB."""
    result = db.execute(text(
        """
        SELECT 
            a.asset_id,
            a.name,
            a.description,
            a.asset_type
        FROM assets a
        WHERE a.scope_id = :scope_id
        ORDER BY a.name
        """
    ), {"scope_id": scope_id})

    assets = []
    for row in result.fetchall():
        m = row._mapping
        assets.append({
            "asset_id": m.get("asset_id"),
            "name": m.get("name"),
            "description": m.get("description"),
            "asset_type": m.get("asset_type")
        })

    return assets


def get_asset_damage_links(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get links between assets and damage scenarios within the scope."""
    result = db.execute(text(
        """
        SELECT ads.asset_id, ads.scenario_id
        FROM asset_damage_scenario ads
        JOIN damage_scenarios ds ON ds.scenario_id = ads.scenario_id
        WHERE ds.scope_id = :scope_id
        """
    ), {"scope_id": scope_id})

    links = []
    for row in result.fetchall():
        m = row._mapping
        links.append({
            "asset_id": m.get("asset_id"),
            "scenario_id": m.get("scenario_id"),
        })
    return links


def get_threat_damage_links(scope_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get links between threats and damage scenarios within the scope."""
    result = db.execute(text(
        """
        SELECT tdl.threat_scenario_id, tdl.damage_scenario_id AS scenario_id
        FROM threat_damage_links tdl
        JOIN threat_scenarios ts ON ts.threat_scenario_id = tdl.threat_scenario_id
        WHERE ts.scope_id = :scope_id
        """
    ), {"scope_id": scope_id})

    links = []
    for row in result.fetchall():
        m = row._mapping
        links.append({
            "threat_scenario_id": m.get("threat_scenario_id"),
            "scenario_id": m.get("scenario_id"),
        })
    return links
