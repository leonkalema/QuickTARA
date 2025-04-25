"""
Analysis service layer
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime
import logging

from db.base import Component as DBComponent, Analysis as DBAnalysis, ComponentAnalysis as DBComponentAnalysis

from api.models.component import Component
from api.models.analysis import (
    Analysis, AnalysisCreate, AnalysisSummary, ComponentAnalysis,
    Threat, StrideRecommendation, ComplianceRequirement, AttackerFeasibility,
    RiskAcceptance, AttackPath
)
from api.services.component_service import get_component, get_components, _db_component_to_schema

# Import core analysis functionality
from core.quicktara import (
    load_components, analyze_threats, analyze_attack_paths
)
from core.stride_analysis import analyze_stride_categories, get_stride_recommendations, StrideCategory
from core.threat_analysis import load_threats_from_capec, AUTOMOTIVE_THREATS, analyze_impact_categories
from core.attacker_feasibility import assess_all_component_threats
from core.risk_acceptance import assess_component_risk_acceptance
from core.cybersecurity_goals import map_all_component_threats_to_goals
from core.compliance_mappings import map_threat_to_standards

logger = logging.getLogger(__name__)

def calculate_component_risk_factors(component: Any) -> Dict[str, float]:
    """Calculate risk factors based on component attributes - safe version"""
    risk_factors = {
        'exposure': 0.5,
        'complexity': 0.5,
        'attack_surface': 0.5
    }
    
    try:
        # Exposure based on location and trust zone
        exposure_scores = {
            'External': 1.0,
            'Internal': 0.6
        }
        
        # Get trust zone value safely
        trust_zone_value = None
        if hasattr(component, 'trust_zone'):
            if hasattr(component.trust_zone, 'value'):
                trust_zone_value = component.trust_zone.value
            else:
                trust_zone_value = component.trust_zone
        
        # Map string trust zones to scores
        trust_scores = {
            'Untrusted': 1.0,
            'Boundary': 0.8,
            'Standard': 0.6,
            'Critical': 0.4
        }
        
        # Get location safely
        location = None
        if hasattr(component, 'location'):
            location = component.location
        
        # Calculate exposure
        exposure_score = exposure_scores.get(location, 0.5) if location else 0.5
        trust_score = trust_scores.get(trust_zone_value, 0.5) if trust_zone_value else 0.5
        risk_factors['exposure'] = (exposure_score + trust_score) / 2

        # Complexity based on interfaces and connections
        interfaces = []
        if hasattr(component, 'interfaces'):
            interfaces = component.interfaces
            
        connected_to = []
        if hasattr(component, 'connected_to'):
            connected_to = component.connected_to
            
        interfaces_len = len(interfaces) if interfaces else 0
        connected_len = len(connected_to) if connected_to else 0
        risk_factors['complexity'] = min(1.0, (interfaces_len * 0.2 + connected_len * 0.1))

        # Attack surface based on access points and data types
        access_points = []
        if hasattr(component, 'access_points'):
            access_points = component.access_points
            
        data_types = []
        if hasattr(component, 'data_types'):
            data_types = component.data_types
            
        access_points_len = len(access_points) if access_points else 0
        data_types_len = len(data_types) if data_types else 0
        risk_factors['attack_surface'] = min(1.0, (access_points_len * 0.3 + data_types_len * 0.2))
    
    except Exception as e:
        logger.error(f"Error calculating risk factors: {str(e)}")
        # Return default values if calculation fails
    
    return risk_factors

def run_analysis(db: Session, analysis_create: AnalysisCreate) -> Analysis:
    """Run analysis on selected components"""
    # Generate unique ID for the analysis
    analysis_id = str(uuid.uuid4())
    
    # Create analysis database record
    db_analysis = DBAnalysis(
        id=analysis_id,
        name=analysis_create.name or f"Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=analysis_create.description
    )
    
    # Initialize counters for the analysis summary
    component_count = 0
    threat_count = 0
    critical_count = 0
    high_risk_count = 0
    
    # Dictionary to store component analyses
    component_analyses = {}
    
    # Get all components (fetch once)
    all_components = get_components(db)
    
    # Create a lookup dictionary for faster access
    component_lookup = {}
    for comp in all_components:
        component_lookup[comp.component_id] = comp
        # Also add lowercase version for case-insensitive matching
        component_lookup[comp.component_id.lower()] = comp
    
    logger.info(f"Processing {len(analysis_create.component_ids)} components")
    
    # Process each requested component
    for component_id in analysis_create.component_ids:
        # Check if component exists in our lookup
        db_component = None
        
        # Try direct lookup
        if component_id in component_lookup:
            db_component = component_lookup[component_id]
            logger.info(f"Found component {component_id}")
        # Try case-insensitive lookup
        elif component_id.lower() in component_lookup:
            db_component = component_lookup[component_id.lower()]
            logger.info(f"Found component {component_id} (case-insensitive match)")
        else:
            logger.warning(f"Component {component_id} not found in database")
            continue
            
        try:
            # Increment component counter
            component_count += 1
            
            # Check if it's a critical component
            if db_component.trust_zone == "Critical":
                critical_count += 1
            
            # Create predefined threats based on component type
            component_threats = []
            
            # Create type-specific threats
            if "Sensor" in db_component.type:
                # Add sensor-specific threats
                sensor_threat = Threat(
                    name="Sensor Data Tampering",
                    description="Manipulation of sensor data to cause incorrect system behavior",
                    likelihood=3,
                    impact={
                        'financial': 3, 
                        'safety': 4, 
                        'privacy': 2
                    },
                    risk_factors={
                        'exposure': 0.7, 
                        'complexity': 0.5, 
                        'attack_surface': 0.6
                    }
                )
                component_threats.append(sensor_threat)
                threat_count += 1
                
                # High risk threat - increment counter
                if sensor_threat.impact['safety'] >= 4:
                    high_risk_count += 1
            
            elif "ECU" in db_component.type:
                # Add ECU-specific threats
                ecu_threat = Threat(
                    name="ECU Firmware Tampering",
                    description="Malicious modification of ECU firmware",
                    likelihood=3,
                    impact={
                        'financial': 4, 
                        'safety': 5, 
                        'privacy': 3
                    },
                    risk_factors={
                        'exposure': 0.5, 
                        'complexity': 0.7, 
                        'attack_surface': 0.4
                    }
                )
                component_threats.append(ecu_threat)
                threat_count += 1
                
                # High risk threat - increment counter
                if ecu_threat.impact['safety'] >= 4:
                    high_risk_count += 1
            
            elif "Gateway" in db_component.type:
                # Add Gateway-specific threats
                gateway_threat = Threat(
                    name="Gateway Compromise",
                    description="Unauthorized access to the gateway allowing pivoting between networks",
                    likelihood=3,
                    impact={
                        'financial': 4, 
                        'safety': 3, 
                        'privacy': 5
                    },
                    risk_factors={
                        'exposure': 0.7, 
                        'complexity': 0.8, 
                        'attack_surface': 0.7
                    }
                )
                component_threats.append(gateway_threat)
                threat_count += 1
                
                # High risk threat check
                if gateway_threat.impact['privacy'] >= 4:
                    high_risk_count += 1
            
            # Create STRIDE analysis for the component
            stride_analysis = {}
            for category in StrideCategory:
                stride_analysis[category.value] = StrideRecommendation(
                    category=category.value,
                    risk_level="Medium",
                    recommendations=[f"Implement proper {category.value} controls"]
                )
            
            # Create a ComponentAnalysis object for this component
            component_analyses[db_component.component_id] = ComponentAnalysis(
                component_id=db_component.component_id,
                name=db_component.name,
                type=db_component.type,
                safety_level=db_component.safety_level,
                threats=component_threats,
                stride_analysis=stride_analysis,
                compliance=[],
                feasibility_assessments={},
                risk_acceptance={},
                attack_paths=[]
            )
            
        except Exception as e:
            logger.error(f"Error analyzing component {component_id}: {str(e)}")
            # Continue with next component
    
    # Set the analysis summary
    summary = AnalysisSummary(
        total_components=component_count,
        total_threats=threat_count,
        critical_components=critical_count,
        high_risk_threats=high_risk_count
    )
    
    # Set counts in the database
    db_analysis.total_components = component_count
    db_analysis.total_threats = threat_count
    db_analysis.critical_components = critical_count
    db_analysis.high_risk_threats = high_risk_count
    
    # Create Analysis object
    analysis = Analysis(
        id=analysis_id,
        name=db_analysis.name,
        description=db_analysis.description,
        created_at=db_analysis.created_at,
        updated_at=db_analysis.updated_at,
        component_analyses=component_analyses,
        summary=summary
    )
    
    # Add to database and commit
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Store component analysis records with threats
    for comp_id, comp_analysis in component_analyses.items():
        # Generate unique ID for component analysis
        component_analysis_id = str(uuid.uuid4())
        
        # Create a database record with threats
        db_component_analysis = DBComponentAnalysis(
            id=component_analysis_id,
            analysis_id=analysis_id,
            component_id=comp_id,
            threats=json.dumps([threat.dict() for threat in comp_analysis.threats]),
            stride_analysis=json.dumps({k: v.dict() for k, v in comp_analysis.stride_analysis.items()}),
            compliance=json.dumps([]),
            feasibility_assessments=json.dumps({}),
            risk_acceptance=json.dumps({}),
            attack_paths=json.dumps([])
        )
        
        # Add to database
        db.add(db_component_analysis)
    
    # Commit all component analyses
    db.commit()
    
    return analysis

def get_analysis(db: Session, analysis_id: str) -> Optional[Analysis]:
    """
    Get analysis results by ID
    """
    # Get analysis
    db_analysis = db.query(DBAnalysis).filter(DBAnalysis.id == analysis_id).first()
    if not db_analysis:
        return None
    
    # Get component analyses
    db_component_analyses = db.query(DBComponentAnalysis).filter(
        DBComponentAnalysis.analysis_id == analysis_id
    ).all()
    
    # Convert to Pydantic models
    component_analyses = {}
    for db_comp_analysis in db_component_analyses:
        # Extract component ID
        comp_id = db_comp_analysis.component_id
        
        # Parse JSON fields
        threats = json.loads(db_comp_analysis.threats) if db_comp_analysis.threats else []
        stride_analysis_data = json.loads(db_comp_analysis.stride_analysis) if db_comp_analysis.stride_analysis else {}
        compliance = json.loads(db_comp_analysis.compliance) if db_comp_analysis.compliance else []
        feasibility_assessments_data = json.loads(db_comp_analysis.feasibility_assessments) if db_comp_analysis.feasibility_assessments else {}
        risk_acceptance_data = json.loads(db_comp_analysis.risk_acceptance) if db_comp_analysis.risk_acceptance else {}
        attack_paths_data = json.loads(db_comp_analysis.attack_paths) if db_comp_analysis.attack_paths else []
        
        # Get component
        component = get_component(db, comp_id)
        if not component:
            logger.warning(f"Component {comp_id} not found")
            continue
        
        # Create ComponentAnalysis
        component_analyses[comp_id] = ComponentAnalysis(
            component_id=comp_id,
            name=component.name,
            type=component.type,
            safety_level=component.safety_level,
            threats=[Threat(**t) for t in threats],
            stride_analysis={k: StrideRecommendation(**v) for k, v in stride_analysis_data.items()},
            compliance=[ComplianceRequirement(**req) for req in compliance],
            feasibility_assessments={k: AttackerFeasibility(**v) for k, v in feasibility_assessments_data.items()},
            risk_acceptance={k: RiskAcceptance(**v) for k, v in risk_acceptance_data.items()},
            attack_paths=[AttackPath(**p) for p in attack_paths_data]
        )
    
    # Create summary
    summary = AnalysisSummary(
        total_components=db_analysis.total_components,
        total_threats=db_analysis.total_threats,
        critical_components=db_analysis.critical_components,
        high_risk_threats=db_analysis.high_risk_threats
    )
    
    # Create Analysis
    analysis = Analysis(
        id=db_analysis.id,
        name=db_analysis.name,
        description=db_analysis.description,
        created_at=db_analysis.created_at,
        updated_at=db_analysis.updated_at,
        component_analyses=component_analyses,
        summary=summary
    )
    
    return analysis

def list_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[AnalysisSummary]:
    """
    List all analyses with pagination
    """
    db_analyses = db.query(DBAnalysis).order_by(DBAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to Pydantic models
    analyses = []
    for db_analysis in db_analyses:
        summary = AnalysisSummary(
            id=db_analysis.id,
            name=db_analysis.name,
            description=db_analysis.description,
            created_at=db_analysis.created_at,
            total_components=db_analysis.total_components,
            total_threats=db_analysis.total_threats,
            critical_components=db_analysis.critical_components,
            high_risk_threats=db_analysis.high_risk_threats
        )
        analyses.append(summary)
    
    return analyses
