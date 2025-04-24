"""
Compliance Mappings Module for QuickTARA
Maps threats to ISO 26262 and UN R155 requirements
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

class ComplianceType(Enum):
    ISO_26262 = "ISO 26262"
    UN_R155 = "UN R155"

@dataclass
class ComplianceRequirement:
    standard: str
    requirement: str
    description: str
    
    def to_dict(self) -> Dict:
        return {
            "standard": self.standard,
            "requirement": self.requirement,
            "description": self.description
        }

# ISO 26262 Requirements Database
ISO_26262_REQUIREMENTS = {
    "ASIL D": {
        "4-6": ComplianceRequirement(
            "ISO 26262",
            "4-6",
            "Item integration and testing"
        ),
        "4-7": ComplianceRequirement(
            "ISO 26262",
            "4-7",
            "Safety validation"
        ),
        "6-7": ComplianceRequirement(
            "ISO 26262",
            "6-7",
            "Safety mechanisms"
        ),
        "6-8": ComplianceRequirement(
            "ISO 26262",
            "6-8",
            "Safety analysis"
        )
    },
    "ASIL C": {
        "4-6": ComplianceRequirement(
            "ISO 26262",
            "4-6",
            "Item integration and testing"
        ),
        "6-7": ComplianceRequirement(
            "ISO 26262",
            "6-7",
            "Safety mechanisms"
        )
    },
    "ASIL B": {
        "4-6": ComplianceRequirement(
            "ISO 26262",
            "4-6",
            "Item integration and testing"
        ),
        "6-7": ComplianceRequirement(
            "ISO 26262",
            "6-7",
            "Safety mechanisms"
        )
    }
}

# UN R155 Requirements Database
UN_R155_REQUIREMENTS = {
    "Critical": {
        "7.3.1": ComplianceRequirement(
            "UN R155",
            "7.3.1",
            "Security critical elements"
        ),
        "7.3.2": ComplianceRequirement(
            "UN R155",
            "7.3.2",
            "Risk assessment"
        ),
        "7.3.3": ComplianceRequirement(
            "UN R155",
            "7.3.3",
            "Security controls"
        ),
        "7.3.4": ComplianceRequirement(
            "UN R155",
            "7.3.4",
            "Security testing"
        )
    },
    "Boundary": {
        "7.3.3": ComplianceRequirement(
            "UN R155",
            "7.3.3",
            "Security controls"
        ),
        "7.3.5": ComplianceRequirement(
            "UN R155",
            "7.3.5",
            "Data protection"
        )
    },
    "Standard": {
        "7.3.6": ComplianceRequirement(
            "UN R155",
            "7.3.6",
            "Monitoring and response"
        )
    }
}

def map_threat_to_standards(threat_type: str, safety_level: str, trust_zone: str) -> List[ComplianceRequirement]:
    """Map threats to relevant ISO 26262 and UN R155 requirements"""
    requirements = []
    
    # ISO 26262 mappings based on safety level
    if safety_level == "ASIL D":
        requirements.extend([
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 4-7",
                description="Hardware-software interface specification and verification"
            ),
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 6-8",
                description="Software unit design and implementation"
            )
        ])
    elif safety_level == "ASIL C":
        requirements.extend([
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 4-6",
                description="Technical safety requirements specification"
            ),
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 6-7",
                description="Software architectural design"
            )
        ])
    elif safety_level in ["ASIL B", "ASIL A"]:
        requirements.extend([
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 4-5",
                description="Initiation of product development at the system level"
            ),
            ComplianceRequirement(
                standard="ISO 26262",
                requirement="Part 6-6",
                description="Software safety requirements specification"
            )
        ])
    
    # UN R155 mappings based on trust zone
    if trust_zone == "Critical":
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.1",
                description="Access control for critical vehicle systems"
            ),
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.4",
                description="Security monitoring and incident response"
            )
        ])
    elif trust_zone == "Boundary":
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.2",
                description="Protection of external interfaces"
            ),
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.3",
                description="Security of wireless communications"
            )
        ])
    elif trust_zone == "Standard":
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.2.2.2",
                description="Security controls for vehicle systems"
            )
        ])
    
    # Add threat-specific requirements
    if "injection" in threat_type.lower():
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.8",
                description="Input validation and sanitization"
            )
        ])
    elif "firmware" in threat_type.lower():
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.5",
                description="Software update security"
            )
        ])
    elif "sensor" in threat_type.lower():
        requirements.extend([
            ComplianceRequirement(
                standard="UN R155",
                requirement="7.3.6",
                description="Sensor data integrity"
            )
        ])
    
    return requirements

def format_compliance_mappings(requirements: List[ComplianceRequirement]) -> str:
    """Format compliance requirements for display"""
    if not requirements:
        return "No specific compliance requirements identified."
    
    result = []
    
    # Group by standard
    by_standard = {}
    for req in requirements:
        if req.standard not in by_standard:
            by_standard[req.standard] = []
        by_standard[req.standard].append(req)
    
    # Format each standard's requirements
    for standard, reqs in by_standard.items():
        result.append(f"\n{standard} Requirements:")
        for req in reqs:
            result.append(f"- Requirement {req.requirement}: {req.description}")
    
    return "\n".join(result)
