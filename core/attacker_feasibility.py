"""
Attacker Feasibility Module for QuickTARA
Analyzes feasibility of threats based on attacker capability, knowledge, and resources
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple

class AttackerProfile(Enum):
    HOBBYIST = "Hobbyist"
    CRIMINAL = "Criminal"
    HACKTIVIST = "Hacktivist"
    INSIDER = "Insider"
    APT = "Advanced Persistent Threat"

@dataclass
class FeasibilityScore:
    technical_capability: int  # 1-5 scale (1: low, 5: high)
    knowledge_required: int    # 1-5 scale (1: common knowledge, 5: specialized knowledge)
    resources_needed: int      # 1-5 scale (1: minimal resources, 5: significant resources)
    time_required: int         # 1-5 scale (1: quick, 5: extended period)
    
    @property
    def overall_score(self) -> int:
        """Calculate overall feasibility score (higher is more feasible for attacker)"""
        # Invert the scales for knowledge, resources, and time (lower is more feasible)
        inverted_knowledge = 6 - self.knowledge_required
        inverted_resources = 6 - self.resources_needed
        inverted_time = 6 - self.time_required
        
        # Weight technical capability higher
        return round(
            (self.technical_capability * 0.35) +
            (inverted_knowledge * 0.25) +
            (inverted_resources * 0.25) +
            (inverted_time * 0.15)
        )
    
    @property
    def feasibility_level(self) -> str:
        """Return a textual representation of feasibility"""
        score = self.overall_score
        if score >= 4.5:
            return "Very High"
        elif score >= 3.5:
            return "High"
        elif score >= 2.5:
            return "Medium"
        elif score >= 1.5:
            return "Low"
        else:
            return "Very Low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'technical_capability': self.technical_capability,
            'knowledge_required': self.knowledge_required,
            'resources_needed': self.resources_needed,
            'time_required': self.time_required,
            'overall_score': self.overall_score,
            'feasibility_level': self.feasibility_level
        }

@dataclass
class AttackerAssessment:
    profiles: Dict[AttackerProfile, int]  # Profile to relevance score (1-5)
    feasibility: FeasibilityScore
    mitigating_factors: List[str]
    enabling_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'profiles': {p.value: s for p, s in self.profiles.items()},
            'feasibility': self.feasibility.to_dict(),
            'mitigating_factors': self.mitigating_factors,
            'enabling_factors': self.enabling_factors
        }

def get_profile_capabilities(profile: AttackerProfile) -> Dict[str, int]:
    """Get default capabilities for different attacker profiles"""
    capabilities = {
        AttackerProfile.HOBBYIST: {
            'technical_capability': 2,
            'knowledge_required': 2,
            'resources_needed': 1,
            'time_required': 3
        },
        AttackerProfile.CRIMINAL: {
            'technical_capability': 3,
            'knowledge_required': 3,
            'resources_needed': 3,
            'time_required': 2
        },
        AttackerProfile.HACKTIVIST: {
            'technical_capability': 3,
            'knowledge_required': 3,
            'resources_needed': 2,
            'time_required': 3
        },
        AttackerProfile.INSIDER: {
            'technical_capability': 2,
            'knowledge_required': 4,
            'resources_needed': 2,
            'time_required': 2
        },
        AttackerProfile.APT: {
            'technical_capability': 5,
            'knowledge_required': 5,
            'resources_needed': 5,
            'time_required': 4
        }
    }
    
    return capabilities.get(profile, {
        'technical_capability': 3,
        'knowledge_required': 3,
        'resources_needed': 3,
        'time_required': 3
    })

def get_interface_complexity(interfaces: List[str]) -> int:
    """Evaluate complexity based on interfaces"""
    complexity_scores = {
        'can': 2,
        'flexray': 4,
        'ethernet': 3,
        'lin': 2,
        'wifi': 3,
        '4g': 4,
        '5g': 5,
        'bluetooth': 3,
        'usb': 2,
        'obd-ii': 2
    }
    
    if not interfaces:
        return 3  # Default medium complexity
    
    # Calculate average complexity
    total_score = 0
    count = 0
    
    for interface in interfaces:
        interface_lower = interface.lower()
        for key, score in complexity_scores.items():
            if key in interface_lower:
                total_score += score
                count += 1
                break
    
    return round(total_score / max(1, count))

def get_component_accessibility(component_type: str, location: str, access_points: List[str]) -> int:
    """Evaluate accessibility based on component type and location"""
    # Base accessibility score based on location
    if location.lower() == 'external':
        base_score = 4
    else:
        base_score = 2
    
    # Adjust for component type
    type_adjustments = {
        'ecu': 0,
        'sensor': 1,
        'gateway': -1,
        'actuator': 1,
        'network': 0
    }
    
    component_adjustment = 0
    for comp_type, adjustment in type_adjustments.items():
        if comp_type in component_type.lower():
            component_adjustment = adjustment
            break
    
    # Adjust for access points
    access_adjustment = 0
    if access_points:
        critical_access = ['debug', 'usb', 'obd', 'diagnostic', 'jtag']
        for point in access_points:
            if any(access in point.lower() for access in critical_access):
                access_adjustment = 1
                break
    
    # Calculate final score (clamped to 1-5)
    return max(1, min(5, base_score + component_adjustment + access_adjustment))

def analyze_threat_feasibility(
    threat_name: str, 
    threat_description: str,
    component_type: str,
    interfaces: List[str],
    access_points: List[str],
    location: str,
    safety_level: str
) -> AttackerAssessment:
    """Analyze the feasibility of a threat based on component attributes"""
    
    # Determine relevant attacker profiles
    profiles = {}
    threat_lower = (threat_name + " " + threat_description).lower()
    
    # Look for keywords suggesting different attacker profiles
    profile_keywords = {
        AttackerProfile.HOBBYIST: ['hobbyist', 'amateur', 'enthusiast', 'easy', 'simple', 'script kiddie'],
        AttackerProfile.CRIMINAL: ['criminal', 'financial', 'profit', 'ransom', 'monetize', 'black market'],
        AttackerProfile.HACKTIVIST: ['hacktivist', 'activist', 'political', 'protest', 'statement', 'public'],
        AttackerProfile.INSIDER: ['insider', 'employee', 'contractor', 'internal', 'privileged', 'access'],
        AttackerProfile.APT: ['apt', 'nation', 'state', 'sophisticated', 'persistent', 'advanced', 'targeted']
    }
    
    # Score each profile based on keyword relevance
    for profile, keywords in profile_keywords.items():
        matches = sum(keyword in threat_lower for keyword in keywords)
        if matches > 0:
            relevance = min(5, 1 + matches)
        else:
            # Default relevance based on threat characteristics
            if profile == AttackerProfile.APT and ('firmware' in threat_lower or 'critical' in threat_lower):
                relevance = 3
            elif profile == AttackerProfile.CRIMINAL and ('data' in threat_lower or 'theft' in threat_lower):
                relevance = 4
            elif profile == AttackerProfile.INSIDER and ('internal' in threat_lower or 'privileged' in threat_lower):
                relevance = 3
            elif profile == AttackerProfile.HOBBYIST and ('scan' in threat_lower or 'probe' in threat_lower):
                relevance = 3
            else:
                relevance = 2
        
        profiles[profile] = relevance
    
    # Calculate technical capability required
    interface_complexity = get_interface_complexity(interfaces)
    
    # Calculate knowledge required based on safety level and component type
    safety_knowledge_map = {
        'QM': 2,
        'ASIL A': 2,
        'ASIL B': 3,
        'ASIL C': 4,
        'ASIL D': 5
    }
    knowledge_required = safety_knowledge_map.get(safety_level, 3)
    
    # Assess resources needed
    resources_needed = 3  # Default medium
    if 'hardware' in threat_lower or 'physical' in threat_lower:
        resources_needed = 4
    elif 'specialized' in threat_lower or 'custom' in threat_lower:
        resources_needed = 5
    elif 'software' in threat_lower or 'remote' in threat_lower:
        resources_needed = 2
        
    # Calculate accessibility based on location, type, and access points
    accessibility = get_component_accessibility(component_type, location, access_points)
    
    # Time required is inversely related to accessibility
    time_required = 6 - accessibility
    
    # Determine top attacker profile
    top_profile = max(profiles.items(), key=lambda x: x[1])[0]
    
    # Get baseline capabilities for top profile
    baseline_capabilities = get_profile_capabilities(top_profile)
    
    # Create feasibility score
    feasibility = FeasibilityScore(
        technical_capability=min(5, interface_complexity + 1),
        knowledge_required=knowledge_required,
        resources_needed=resources_needed,
        time_required=time_required
    )
    
    # Generate mitigating and enabling factors
    mitigating_factors = []
    enabling_factors = []
    
    # Add mitigating factors
    if knowledge_required >= 4:
        mitigating_factors.append("Requires specialized knowledge of automotive systems")
    if resources_needed >= 4:
        mitigating_factors.append("Requires significant resources or specialized equipment")
    if time_required >= 4:
        mitigating_factors.append("Requires extended time for exploitation")
    if "ASIL" in safety_level and "D" in safety_level:
        mitigating_factors.append("Protected by ASIL D safety mechanisms")
    if location.lower() == "internal" and not access_points:
        mitigating_factors.append("Limited physical accessibility")
        
    # Add enabling factors
    if feasibility.technical_capability <= 2:
        enabling_factors.append("Low technical capability required")
    if accessibility >= 4:
        enabling_factors.append("Easily accessible component or interface")
    if location.lower() == "external":
        enabling_factors.append("Externally exposed component")
    if any("debug" in ap.lower() for ap in access_points):
        enabling_factors.append("Debug interfaces present")
    if any("can" in intf.lower() for intf in interfaces):
        enabling_factors.append("Uses CAN protocol with limited security")
    
    # Ensure at least one factor in each category
    if not mitigating_factors:
        mitigating_factors.append("Standard security controls may be sufficient")
    if not enabling_factors:
        enabling_factors.append("Standard attack vectors apply")
    
    # Create assessment
    assessment = AttackerAssessment(
        profiles=profiles,
        feasibility=feasibility,
        mitigating_factors=mitigating_factors,
        enabling_factors=enabling_factors
    )
    
    return assessment

def assess_all_component_threats(component_data: Dict[str, Any]) -> Dict[str, AttackerAssessment]:
    """Analyze feasibility for all threats associated with a component"""
    result = {}
    
    component_type = component_data.get('type', '')
    safety_level = component_data.get('safety_level', '')
    interfaces = component_data.get('interfaces', [])
    access_points = component_data.get('access_points', [])
    location = component_data.get('location', 'Internal')
    threats = component_data.get('threats', [])
    
    for threat in threats:
        threat_name = threat.get('name', '')
        threat_description = threat.get('description', '')
        
        assessment = analyze_threat_feasibility(
            threat_name,
            threat_description,
            component_type,
            interfaces,
            access_points,
            location,
            safety_level
        )
        
        result[threat_name] = assessment
    
    return result

def format_feasibility_assessment(assessment: AttackerAssessment) -> str:
    """Format feasibility assessment for display in reports"""
    result = []
    
    # Overall feasibility
    result.append(f"Overall Feasibility: {assessment.feasibility.feasibility_level} ({assessment.feasibility.overall_score}/5)")
    
    # Key factors
    result.append("Key Factors:")
    result.append(f"- Technical Capability Required: {assessment.feasibility.technical_capability}/5")
    result.append(f"- Knowledge Required: {assessment.feasibility.knowledge_required}/5")
    result.append(f"- Resources Needed: {assessment.feasibility.resources_needed}/5")
    result.append(f"- Time Required: {assessment.feasibility.time_required}/5")
    
    # Top attacker profiles
    result.append("\nMost Relevant Attacker Profiles:")
    top_profiles = sorted(assessment.profiles.items(), key=lambda x: x[1], reverse=True)[:2]
    for profile, score in top_profiles:
        result.append(f"- {profile.value}: {score}/5 relevance")
    
    # Enabling/Mitigating factors
    if assessment.enabling_factors:
        result.append("\nEnabling Factors:")
        for factor in assessment.enabling_factors:
            result.append(f"- {factor}")
    
    if assessment.mitigating_factors:
        result.append("\nMitigating Factors:")
        for factor in assessment.mitigating_factors:
            result.append(f"- {factor}")
    
    return "\n".join(result)
