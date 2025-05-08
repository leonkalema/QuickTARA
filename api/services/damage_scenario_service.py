"""
Damage Scenario service layer
"""
from typing import List, Optional, Dict, Any, Set
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime

from db.damage_scenario import DamageScenario as DBDamageScenario
from db.base import Component as DBComponent, SystemScope as DBSystemScope
from api.models.damage_scenario import (
    DamageScenario, 
    DamageScenarioCreate, 
    DamageScenarioUpdate,
    PropagationSuggestion,
    DamageCategory,
    ImpactType,
    SeverityLevel
)


def create_damage_scenario(db: Session, scenario: DamageScenarioCreate) -> DamageScenario:
    """
    Create a new damage scenario in the database
    """
    # Generate a unique ID if not provided
    scenario_id = scenario.scenario_id or f"DS-{uuid.uuid4().hex[:8].upper()}"
    
    # Check if scenario with same ID already exists
    existing = db.query(DBDamageScenario).filter(DBDamageScenario.scenario_id == scenario_id).first()
    if existing:
        raise ValueError(f"Damage scenario with ID {scenario_id} already exists")
    
    # Verify that scope exists
    scope = db.query(DBSystemScope).filter(DBSystemScope.scope_id == scenario.scope_id).first()
    if not scope:
        raise ValueError(f"Scope with ID {scenario.scope_id} does not exist")
    
    # Verify that primary component exists
    primary_component = db.query(DBComponent).filter(
        DBComponent.component_id == scenario.primary_component_id
    ).first()
    if not primary_component:
        raise ValueError(f"Component with ID {scenario.primary_component_id} does not exist")
    
    # Create the damage scenario
    db_scenario = DBDamageScenario(
        scenario_id=scenario_id,
        name=scenario.name,
        description=scenario.description,
        damage_category=scenario.damage_category,
        impact_type=scenario.impact_type,
        confidentiality_impact=scenario.confidentiality_impact,
        integrity_impact=scenario.integrity_impact,
        availability_impact=scenario.availability_impact,
        severity=scenario.severity,
        impact_details=json.dumps(scenario.impact_details) if scenario.impact_details else None,
        version=scenario.version,
        revision_notes=scenario.revision_notes,
        scope_id=scenario.scope_id,
        primary_component_id=scenario.primary_component_id
    )
    
    # Add to database
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    
    # Handle affected components (many-to-many relationship)
    affected_components = []
    for component_id in scenario.affected_component_ids:
        component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
        if component:
            affected_components.append(component)
    
    if affected_components:
        db_scenario.affected_components = affected_components
        db.commit()
        db.refresh(db_scenario)
    
    return _db_scenario_to_schema(db_scenario)


def get_damage_scenario(db: Session, scenario_id: str) -> Optional[DamageScenario]:
    """
    Get a damage scenario by ID
    """
    db_scenario = db.query(DBDamageScenario).filter(
        DBDamageScenario.scenario_id == scenario_id,
        DBDamageScenario.is_deleted == False
    ).first()
    
    if not db_scenario:
        return None
    
    return _db_scenario_to_schema(db_scenario)


def get_damage_scenarios(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    scope_id: Optional[str] = None,
    component_id: Optional[str] = None,
    damage_category: Optional[str] = None,
    severity: Optional[str] = None
) -> List[DamageScenario]:
    """
    Get all damage scenarios with pagination and filtering
    """
    query = db.query(DBDamageScenario).filter(DBDamageScenario.is_deleted == False)
    
    # Apply filters
    if scope_id:
        query = query.filter(DBDamageScenario.scope_id == scope_id)
    
    if component_id:
        # Filter by primary component or affected components
        query = query.filter(
            (DBDamageScenario.primary_component_id == component_id) | 
            (DBDamageScenario.affected_components.any(DBComponent.component_id == component_id))
        )
    
    if damage_category:
        query = query.filter(DBDamageScenario.damage_category == damage_category)
    
    if severity:
        query = query.filter(DBDamageScenario.severity == severity)
    
    # Apply pagination
    db_scenarios = query.order_by(DBDamageScenario.created_at.desc()).offset(skip).limit(limit).all()
    
    return [_db_scenario_to_schema(s) for s in db_scenarios]


def count_damage_scenarios(
    db: Session,
    scope_id: Optional[str] = None,
    component_id: Optional[str] = None,
    damage_category: Optional[str] = None,
    severity: Optional[str] = None
) -> int:
    """
    Count total number of damage scenarios with filters
    """
    query = db.query(DBDamageScenario).filter(DBDamageScenario.is_deleted == False)
    
    # Apply filters
    if scope_id:
        query = query.filter(DBDamageScenario.scope_id == scope_id)
    
    if component_id:
        # Filter by primary component or affected components
        query = query.filter(
            (DBDamageScenario.primary_component_id == component_id) | 
            (DBDamageScenario.affected_components.any(DBComponent.component_id == component_id))
        )
    
    if damage_category:
        query = query.filter(DBDamageScenario.damage_category == damage_category)
    
    if severity:
        query = query.filter(DBDamageScenario.severity == severity)
    
    return query.count()


def update_damage_scenario(
    db: Session, 
    scenario_id: str, 
    scenario: DamageScenarioUpdate
) -> Optional[DamageScenario]:
    """
    Update an existing damage scenario
    """
    db_scenario = db.query(DBDamageScenario).filter(
        DBDamageScenario.scenario_id == scenario_id,
        DBDamageScenario.is_deleted == False
    ).first()
    
    if not db_scenario:
        return None
    
    # Update fields if provided
    if scenario.name is not None:
        db_scenario.name = scenario.name
    
    if scenario.description is not None:
        db_scenario.description = scenario.description
    
    if scenario.damage_category is not None:
        db_scenario.damage_category = scenario.damage_category
    
    if scenario.impact_type is not None:
        db_scenario.impact_type = scenario.impact_type
    
    if scenario.confidentiality_impact is not None:
        db_scenario.confidentiality_impact = scenario.confidentiality_impact
    
    if scenario.integrity_impact is not None:
        db_scenario.integrity_impact = scenario.integrity_impact
    
    if scenario.availability_impact is not None:
        db_scenario.availability_impact = scenario.availability_impact
    
    if scenario.severity is not None:
        db_scenario.severity = scenario.severity
    
    if scenario.impact_details is not None:
        db_scenario.impact_details = json.dumps(scenario.impact_details)
    
    if scenario.version is not None:
        db_scenario.version = scenario.version
    
    if scenario.revision_notes is not None:
        db_scenario.revision_notes = scenario.revision_notes
    
    if scenario.scope_id is not None:
        # Verify that scope exists
        scope = db.query(DBSystemScope).filter(DBSystemScope.scope_id == scenario.scope_id).first()
        if not scope:
            raise ValueError(f"Scope with ID {scenario.scope_id} does not exist")
        db_scenario.scope_id = scenario.scope_id
    
    if scenario.primary_component_id is not None:
        # Verify that primary component exists
        primary_component = db.query(DBComponent).filter(
            DBComponent.component_id == scenario.primary_component_id
        ).first()
        if not primary_component:
            raise ValueError(f"Component with ID {scenario.primary_component_id} does not exist")
        db_scenario.primary_component_id = scenario.primary_component_id
    
    # Update affected components if provided
    if scenario.affected_component_ids is not None:
        affected_components = []
        for component_id in scenario.affected_component_ids:
            component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
            if component:
                affected_components.append(component)
        
        db_scenario.affected_components = affected_components
    
    # Update SFOP impact ratings if provided
    if scenario.safety_impact is not None:
        db_scenario.safety_impact = scenario.safety_impact
    
    if scenario.financial_impact is not None:
        db_scenario.financial_impact = scenario.financial_impact
    
    if scenario.operational_impact is not None:
        db_scenario.operational_impact = scenario.operational_impact
    
    if scenario.privacy_impact is not None:
        db_scenario.privacy_impact = scenario.privacy_impact
    
    if scenario.impact_rating_notes is not None:
        db_scenario.impact_rating_notes = scenario.impact_rating_notes
    
    if scenario.sfop_rating_auto_generated is not None:
        db_scenario.sfop_rating_auto_generated = scenario.sfop_rating_auto_generated
    
    if scenario.sfop_rating_last_edited_by is not None:
        db_scenario.sfop_rating_last_edited_by = scenario.sfop_rating_last_edited_by
    
    if scenario.sfop_rating_last_edited_at is not None:
        db_scenario.sfop_rating_last_edited_at = scenario.sfop_rating_last_edited_at
    
    if scenario.sfop_rating_override_reason is not None:
        db_scenario.sfop_rating_override_reason = scenario.sfop_rating_override_reason
    
    # Update timestamp
    db_scenario.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_scenario)
    
    return _db_scenario_to_schema(db_scenario)


def delete_damage_scenario(db: Session, scenario_id: str) -> bool:
    """
    Soft delete a damage scenario by ID
    """
    db_scenario = db.query(DBDamageScenario).filter(
        DBDamageScenario.scenario_id == scenario_id,
        DBDamageScenario.is_deleted == False
    ).first()
    
    if not db_scenario:
        return False
    
    # Soft delete
    db_scenario.is_deleted = True
    db_scenario.updated_at = datetime.now()
    
    db.commit()
    return True


def generate_propagation_suggestions(
    db: Session, 
    component_id: str,
    confidentiality_impact: bool = False,
    integrity_impact: bool = False,
    availability_impact: bool = False
) -> List[PropagationSuggestion]:
    """
    Generate impact propagation suggestions based on component connections
    """
    # Get the source component
    source_component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
    if not source_component:
        raise ValueError(f"Component with ID {component_id} does not exist")
    
    # Get all connected components (direct connections)
    connected_components = source_component.connected_to
    
    suggestions = []
    
    # Define propagation rules based on component types and security properties
    for target in connected_components:
        # Skip if no impact is selected
        if not any([confidentiality_impact, integrity_impact, availability_impact]):
            continue
        
        # Calculate propagation confidence based on component types and trust zones
        confidence = _calculate_propagation_confidence(source_component, target)
        
        # Determine which impacts propagate based on component types and connection
        c_impact, i_impact, a_impact = _determine_propagated_impacts(
            source_component, 
            target,
            confidentiality_impact,
            integrity_impact,
            availability_impact
        )
        
        # Skip if no impact propagates
        if not any([c_impact, i_impact, a_impact]):
            continue
        
        # Determine appropriate damage category based on component types
        damage_category = _suggest_damage_category(source_component, target)
        
        # Determine impact type (usually Cascading for propagation)
        impact_type = ImpactType.CASCADING
        
        # Determine severity based on component safety levels and trust zones
        severity = _suggest_severity(source_component, target)
        
        # Create suggestion
        suggestion = PropagationSuggestion(
            source_component_id=source_component.component_id,
            target_component_id=target.component_id,
            confidentiality_impact=c_impact,
            integrity_impact=i_impact,
            availability_impact=a_impact,
            damage_category=damage_category,
            impact_type=impact_type,
            severity=severity,
            confidence=confidence,
            path=[source_component.component_id, target.component_id]
        )
        
        suggestions.append(suggestion)
    
    return suggestions


def _calculate_propagation_confidence(source: DBComponent, target: DBComponent) -> float:
    """
    Calculate confidence score for propagation between components
    """
    # Base confidence
    confidence = 0.7
    
    # Adjust based on trust zones
    if source.trust_zone == "Critical" and target.trust_zone == "Critical":
        confidence += 0.2
    elif source.trust_zone == "Critical" and target.trust_zone == "Boundary":
        confidence += 0.1
    elif source.trust_zone == "Untrusted":
        confidence -= 0.2
    
    # Adjust based on component types
    if source.type == "Gateway" and target.type == "Network":
        confidence += 0.1
    elif source.type == "ECU" and target.type == "Sensor":
        confidence += 0.1
    elif source.type == "ECU" and target.type == "Actuator":
        confidence += 0.1
    
    # Ensure confidence is between 0 and 1
    return max(0.1, min(0.95, confidence))


def _determine_propagated_impacts(
    source: DBComponent, 
    target: DBComponent,
    confidentiality_impact: bool,
    integrity_impact: bool,
    availability_impact: bool
) -> tuple:
    """
    Determine which impacts propagate based on component types and connection
    """
    # Default propagation
    c_impact = confidentiality_impact
    i_impact = integrity_impact
    a_impact = availability_impact
    
    # Adjust based on component types
    
    # ECU to Sensor: integrity and availability propagate strongly
    if source.type == "ECU" and target.type == "Sensor":
        c_impact = c_impact and (source.confidentiality == "High")
        i_impact = i_impact
        a_impact = a_impact
    
    # ECU to Actuator: integrity and availability propagate strongly
    elif source.type == "ECU" and target.type == "Actuator":
        c_impact = c_impact and (source.confidentiality == "High")
        i_impact = i_impact
        a_impact = a_impact
    
    # Gateway to Network: all impacts propagate
    elif source.type == "Gateway" and target.type == "Network":
        c_impact = c_impact
        i_impact = i_impact
        a_impact = a_impact
    
    # Network to any: all impacts can propagate
    elif source.type == "Network":
        c_impact = c_impact
        i_impact = i_impact
        a_impact = a_impact
    
    # Sensor to ECU: integrity propagates strongly
    elif source.type == "Sensor" and target.type == "ECU":
        c_impact = c_impact and (source.confidentiality == "High")
        i_impact = i_impact
        a_impact = a_impact and (source.availability == "High")
    
    return c_impact, i_impact, a_impact


def _suggest_damage_category(source: DBComponent, target: DBComponent) -> DamageCategory:
    """
    Suggest appropriate damage category based on component types
    """
    # Safety-critical components
    if source.safety_level in ["ASIL C", "ASIL D"] or target.safety_level in ["ASIL C", "ASIL D"]:
        return DamageCategory.SAFETY
    
    # Based on component types
    if target.type == "Actuator":
        return DamageCategory.OPERATIONAL
    elif target.type == "Sensor":
        return DamageCategory.OPERATIONAL
    elif target.type == "Network":
        return DamageCategory.OPERATIONAL
    elif target.type == "Gateway":
        return DamageCategory.OPERATIONAL
    elif target.type == "ECU":
        return DamageCategory.OPERATIONAL
    
    # Default
    return DamageCategory.OPERATIONAL


def _suggest_severity(source: DBComponent, target: DBComponent) -> SeverityLevel:
    """
    Suggest severity level based on component safety levels and trust zones
    """
    # Safety-critical components get highest severity
    if source.safety_level == "ASIL D" or target.safety_level == "ASIL D":
        return SeverityLevel.CRITICAL
    elif source.safety_level == "ASIL C" or target.safety_level == "ASIL C":
        return SeverityLevel.HIGH
    elif source.safety_level == "ASIL B" or target.safety_level == "ASIL B":
        return SeverityLevel.MEDIUM
    
    # Based on trust zones
    if source.trust_zone == "Critical" or target.trust_zone == "Critical":
        return SeverityLevel.HIGH
    elif source.trust_zone == "Boundary":
        return SeverityLevel.MEDIUM
    
    # Default
    return SeverityLevel.LOW


def _parse_json_field(val: Any) -> Any:
    """
    Parse a JSON field from the database
    """
    if val is None:
        return None
    
    if isinstance(val, dict) or isinstance(val, list):
        return val
    
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return val


def _db_scenario_to_schema(db_scenario: DBDamageScenario) -> DamageScenario:
    """
    Convert DB damage scenario to Pydantic schema
    """
    # Parse JSON fields
    impact_details = _parse_json_field(db_scenario.impact_details)
    
    # Get affected component IDs
    affected_component_ids = [c.component_id for c in db_scenario.affected_components]
    
    return DamageScenario(
        scenario_id=db_scenario.scenario_id,
        name=db_scenario.name,
        description=db_scenario.description,
        damage_category=db_scenario.damage_category,
        impact_type=db_scenario.impact_type,
        confidentiality_impact=db_scenario.confidentiality_impact,
        integrity_impact=db_scenario.integrity_impact,
        availability_impact=db_scenario.availability_impact,
        severity=db_scenario.severity,
        impact_details=impact_details,
        version=db_scenario.version,
        revision_notes=db_scenario.revision_notes,
        is_deleted=db_scenario.is_deleted,
        created_at=db_scenario.created_at,
        updated_at=db_scenario.updated_at,
        scope_id=db_scenario.scope_id,
        primary_component_id=db_scenario.primary_component_id,
        affected_component_ids=affected_component_ids,
        # SFOP impact ratings and notes
        safety_impact=db_scenario.safety_impact,
        financial_impact=db_scenario.financial_impact,
        operational_impact=db_scenario.operational_impact,
        privacy_impact=db_scenario.privacy_impact,
        impact_rating_notes=db_scenario.impact_rating_notes,
        sfop_rating_auto_generated=db_scenario.sfop_rating_auto_generated,
        sfop_rating_last_edited_by=db_scenario.sfop_rating_last_edited_by,
        sfop_rating_last_edited_at=db_scenario.sfop_rating_last_edited_at,
        sfop_rating_override_reason=db_scenario.sfop_rating_override_reason,
    )
