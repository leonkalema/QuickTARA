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
from api.services.component_service import get_component

# Import core analysis functionality
from core.quicktara import (
    load_components, analyze_threats, analyze_attack_paths, calculate_component_risk_factors
)
from core.stride_analysis import analyze_stride_categories, get_stride_recommendations, StrideCategory
from core.threat_analysis import load_threats_from_capec, AUTOMOTIVE_THREATS, analyze_impact_categories
from core.attacker_feasibility import assess_all_component_threats
from core.risk_acceptance import assess_component_risk_acceptance
from core.cybersecurity_goals import map_all_component_threats_to_goals
from core.compliance_mappings import map_threat_to_standards

logger = logging.getLogger(__name__)


def run_analysis(db: Session, analysis_create: AnalysisCreate) -> Analysis:
    """
    Run analysis on selected components
    """
    # Generate unique ID for the analysis
    analysis_id = str(uuid.uuid4())
    
    # Create analysis database record
    db_analysis = DBAnalysis(
        id=analysis_id,
        name=analysis_create.name or f"Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=analysis_create.description
    )
    
    # Get components from database
    components = {}
    for component_id in analysis_create.component_ids:
        component = get_component(db, component_id)
        if component:
            # Convert Pydantic model to the format expected by core analysis
            components[component_id] = _convert_component_for_analysis(component)
    
    if not components:
        raise ValueError("No valid components found for analysis")
    
    # Run analysis using core functionality
    logger.info(f"Starting analysis for {len(components)} components")
    
    # Load threat database
    capec_files = ["1000.csv", "3000.csv"]
    try:
        capec_threats = load_threats_from_capec(capec_files)
        all_threats = {**AUTOMOTIVE_THREATS, **capec_threats}
    except Exception as e:
        logger.error(f"Error loading threats: {str(e)}")
        all_threats = AUTOMOTIVE_THREATS
    
    # Analyze threats for each component
    analyzed_components = {}
    
    for comp_id, component in components.items():
        try:
            # Match threats to component
            matched_threats = _match_threats_to_component(component, all_threats)
            
            # Analyze STRIDE categories
            stride_categories = analyze_stride_categories(
                component.type.value,
                list(component.interfaces),
                list(component.access_points),
                list(component.data_types),
                component.trust_zone.value
            )
            
            # Get security recommendations
            recommendations = get_stride_recommendations(
                stride_categories,
                component.type.value,
                component.safety_level.value
            )
            
            # Map threats to compliance standards
            compliance_reqs = []
            for threat in matched_threats:
                reqs = map_threat_to_standards(
                    threat['name'],
                    component.safety_level.value,
                    component.trust_zone.value
                )
                compliance_reqs.extend(reqs)
            
            # Map threats to cybersecurity goals
            goal_mappings = map_all_component_threats_to_goals({
                'type': component.type.value,
                'safety_level': component.safety_level.value,
                'threats': matched_threats
            })
            
            # Assess attacker feasibility for threats
            feasibility_assessments = assess_all_component_threats({
                'type': component.type.value,
                'safety_level': component.safety_level.value,
                'interfaces': list(component.interfaces),
                'access_points': list(component.access_points),
                'location': component.location,
                'threats': matched_threats
            })
            
            # Assess risk acceptance criteria
            risk_acceptance_assessments = assess_component_risk_acceptance({
                'type': component.type.value,
                'safety_level': component.safety_level.value,
                'threats': matched_threats
            })
            
            # Store results
            analyzed_components[comp_id] = {
                'name': component.name,
                'type': component.type.value,
                'safety_level': component.safety_level.value,
                'interfaces': list(component.interfaces),
                'access_points': list(component.access_points),
                'data_types': list(component.data_types),
                'location': component.location,
                'trust_zone': component.trust_zone.value,
                'connected_to': list(component.connected_to),
                'threats': matched_threats,
                'stride_analysis': {
                    str(category): {
                        'risk_level': 'High' if category in stride_categories else 'Low',
                        'recommendations': [r for r in recommendations if str(category).lower() in r.lower()]
                    }
                    for category in StrideCategory
                },
                'compliance': compliance_reqs,
                'cybersecurity_goals': _serialize_goal_mappings(goal_mappings),
                'feasibility_assessments': _serialize_feasibility_assessments(feasibility_assessments),
                'risk_acceptance': _serialize_risk_acceptance(risk_acceptance_assessments)
            }
        except Exception as e:
            logger.error(f"Error analyzing component {comp_id}: {str(e)}")
            # Continue with next component
    
    # Analyze attack paths between components
    component_list = list(components.values())
    attack_paths = analyze_attack_paths(component_list, all_threats)
    
    # Add attack paths to results
    for comp_id, paths in attack_paths.items():
        if comp_id in analyzed_components:
            analyzed_components[comp_id]['attack_paths'] = [
                {
                    'path': path,
                    'risk': {}  # Placeholder for risk calculations
                }
                for path in paths
            ]
    
    # Calculate analysis summary
    total_threats = sum(len(comp_data.get('threats', [])) for comp_data in analyzed_components.values())
    high_risk_threats = sum(
        1 for comp_data in analyzed_components.values()
        for threat in comp_data.get('threats', [])
        if any(score >= 4 for score in threat.get('impact', {}).values())
    )
    critical_components = sum(
        1 for comp_id, comp_data in analyzed_components.items()
        if comp_data.get('trust_zone') == 'Critical'
    )
    
    summary = AnalysisSummary(
        total_components=len(components),
        total_threats=total_threats,
        critical_components=critical_components,
        high_risk_threats=high_risk_threats
    )
    
    # Convert to Pydantic models
    component_analyses = {}
    for comp_id, analysis_data in analyzed_components.items():
        # Convert threats to Pydantic models
        threats = []
        for threat_data in analysis_data.get('threats', []):
            impact_data = threat_data.get('impact', {})
            risk_factors_data = threat_data.get('risk_factors', {})
            
            threat = Threat(
                name=threat_data.get('name', ''),
                description=threat_data.get('description', ''),
                likelihood=threat_data.get('likelihood', 1),
                impact={
                    'financial': impact_data.get('financial', 1),
                    'safety': impact_data.get('safety', 1),
                    'privacy': impact_data.get('privacy', 1)
                },
                risk_factors={
                    'exposure': risk_factors_data.get('exposure', 0.0),
                    'complexity': risk_factors_data.get('complexity', 0.0),
                    'attack_surface': risk_factors_data.get('attack_surface', 0.0)
                }
            )
            threats.append(threat)
        
        # Convert STRIDE analysis to Pydantic models
        stride_analysis = {}
        for category, data in analysis_data.get('stride_analysis', {}).items():
            stride_analysis[category] = StrideRecommendation(
                category=category,
                risk_level=data.get('risk_level', 'Low'),
                recommendations=data.get('recommendations', [])
            )
        
        # Convert compliance requirements to Pydantic models
        compliance = []
        for req_data in analysis_data.get('compliance', []):
            compliance.append(ComplianceRequirement(
                standard=req_data.get('standard', ''),
                requirement=req_data.get('requirement', ''),
                description=req_data.get('description', '')
            ))
        
        # Convert attacker feasibility to Pydantic models
        feasibility_assessments = {}
        for threat_name, assessment_data in analysis_data.get('feasibility_assessments', {}).items():
            if isinstance(assessment_data, dict):
                # It's already a dict
                attacker_profiles = []
                for profile_type, relevance in assessment_data.get('profiles', {}).items():
                    attacker_profiles.append({
                        'profile_type': profile_type,
                        'relevance': relevance,
                        'capabilities': []
                    })
                
                feasibility_assessments[threat_name] = AttackerFeasibility(
                    feasibility_level=assessment_data.get('feasibility_level', 'Medium'),
                    technical_capability=assessment_data.get('technical_capability', 3),
                    knowledge_required=assessment_data.get('knowledge_required', 3),
                    resources_needed=assessment_data.get('resources_needed', 3),
                    time_required=assessment_data.get('time_required', 3),
                    overall_score=assessment_data.get('overall_score', 3),
                    enabling_factors=assessment_data.get('enabling_factors', []),
                    mitigating_factors=assessment_data.get('mitigating_factors', []),
                    attacker_profiles=attacker_profiles
                )
        
        # Convert risk acceptance to Pydantic models
        risk_acceptance = {}
        for threat_name, acceptance_data in analysis_data.get('risk_acceptance', {}).items():
            if isinstance(acceptance_data, dict):
                risk_acceptance[threat_name] = RiskAcceptance(
                    decision=acceptance_data.get('decision', 'Mitigate'),
                    risk_severity=acceptance_data.get('risk_severity', 'Medium'),
                    residual_risk=acceptance_data.get('residual_risk', 0.5),
                    justification=acceptance_data.get('justification', ''),
                    conditions=acceptance_data.get('conditions', []),
                    approvers=acceptance_data.get('approvers', []),
                    reassessment_period=acceptance_data.get('reassessment_period', 12)
                )
        
        # Convert attack paths to Pydantic models
        attack_paths = []
        for path_data in analysis_data.get('attack_paths', []):
            attack_paths.append(AttackPath(
                path=path_data.get('path', []),
                risk=path_data.get('risk', {})
            ))
        
        # Create ComponentAnalysis
        component_analyses[comp_id] = ComponentAnalysis(
            component_id=comp_id,
            name=analysis_data.get('name', ''),
            type=analysis_data.get('type', ''),
            safety_level=analysis_data.get('safety_level', ''),
            threats=threats,
            stride_analysis=stride_analysis,
            compliance=compliance,
            feasibility_assessments=feasibility_assessments,
            risk_acceptance=risk_acceptance,
            attack_paths=attack_paths
        )
    
    # Create Analysis object
    analysis = Analysis(
        id=analysis_id,
        name=analysis_create.name or f"Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=analysis_create.description,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        components=component_analyses,
        summary=summary
    )
    
    # Update analysis summary metrics in database
    db_analysis.total_components = summary.total_components
    db_analysis.total_threats = summary.total_threats
    db_analysis.critical_components = summary.critical_components
    db_analysis.high_risk_threats = summary.high_risk_threats
    
    # Add to database
    db.add(db_analysis)
    db.commit()
    
    # Store component analysis results
    for comp_id, comp_analysis in component_analyses.items():
        # Generate unique ID for component analysis
        component_analysis_id = str(uuid.uuid4())
        
        # Create database record
        db_component_analysis = DBComponentAnalysis(
            id=component_analysis_id,
            analysis_id=analysis_id,
            component_id=comp_id,
            threats=json.dumps([threat.dict() for threat in comp_analysis.threats]),
            stride_analysis=json.dumps({k: v.dict() for k, v in comp_analysis.stride_analysis.items()}),
            compliance=json.dumps([req.dict() for req in comp_analysis.compliance]),
            feasibility_assessments=json.dumps({k: v.dict() for k, v in comp_analysis.feasibility_assessments.items()}),
            risk_acceptance=json.dumps({k: v.dict() for k, v in comp_analysis.risk_acceptance.items()}),
            attack_paths=json.dumps([path.dict() for path in comp_analysis.attack_paths])
        )
        
        # Add to database
        db.add(db_component_analysis)
    
    # Commit all component analyses
    db.commit()
    db.refresh(db_analysis)
    
    # Return the Pydantic model
    return analysis


def get_analysis(db: Session, analysis_id: str) -> Optional[Analysis]:
    """
    Get analysis by ID
    """
    # Retrieve analysis from database
    db_analysis = db.query(DBAnalysis).filter(DBAnalysis.id == analysis_id).first()
    if not db_analysis:
        return None
    
    # Get component analyses
    db_component_analyses = (
        db.query(DBComponentAnalysis)
        .filter(DBComponentAnalysis.analysis_id == analysis_id)
        .all()
    )
    
    # Convert to Pydantic models
    component_analyses = {}
    for db_comp_analysis in db_component_analyses:
        # Parse JSON fields
        threats = json.loads(db_comp_analysis.threats) if db_comp_analysis.threats else []
        stride_analysis = json.loads(db_comp_analysis.stride_analysis) if db_comp_analysis.stride_analysis else {}
        compliance = json.loads(db_comp_analysis.compliance) if db_comp_analysis.compliance else []
        feasibility_assessments = json.loads(db_comp_analysis.feasibility_assessments) if db_comp_analysis.feasibility_assessments else {}
        risk_acceptance = json.loads(db_comp_analysis.risk_acceptance) if db_comp_analysis.risk_acceptance else {}
        attack_paths = json.loads(db_comp_analysis.attack_paths) if db_comp_analysis.attack_paths else []
        
        # Get component info
        component = get_component(db, db_comp_analysis.component_id)
        if not component:
            continue
        
        # Create ComponentAnalysis
        component_analyses[db_comp_analysis.component_id] = ComponentAnalysis(
            component_id=db_comp_analysis.component_id,
            name=component.name,
            type=component.type,
            safety_level=component.safety_level,
            threats=[Threat(**threat) for threat in threats],
            stride_analysis={k: StrideRecommendation(**v) for k, v in stride_analysis.items()},
            compliance=[ComplianceRequirement(**req) for req in compliance],
            feasibility_assessments={k: AttackerFeasibility(**v) for k, v in feasibility_assessments.items()},
            risk_acceptance={k: RiskAcceptance(**v) for k, v in risk_acceptance.items()},
            attack_paths=[AttackPath(**path) for path in attack_paths]
        )
    
    # Create Analysis summary
    summary = AnalysisSummary(
        total_components=db_analysis.total_components,
        total_threats=db_analysis.total_threats,
        critical_components=db_analysis.critical_components,
        high_risk_threats=db_analysis.high_risk_threats
    )
    
    # Create Analysis object
    return Analysis(
        id=db_analysis.id,
        name=db_analysis.name,
        description=db_analysis.description,
        created_at=db_analysis.created_at,
        updated_at=db_analysis.updated_at,
        components=component_analyses,
        summary=summary
    )


def list_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[Analysis]:
    """
    List all analyses with pagination
    """
    # Retrieve analyses from database
    db_analyses = db.query(DBAnalysis).order_by(DBAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to Pydantic models
    analyses = []
    for db_analysis in db_analyses:
        # Create Analysis summary
        summary = AnalysisSummary(
            total_components=db_analysis.total_components,
            total_threats=db_analysis.total_threats,
            critical_components=db_analysis.critical_components,
            high_risk_threats=db_analysis.high_risk_threats
        )
        
        # For list view, we don't need the full component details
        analyses.append(Analysis(
            id=db_analysis.id,
            name=db_analysis.name,
            description=db_analysis.description,
            created_at=db_analysis.created_at,
            updated_at=db_analysis.updated_at,
            components={},  # Empty for list view
            summary=summary
        ))
    
    return analyses


def count_analyses(db: Session) -> int:
    """
    Count total number of analyses
    """
    return db.query(DBAnalysis).count()


def get_stride_analysis(db: Session, analysis_id: str) -> Dict[str, Any]:
    """
    Get STRIDE analysis from an analysis
    """
    # Retrieve analysis from database
    db_analysis = db.query(DBAnalysis).filter(DBAnalysis.id == analysis_id).first()
    if not db_analysis:
        return {}
    
    # Get component analyses
    db_component_analyses = (
        db.query(DBComponentAnalysis)
        .filter(DBComponentAnalysis.analysis_id == analysis_id)
        .all()
    )
    
    # Extract STRIDE analysis for each component
    result = {}
    for db_comp_analysis in db_component_analyses:
        # Get component info
        component = get_component(db, db_comp_analysis.component_id)
        if not component:
            continue
            
        # Parse STRIDE analysis JSON
        stride_analysis = json.loads(db_comp_analysis.stride_analysis) if db_comp_analysis.stride_analysis else {}
        
        # Add to result
        result[db_comp_analysis.component_id] = {
            "component_name": component.name,
            "stride_categories": stride_analysis
        }
    
    return result


def get_attack_paths(db: Session, analysis_id: str) -> List[Dict[str, Any]]:
    """
    Get attack paths from an analysis
    """
    # Retrieve analysis from database
    db_analysis = db.query(DBAnalysis).filter(DBAnalysis.id == analysis_id).first()
    if not db_analysis:
        return []
    
    # Get component analyses
    db_component_analyses = (
        db.query(DBComponentAnalysis)
        .filter(DBComponentAnalysis.analysis_id == analysis_id)
        .all()
    )
    
    # Extract attack paths
    attack_paths = []
    component_names = {}
    
    # First get all component names for reference
    for db_comp_analysis in db_component_analyses:
        component = get_component(db, db_comp_analysis.component_id)
        if component:
            component_names[db_comp_analysis.component_id] = component.name
    
    # Now extract attack paths
    for db_comp_analysis in db_component_analyses:
        # Parse attack paths JSON
        paths = json.loads(db_comp_analysis.attack_paths) if db_comp_analysis.attack_paths else []
        
        for path in paths:
            # Add component names to path
            path_with_names = {
                "component_id": db_comp_analysis.component_id,
                "component_name": component_names.get(db_comp_analysis.component_id, "Unknown"),
                "path": [
                    {
                        "id": comp_id,
                        "name": component_names.get(comp_id, "Unknown")
                    } for comp_id in path.get("path", [])
                ],
                "risk": path.get("risk", {})
            }
            attack_paths.append(path_with_names)
    
    return attack_paths


def _convert_component_for_analysis(component: Component) -> Any:
    """
    Convert Pydantic component model to a format that works with core analysis
    """
    # Create a component object with attributes expected by the analysis functions
    class ComponentForAnalysis:
        def __init__(self, component: Component):
            self.component_id = component.component_id
            self.name = component.name
            
            # Type enum
            class TypeEnum:
                def __init__(self, value):
                    self.value = value
            self.type = TypeEnum(component.type)
            
            # Safety level enum
            class SafetyLevelEnum:
                def __init__(self, value):
                    self.value = value
            self.safety_level = SafetyLevelEnum(component.safety_level)
            
            # Convert lists to sets
            self.interfaces = set(component.interfaces)
            self.access_points = set(component.access_points)
            self.data_types = set(component.data_types)
            
            self.location = component.location
            
            # Trust zone enum
            class TrustZoneEnum:
                def __init__(self, value):
                    self.value = value
            self.trust_zone = TrustZoneEnum(component.trust_zone)
            
            # Connected components
            self.connected_to = set(component.connected_to)
    
    return ComponentForAnalysis(component)


def _match_threats_to_component(component: Any, threats: Dict[str, Dict]) -> List[Dict]:
    """
    Match threats to a component
    """
    matched_threats = []
    
    for name, threat in threats.items():
        # Match based on component type and interfaces
        type_match = component.type.value.lower() in name.lower()
        interface_match = any(
            interface.lower() in threat.get('description', '').lower()
            for interface in component.interfaces
        )
        data_match = any(
            data_type.lower() in threat.get('description', '').lower()
            for data_type in component.data_types
        )
        
        if type_match or interface_match or data_match:
            # Calculate risk factors
            risk_factors = calculate_component_risk_factors(component)
            
            # Adjust threat likelihood based on risk factors
            base_likelihood = threat.get('likelihood', 3)
            exposure_factor = risk_factors.get('exposure', 0.5)
            attack_surface_factor = risk_factors.get('attack_surface', 0.5)
            
            # Weighted adjustment
            adjusted_likelihood = min(5, max(1, base_likelihood * (
                0.4 * exposure_factor +
                0.3 * attack_surface_factor +
                0.3
            )))
            
            # Adjust impact based on safety level
            safety_impact_factors = {
                'QM': 0.6,
                'ASIL A': 0.8,
                'ASIL B': 1.0,
                'ASIL C': 1.2,
                'ASIL D': 1.4
            }
            
            safety_factor = safety_impact_factors.get(component.safety_level.value, 1.0)
            adjusted_impact = {
                category: min(5, max(1, score * safety_factor))
                for category, score in threat.get('impact', {}).items()
            }
            
            # Create adjusted threat
            adjusted_threat = threat.copy()
            adjusted_threat['likelihood'] = adjusted_likelihood
            adjusted_threat['impact'] = adjusted_impact
            adjusted_threat['risk_factors'] = risk_factors
            
            matched_threats.append({
                'name': name,
                **adjusted_threat
            })
    
    return matched_threats


def _serialize_goal_mappings(goal_mappings: Dict) -> Dict:
    """
    Serialize cybersecurity goal mappings to JSON-serializable format
    """
    serialized = {}
    for threat_name, mappings in goal_mappings.items():
        serialized[threat_name] = [
            {
                'goal': mapping.goal.value,
                'relevance': mapping.relevance,
                'description': mapping.description,
                'requirements': mapping.requirements
            } for mapping in mappings
        ]
    return serialized


def _serialize_feasibility_assessments(feasibility_assessments: Dict) -> Dict:
    """
    Serialize attacker feasibility assessments to JSON-serializable format
    """
    serialized = {}
    for threat_name, assessment in feasibility_assessments.items():
        # Convert to dictionary
        assessment_dict = assessment.to_dict() if hasattr(assessment, 'to_dict') else {
            'feasibility_level': getattr(assessment.feasibility, 'feasibility_level', 'Medium'),
            'technical_capability': getattr(assessment.feasibility, 'technical_capability', 3),
            'knowledge_required': getattr(assessment.feasibility, 'knowledge_required', 3),
            'resources_needed': getattr(assessment.feasibility, 'resources_needed', 3),
            'time_required': getattr(assessment.feasibility, 'time_required', 3),
            'overall_score': getattr(assessment.feasibility, 'overall_score', 3),
            'enabling_factors': getattr(assessment, 'enabling_factors', []),
            'mitigating_factors': getattr(assessment, 'mitigating_factors', []),
            'profiles': {
                profile.value if hasattr(profile, 'value') else profile: score
                for profile, score in getattr(assessment, 'profiles', {}).items()
            }
        }
        serialized[threat_name] = assessment_dict
    return serialized


def _serialize_risk_acceptance(risk_acceptance: Dict) -> Dict:
    """
    Serialize risk acceptance assessments to JSON-serializable format
    """
    serialized = {}
    for threat_name, assessment in risk_acceptance.items():
        # Convert to dictionary
        assessment_dict = assessment.to_dict() if hasattr(assessment, 'to_dict') else {
            'decision': assessment.decision.value if hasattr(assessment.decision, 'value') else assessment.decision,
            'risk_severity': assessment.risk_severity.value if hasattr(assessment.risk_severity, 'value') else assessment.risk_severity,
            'residual_risk': assessment.residual_risk,
            'justification': assessment.justification,
            'conditions': assessment.conditions,
            'approvers': [approver.value if hasattr(approver, 'value') else approver for approver in assessment.approvers],
            'reassessment_period': assessment.criteria.reassessment_period if hasattr(assessment, 'criteria') else 12
        }
        serialized[threat_name] = assessment_dict
    return serialized
