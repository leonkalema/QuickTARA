"""
Cybersecurity Goals Module for QuickTARA
Maps threats to cybersecurity goals and requirements
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional, Any

class CybersecurityGoal(Enum):
    CONFIDENTIALITY = "Confidentiality"
    INTEGRITY = "Integrity"
    AVAILABILITY = "Availability"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    NON_REPUDIATION = "Non-Repudiation"
    PRIVACY = "Privacy"
    RESILIENCE = "Resilience"

@dataclass
class GoalMapping:
    goal: CybersecurityGoal
    relevance: int  # 1-5 scale of relevance
    description: str
    requirements: List[str]

def map_threat_to_goals(threat_name: str, threat_description: str, 
                        component_type: str, safety_level: str) -> List[GoalMapping]:
    """Map a threat to relevant cybersecurity goals"""
    mappings = []
    
    # Keywords that indicate different security goals
    goal_keywords = {
        CybersecurityGoal.CONFIDENTIALITY: [
            'confidentiality', 'disclosure', 'leak', 'exposure', 'eavesdropping',
            'sniffing', 'intercept', 'sensitive', 'private'
        ],
        CybersecurityGoal.INTEGRITY: [
            'integrity', 'tamper', 'modify', 'alter', 'corrupt', 'falsify',
            'fabricate', 'manipulation', 'injection'
        ],
        CybersecurityGoal.AVAILABILITY: [
            'availability', 'denial', 'service', 'dos', 'crash', 'overload',
            'flood', 'exhaust', 'resource'
        ],
        CybersecurityGoal.AUTHENTICATION: [
            'authentication', 'identity', 'credential', 'password', 'token',
            'certificate', 'validate', 'verification', 'spoofing'
        ],
        CybersecurityGoal.AUTHORIZATION: [
            'authorization', 'permission', 'privilege', 'access control',
            'elevation', 'privilege'
        ],
        CybersecurityGoal.NON_REPUDIATION: [
            'repudiation', 'audit', 'log', 'trace', 'evidence', 'accountability',
            'tracking', 'non-repudiation'
        ],
        CybersecurityGoal.PRIVACY: [
            'privacy', 'personal', 'tracking', 'profiling', 'gdpr', 'identity theft',
            'location', 'behavior'
        ],
        CybersecurityGoal.RESILIENCE: [
            'resilience', 'recovery', 'backup', 'redundancy', 'fault',
            'tolerance', 'continuity', 'disaster'
        ]
    }
    
    # Predefined requirements for each goal
    goal_requirements = {
        CybersecurityGoal.CONFIDENTIALITY: [
            "Implement data encryption in transit and at rest",
            "Control access to sensitive data",
            "Secure storage and transmission channels"
        ],
        CybersecurityGoal.INTEGRITY: [
            "Validate all input data",
            "Implement integrity checks and digital signatures",
            "Use secure boot mechanisms"
        ],
        CybersecurityGoal.AVAILABILITY: [
            "Implement resource monitoring and rate limiting",
            "Provide redundancy for critical components",
            "Design for fault tolerance and graceful degradation"
        ],
        CybersecurityGoal.AUTHENTICATION: [
            "Implement strong authentication mechanisms",
            "Secure credential storage",
            "Use multi-factor authentication for critical functions"
        ],
        CybersecurityGoal.AUTHORIZATION: [
            "Implement principle of least privilege",
            "Enforce separation of duties",
            "Regular review of access rights"
        ],
        CybersecurityGoal.NON_REPUDIATION: [
            "Implement secure audit logging",
            "Use cryptographic signatures for critical operations",
            "Protect log integrity"
        ],
        CybersecurityGoal.PRIVACY: [
            "Minimize collection and storage of personal data",
            "Implement data anonymization/pseudonymization",
            "Allow user control over personal data"
        ],
        CybersecurityGoal.RESILIENCE: [
            "Implement backup and recovery procedures",
            "Design for graceful degradation under attack",
            "Regular testing of recovery mechanisms"
        ]
    }
    
    # Enhanced requirements based on safety level
    safety_enhancements = {
        "ASIL D": [
            "Use hardware security modules for critical operations",
            "Implement redundant verification mechanisms",
            "Apply defense-in-depth strategies"
        ],
        "ASIL C": [
            "Implement hardware-assisted security features",
            "Use formal verification for critical components"
        ],
        "ASIL B": [
            "Implement comprehensive testing for security functions",
            "Provide fail-safe mechanisms"
        ]
    }
    
    # Component-specific requirements
    component_requirements = {
        "ECU": {
            CybersecurityGoal.INTEGRITY: ["Secure boot process", "Firmware verification"],
            CybersecurityGoal.AUTHENTICATION: ["Secure key storage", "ECU authentication"]
        },
        "Gateway": {
            CybersecurityGoal.CONFIDENTIALITY: ["Network traffic encryption", "Message filtering"],
            CybersecurityGoal.AVAILABILITY: ["Traffic prioritization", "Overload protection"]
        },
        "Sensor": {
            CybersecurityGoal.INTEGRITY: ["Sensor data validation", "Plausibility checks"],
            CybersecurityGoal.AVAILABILITY: ["Signal redundancy", "Degraded mode operation"]
        }
    }
    
    # Analyze threat description and name to determine relevance to each goal
    threat_text = (threat_name + " " + threat_description).lower()
    
    for goal, keywords in goal_keywords.items():
        relevance = 0
        
        # Calculate relevance score based on keyword matches
        for keyword in keywords:
            if keyword in threat_text:
                relevance += 1
        
        # Normalize to 1-5 scale
        if relevance > 0:
            relevance = min(5, 1 + int(relevance * 4 / len(keywords)))
            
            # Build requirements list
            requirements = goal_requirements[goal].copy()
            
            # Add safety level specific requirements
            for safety_key, enhancements in safety_enhancements.items():
                if safety_key in safety_level:
                    requirements.extend(enhancements)
                    break
            
            # Add component-specific requirements
            if component_type in component_requirements and goal in component_requirements[component_type]:
                requirements.extend(component_requirements[component_type][goal])
            
            # Create mapping with customized description
            description = get_goal_description(goal, threat_name, component_type)
            
            mappings.append(GoalMapping(
                goal=goal,
                relevance=relevance,
                description=description,
                requirements=requirements
            ))
    
    # Sort by relevance (highest first)
    mappings.sort(key=lambda m: m.relevance, reverse=True)
    
    # Ensure at least one goal mapping if none found
    if not mappings and threat_name:
        # Default to integrity as fallback
        mappings.append(GoalMapping(
            goal=CybersecurityGoal.INTEGRITY,
            relevance=1,
            description=f"General system integrity protection against {threat_name}",
            requirements=goal_requirements[CybersecurityGoal.INTEGRITY]
        ))
    
    return mappings

def get_goal_description(goal: CybersecurityGoal, threat_name: str, component_type: str) -> str:
    """Generate a contextual description for a cybersecurity goal"""
    descriptions = {
        CybersecurityGoal.CONFIDENTIALITY: f"Protect {component_type} data from unauthorized disclosure during {threat_name}",
        CybersecurityGoal.INTEGRITY: f"Ensure {component_type} data and code integrity against {threat_name}",
        CybersecurityGoal.AVAILABILITY: f"Maintain {component_type} availability and operation during {threat_name}",
        CybersecurityGoal.AUTHENTICATION: f"Verify identity of entities interacting with {component_type} to prevent {threat_name}",
        CybersecurityGoal.AUTHORIZATION: f"Control access to {component_type} functions and resources to mitigate {threat_name}",
        CybersecurityGoal.NON_REPUDIATION: f"Maintain audit trail of {component_type} activities to address {threat_name}",
        CybersecurityGoal.PRIVACY: f"Protect personal data processed by {component_type} from {threat_name}",
        CybersecurityGoal.RESILIENCE: f"Ensure {component_type} can recover and maintain critical functions during {threat_name}"
    }
    
    return descriptions.get(goal, f"Address {threat_name} through appropriate {goal.value} controls")

def format_goal_mappings(mappings: List[GoalMapping]) -> str:
    """Format goal mappings for display in reports"""
    if not mappings:
        return "No specific cybersecurity goals identified."
    
    result = []
    
    # Format each mapping
    for mapping in mappings:
        result.append(f"Goal: {mapping.goal.value} (Relevance: {mapping.relevance}/5)")
        result.append(f"Description: {mapping.description}")
        result.append("Requirements:")
        for req in mapping.requirements[:3]:  # Limit to top 3 requirements
            result.append(f"- {req}")
        result.append("")
    
    return "\n".join(result)

def map_all_component_threats_to_goals(component_data: Dict[str, Any]) -> Dict[str, List[GoalMapping]]:
    """Map all threats for a component to cybersecurity goals"""
    result = {}
    
    component_type = component_data.get('type', '')
    safety_level = component_data.get('safety_level', '')
    threats = component_data.get('threats', [])
    
    for threat in threats:
        threat_name = threat.get('name', '')
        threat_description = threat.get('description', '')
        
        mappings = map_threat_to_goals(
            threat_name, 
            threat_description, 
            component_type, 
            safety_level
        )
        
        if mappings:
            result[threat_name] = mappings
    
    return result
