"""
Threat Scenario API routes for QuickTARA
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from api.deps.db import get_db
from core.audit_helpers import get_user_from_request, audit_create, audit_update, audit_delete, audit_status_change
from api.models.threat_scenario import ThreatScenario, ThreatScenarioCreate, ThreatScenarioUpdate, ThreatScenarioList
from db.threat_scenario import ThreatScenario as DBThreatScenario
from db.product_asset_models import ProductScope as DBProductScope
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_threat_scenario_id(db: Session, scope_id: str) -> str:
    """Generate next available threat scenario ID (TS-001, TS-002, etc.)"""
    # Get ALL existing threat scenario IDs (not just for this scope)
    # to ensure global uniqueness across all products
    existing_scenarios = db.query(DBThreatScenario).filter(
        DBThreatScenario.is_deleted == False
    ).all()
    
    # Extract numeric parts and find the highest
    max_num = 0
    for scenario in existing_scenarios:
        if scenario.threat_scenario_id and scenario.threat_scenario_id.startswith("TS-"):
            try:
                num = int(scenario.threat_scenario_id[3:])
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    # Generate next ID and check if it already exists
    next_num = max_num + 1
    while True:
        candidate_id = f"TS-{next_num:03d}"
        existing = db.query(DBThreatScenario).filter(
            DBThreatScenario.threat_scenario_id == candidate_id
        ).first()
        if not existing:
            return candidate_id
        next_num += 1


@router.get("", response_model=ThreatScenarioList)
async def list_threat_scenarios(
    scope_id: Optional[str] = None,
    damage_scenario_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List threat scenarios with optional filtering"""
    if damage_scenario_id:
        # Filter by damage scenario if provided (using junction table)
        if damage_scenario_id:
            from sqlalchemy import text
            linked_threat_ids = db.execute(
                text("SELECT threat_scenario_id FROM threat_damage_links WHERE damage_scenario_id = :damage_scenario_id"), 
                {"damage_scenario_id": damage_scenario_id}
            ).fetchall()
        threat_ids = [row[0] for row in linked_threat_ids]
        
        if threat_ids:
            query = db.query(DBThreatScenario).filter(
                DBThreatScenario.threat_scenario_id.in_(threat_ids),
                DBThreatScenario.is_deleted == False
            )
        else:
            # No linked threats found
            query = db.query(DBThreatScenario).filter(DBThreatScenario.threat_scenario_id == None)
    else:
        query = db.query(DBThreatScenario).filter(DBThreatScenario.is_deleted == False)
    
    if scope_id:
        query = query.filter(DBThreatScenario.scope_id == scope_id)
    
    total = query.count()
    threat_scenarios = query.offset(skip).limit(limit).all()
    
    return ThreatScenarioList(
        threat_scenarios=threat_scenarios,
        total=total
    )


@router.post("", response_model=ThreatScenario, status_code=status.HTTP_201_CREATED)
async def create_threat_scenario(
    request: Request,
    threat_scenario: ThreatScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create a new threat scenario"""
    try:
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
        
        # Create new threat scenario (without damage_scenario_id in main table)
        db_threat_scenario = DBThreatScenario(
            threat_scenario_id=threat_scenario.threat_scenario_id,
            damage_scenario_id=None,  # Will use junction table instead
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
        
        # Handle damage scenario links for many-to-many relationship
        from sqlalchemy import text
        if hasattr(threat_scenario, 'damage_scenario_ids') and threat_scenario.damage_scenario_ids:
            for damage_scenario_id in threat_scenario.damage_scenario_ids:
                db.execute(
                    text("INSERT OR IGNORE INTO threat_damage_links (threat_scenario_id, damage_scenario_id) VALUES (:threat_scenario_id, :damage_scenario_id)"),
                    {"threat_scenario_id": threat_scenario.threat_scenario_id, "damage_scenario_id": damage_scenario_id}
                )
        elif threat_scenario.damage_scenario_id:
            # Support legacy single damage scenario ID
            db.execute(
                text("INSERT OR IGNORE INTO threat_damage_links (threat_scenario_id, damage_scenario_id) VALUES (:threat_scenario_id, :damage_scenario_id)"),
                {"threat_scenario_id": threat_scenario.threat_scenario_id, "damage_scenario_id": threat_scenario.damage_scenario_id}
            )  
        user = get_user_from_request(request)
        audit_create(db, "threat_scenario", threat_scenario.threat_scenario_id, user, scope_id=threat_scenario.scope_id)
        db.commit()
        return db_threat_scenario
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating threat scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create threat scenario: {str(e)}"
        )


@router.get("/{threat_scenario_id}", response_model=ThreatScenario)
async def get_threat_scenario(
    threat_scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific threat scenario by ID"""
    threat_scenario = db.query(DBThreatScenario).filter(
        DBThreatScenario.threat_scenario_id == threat_scenario_id,
        DBThreatScenario.is_deleted == False
    ).first()
    
    if not threat_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat scenario {threat_scenario_id} not found"
        )
    
    return threat_scenario


@router.get("/{threat_scenario_id}/damage-scenarios")
async def get_threat_scenario_damage_scenarios(
    threat_scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get all damage scenarios linked to a specific threat scenario"""
    # Check if threat scenario exists
    threat_scenario = db.query(DBThreatScenario).filter(
        DBThreatScenario.threat_scenario_id == threat_scenario_id,
        DBThreatScenario.is_deleted == False
    ).first()
    
    if not threat_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat scenario {threat_scenario_id} not found"
        )
    
    # Get linked damage scenario IDs from junction table
    from sqlalchemy import text
    linked_damage_ids = db.execute(
        text("SELECT damage_scenario_id FROM threat_damage_links WHERE threat_scenario_id = :threat_scenario_id"),
        {"threat_scenario_id": threat_scenario_id}
    ).fetchall()
    
    damage_scenario_ids = [row[0] for row in linked_damage_ids]
    
    return {"damage_scenario_ids": damage_scenario_ids}


@router.put("/{threat_scenario_id}", response_model=ThreatScenario)
async def update_threat_scenario(
    threat_scenario_id: str,
    threat_scenario_update: ThreatScenarioUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a threat scenario"""
    # Get existing threat scenario
    from sqlalchemy import and_
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
    
    user = get_user_from_request(request)
    audit_update(db, "threat_scenario", threat_scenario_id, user, scope_id=getattr(db_threat_scenario, 'scope_id', None), summary="Threat scenario updated")
    db.commit()
    db.refresh(db_threat_scenario)
    
    return db_threat_scenario


@router.patch("/{threat_scenario_id}/accept", response_model=ThreatScenario)
async def accept_threat_scenario(
    threat_scenario_id: str,
    db: Session = Depends(get_db),
):
    """Accept a draft threat scenario (move from draft → accepted)."""
    scenario = db.query(DBThreatScenario).filter(
        DBThreatScenario.threat_scenario_id == threat_scenario_id,
        DBThreatScenario.is_deleted == False,
    ).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Threat scenario not found")
    old_status = scenario.status or "draft"
    scenario.status = "accepted"
    audit_status_change(db, "threat_scenario", threat_scenario_id, "system", old_status, "accepted", scope_id=getattr(scenario, 'scope_id', None))
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{threat_scenario_id}")
async def delete_threat_scenario(
    threat_scenario_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a threat scenario (soft delete)"""
    from sqlalchemy import and_
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
    user = get_user_from_request(request)
    audit_delete(db, "threat_scenario", threat_scenario_id, user, scope_id=getattr(threat_scenario, 'scope_id', None))
    db.commit()
    
    return {"message": f"Threat scenario {threat_scenario_id} deleted successfully"}
