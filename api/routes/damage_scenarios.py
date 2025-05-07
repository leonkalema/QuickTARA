"""
Damage Scenario API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.damage_scenario import (
    DamageScenario, 
    DamageScenarioCreate, 
    DamageScenarioUpdate, 
    DamageScenarioList,
    PropagationSuggestion,
    PropagationSuggestionResponse
)
from api.services.damage_scenario_service import (
    create_damage_scenario as service_create_scenario,
    get_damage_scenario as service_get_scenario,
    get_damage_scenarios as service_get_scenarios,
    count_damage_scenarios as service_count_scenarios,
    update_damage_scenario as service_update_scenario,
    delete_damage_scenario as service_delete_scenario,
    generate_propagation_suggestions as service_generate_suggestions
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=DamageScenarioList)
async def list_damage_scenarios(
    skip: int = 0, 
    limit: int = 100,
    scope_id: Optional[str] = None,
    component_id: Optional[str] = None,
    damage_category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all damage scenarios with pagination and filtering
    """
    scenarios = service_get_scenarios(
        db, 
        skip=skip, 
        limit=limit,
        scope_id=scope_id,
        component_id=component_id,
        damage_category=damage_category,
        severity=severity
    )
    total = service_count_scenarios(
        db,
        scope_id=scope_id,
        component_id=component_id,
        damage_category=damage_category,
        severity=severity
    )
    return DamageScenarioList(scenarios=scenarios, total=total)


@router.post("", response_model=DamageScenario, status_code=status.HTTP_201_CREATED)
async def create_damage_scenario(
    scenario: DamageScenarioCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new damage scenario
    """
    try:
        return service_create_scenario(db, scenario)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{scenario_id}", response_model=DamageScenario)
async def get_damage_scenario(
    scenario_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get a damage scenario by ID
    """
    scenario = service_get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Damage scenario with ID {scenario_id} not found"
        )
    return scenario


@router.put("/{scenario_id}", response_model=DamageScenario)
async def update_damage_scenario(
    scenario_id: str, 
    scenario: DamageScenarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a damage scenario
    """
    try:
        updated = service_update_scenario(db, scenario_id, scenario)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Damage scenario with ID {scenario_id} not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_damage_scenario(
    scenario_id: str, 
    db: Session = Depends(get_db)
):
    """
    Delete a damage scenario
    """
    success = service_delete_scenario(db, scenario_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Damage scenario with ID {scenario_id} not found"
        )
    return None


@router.get("/propagation/suggestions", response_model=PropagationSuggestionResponse)
async def get_propagation_suggestions(
    component_id: str,
    confidentiality_impact: bool = Query(False, description="Whether confidentiality is impacted"),
    integrity_impact: bool = Query(False, description="Whether integrity is impacted"),
    availability_impact: bool = Query(False, description="Whether availability is impacted"),
    db: Session = Depends(get_db)
):
    """
    Get impact propagation suggestions for a component
    """
    try:
        suggestions = service_generate_suggestions(
            db, 
            component_id,
            confidentiality_impact,
            integrity_impact,
            availability_impact
        )
        return PropagationSuggestionResponse(suggestions=suggestions, total=len(suggestions))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
