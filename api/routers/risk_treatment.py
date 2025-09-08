from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from api.deps.db import get_db

router = APIRouter()

def _pick_cia(ds_row: Any) -> str:
    """Pick the dominant CIA property based on impact severity order."""
    order = {"negligible": 0, "low": 1, "moderate": 2, "medium": 2, "major": 3, "high": 3, "severe": 4, "critical": 4}
    candidates = []
    for label, val in (
        ("Confidentiality", getattr(ds_row, "confidentiality_impact", None)),
        ("Integrity", getattr(ds_row, "integrity_impact", None)),
        ("Availability", getattr(ds_row, "availability_impact", None)),
    ):
        if val is None:
            continue
        key = str(val).strip().lower()
        candidates.append((order.get(key, 0), label))
    if not candidates:
        return "Confidentiality"
    candidates.sort(reverse=True)
    return candidates[0][1]


@router.get("/risk-treatment")
async def get_risk_treatment_data(scope_id: str, db: Session = Depends(get_db)):
    """
    Get risk treatment data for a product scope.
    Returns damage scenarios with their associated attack path feasibility ratings.
    """
    try:
        # Query to get risk treatments from the stored table
        query = text("""
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
                rt.treatment_status,
                ds.name,
                ds.description,
                ds.primary_component_id,
                ds.safety_impact,
                ds.financial_impact,
                ds.operational_impact,
                ds.privacy_impact,
                ds.confidentiality_impact,
                ds.integrity_impact,
                ds.availability_impact,
                ds.severity,
                COALESCE(a.name, ap.name) AS asset_name,
                ps.name AS product_name
            FROM risk_treatments rt
            JOIN damage_scenarios ds ON rt.damage_scenario_id = ds.scenario_id
            LEFT JOIN asset_damage_scenario ads ON ads.scenario_id = ds.scenario_id
            LEFT JOIN assets a ON a.asset_id = ads.asset_id
            LEFT JOIN assets ap ON ap.asset_id = ds.primary_component_id
            LEFT JOIN product_scopes ps ON ps.scope_id = rt.scope_id
            WHERE rt.scope_id = :scope_id
            ORDER BY ds.name, rt.risk_level DESC
        """)
        
        result = db.execute(query, {"scope_id": scope_id})
        rows = result.fetchall()
        
        # Convert rows to risk treatment data
        risk_treatments = []
        for row in rows:
            # Determine CIA and suggested goal (if not explicitly set)
            cia = _pick_cia(row)
            product = row.product_name or "Product"
            asset = row.asset_name or "asset"
            auto_goal = f"The {product} shall ensure {cia.lower()} of {asset}."

            risk_treatment = {
                "risk_treatment_id": row.risk_treatment_id,
                "scenario_id": row.damage_scenario_id,
                "name": row.name,
                "description": row.description,
                "primary_component_id": row.primary_component_id,
                "safety_impact": row.safety_impact,
                "financial_impact": row.financial_impact,
                "operational_impact": row.operational_impact,
                "privacy_impact": row.privacy_impact,
                "confidentiality_impact": row.confidentiality_impact,
                "integrity_impact": row.integrity_impact,
                "availability_impact": row.availability_impact,
                "severity": row.severity,
                "attack_path_id": row.attack_path_id,
                "highest_feasibility_score": row.feasibility_score,
                "impact_level": row.impact_level,
                "feasibility_level": row.feasibility_level,
                "risk_level": row.risk_level,
                "suggested_treatment": row.suggested_treatment,
                "selected_treatment": row.selected_treatment,
                "treatment_goal": row.treatment_goal,
                "treatment_status": row.treatment_status,
                "asset_name": row.asset_name,
                "product_name": row.product_name,
                "cia": cia,
                "suggested_goal": row.treatment_goal or auto_goal
            }
            risk_treatments.append(risk_treatment)
        
        return {
            "damage_scenarios": risk_treatments,
            "total_count": len(risk_treatments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk treatment data: {str(e)}")

@router.put("/risk-treatment/{risk_treatment_id}")
async def update_risk_treatment(
    risk_treatment_id: str,
    treatment_data: dict,
    db: Session = Depends(get_db)
):
    """Update risk treatment selection and goal"""
    try:
        update_query = text("""
            UPDATE risk_treatments 
            SET selected_treatment = :selected_treatment,
                treatment_goal = :treatment_goal,
                treatment_status = :treatment_status,
                updated_at = CURRENT_TIMESTAMP
            WHERE risk_treatment_id = :risk_treatment_id
        """)
        
        db.execute(update_query, {
            "risk_treatment_id": risk_treatment_id,
            "selected_treatment": treatment_data.get("selected_treatment"),
            "treatment_goal": treatment_data.get("treatment_goal"),
            "treatment_status": treatment_data.get("treatment_status", "draft")
        })
        
        db.commit()
        
        return {"message": "Risk treatment updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update risk treatment: {str(e)}")

@router.put("/risk-treatment/{risk_treatment_id}/approve")
async def approve_risk_treatment(
    risk_treatment_id: str,
    db: Session = Depends(get_db)
):
    """Approve a risk treatment"""
    try:
        update_query = text("""
            UPDATE risk_treatments 
            SET treatment_status = 'approved',
                approved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE risk_treatment_id = :risk_treatment_id
        """)
        
        db.execute(update_query, {"risk_treatment_id": risk_treatment_id})
        db.commit()
        
        return {"message": "Risk treatment approved successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve risk treatment: {str(e)}")

