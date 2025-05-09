#!/usr/bin/env python3
"""
QuickTARA - Lightweight Automotive Risk Assessor
Enhanced with detailed component analysis and STRIDE
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

from core.compliance_mappings import map_threat_to_standards, format_compliance_mappings
from core.export_formats import export_report
from core.stride_analysis import (
    analyze_stride_categories,
    get_stride_recommendations,
    format_stride_analysis,
    StrideCategory
)
from core.risk_acceptance import (
    assess_component_risk_acceptance,
    format_risk_acceptance,
    RiskAcceptanceAssessment
)
from core.threat_analysis import (
    load_threats_from_capec,
    AUTOMOTIVE_THREATS,
    analyze_impact_categories,
    ImpactScore
)
from core.cybersecurity_goals import map_all_component_threats_to_goals
from core.attacker_feasibility import assess_all_component_threats

class AssetType(Enum):
    ECU = "ECU"
    SENSOR = "Sensor"
    GATEWAY = "Gateway"
    ACTUATOR = "Actuator"
    NETWORK = "Network"

class SafetyLevel(Enum):
    QM = "QM"
    ASIL_A = "ASIL A"
    ASIL_B = "ASIL B"
    ASIL_C = "ASIL C"
    ASIL_D = "ASIL D"

class TrustZone(Enum):
    CRITICAL = "Critical"
    BOUNDARY = "Boundary"
    STANDARD = "Standard"
    UNTRUSTED = "Untrusted"

@dataclass
class Component:
    component_id: str
    name: str
    type: AssetType
    safety_level: SafetyLevel
    interfaces: Set[str]
    access_points: Set[str]
    data_types: Set[str]
    location: str
    trust_zone: TrustZone
    connected_to: Set[str]

def parse_component(row: Dict[str, str]) -> Component:
    """Parse a CSV row into a Component object"""
    try:
        # Clean and validate type
        component_type = row['type'].strip().upper()
        if component_type not in AssetType.__members__:
            raise ValueError(f"Invalid component type: {component_type}")
        
        # Clean and validate safety level
        safety_level = row['safety_level'].strip().upper().replace(' ', '_')
        if safety_level not in SafetyLevel.__members__:
            raise ValueError(f"Invalid safety level: {safety_level}")
        
        # Clean and validate trust zone
        trust_zone = row['trust_zone'].strip().upper()
        if trust_zone not in TrustZone.__members__:
            raise ValueError(f"Invalid trust zone: {trust_zone}")
        
        # Clean and validate location
        location = row['location'].strip()
        if location not in ('Internal', 'External'):
            raise ValueError(f"Invalid location: {location}")
        
        return Component(
            component_id=row['component_id'].strip(),
            name=row['name'].strip(),
            type=AssetType[component_type],
            safety_level=SafetyLevel[safety_level],
            interfaces=set(filter(None, (i.strip() for i in row['interfaces'].split('|')))),
            access_points=set(filter(None, (a.strip() for a in row['access_points'].split('|')))),
            data_types=set(filter(None, (d.strip() for d in row['data_types'].split('|')))),
            location=location,
            trust_zone=TrustZone[trust_zone],
            connected_to=set(filter(None, (c.strip() for c in row['connected_to'].split('|'))))
        )
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid component data: {e}")

def load_components(asset_file: Path) -> Dict[str, Component]:
    """Load and parse components from enhanced CSV format"""
    components = {}
    try:
        with asset_file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    component = parse_component(row)
                    components[component.component_id] = component
                except ValueError as e:
                    print(f"Warning: Could not parse component {row.get('name', 'Unknown')}: {e}", file=sys.stderr)
                    continue
    except (csv.Error, IOError) as e:
        print(f"Error loading components: {e}", file=sys.stderr)
        raise ValueError(f"Error loading components: {e}")
    
    if not components:
        print("Error: No valid components found in the CSV file", file=sys.stderr)
        raise ValueError("No valid components found in the CSV file")
    
    return components

def calculate_component_risk_factors(component: Component) -> Dict[str, float]:
    """Calculate risk factors based on component attributes"""
    risk_factors = {
        'exposure': 0.0,
        'complexity': 0.0,
        'attack_surface': 0.0
    }
    
    # Exposure based on location and trust zone
    exposure_scores = {
        'External': 1.0,
        'Internal': 0.6
    }
    trust_scores = {
        TrustZone.UNTRUSTED: 1.0,
        TrustZone.BOUNDARY: 0.8,
        TrustZone.STANDARD: 0.6,
        TrustZone.CRITICAL: 0.4
    }
    risk_factors['exposure'] = (exposure_scores.get(component.location, 0.5) + 
                              trust_scores.get(component.trust_zone, 0.5)) / 2

    # Complexity based on interfaces and connections
    risk_factors['complexity'] = min(1.0, (
        len(component.interfaces) * 0.2 +
        len(component.connected_to) * 0.1
    ))

    # Attack surface based on access points and data types
    risk_factors['attack_surface'] = min(1.0, (
        len(component.access_points) * 0.3 +
        len(component.data_types) * 0.2
    ))

    return risk_factors

def adjust_threat_scores(threat: Dict, component: Component) -> Dict:
    """Adjust threat scores based on component characteristics"""
    risk_factors = calculate_component_risk_factors(component)
    
    # Adjust likelihood based on risk factors
    base_likelihood = threat['likelihood']
    exposure_factor = risk_factors['exposure']
    attack_surface_factor = risk_factors['attack_surface']
    
    # Weighted adjustment
    adjusted_likelihood = min(5, max(1, base_likelihood * (
        0.4 * exposure_factor +
        0.3 * attack_surface_factor +
        0.3
    )))
    
    # Adjust impact based on safety level
    safety_impact_factors = {
        SafetyLevel.QM: 0.6,
        SafetyLevel.ASIL_A: 0.8,
        SafetyLevel.ASIL_B: 1.0,
        SafetyLevel.ASIL_C: 1.2,
        SafetyLevel.ASIL_D: 1.4
    }
    
    safety_factor = safety_impact_factors.get(component.safety_level, 1.0)
    adjusted_impact = {
        category: min(5, max(1, score * safety_factor))
        for category, score in threat['impact'].items()
    }
    
    # Create adjusted threat
    adjusted_threat = threat.copy()
    adjusted_threat['likelihood'] = adjusted_likelihood
    adjusted_threat['impact'] = adjusted_impact
    adjusted_threat['risk_factors'] = risk_factors
    
    return adjusted_threat

def match_threats_to_component(component: Component, threats: Dict[str, Dict]) -> List[Dict]:
    """Match and adjust threats based on enhanced component attributes"""
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
            adjusted_threat = adjust_threat_scores(threat, component)
            matched_threats.append({
                'name': name,
                **adjusted_threat
            })
    
    return matched_threats

def analyze_threats(components: Dict[str, Component]) -> Dict[str, Dict]:
    """
    Analyze threats for all components using STRIDE methodology
    Returns a dictionary mapping component IDs to their threats
    """
    # Load CAPEC threats
    print("Loading threats from CAPEC files...")
    capec_files = [Path('1000.csv'), Path('3000.csv')]
    try:
        capec_threats = load_threats_from_capec(capec_files)
        all_threats = {**AUTOMOTIVE_THREATS, **capec_threats}
    except Exception as e:
        print(f"Warning: Could not load CAPEC threats: {e}", file=sys.stderr)
        all_threats = AUTOMOTIVE_THREATS
    
    analyzed_components = {}
    
    for comp_id, component in components.items():
        # Match threats to component
        matched_threats = match_threats_to_component(component, all_threats)
        
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
        
        # Map threats to compliance standards and format results
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
            'cybersecurity_goals': goal_mappings,
            'feasibility_assessments': feasibility_assessments,
            'risk_acceptance': risk_acceptance_assessments
        }
    
    # Convert components dictionary to list for attack path analysis
    component_list = list(components.values())
    
    # Analyze attack paths between components
    attack_paths = analyze_attack_paths(component_list, all_threats)
    
    # Add attack paths to results
    for comp_id, paths in attack_paths.items():
        if comp_id in analyzed_components:
            analyzed_components[comp_id]['attack_paths'] = [
                {
                    'path': path,
                    'risk': calculate_chain_risk(path, all_threats)
                }
                for path in paths
            ]
    
    return analyzed_components

def analyze_attack_paths(components: List[Component], threats: Dict[str, Dict]) -> Dict[str, List[List[str]]]:
    """Analyze potential attack paths through connected components"""
    paths = defaultdict(list)
    
    def find_paths(start: str, target: str, visited: Set[str], current_path: List[str]):
        if len(current_path) > 5:  # Limit path length
            return
        
        current = next((c for c in components if c.component_id == start), None)
        if not current or start in visited:
            return
        
        current_path.append(start)
        visited.add(start)
        
        if start == target:
            paths[start].append(current_path)
            return
        
        for next_id in current.connected_to:
            find_paths(next_id, target, visited.copy(), current_path.copy())
    
    # Find paths to critical components
    critical_components = [c for c in components if c.trust_zone == TrustZone.CRITICAL]
    untrusted_components = [c for c in components if c.trust_zone == TrustZone.UNTRUSTED]
    
    for start in untrusted_components:
        for target in critical_components:
            find_paths(start.component_id, target.component_id, set(), [])
    
    return paths

def calculate_chain_risk(chain: List[str], threats: Dict[str, Dict]) -> Dict[str, int]:
    """Calculate cumulative risk for an attack chain"""
    # Base risk scores for chain analysis
    chain_impacts = {
        "financial": 0,
        "safety": 0,
        "privacy": 0
    }
    chain_likelihood = 1  # Base likelihood
    
    # Analyze each step in the chain
    for threat_name in threats:
        threat = threats[threat_name]
        if any(comp_id in threat_name.lower() for comp_id in chain):
            # Update impacts - take maximum impact for each category
            for category, score in threat['impact'].items():
                chain_impacts[category] = max(chain_impacts[category], score)
            # Increase likelihood based on chain length
            chain_likelihood = min(5, chain_likelihood + threat['likelihood'])
    
    # Calculate final risk scores
    risk_scores = {}
    for category, impact in chain_impacts.items():
        risk_scores[category] = min(5, int((impact * chain_likelihood) / 3))
    
    return risk_scores

def write_report(components: Dict[str, Component], analyzed_components: Dict[str, Dict], output_path: Path, format: str = 'txt') -> None:
    """Generate and write risk report"""
    try:
        # Prepare structured report data
        report_data = {
            'components': {},
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_components': len(components),
                'total_threats': sum(len(comp_data['threats']) for comp_data in analyzed_components.values()),
                'critical_components': sum(1 for comp in components.values() if comp.trust_zone == TrustZone.CRITICAL),
                'high_risk_threats': sum(
                    1 for comp_data in analyzed_components.values()
                    for threat in comp_data['threats']
                    if any(score >= 4 for score in threat.get('impact', {}).values())
                )
            }
        }
        
        # Convert components to serializable format
        for comp_id, comp in components.items():
            # Convert cybersecurity goals to serializable format
            if comp_id in analyzed_components and 'cybersecurity_goals' in analyzed_components[comp_id]:
                goals_dict = {}
                for threat_name, mappings in analyzed_components[comp_id]['cybersecurity_goals'].items():
                    goals_dict[threat_name] = [
                        {
                            'goal': mapping.goal.value,
                            'relevance': mapping.relevance,
                            'description': mapping.description,
                            'requirements': mapping.requirements
                        } for mapping in mappings
                    ]
                analyzed_components[comp_id]['cybersecurity_goals'] = goals_dict
            
            # Convert feasibility assessments to serializable format
            if comp_id in analyzed_components and 'feasibility_assessments' in analyzed_components[comp_id]:
                feasibility_dict = {}
                for threat_name, assessment in analyzed_components[comp_id]['feasibility_assessments'].items():
                    feasibility_dict[threat_name] = assessment.to_dict()
                analyzed_components[comp_id]['feasibility_assessments'] = feasibility_dict
            
            # Convert risk acceptance assessments to serializable format
            if comp_id in analyzed_components and 'risk_acceptance' in analyzed_components[comp_id]:
                risk_acceptance_dict = {}
                for threat_name, assessment in analyzed_components[comp_id]['risk_acceptance'].items():
                    risk_acceptance_dict[threat_name] = assessment.to_dict()
                analyzed_components[comp_id]['risk_acceptance'] = risk_acceptance_dict
                
            # Add component to report
            report_data['components'][comp_id] = {
                'name': comp.name,
                'type': comp.type.value,
                'safety_level': comp.safety_level.value,
                'interfaces': list(comp.interfaces),
                'access_points': list(comp.access_points),
                'data_types': list(comp.data_types),
                'location': comp.location,
                'trust_zone': comp.trust_zone.value,
                'connected_to': list(comp.connected_to),
                'threats': analyzed_components[comp_id]['threats'],
                'stride_analysis': analyzed_components[comp_id]['stride_analysis'],
                'compliance': analyzed_components[comp_id]['compliance'],
                'cybersecurity_goals': analyzed_components[comp_id].get('cybersecurity_goals', {}),
                'feasibility_assessments': analyzed_components[comp_id].get('feasibility_assessments', {}),
                'risk_acceptance': analyzed_components[comp_id].get('risk_acceptance', {})
            }
        
        # Export in different formats
        export_report(report_data, output_path, format)
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        raise
