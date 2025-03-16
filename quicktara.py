#!/usr/bin/env python3
"""
QuickTARA - Lightweight Automotive Risk Assessor
Enhanced with detailed component analysis and STRIDE
"""

import csv
import click
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from compliance_mappings import map_threat_to_standards, format_compliance_mappings
from export_formats import export_report
from stride_analysis import (
    analyze_stride_categories,
    get_stride_recommendations,
    format_stride_analysis
)
from threat_analysis import (
    load_threats_from_capec,
    AUTOMOTIVE_THREATS,
    analyze_impact_categories,
    ImpactScore
)

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
    """Parse CSV row into Component object with enhanced attributes"""
    return Component(
        component_id=row['component_id'],
        name=row['name'],
        type=AssetType(row['type']),
        safety_level=SafetyLevel(row['safety_level']),
        interfaces=set(filter(None, row['interfaces'].split('|'))),
        access_points=set(filter(None, row['access_points'].split('|'))),
        data_types=set(filter(None, row['data_types'].split('|'))),
        location=row['location'],
        trust_zone=TrustZone(row['trust_zone']),
        connected_to=set(filter(None, row['connected_to'].split('|')))
    )

def load_components(asset_file: Path) -> List[Component]:
    """Load and parse components from enhanced CSV format"""
    components = []
    try:
        with asset_file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    component = parse_component(row)
                    components.append(component)
                except (ValueError, KeyError) as e:
                    click.echo(f"Warning: Could not parse component {row.get('name', 'Unknown')}: {e}", err=True)
    except (csv.Error, IOError) as e:
        click.echo(f"Error loading components: {e}", err=True)
        sys.exit(1)
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

def analyze_attack_paths(components: List[Component], threats: Dict[str, Dict]) -> Dict[str, List[List[str]]]:
    """Analyze potential attack paths through connected components"""
    paths = defaultdict(list)
    
    def find_paths(start: str, target: str, visited: Set[str], current_path: List[str]):
        if len(current_path) > 5:  # Limit path length
            return
        
        current = next((c for c in components if c.component_id == start), None)
        if not current or start in visited:
            return
        
        visited.add(start)
        current_path.append(start)
        
        if start == target:
            paths[target].append(current_path.copy())
        else:
            for next_id in current.connected_to:
                find_paths(next_id, target, visited.copy(), current_path.copy())
    
    # Find paths to critical components
    critical_components = [c for c in components if c.trust_zone == TrustZone.CRITICAL]
    untrusted_components = [c for c in components if c.trust_zone == TrustZone.UNTRUSTED]
    
    for start in untrusted_components:
        for target in critical_components:
            find_paths(start.component_id, target.component_id, set(), [])
    
    return dict(paths)

def format_impact_scores(impact: Dict[str, int]) -> str:
    """Format impact scores for display"""
    return (
        f"Financial: {impact['financial']}, "
        f"Safety: {impact['safety']}, "
        f"Privacy: {impact['privacy']}"
    )

def calculate_risk(impact: Dict[str, int], likelihood: int) -> Dict[str, int]:
    """Calculate risk scores for each impact category"""
    return {
        category: score * likelihood
        for category, score in impact.items()
    }

def calculate_chain_risk(chain: List[str], threats: Dict[str, Dict]) -> Dict[str, int]:
    """Calculate cumulative risk for an attack chain"""
    # Get maximum impact for each category
    max_impacts = {
        category: max(threats[name]['impact'][category] for name in chain)
        for category in ['financial', 'safety', 'privacy']
    }
    
    # Chain likelihood is product of individual likelihoods (normalized)
    chain_likelihood = 1
    for name in chain:
        chain_likelihood *= threats[name]['likelihood'] / 4  # Normalize by max likelihood
    chain_likelihood = int(chain_likelihood * 4)  # Scale back to 1-4 range
    
    return calculate_risk(max_impacts, max(1, chain_likelihood))

def write_report(components: List[Component], threats: Dict[str, Dict], output_path: Path) -> None:
    """Generate and write risk report"""
    try:
        # Build attack chains once
        attack_chains = analyze_attack_paths(components, threats)
        
        # Prepare structured report data
        report_data = {
            "components": {}
        }
        
        for component in components:
            comp_data = {
                "name": component.name,
                "type": component.type.value,
                "safety_level": component.safety_level.value,
                "interfaces": list(component.interfaces),
                "access_points": list(component.access_points),
                "data_types": list(component.data_types),
                "location": component.location,
                "trust_zone": component.trust_zone.value,
                "connected_to": list(component.connected_to),
                "threats": []
            }
            
            # Match threats to component
            matched_threats = match_threats_to_component(component, threats)
            
            if matched_threats:
                # Sort threats by maximum risk score across all categories
                sorted_threats = sorted(
                    matched_threats,
                    key=lambda x: max(calculate_risk(x['impact'], x['likelihood']).values()),
                    reverse=True
                )
                
                for threat in sorted_threats:
                    threat_data = {
                        "name": threat['name'],
                        "impact_scores": format_impact_scores(threat['impact']),
                        "risk_scores": format_impact_scores(calculate_risk(threat['impact'], threat['likelihood'])),
                        "risk_factors": threat['risk_factors']
                    }
                    
                    if 'description' in threat:
                        threat_data['description'] = threat['description']
                    if 'mitigations' in threat:
                        threat_data['mitigations'] = threat['mitigations']
                    if 'compliance' in threat:
                        threat_data['compliance'] = threat['compliance']
                    if 'stride' in threat:
                        threat_data['stride'] = threat['stride']
                    
                    # Add attack chains
                    if component.name in attack_chains:
                        threat_data['attack_chains'] = []
                        for chain in attack_chains[component.name]:
                            chain_risks = calculate_chain_risk(chain, threats)
                            threat_data['attack_chains'].append({
                                "chain": chain,
                                "risk_scores": format_impact_scores(chain_risks)
                            })
                    
                    comp_data['threats'].append(threat_data)
            
            report_data['components'][component.name] = comp_data
        
        # Generate text report
        with output_path.open('w') as f:
            f.write("QuickTARA Report\n================\n")
            
            for comp_name, comp_data in report_data['components'].items():
                f.write(f"\nComponent: {comp_name}\n")
                f.write(f"Type: {comp_data['type']}\n")
                f.write(f"Safety Level: {comp_data['safety_level']}\n")
                f.write(f"Interfaces: {', '.join(comp_data['interfaces'])}\n")
                f.write(f"Access Points: {', '.join(comp_data['access_points'])}\n")
                f.write(f"Data Types: {', '.join(comp_data['data_types'])}\n")
                f.write(f"Location: {comp_data['location']}\n")
                f.write(f"Trust Zone: {comp_data['trust_zone']}\n")
                f.write(f"Connected To: {', '.join(comp_data['connected_to'])}\n")
                
                if comp_data['threats']:
                    f.write("\nIdentified Threats:\n")
                    for threat in comp_data['threats']:
                        f.write(f"\n- {threat['name']}\n")
                        f.write(f"  Impact Scores: {threat['impact_scores']}\n")
                        f.write(f"  Risk Scores: {threat['risk_scores']}\n")
                        f.write(f"  Risk Factors: {threat['risk_factors']}\n")
                        
                        if 'description' in threat:
                            f.write(f"  Description: {threat['description'][:200]}...\n")
                        if 'mitigations' in threat:
                            f.write(f"  Mitigations: {threat['mitigations'][:200]}...\n")
                        
                        # Add compliance mappings
                        if 'compliance' in threat:
                            f.write("\n  Compliance Requirements:\n")
                            f.write(format_compliance_mappings(threat['compliance']))
                            f.write("\n")
                        
                        # Add STRIDE analysis
                        if 'stride' in threat:
                            f.write("\n  STRIDE Analysis:\n")
                            f.write(format_stride_analysis(
                                threat['stride']['categories'],
                                threat['stride']['recommendations']
                            ))
                            f.write("\n")
                        
                        # Add attack chains
                        if 'attack_chains' in threat:
                            f.write("\n  Possible Attack Chains:\n")
                            for chain in threat['attack_chains']:
                                f.write(f"    * {' -> '.join(chain['chain'])}\n")
                                f.write(f"      Combined Risk Scores: {chain['risk_scores']}\n")
                else:
                    f.write("No applicable threats found\n")
            
            f.flush()
        
        # Export to other formats
        export_report(report_data, output_path, 'json')
        export_report(report_data, output_path, 'pdf')
        export_report(report_data, output_path, 'excel')
        
    except IOError as e:
        click.echo(f"Error writing report: {e}", err=True)
        sys.exit(1)

@click.command()
@click.option('-i', '--input-file', 'asset_file',
              type=click.Path(exists=True, path_type=Path),
              help='Input asset CSV file',
              required=True)
@click.option('-o', '--output-file', 'output_path',
              type=click.Path(path_type=Path),
              help='Output report file',
              default=Path('report.txt'))
def main(asset_file: Path, output_path: Path):
    """Enhanced TARA tool for automotive systems"""
    # Load components with detailed attributes
    components = load_components(asset_file)
    if not components:
        click.echo("No valid components found in input file", err=True)
        sys.exit(1)

    # Load CAPEC threats
    capec_files = [Path('1000.csv'), Path('3000.csv')]
    click.echo(f"Loading threats from {len(capec_files)} CAPEC files...")
    threats = {**AUTOMOTIVE_THREATS, **load_threats_from_capec(capec_files)}
    
    # Generate and write report
    write_report(components, threats, output_path)
    click.echo(f"Report written to {output_path}")
    click.echo(f"Additional formats: {output_path.with_suffix('.json')}, "
              f"{output_path.with_suffix('.xlsx')}, "
              f"{output_path.with_suffix('.pdf')}")

if __name__ == '__main__':
    main()