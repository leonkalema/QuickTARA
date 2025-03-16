"""
Compliance Mappings Module for QuickTARA
Maps threats to ISO 26262 and UN R155 requirements
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional

class ComplianceType(Enum):
    ISO_26262 = "ISO 26262"
    UN_R155 = "UN R155"

@dataclass
class ComplianceRequirement:
    standard: ComplianceType
    section: str
    title: str
    description: str
    
    def to_dict(self) -> Dict:
        return {
            "standard": self.standard.value,
            "section": self.section,
            "title": self.title,
            "description": self.description
        }

# ISO 26262 Requirements Database
ISO_26262_REQUIREMENTS = {
    "ASIL D": {
        "4-6": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "4-6",
            "Item integration and testing",
            "Requirements for integration testing of the item including hardware-software integration"
        ),
        "4-7": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "4-7",
            "Safety validation",
            "Requirements for safety validation of the item"
        ),
        "6-7": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "6-7",
            "Safety mechanisms",
            "Requirements for safety mechanisms including diagnostic coverage"
        ),
        "6-8": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "6-8",
            "Safety analysis",
            "Requirements for safety analysis of the hardware design"
        )
    },
    "ASIL C": {
        "4-6": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "4-6",
            "Item integration and testing",
            "Requirements for integration testing with reduced rigor compared to ASIL D"
        ),
        "6-7": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "6-7",
            "Safety mechanisms",
            "Requirements for safety mechanisms with reduced diagnostic coverage"
        )
    },
    "ASIL B": {
        "4-6": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "4-6",
            "Item integration and testing",
            "Basic requirements for integration testing"
        ),
        "6-7": ComplianceRequirement(
            ComplianceType.ISO_26262,
            "6-7",
            "Safety mechanisms",
            "Basic requirements for safety mechanisms"
        )
    }
}

# UN R155 Requirements Database
UN_R155_REQUIREMENTS = {
    "Critical": {
        "7.3.1": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.1",
            "Security critical elements",
            "Requirements for protection of security critical elements"
        ),
        "7.3.2": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.2",
            "Risk assessment",
            "Requirements for risk assessment methodology"
        ),
        "7.3.3": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.3",
            "Security controls",
            "Requirements for security controls implementation"
        ),
        "7.3.4": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.4",
            "Security testing",
            "Requirements for security testing and validation"
        )
    },
    "Boundary": {
        "7.3.3": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.3",
            "Security controls",
            "Requirements for security controls at trust boundaries"
        ),
        "7.3.5": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.5",
            "Data protection",
            "Requirements for protection of sensitive data"
        )
    },
    "Standard": {
        "7.3.6": ComplianceRequirement(
            ComplianceType.UN_R155,
            "7.3.6",
            "Monitoring and response",
            "Requirements for security monitoring and incident response"
        )
    }
}

def map_threat_to_standards(threat_type: str, safety_level: str, 
                          trust_zone: str) -> List[ComplianceRequirement]:
    """Map threat to relevant ISO 26262 and UN R155 requirements"""
    requirements = []
    
    # Map ISO 26262 requirements based on ASIL level
    if safety_level.startswith("ASIL"):
        if safety_level in ISO_26262_REQUIREMENTS:
            requirements.extend(ISO_26262_REQUIREMENTS[safety_level].values())
    
    # Map UN R155 requirements based on trust zone
    if trust_zone in UN_R155_REQUIREMENTS:
        requirements.extend(UN_R155_REQUIREMENTS[trust_zone].values())
    
    # Add specific requirements based on threat type
    if threat_type == "CAN Injection":
        if safety_level in ["ASIL C", "ASIL D"]:
            requirements.append(
                ComplianceRequirement(
                    ComplianceType.UN_R155,
                    "7.3.7",
                    "Network security",
                    "Requirements for securing vehicle internal networks"
                )
            )
    elif threat_type == "ECU Firmware Tampering":
        if safety_level in ["ASIL C", "ASIL D"]:
            requirements.append(
                ComplianceRequirement(
                    ComplianceType.UN_R155,
                    "7.3.8",
                    "Software security",
                    "Requirements for securing ECU software and firmware"
                )
            )
    elif threat_type == "Sensor Data Manipulation":
        if safety_level in ["ASIL C", "ASIL D"]:
            requirements.append(
                ComplianceRequirement(
                    ComplianceType.UN_R155,
                    "7.3.9",
                    "Sensor security",
                    "Requirements for securing vehicle sensors and their data"
                )
            )
    
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
        result.append(f"\n{standard.value} Requirements:")
        for req in reqs:
            result.append(f"- Section {req.section}: {req.title}")
            result.append(f"  {req.description}")
    
    return "\n".join(result)
