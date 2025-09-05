"""
Simple Attack Path API routes for Risk Assessment
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
import logging

from api.models.simple_attack_path import (
    AttackPath, AttackPathCreate, AttackPathResponse, AttackPathDB, FeasibilityRating
)
from api.deps.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

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
        ) / 5.0
        
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
        ) / 5.0
        
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
