"""
Threat catalog and analysis service for QuickTARA
"""
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db.threat_catalog import ThreatCatalog, ThreatAnalysisResult, StrideCategoryEnum
from db.base import Analysis, ComponentAnalysis
from api.models.threat import (
    ThreatCatalogItem, 
    ThreatCatalogCreate, 
    ThreatCatalogUpdate,
    ThreatMatchResult,
    ComponentThreatAnalysis,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    StrideCategory,
    ComponentType,
    TrustZone,
    AttackVector
)
from api.services.risk_service import get_active_risk_framework, calculate_risk_level
from api.services.component_service import get_component


def create_threat_catalog_item(db: Session, threat: ThreatCatalogCreate) -> ThreatCatalogItem:
    """
    Create a new threat catalog item
    """
    threat_id = f"THREAT-{uuid.uuid4()}"
    
    # Convert StrideCategory enum to string value
    stride_category = threat.stride_category.value
    
    db_threat = ThreatCatalog(
        id=threat_id,
        title=threat.title,
        description=threat.description,
        stride_category=stride_category,
        applicable_component_types=[ct.value for ct in threat.applicable_component_types],
        applicable_trust_zones=[tz.value for tz in threat.applicable_trust_zones],
        attack_vectors=[av.value for av in threat.attack_vectors],
        prerequisites=threat.prerequisites,
        typical_likelihood=threat.typical_likelihood,
        typical_severity=threat.typical_severity,
        mitigation_strategies=[ms.dict() for ms in threat.mitigation_strategies],
        cwe_ids=threat.cwe_ids,
        capec_ids=threat.capec_ids,
        examples=threat.examples,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Simplified database model now uses JSON columns for these lists
    # No need to handle relationships separately
    
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    
    # Convert back to Pydantic model
    return _convert_db_threat_to_model(db_threat)


def get_threat_catalog_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    stride_category: Optional[StrideCategory] = None,
    component_type: Optional[str] = None,
    trust_zone: Optional[str] = None
) -> List[ThreatCatalogItem]:
    """
    Get threat catalog items with optional filtering
    """
    query = db.query(ThreatCatalog)
    
    # Apply filters
    # Note: for JSON columns, SQLite filtering is limited, so we'll filter in-memory for now
    # In a production postgres database, you could use the JSON operators
    if stride_category:
        query = query.filter(ThreatCatalog.stride_category == stride_category.value)
    
    db_threats = query.offset(skip).limit(limit).all()
    return [_convert_db_threat_to_model(db_threat) for db_threat in db_threats]


def get_threat_catalog_item(db: Session, threat_id: str) -> Optional[ThreatCatalogItem]:
    """
    Get a specific threat catalog item by ID
    """
    db_threat = db.query(ThreatCatalog).filter(ThreatCatalog.id == threat_id).first()
    if not db_threat:
        return None
    
    return _convert_db_threat_to_model(db_threat)


def update_threat_catalog_item(
    db: Session, 
    threat_id: str, 
    threat_update: ThreatCatalogUpdate
) -> Optional[ThreatCatalogItem]:
    """
    Update an existing threat catalog item
    """
    db_threat = db.query(ThreatCatalog).filter(ThreatCatalog.id == threat_id).first()
    if not db_threat:
        return None
    
    # Update fields
    update_data = threat_update.dict(exclude_unset=True)
    
    # Convert stride_category enum to string value
    if "stride_category" in update_data and update_data["stride_category"] is not None:
        update_data["stride_category"] = update_data["stride_category"].value
    
    # Handle list fields
    if "applicable_component_types" in update_data and update_data["applicable_component_types"] is not None:
        update_data["applicable_component_types"] = [ct.value for ct in update_data["applicable_component_types"]]
        
    if "applicable_trust_zones" in update_data and update_data["applicable_trust_zones"] is not None:
        update_data["applicable_trust_zones"] = [tz.value for tz in update_data["applicable_trust_zones"]]
        
    if "attack_vectors" in update_data and update_data["attack_vectors"] is not None:
        update_data["attack_vectors"] = [av.value for av in update_data["attack_vectors"]]
    
    # Special handling for mitigation_strategies
    if "mitigation_strategies" in update_data and update_data["mitigation_strategies"] is not None:
        # Make sure we have a list of dictionaries for storage
        try:
            # If these are Pydantic models with dict method
            if hasattr(update_data["mitigation_strategies"][0], 'dict'):
                update_data["mitigation_strategies"] = [ms.dict() for ms in update_data["mitigation_strategies"]]
            # Otherwise, they might already be dictionaries
            elif isinstance(update_data["mitigation_strategies"][0], dict):
                # Keep as is
                pass
            else:
                # Convert to string representation as fallback
                update_data["mitigation_strategies"] = [str(ms) for ms in update_data["mitigation_strategies"]]
        except (IndexError, AttributeError):
            # Handle empty list or other errors
            pass
    
    # Update fields
    for key, value in update_data.items():
        # Skip component_types, trust_zones, attack_vectors (handle separately)
        if key not in ["applicable_component_types", "applicable_trust_zones", "attack_vectors"]:
            setattr(db_threat, key, value)
    
    # Handle component types, trust zones, and attack vectors
    # Would be implemented here if we used actual relationship tables
    
    db_threat.updated_at = datetime.now()
    db.commit()
    db.refresh(db_threat)
    
    return _convert_db_threat_to_model(db_threat)


def delete_threat_catalog_item(db: Session, threat_id: str) -> bool:
    """
    Delete a threat catalog item
    """
    db_threat = db.query(ThreatCatalog).filter(ThreatCatalog.id == threat_id).first()
    if not db_threat:
        return False
    
    db.delete(db_threat)
    db.commit()
    return True


def perform_threat_analysis(
    db: Session, 
    analysis_request: ThreatAnalysisRequest
) -> ThreatAnalysisResponse:
    """
    Perform threat analysis for the specified components
    """
    # Create a new analysis record
    analysis_id = f"ANALYSIS-{uuid.uuid4()}"
    
    # Get components
    components = []
    for component_id in analysis_request.component_ids:
        component = get_component(db, component_id)
        if component:
            components.append(component)
    
    # Get active risk framework or the specified one
    risk_framework_id = analysis_request.risk_framework_id
    # If risk_framework_id is specified, get that framework specifically
    if risk_framework_id:
        risk_framework = get_risk_framework(db, risk_framework_id)
    else:
        # Otherwise get the active one
        risk_framework = get_active_risk_framework(db)
    
    # Get all threat catalog items
    all_threats = get_threat_catalog_items(db, limit=1000)
    
    # Custom threats from the request
    custom_threats = analysis_request.custom_threats or []
    all_threats.extend(custom_threats)
    
    # Create analysis record
    db_analysis = Analysis(
        id=analysis_id,
        name=f"STRIDE Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description="Automated STRIDE threat analysis",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        total_components=len(components),
        total_threats=0,
        critical_components=0,
        high_risk_threats=0
    )
    db.add(db_analysis)
    
    # Perform threat matching for each component
    component_analyses = []
    total_high_risk = 0
    total_threats = 0
    stride_summary = {
        "spoofing": 0,
        "tampering": 0,
        "repudiation": 0,
        "info_disclosure": 0,
        "denial_of_service": 0,
        "elevation_of_privilege": 0
    }
    
    for component in components:
        component_analysis = _analyze_component_threats(
            db, component, all_threats, risk_framework, analysis_id
        )
        component_analyses.append(component_analysis)
        
        # Update totals
        total_threats += component_analysis.total_threats_identified
        total_high_risk += component_analysis.high_risk_threats
        
        # Update STRIDE summary
        for match in component_analysis.threat_matches:
            stride_category = match.stride_category.value
            stride_summary[stride_category] = stride_summary.get(stride_category, 0) + 1
    
    # Update analysis record
    db_analysis.total_threats = total_threats
    db_analysis.high_risk_threats = total_high_risk
    db_analysis.critical_components = sum(1 for ca in component_analyses if ca.high_risk_threats > 0)
    db.commit()
    
    return ThreatAnalysisResponse(
        analysis_id=analysis_id,
        component_analyses=component_analyses,
        total_components=len(components),
        total_threats=total_threats,
        high_risk_threats=total_high_risk,
        stride_summary=stride_summary,
        timestamp=datetime.now()
    )


def _analyze_component_threats(
    db: Session, 
    component: Any, 
    threats: List[ThreatCatalogItem],
    risk_framework: Any,
    analysis_id: str
) -> ComponentThreatAnalysis:
    """
    Analyze a component against all threats in the catalog
    """
    # Match threats to the component
    matches = []
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    stride_summary = {
        "spoofing": 0,
        "tampering": 0,
        "repudiation": 0,
        "info_disclosure": 0,
        "denial_of_service": 0,
        "elevation_of_privilege": 0
    }
    
    for threat in threats:
        # Calculate match confidence based on component type, trust zone, etc.
        match_confidence = _calculate_match_confidence(component, threat)
        
        # Skip if confidence is too low or if component type is not applicable
        if match_confidence < 0.3:
            continue
        
        # Additional filtering for component types (needed since we removed DB-level filtering)
        if component_type_mismatch(component, threat):
            continue
        
        # Calculate likelihood and severity based on component properties
        likelihood = _calculate_likelihood(component, threat, match_confidence)
        severity = _calculate_severity(component, threat)
        
        # Calculate risk score
        risk_score = likelihood * severity
        
        # Determine applicable mitigation strategies
        applicable_mitigations = threat.mitigation_strategies
        
        # Create match result
        match_result = ThreatMatchResult(
            threat_id=threat.id,
            component_id=component.component_id,
            title=threat.title,
            stride_category=threat.stride_category,
            match_confidence=match_confidence,
            calculated_likelihood=likelihood,
            calculated_severity=severity,
            calculated_risk_score=risk_score,
            applicable_mitigation_strategies=applicable_mitigations,
            notes=f"Automatically matched with {match_confidence:.2f} confidence"
        )
        matches.append(match_result)
        
        # Update risk level counts
        risk_level = calculate_risk_level(risk_framework, likelihood, severity)
        if risk_level.lower() == "high":
            high_risk += 1
        elif risk_level.lower() == "medium":
            medium_risk += 1
        else:
            low_risk += 1
        
        # Update STRIDE summary
        stride_category = threat.stride_category.value
        stride_summary[stride_category] = stride_summary.get(stride_category, 0) + 1
        
        # Store the analysis result in the database
        db_analysis_result = ThreatAnalysisResult(
            id=f"RESULT-{uuid.uuid4()}",
            analysis_id=analysis_id,
            component_id=component.component_id,
            threat_id=threat.id,
            match_confidence=int(match_confidence * 100),
            calculated_likelihood=likelihood,
            calculated_severity=severity,
            calculated_risk_score=risk_score,
            applicable_mitigations=[m.dict() for m in applicable_mitigations],
            notes=match_result.notes,
            created_at=datetime.now()
        )
        db.add(db_analysis_result)
    
    # Create component analysis record
    db_component_analysis = ComponentAnalysis(
        id=f"COMP-ANALYSIS-{uuid.uuid4()}",
        analysis_id=analysis_id,
        component_id=component.component_id,
        threats=[{
            "threat_id": match.threat_id,
            "title": match.title,
            "likelihood": match.calculated_likelihood,
            "severity": match.calculated_severity,
            "risk_score": match.calculated_risk_score,
            "stride_category": match.stride_category.value
        } for match in matches],
        stride_analysis=stride_summary
    )
    db.add(db_component_analysis)
    db.commit()
    
    return ComponentThreatAnalysis(
        component_id=component.component_id,
        component_name=component.name,
        component_type=component.type,
        total_threats_identified=len(matches),
        high_risk_threats=high_risk,
        medium_risk_threats=medium_risk,
        low_risk_threats=low_risk,
        threat_matches=matches,
        stride_summary=stride_summary
    )


def component_type_mismatch(component: Any, threat: ThreatCatalogItem) -> bool:
    """
    Check if a component type doesn't match any of the applicable component types for a threat
    
    Args:
        component: Component to check
        threat: Threat catalog item to check against
        
    Returns:
        True if there's a mismatch (component type not applicable), False otherwise
    """
    # If no applicable component types are specified, assume all are applicable
    if not threat.applicable_component_types:
        return False
        
    # Check if component type matches any applicable type
    component_type = component.type.lower()
    applicable_types = [ct.value.lower() for ct in threat.applicable_component_types]
    
    # If 'other' is in applicable types, all components are potential targets
    if 'other' in applicable_types:
        return False
        
    # Check for direct match or partial match (component type might be more specific)
    for app_type in applicable_types:
        if app_type in component_type or component_type in app_type:
            return False
            
    # No match found, component type is not applicable
    return True


def _calculate_match_confidence(component: Any, threat: ThreatCatalogItem) -> float:
    """
    Calculate the confidence level of a threat match to a component
    """
    # This is a simplified version - in a real implementation, this would use
    # more sophisticated matching logic based on component properties
    
    # Basic matching based on component type
    type_match = 0.0
    if component.type.lower() in [ct.value.lower() for ct in threat.applicable_component_types]:
        type_match = 0.6
    
    # Trust zone matching
    trust_match = 0.0
    if component.trust_zone.lower() in [tz.value.lower() for tz in threat.applicable_trust_zones]:
        trust_match = 0.4
    
    # Combine confidence factors (simplified)
    confidence = type_match + trust_match
    
    # Cap at 1.0
    return min(confidence, 1.0)


def _calculate_likelihood(component: Any, threat: ThreatCatalogItem, match_confidence: float) -> int:
    """
    Calculate the likelihood of a threat for a specific component
    """
    # Start with the typical likelihood from the threat
    base_likelihood = threat.typical_likelihood
    
    # Adjust based on component properties
    # This is simplified - a real implementation would include more factors
    
    # Reduce likelihood if match confidence is low
    confidence_adjustment = 0
    if match_confidence < 0.5:
        confidence_adjustment = -1
    
    # Adjust based on trust zone
    trust_adjustment = 0
    if component.trust_zone.lower() == "untrusted":
        trust_adjustment = 1
    elif component.trust_zone.lower() == "secure":
        trust_adjustment = -1
    
    # Calculate final likelihood (capped between 1 and 5)
    final_likelihood = base_likelihood + confidence_adjustment + trust_adjustment
    return max(1, min(5, final_likelihood))


def _calculate_severity(component: Any, threat: ThreatCatalogItem) -> int:
    """
    Calculate the severity of a threat for a specific component
    """
    # Start with the typical severity from the threat
    base_severity = threat.typical_severity
    
    # Adjust based on component properties
    # This is simplified - a real implementation would include more factors
    
    # Adjust based on safety level
    safety_adjustment = 0
    if component.safety_level.lower() in ["asil d", "asil c"]:
        safety_adjustment = 1
    
    # Calculate final severity (capped between 1 and 5)
    final_severity = base_severity + safety_adjustment
    return max(1, min(5, final_severity))


def _convert_db_threat_to_model(db_threat: ThreatCatalog) -> ThreatCatalogItem:
    """
    Convert a database threat model to a Pydantic model
    """
    # Convert string to Pydantic enum
    stride_category = StrideCategory(db_threat.stride_category)
    
    # Convert component types, trust zones, and attack vectors from strings to enums
    component_types = []
    for ct_str in db_threat.applicable_component_types or []:
        try:
            component_types.append(ComponentType(ct_str))
        except (ValueError, TypeError):
            pass
    
    trust_zones = []
    for tz_str in db_threat.applicable_trust_zones or []:
        try:
            trust_zones.append(TrustZone(tz_str))
        except (ValueError, TypeError):
            pass
    
    attack_vectors = []
    for av_str in db_threat.attack_vectors or []:
        try:
            attack_vectors.append(AttackVector(av_str))
        except (ValueError, TypeError):
            pass
    
    return ThreatCatalogItem(
        id=db_threat.id,
        title=db_threat.title,
        description=db_threat.description,
        stride_category=stride_category,
        applicable_component_types=component_types,
        applicable_trust_zones=trust_zones,
        attack_vectors=attack_vectors,
        prerequisites=db_threat.prerequisites,
        typical_likelihood=db_threat.typical_likelihood,
        typical_severity=db_threat.typical_severity,
        mitigation_strategies=db_threat.mitigation_strategies,
        cwe_ids=db_threat.cwe_ids,
        capec_ids=db_threat.capec_ids,
        examples=db_threat.examples,
        created_at=db_threat.created_at,
        updated_at=db_threat.updated_at
    )
