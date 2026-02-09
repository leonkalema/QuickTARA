"""
Damage Scenario service layer
"""
from typing import List, Optional, Dict, Any, Set
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime

# Import legacy models (needed for transition period)
from db.damage_scenario import DamageScenario as DBDamageScenario
from db.base import Component as DBComponent, SystemScope as DBSystemScope

# Import product-centric models
from db.product_asset_models import DamageScenario as ProductDamageScenario
from db.product_asset_models import Asset, ProductScope
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
    Create a new damage scenario in the database using the product-centric model
    """
    import logging
    logger = logging.getLogger("quicktara")
    logger.setLevel(logging.DEBUG)
    
    try:
        # Generate a unique ID if not provided
        scenario_id = scenario.scenario_id or f"DS-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Creating damage scenario with ID: {scenario_id}")
        
        # Check if scenario with same ID already exists
        existing = db.query(ProductDamageScenario).filter(ProductDamageScenario.scenario_id == scenario_id).first()
        if existing:
            raise ValueError(f"Damage scenario with ID {scenario_id} already exists")
        
        # Verify that product scope exists
        logger.info(f"Checking for product scope: {scenario.scope_id}")
        scope = db.query(ProductScope).filter(ProductScope.scope_id == scenario.scope_id).first()
        if not scope:
            raise ValueError(f"Product scope with ID {scenario.scope_id} does not exist")
        
        # Verify that primary asset exists if provided (frontend sends asset_id as primary_component_id)
        primary_asset = None
        if scenario.primary_component_id:
            logger.info(f"Checking for primary asset: {scenario.primary_component_id}")
            primary_asset = db.query(Asset).filter(
                Asset.asset_id == scenario.primary_component_id
            ).first()
            if not primary_asset:
                raise ValueError(f"Asset with ID {scenario.primary_component_id} does not exist")
        else:
            logger.info("No primary asset specified - creating scenario without asset link")
        
        # Use SFOP impact ratings from the form if available
        logger.info(f"Processing SFOP impact ratings: {scenario.impact_rating}")
        
        # Extract SFOP ratings from impact_rating field
        safety_impact = "negligible"
        financial_impact = "negligible"
        operational_impact = "negligible"
        privacy_impact = "negligible"
        
        if scenario.impact_rating:
            safety_impact = scenario.impact_rating.safety
            financial_impact = scenario.impact_rating.financial
            operational_impact = scenario.impact_rating.operational
            privacy_impact = scenario.impact_rating.privacy
        else:
            # Fallback to negligible if no SFOP ratings provided
            logger.info(f"No SFOP ratings provided, using negligible defaults")
            safety_impact = "negligible"
            financial_impact = "negligible"
            operational_impact = "negligible"
            privacy_impact = "negligible"
        
        # Create violated_properties JSON including SFOP ratings
        violated_properties_dict = {
            "confidentiality": scenario.confidentiality_impact,
            "integrity": scenario.integrity_impact,
            "availability": scenario.availability_impact,
            "severity": scenario.severity
        }
        
        # Add SFOP impact ratings to violated_properties
        if scenario.impact_rating:
            violated_properties_dict["sfop_ratings"] = {
                "safety": scenario.impact_rating.safety,
                "financial": scenario.impact_rating.financial,
                "operational": scenario.impact_rating.operational,
                "privacy": scenario.impact_rating.privacy
            }
        
        # Add impact details if available
        if scenario.impact_details:
            violated_properties_dict["details"] = scenario.impact_details
            
        violated_properties = json.dumps(violated_properties_dict)
        logger.info(f"Violated properties: {violated_properties}")
        
        # Create the damage scenario using product-centric model
        try:
            db_scenario = ProductDamageScenario(
                scenario_id=scenario_id,
                name=scenario.name,
                description=scenario.description,
                # Both new and legacy categorization fields
                category=scenario.damage_category,
                damage_category=scenario.damage_category,
                impact_type=scenario.impact_type,
                severity=scenario.severity,
                # CIA impact booleans for legacy columns
                confidentiality_impact=scenario.confidentiality_impact,
                integrity_impact=scenario.integrity_impact,
                availability_impact=scenario.availability_impact,
                # Primary asset reference for legacy column
                primary_component_id=scenario.primary_component_id,
                # New JSON field
                violated_properties=violated_properties,
                scope_id=scenario.scope_id,
                safety_impact=safety_impact,
                financial_impact=financial_impact,
                operational_impact=operational_impact,
                privacy_impact=privacy_impact,
                version=scenario.version,
                is_current=True,
                revision_notes=scenario.revision_notes,
                created_at=datetime.now(),
                updated_at=datetime.now()
                # Not using created_by and updated_by as they don't exist in DB schema
            )
            logger.info(f"Created damage scenario object: {db_scenario.scenario_id}")
        except Exception as e:
            logger.error(f"Error creating damage scenario object: {str(e)}")
            raise
        
        # Combine all database operations into a single transaction
        try:
            # Process affected assets
            affected_assets = []
            logger.info(f"Processing affected assets: {scenario.affected_component_ids}")
            
            for asset_id in scenario.affected_component_ids:  # frontend still uses affected_component_ids for asset_ids
                asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
                if asset:
                    affected_assets.append(asset)
                    logger.info(f"Added asset to affected list: {asset_id}")
                else:
                    logger.warning(f"Asset not found: {asset_id}")
            
            # Add damage scenario to database
            db.add(db_scenario)
            db.flush()  # This assigns the ID but doesn't commit the transaction yet
            logger.info(f"Added damage scenario to database: {db_scenario.scenario_id}")
            
            # Set affected assets relationship
            if affected_assets:
                db_scenario.affected_assets = affected_assets
                logger.info(f"Set {len(affected_assets)} affected assets for damage scenario")
            
            # Now commit the entire transaction
            db.commit()
            db.refresh(db_scenario)
            logger.info(f"Successfully committed damage scenario with all relationships")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in database transaction: {str(e)}")
            raise
        
        # Return the created damage scenario
        return _db_scenario_to_schema(db_scenario)
        
    except Exception as e:
        logger.error(f"Error in create_damage_scenario: {str(e)}")
        # Re-raise the exception to be handled by the API endpoint
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


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
    Update an existing damage scenario - handles both legacy and product-centric models
    """
    # Try to find the scenario in the product-centric model first
    db_scenario = db.query(ProductDamageScenario).filter(
        ProductDamageScenario.scenario_id == scenario_id
    ).first()
    
    # If not found in product model, try legacy model
    if not db_scenario:
        db_scenario = db.query(DBDamageScenario).filter(
            DBDamageScenario.scenario_id == scenario_id,
            DBDamageScenario.is_deleted == False
        ).first()
    
    if not db_scenario:
        return None
        
    # Determine if this is a product-centric damage scenario
    is_product_scenario = isinstance(db_scenario, ProductDamageScenario)
    
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
        # Handle scope validation based on scenario type
        if is_product_scenario:
            # Verify that product scope exists
            scope = db.query(ProductScope).filter(ProductScope.scope_id == scenario.scope_id).first()
            if not scope:
                raise ValueError(f"Product scope with ID {scenario.scope_id} does not exist")
        else:
            # Legacy scenario - verify system scope
            scope = db.query(DBSystemScope).filter(DBSystemScope.scope_id == scenario.scope_id).first()
            if not scope:
                raise ValueError(f"System scope with ID {scenario.scope_id} does not exist")
        
        db_scenario.scope_id = scenario.scope_id
    
    if scenario.primary_component_id is not None:
        if is_product_scenario:
            # Verify that asset exists for product-centric model
            primary_asset = db.query(Asset).filter(
                Asset.asset_id == scenario.primary_component_id
            ).first()
            if not primary_asset:
                raise ValueError(f"Asset with ID {scenario.primary_component_id} does not exist")
            # Note: Product model doesn't have primary_component_id field, this will be handled via affected_assets
        else:
            # Legacy model - verify component exists
            primary_component = db.query(DBComponent).filter(
                DBComponent.component_id == scenario.primary_component_id
            ).first()
            if not primary_component:
                raise ValueError(f"Component with ID {scenario.primary_component_id} does not exist")
            db_scenario.primary_component_id = scenario.primary_component_id
    
    # Update affected components/assets if provided
    if scenario.affected_component_ids is not None:
        if is_product_scenario:
            # Handle product-centric model assets
            affected_assets = []
            for asset_id in scenario.affected_component_ids:
                asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
                if asset:
                    affected_assets.append(asset)
            
            # Make sure the primary asset is included
            if scenario.primary_component_id and scenario.primary_component_id not in [a.asset_id for a in affected_assets]:
                primary_asset = db.query(Asset).filter(Asset.asset_id == scenario.primary_component_id).first()
                if primary_asset:
                    affected_assets.append(primary_asset)
            
            db_scenario.affected_assets = affected_assets
        else:
            # Handle legacy model components
            affected_components = []
            for component_id in scenario.affected_component_ids:
                component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
                if component:
                    affected_components.append(component)
            
            db_scenario.affected_components = affected_components
    
    # Update CIA impacts and SFOP ratings based on model type
    if is_product_scenario:
        # For product model, update violated_properties JSON
        if any([scenario.confidentiality_impact is not None, 
                scenario.integrity_impact is not None, 
                scenario.availability_impact is not None, 
                scenario.severity is not None]):
            
            # Get current violated properties
            violated_props = _parse_json_field(db_scenario.violated_properties) or {}
            
            # Update fields if provided
            if scenario.confidentiality_impact is not None:
                violated_props['confidentiality'] = scenario.confidentiality_impact
            
            if scenario.integrity_impact is not None:
                violated_props['integrity'] = scenario.integrity_impact
            
            if scenario.availability_impact is not None:
                violated_props['availability'] = scenario.availability_impact
            
            if scenario.severity is not None:
                violated_props['severity'] = scenario.severity
            
            if scenario.impact_details is not None:
                violated_props['details'] = scenario.impact_details
            
            # Update violated_properties JSON
            db_scenario.violated_properties = json.dumps(violated_props)
        
        # For product model, SFOP are boolean flags
        if scenario.damage_category is not None:
            db_scenario.category = scenario.damage_category
            
        if scenario.safety_impact is not None:
            # Convert SeverityLevel to boolean (any non-LOW value is True)
            db_scenario.safety_impact = (scenario.safety_impact != SeverityLevel.LOW)
        
        if scenario.financial_impact is not None:
            db_scenario.financial_impact = (scenario.financial_impact != SeverityLevel.LOW)
        
        if scenario.operational_impact is not None:
            db_scenario.operational_impact = (scenario.operational_impact != SeverityLevel.LOW)
        
        if scenario.privacy_impact is not None:
            db_scenario.privacy_impact = (scenario.privacy_impact != SeverityLevel.LOW)
    else:
        # Legacy model - direct field updates
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
            
        # Update CIA impacts for legacy model
        if scenario.confidentiality_impact is not None:
            db_scenario.confidentiality_impact = scenario.confidentiality_impact
        
        if scenario.integrity_impact is not None:
            db_scenario.integrity_impact = scenario.integrity_impact
        
        if scenario.availability_impact is not None:
            db_scenario.availability_impact = scenario.availability_impact
    
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


def _to_severity(value) -> SeverityLevel:
    """Convert various DB representations (enum, int, bool, str) to SeverityLevel enum."""
    if isinstance(value, SeverityLevel):
        return value
    # Booleans or ints treated as binary HIGH/LOW
    if isinstance(value, (bool, int)):
        return SeverityLevel.HIGH if bool(value) else SeverityLevel.LOW
    if isinstance(value, str):
        upper = value.upper()
        if upper in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            return SeverityLevel[upper]
        if upper in {"1", "TRUE", "YES"}:
            return SeverityLevel.HIGH
        if upper in {"0", "FALSE", "NO"}:
            return SeverityLevel.LOW
    # Fallback
    return SeverityLevel.LOW


def _db_scenario_to_schema(db_scenario) -> DamageScenario:
    """
    Convert DB damage scenario to Pydantic schema
    Works with both legacy DBDamageScenario and new ProductDamageScenario
    """
    # Check if this is a product-centric damage scenario
    is_product_scenario = isinstance(db_scenario, ProductDamageScenario)

    if is_product_scenario:
        # Handle ProductDamageScenario
        violated_props = _parse_json_field(db_scenario.violated_properties) or {}
        
        # Extract CIA impacts and severity from violated_properties
        # Use database fields as fallback if violated_properties doesn't have CIA data
        confidentiality_impact = violated_props.get('confidentiality', db_scenario.confidentiality_impact if hasattr(db_scenario, 'confidentiality_impact') else False)
        integrity_impact = violated_props.get('integrity', db_scenario.integrity_impact if hasattr(db_scenario, 'integrity_impact') else False)
        availability_impact = violated_props.get('availability', db_scenario.availability_impact if hasattr(db_scenario, 'availability_impact') else False)
        severity = db_scenario.severity or 'Medium'
        impact_details = violated_props.get('details', {})
        
        # Use primary_component_id from database, then fallback to first affected asset
        primary_asset_id = db_scenario.primary_component_id
        affected_asset_ids = [a.asset_id for a in db_scenario.affected_assets] if hasattr(db_scenario, 'affected_assets') else []
        
        # Determine impact type from category
        impact_type = ImpactType.DIRECT  # Default
        
        # Extract SFOP ratings from violated_properties if available
        sfop_ratings = violated_props.get('sfop_ratings', {})
        
        # Create ImpactRating object from SFOP data
        from api.models.damage_scenario import ImpactRating, ImpactRatingLevel
        impact_rating = None
        if sfop_ratings:
            impact_rating = ImpactRating(
                safety=ImpactRatingLevel(sfop_ratings.get('safety', 'negligible')),
                financial=ImpactRatingLevel(sfop_ratings.get('financial', 'negligible')),
                operational=ImpactRatingLevel(sfop_ratings.get('operational', 'negligible')),
                privacy=ImpactRatingLevel(sfop_ratings.get('privacy', 'negligible'))
            )

        return DamageScenario(
            scenario_id=db_scenario.scenario_id,
            name=db_scenario.name,
            description=db_scenario.description,
            damage_category=db_scenario.category or DamageCategory.OPERATIONAL,
            impact_type=impact_type,
            confidentiality_impact=confidentiality_impact,
            integrity_impact=integrity_impact,
            availability_impact=availability_impact,
            severity=severity,
            impact_details=impact_details,
            impact_rating=impact_rating,
            version=db_scenario.version,
            revision_notes=db_scenario.revision_notes,
            is_deleted=False,  # Product model doesn't use is_deleted
            created_at=db_scenario.created_at,
            updated_at=db_scenario.updated_at,
            scope_id=db_scenario.scope_id,
            primary_component_id=primary_asset_id or "",
            affected_component_ids=affected_asset_ids,
            impact_rating_notes=None,  # Not in product model
            sfop_rating_auto_generated=True,
            sfop_rating_last_edited_by=None,
            sfop_rating_last_edited_at=None,
            sfop_rating_override_reason=None,
            status=getattr(db_scenario, 'status', 'accepted'),
        )
    else:
        # Handle legacy DBDamageScenario
        impact_details = _parse_json_field(db_scenario.impact_details)
        affected_component_ids = [c.component_id for c in db_scenario.affected_components]
        
        # Create ImpactRating object from legacy SFOP data
        from api.models.damage_scenario import ImpactRating, ImpactRatingLevel
        
        # Convert legacy SFOP values to proper format
        def convert_legacy_impact(value):
            if value is None:
                return "negligible"
            if isinstance(value, str):
                return value.lower()
            # Handle boolean or other types
            return "negligible"
        
        impact_rating = ImpactRating(
            safety=ImpactRatingLevel(convert_legacy_impact(db_scenario.safety_impact)),
            financial=ImpactRatingLevel(convert_legacy_impact(db_scenario.financial_impact)),
            operational=ImpactRatingLevel(convert_legacy_impact(db_scenario.operational_impact)),
            privacy=ImpactRatingLevel(convert_legacy_impact(db_scenario.privacy_impact))
        )

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
            impact_rating=impact_rating,
            version=db_scenario.version,
            revision_notes=db_scenario.revision_notes,
            is_deleted=db_scenario.is_deleted,
            created_at=db_scenario.created_at,
            updated_at=db_scenario.updated_at,
            scope_id=db_scenario.scope_id,
            primary_component_id=db_scenario.primary_component_id,
            affected_component_ids=affected_component_ids,
            impact_rating_notes=db_scenario.impact_rating_notes,
            sfop_rating_auto_generated=db_scenario.sfop_rating_auto_generated,
            sfop_rating_last_edited_by=db_scenario.sfop_rating_last_edited_by,
            sfop_rating_last_edited_at=db_scenario.sfop_rating_last_edited_at,
            sfop_rating_override_reason=db_scenario.sfop_rating_override_reason,
            status=getattr(db_scenario, 'status', 'accepted'),
        )
