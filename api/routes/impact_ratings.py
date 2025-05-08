"""
Impact Rating API routes
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.damage_scenario import DamageScenario, SeverityLevel, DamageCategory
from api.models.impact_rating import ImpactRatingUpdate, ImpactRatingExplanation, ImpactRatingSuggestion
from api.services.damage_scenario_service import (
    get_damage_scenario,
    update_damage_scenario as service_update_scenario,
    get_damage_scenarios as service_get_scenarios,
    count_damage_scenarios as service_count_scenarios
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/scenarios/{scenario_id}/impact-ratings", response_model=DamageScenario)
async def get_impact_ratings(
    scenario_id: str = Path(..., description="The ID of the damage scenario"),
    db: Session = Depends(get_db)
):
    """
    Get impact ratings for a specific damage scenario
    """
    scenario = get_damage_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Damage scenario with ID {scenario_id} not found"
        )
    return scenario


@router.put("/scenarios/{scenario_id}/impact-ratings", response_model=DamageScenario)
async def update_impact_ratings(
    scenario_id: str = Path(..., description="The ID of the damage scenario"),
    ratings: ImpactRatingUpdate = ...,
    db: Session = Depends(get_db)
):
    """
    Update impact ratings for a damage scenario
    """
    # Validate that override reason is provided if auto-generated ratings are being changed
    scenario = get_damage_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
        
    if scenario.sfop_rating_auto_generated and not ratings.sfop_rating_override_reason:
        raise HTTPException(
            status_code=400, 
            detail="Override reason is required when changing auto-generated ratings"
        )
    
    # Add audit information
    update_data = ratings.dict(exclude_unset=True)
    update_data["sfop_rating_auto_generated"] = False  # Mark as manually edited
    update_data["sfop_rating_last_edited_by"] = "system"  # Use a default value since we don't have auth
    update_data["sfop_rating_last_edited_at"] = datetime.now()
    
    # Convert dictionary to DamageScenarioUpdate object
    from api.models.damage_scenario import DamageScenarioUpdate
    update_obj = DamageScenarioUpdate(**update_data)
    
    # Update the scenario
    updated = service_update_scenario(db, scenario_id, update_obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
    return updated


@router.get("/suggest-ratings", response_model=ImpactRatingSuggestion)
async def suggest_sfop_ratings(
    component_id: str = Query(..., description="The ID of the primary component"),
    damage_category: DamageCategory = Query(..., description="The damage category"),
    confidentiality_impact: bool = Query(False, description="Whether confidentiality is impacted"),
    integrity_impact: bool = Query(False, description="Whether integrity is impacted"),
    availability_impact: bool = Query(False, description="Whether availability is impacted"),
    db: Session = Depends(get_db)
):
    """
    Get suggested SFOP impact ratings based on component properties and damage details
    """
    # This would typically call a service function that implements the suggestion algorithm
    # For now, we'll return a simple placeholder implementation
    
    # In a real implementation, this would analyze:
    # 1. Component type, criticality, and safety level
    # 2. Damage category and CIA impacts
    # 3. System context and dependencies
    
    # Placeholder logic - would be replaced with actual algorithm
    safety_impact = SeverityLevel.HIGH if damage_category == DamageCategory.SAFETY else SeverityLevel.LOW
    financial_impact = SeverityLevel.HIGH if damage_category == DamageCategory.FINANCIAL else SeverityLevel.MEDIUM
    operational_impact = SeverityLevel.HIGH if damage_category == DamageCategory.OPERATIONAL else SeverityLevel.MEDIUM
    privacy_impact = SeverityLevel.HIGH if damage_category == DamageCategory.PRIVACY else SeverityLevel.LOW
    
    # If availability is impacted, operational impact is at least MEDIUM
    if availability_impact and operational_impact == SeverityLevel.LOW:
        operational_impact = SeverityLevel.MEDIUM
        
    # If confidentiality is impacted, privacy impact is at least MEDIUM
    if confidentiality_impact and privacy_impact == SeverityLevel.LOW:
        privacy_impact = SeverityLevel.MEDIUM
    
    explanations = ImpactRatingExplanation(
        safety_impact=f"Based on component type and {damage_category.value} damage category",
        financial_impact=f"Based on component criticality and {damage_category.value} damage category",
        operational_impact=f"Based on system dependencies and {'availability impact' if availability_impact else 'no availability impact'}",
        privacy_impact=f"Based on data sensitivity and {'confidentiality impact' if confidentiality_impact else 'no confidentiality impact'}"
    )
    
    return ImpactRatingSuggestion(
        safety_impact=safety_impact,
        financial_impact=financial_impact,
        operational_impact=operational_impact,
        privacy_impact=privacy_impact,
        explanations=explanations
    )


@router.get("/list", response_model=List[DamageScenario])
async def list_impact_ratings(
    skip: int = 0,
    limit: int = 100,
    scope_id: Optional[str] = None,
    safety_impact: Optional[SeverityLevel] = None,
    financial_impact: Optional[SeverityLevel] = None,
    operational_impact: Optional[SeverityLevel] = None,
    privacy_impact: Optional[SeverityLevel] = None,
    auto_generated_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all damage scenarios with their impact ratings, with filtering options
    """
    # Get all scenarios first
    base_filters = {}
    if scope_id:
        base_filters["scope_id"] = scope_id
        
    # Get all scenarios with basic filters
    scenarios = service_get_scenarios(db, skip=skip, limit=limit, **base_filters)
    
    # Apply SFOP-specific filters manually
    filtered_scenarios = []
    for scenario in scenarios:
        # Skip if any of the SFOP filters don't match
        if safety_impact and scenario.safety_impact != safety_impact:
            continue
        if financial_impact and scenario.financial_impact != financial_impact:
            continue
        if operational_impact and scenario.operational_impact != operational_impact:
            continue
        if privacy_impact and scenario.privacy_impact != privacy_impact:
            continue
        if auto_generated_only and not scenario.sfop_rating_auto_generated:
            continue
            
        filtered_scenarios.append(scenario)
    
    return filtered_scenarios
