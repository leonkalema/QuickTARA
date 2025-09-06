"""
Simple Attack Path API routes for Risk Assessment
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
import logging
import uuid

from api.models.simple_attack_path import (
    AttackPath, AttackPathCreate, AttackPathResponse, AttackPathDB, FeasibilityRating
)
from api.deps.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

def create_risk_treatments_for_attack_path(db: Session, attack_path: AttackPathDB):
    """Create risk treatment entries when an attack path is created"""
    try:
        # Get all damage scenarios linked to this threat scenario
        query = text("""
            SELECT ds.scenario_id, ds.scope_id, ds.safety_impact, ds.financial_impact, 
                   ds.operational_impact, ds.privacy_impact, ds.confidentiality_impact,
                   ds.integrity_impact, ds.availability_impact, ds.severity
            FROM damage_scenarios ds
            JOIN threat_damage_links tdl ON ds.scenario_id = tdl.damage_scenario_id
            WHERE tdl.threat_scenario_id = :threat_scenario_id
        """)
        
        result = db.execute(query, {"threat_scenario_id": attack_path.threat_scenario_id})
        damage_scenarios = result.fetchall()
        
        for ds in damage_scenarios:
            # Calculate impact level from SFOP or CIA fields
            impact_level = calculate_impact_level_from_scenario(ds)
            
            # Calculate feasibility level from attack path rating
            feasibility_level = calculate_feasibility_level_from_score(attack_path.overall_rating)
            
            # Calculate risk level using ISO 21434 matrix
            risk_level = calculate_risk_level_from_matrix(impact_level, feasibility_level)
            
            # Determine suggested treatment based on risk level
            suggested_treatment = get_suggested_treatment_from_risk(risk_level)
            
            # Create risk treatment entry
            risk_treatment_id = f"rt_{uuid.uuid4().hex[:8]}"
            
            insert_query = text("""
                INSERT INTO risk_treatments (
                    risk_treatment_id, damage_scenario_id, attack_path_id, scope_id,
                    impact_level, feasibility_level, risk_level, feasibility_score,
                    suggested_treatment, treatment_status
                ) VALUES (
                    :risk_treatment_id, :damage_scenario_id, :attack_path_id, :scope_id,
                    :impact_level, :feasibility_level, :risk_level, :feasibility_score,
                    :suggested_treatment, 'draft'
                )
            """)
            
            db.execute(insert_query, {
                "risk_treatment_id": risk_treatment_id,
                "damage_scenario_id": ds.scenario_id,
                "attack_path_id": attack_path.attack_path_id,
                "scope_id": ds.scope_id,
                "impact_level": impact_level,
                "feasibility_level": feasibility_level,
                "risk_level": risk_level,
                "feasibility_score": attack_path.overall_rating,
                "suggested_treatment": suggested_treatment
            })
        
        db.commit()
        logger.info(f"Created {len(damage_scenarios)} risk treatment entries for attack path {attack_path.attack_path_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating risk treatments for attack path {attack_path.attack_path_id}: {str(e)}")
        raise

def calculate_impact_level_from_scenario(scenario):
    """Calculate impact level from damage scenario SFOP or CIA fields"""
    impacts = []
    
    # Check SFOP impact fields first
    if scenario.safety_impact:
        impacts.append(scenario.safety_impact.title())
    if scenario.financial_impact:
        impacts.append(scenario.financial_impact.title())
    if scenario.operational_impact:
        impacts.append(scenario.operational_impact.title())
    if scenario.privacy_impact:
        impacts.append(scenario.privacy_impact.title())
    
    # If no SFOP impacts, check CIA boolean fields with severity
    if not impacts:
        has_impact = (scenario.confidentiality_impact or 
                     scenario.integrity_impact or 
                     scenario.availability_impact)
        if has_impact and scenario.severity:
            impacts.append(scenario.severity.title())
    
    # Determine highest impact based on severity order
    if not impacts:
        return "Negligible"
    
    severity_order = ["Negligible", "Moderate", "Major", "Severe"]
    highest_impact = "Negligible"
    
    for impact in impacts:
        if impact in severity_order:
            if severity_order.index(impact) > severity_order.index(highest_impact):
                highest_impact = impact
    
    return highest_impact

def calculate_feasibility_level_from_score(score: float) -> str:
    """Convert Attack Feasibility Score to qualitative level"""
    if score >= 25:
        return "Very Low"
    elif score >= 20:
        return "Low"
    elif score >= 14:
        return "Medium"
    elif score >= 1:
        return "High"
    else:
        return "Very High"

def calculate_risk_level_from_matrix(impact: str, feasibility: str) -> str:
    """Calculate risk level using ISO 21434 risk matrix"""
    risk_matrix = {
        "Severe": {"Very High": "Critical", "High": "Critical", "Medium": "High", "Low": "Medium", "Very Low": "Medium"},
        "Major": {"Very High": "High", "High": "High", "Medium": "Medium", "Low": "Low", "Very Low": "Low"},
        "Moderate": {"Very High": "Medium", "High": "Medium", "Medium": "Low", "Low": "Low", "Very Low": "Low"},
        "Negligible": {"Very High": "Low", "High": "Low", "Medium": "Low", "Low": "Low", "Very Low": "Low"}
    }
    return risk_matrix.get(impact, {}).get(feasibility, "Low")

def get_suggested_treatment_from_risk(risk_level: str) -> str:
    """Get suggested treatment based on risk level"""
    treatment_suggestions = {
        "Critical": "Reducing",
        "High": "Reducing", 
        "Medium": "Sharing",
        "Low": "Retaining"
    }
    return treatment_suggestions.get(risk_level, "Retaining")

@router.get("/product/{product_id}", response_model=AttackPathResponse)
async def get_attack_paths_by_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get all attack paths for a specific product via threat scenarios"""
    try:
        # Get attack paths through threat scenarios that belong to the product
        query = text("""
        SELECT ap.* FROM attack_paths ap
        JOIN threat_scenarios ts ON ap.threat_scenario_id = ts.threat_scenario_id
        WHERE ts.scope_id = :product_id
        ORDER BY ap.created_at DESC
        """)
        
        result = db.execute(query, {"product_id": product_id})
        rows = result.fetchall()
        
        attack_paths = []
        for row in rows:
            feasibility_rating = FeasibilityRating(
                elapsed_time=row.elapsed_time,
                specialist_expertise=row.specialist_expertise,
                knowledge_of_target=row.knowledge_of_target,
                window_of_opportunity=row.window_of_opportunity,
                equipment=row.equipment,
                overall_rating=row.overall_rating
            )
            
            attack_path = AttackPath(
                attack_path_id=row.attack_path_id,
                threat_scenario_id=row.threat_scenario_id,
                name=row.name,
                description=row.description,
                attack_steps=row.attack_steps,
                feasibility_rating=feasibility_rating,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            attack_paths.append(attack_path)
        
        return AttackPathResponse(attack_paths=attack_paths, total=len(attack_paths))
        
    except Exception as e:
        logger.error(f"Error getting attack paths for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack paths: {str(e)}")

@router.get("/threat-scenario/{threat_scenario_id}", response_model=AttackPathResponse)
async def get_attack_paths_by_threat_scenario(
    threat_scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get all attack paths for a specific threat scenario"""
    try:
        attack_paths_db = db.query(AttackPathDB).filter(
            AttackPathDB.threat_scenario_id == threat_scenario_id
        ).order_by(AttackPathDB.created_at.desc()).all()
        
        attack_paths = []
        for ap_db in attack_paths_db:
            feasibility_rating = FeasibilityRating(
                elapsed_time=ap_db.elapsed_time,
                specialist_expertise=ap_db.specialist_expertise,
                knowledge_of_target=ap_db.knowledge_of_target,
                window_of_opportunity=ap_db.window_of_opportunity,
                equipment=ap_db.equipment,
                overall_rating=ap_db.overall_rating
            )
            
            attack_path = AttackPath(
                attack_path_id=ap_db.attack_path_id,
                threat_scenario_id=ap_db.threat_scenario_id,
                name=ap_db.name,
                description=ap_db.description,
                attack_steps=ap_db.attack_steps,
                feasibility_rating=feasibility_rating,
                created_at=ap_db.created_at,
                updated_at=ap_db.updated_at
            )
            attack_paths.append(attack_path)
        
        return AttackPathResponse(attack_paths=attack_paths, total=len(attack_paths))
        
    except Exception as e:
        logger.error(f"Error getting attack paths for threat scenario {threat_scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack paths: {str(e)}")

@router.post("", response_model=AttackPath)
async def create_attack_path(
    attack_path: AttackPathCreate,
    db: Session = Depends(get_db)
):
    """Create a new attack path"""
    try:
        # Calculate overall rating
        rating = attack_path.feasibility_rating
        overall_rating = (
            rating.elapsed_time + 
            rating.specialist_expertise + 
            rating.knowledge_of_target + 
            rating.window_of_opportunity + 
            rating.equipment
        )
        
        # Create database record
        db_attack_path = AttackPathDB(
            threat_scenario_id=attack_path.threat_scenario_id,
            name=attack_path.name,
            description=attack_path.description,
            attack_steps=attack_path.attack_steps,
            elapsed_time=rating.elapsed_time,
            specialist_expertise=rating.specialist_expertise,
            knowledge_of_target=rating.knowledge_of_target,
            window_of_opportunity=rating.window_of_opportunity,
            equipment=rating.equipment,
            overall_rating=overall_rating
        )
        
        db.add(db_attack_path)
        db.commit()
        db.refresh(db_attack_path)
        
        # Create risk treatment entries for all damage scenarios linked to this threat scenario
        create_risk_treatments_for_attack_path(db, db_attack_path)
        
        
        # Return the created attack path
        feasibility_rating = FeasibilityRating(
            elapsed_time=db_attack_path.elapsed_time,
            specialist_expertise=db_attack_path.specialist_expertise,
            knowledge_of_target=db_attack_path.knowledge_of_target,
            window_of_opportunity=db_attack_path.window_of_opportunity,
            equipment=db_attack_path.equipment,
            overall_rating=db_attack_path.overall_rating
        )
        
        return AttackPath(
            attack_path_id=db_attack_path.attack_path_id,
            threat_scenario_id=db_attack_path.threat_scenario_id,
            name=db_attack_path.name,
            description=db_attack_path.description,
            attack_steps=db_attack_path.attack_steps,
            feasibility_rating=feasibility_rating,
            created_at=db_attack_path.created_at,
            updated_at=db_attack_path.updated_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating attack path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating attack path: {str(e)}")

@router.put("/{attack_path_id}", response_model=AttackPath)
async def update_attack_path(
    attack_path_id: str,
    attack_path: AttackPathCreate,
    db: Session = Depends(get_db)
):
    """Update an existing attack path"""
    try:
        db_attack_path = db.query(AttackPathDB).filter(
            AttackPathDB.attack_path_id == attack_path_id
        ).first()
        
        if not db_attack_path:
            raise HTTPException(status_code=404, detail="Attack path not found")
        
        # Calculate overall rating
        rating = attack_path.feasibility_rating
        overall_rating = (
            rating.elapsed_time + 
            rating.specialist_expertise + 
            rating.knowledge_of_target + 
            rating.window_of_opportunity + 
            rating.equipment
        )
        
        # Update fields
        db_attack_path.threat_scenario_id = attack_path.threat_scenario_id
        db_attack_path.name = attack_path.name
        db_attack_path.description = attack_path.description
        db_attack_path.attack_steps = attack_path.attack_steps
        db_attack_path.elapsed_time = rating.elapsed_time
        db_attack_path.specialist_expertise = rating.specialist_expertise
        db_attack_path.knowledge_of_target = rating.knowledge_of_target
        db_attack_path.window_of_opportunity = rating.window_of_opportunity
        db_attack_path.equipment = rating.equipment
        db_attack_path.overall_rating = overall_rating
        
        db.commit()
        db.refresh(db_attack_path)
        
        # Return updated attack path
        feasibility_rating = FeasibilityRating(
            elapsed_time=db_attack_path.elapsed_time,
            specialist_expertise=db_attack_path.specialist_expertise,
            knowledge_of_target=db_attack_path.knowledge_of_target,
            window_of_opportunity=db_attack_path.window_of_opportunity,
            equipment=db_attack_path.equipment,
            overall_rating=db_attack_path.overall_rating
        )
        
        return AttackPath(
            attack_path_id=db_attack_path.attack_path_id,
            threat_scenario_id=db_attack_path.threat_scenario_id,
            name=db_attack_path.name,
            description=db_attack_path.description,
            attack_steps=db_attack_path.attack_steps,
            feasibility_rating=feasibility_rating,
            created_at=db_attack_path.created_at,
            updated_at=db_attack_path.updated_at
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating attack path {attack_path_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating attack path: {str(e)}")

@router.delete("/{attack_path_id}")
async def delete_attack_path(
    attack_path_id: str,
    db: Session = Depends(get_db)
):
    """Delete an attack path"""
    try:
        db_attack_path = db.query(AttackPathDB).filter(
            AttackPathDB.attack_path_id == attack_path_id
        ).first()
        
        if not db_attack_path:
            raise HTTPException(status_code=404, detail="Attack path not found")
        
        db.delete(db_attack_path)
        db.commit()
        
        return {"message": "Attack path deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting attack path {attack_path_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting attack path: {str(e)}")
