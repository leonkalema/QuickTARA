"""
Threat Scenario API routes for QuickTARA
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..deps.db import get_db
from ..models.threat_scenario import (
    ThreatScenario,
    ThreatScenarioCreate,
    ThreatScenarioUpdate,
    ThreatScenarioList
)
from db.threat_scenario import ThreatScenario as DBThreatScenario
from db.product_asset_models import ProductScope as DBProductScope

router = APIRouter()


def generate_threat_scenario_id(db: Session, scope_id: str) -> str:
    """Generate next available threat scenario ID (TS-001, TS-002, etc.)"""
    # Get the highest existing ID for this scope
    existing_scenarios = db.query(DBThreatScenario).filter(
        DBThreatScenario.scope_id == scope_id,
        DBThreatScenario.is_deleted == False
    ).all()
    
    # Extract numeric parts and find the highest
    max_num = 0
    for scenario in existing_scenarios:
        if scenario.threat_scenario_id.startswith("TS-"):
            try:
                num = int(scenario.threat_scenario_id[3:])
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"TS-{max_num + 1:03d}"


@router.get("", response_model=ThreatScenarioList)
async def list_threat_scenarios(
    skip: int = 0,
    limit: int = 100,
    scope_id: Optional[str] = None,
    damage_scenario_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List threat scenarios with optional filtering"""
    query = db.query(DBThreatScenario).filter(DBThreatScenario.is_deleted == False)
    
    if scope_id:
        query = query.filter(DBThreatScenario.scope_id == scope_id)
    
    if damage_scenario_id:
        query = query.filter(DBThreatScenario.damage_scenario_id == damage_scenario_id)
    
    total = query.count()
    threat_scenarios = query.offset(skip).limit(limit).all()
    
    return {"threat_scenarios": threat_scenarios, "total": total}


@router.post("", response_model=ThreatScenario, status_code=status.HTTP_201_CREATED)
async def create_threat_scenario(
    threat_scenario: ThreatScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create a new threat scenario"""
    # Verify the product scope exists
    product = db.query(DBProductScope).filter(
        DBProductScope.scope_id == threat_scenario.scope_id,
        DBProductScope.is_current == True
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product scope {threat_scenario.scope_id} not found"
        )
    
    # Generate ID if not provided
    if not threat_scenario.threat_scenario_id:
        threat_scenario.threat_scenario_id = generate_threat_scenario_id(db, threat_scenario.scope_id)
    
    # Create new threat scenario
    db_threat_scenario = DBThreatScenario(
        threat_scenario_id=threat_scenario.threat_scenario_id,
        damage_scenario_id=threat_scenario.damage_scenario_id,
        name=threat_scenario.name,
        description=threat_scenario.description,
        attack_vector=threat_scenario.attack_vector,
        scope_id=threat_scenario.scope_id,
        scope_version=threat_scenario.scope_version,
        version=1,
        is_deleted=False
    )
    
    db.add(db_threat_scenario)
    db.commit()
    db.refresh(db_threat_scenario)
    
    return db_threat_scenario


@router.get("/{threat_scenario_id}", response_model=ThreatScenario)
async def get_threat_scenario(
    threat_scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific threat scenario by ID"""
    threat_scenario = db.query(DBThreatScenario).filter(
        and_(
            DBThreatScenario.threat_scenario_id == threat_scenario_id,
            DBThreatScenario.is_deleted == False
        )
    ).first()
    
    if not threat_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat scenario {threat_scenario_id} not found"
        )
    
    return threat_scenario


@router.put("/{threat_scenario_id}", response_model=ThreatScenario)
async def update_threat_scenario(
    threat_scenario_id: str,
    threat_scenario_update: ThreatScenarioUpdate,
    db: Session = Depends(get_db)
):
    """Update a threat scenario"""
    # Get existing threat scenario
    db_threat_scenario = db.query(DBThreatScenario).filter(
        and_(
            DBThreatScenario.threat_scenario_id == threat_scenario_id,
            DBThreatScenario.is_deleted == False
        )
    ).first()
    
    if not db_threat_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat scenario {threat_scenario_id} not found"
        )
    
    # Update fields
    update_data = threat_scenario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_threat_scenario, field, value)
    
    # Increment version
    db_threat_scenario.version += 1
    
    db.commit()
    db.refresh(db_threat_scenario)
    
    return db_threat_scenario


@router.delete("/{threat_scenario_id}")
async def delete_threat_scenario(
    threat_scenario_id: str,
    db: Session = Depends(get_db)
):
    """Delete a threat scenario (soft delete)"""
    threat_scenario = db.query(DBThreatScenario).filter(
        and_(
            DBThreatScenario.threat_scenario_id == threat_scenario_id,
            DBThreatScenario.is_deleted == False
        )
    ).first()
    
    if not threat_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat scenario {threat_scenario_id} not found"
        )
    
    # Soft delete
    threat_scenario.is_deleted = True
    db.commit()
    
    return {"message": f"Threat scenario {threat_scenario_id} deleted successfully"}
