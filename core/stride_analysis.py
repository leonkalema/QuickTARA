"""
STRIDE Analysis Module for QuickTARA
Handles STRIDE categorization and recommendations
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional

class StrideCategory(Enum):
    SPOOFING = "spoofing"
    TAMPERING = "tampering"
    REPUDIATION = "repudiation"
    INFO_DISCLOSURE = "info_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"
    ELEVATION = "elevation_of_privilege"

@dataclass
class StrideAnalysis:
    categories: Set[StrideCategory]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "categories": [c.value for c in self.categories],
            "recommendations": self.recommendations
        }

def analyze_stride_categories(component_type: str, interfaces: List[str], 
                            access_points: List[str], data_types: List[str],
                            trust_zone: str) -> Set[StrideCategory]:
    """Analyze component attributes to determine applicable STRIDE categories"""
    categories = set()
    
    # Spoofing analysis
    if any(i in ["CAN", "FlexRay", "Ethernet", "WiFi", "4G"] for i in interfaces):
        categories.add(StrideCategory.SPOOFING)
    if any(ap in ["OBD-II", "Debug Port", "USB"] for ap in access_points):
        categories.add(StrideCategory.SPOOFING)
    
    # Tampering analysis
    if "External" in trust_zone or trust_zone == "Untrusted":
        categories.add(StrideCategory.TAMPERING)
    if any(dt in ["Control Commands", "Configuration"] for dt in data_types):
        categories.add(StrideCategory.TAMPERING)
    
    # Repudiation analysis
    if component_type in ["Gateway", "ECU"]:
        categories.add(StrideCategory.REPUDIATION)
    if any(dt in ["Diagnostic Data", "Telemetry"] for dt in data_types):
        categories.add(StrideCategory.REPUDIATION)
    
    # Information Disclosure analysis
    if any(dt in ["Sensor Data", "Diagnostic Data", "Telemetry"] for dt in data_types):
        categories.add(StrideCategory.INFO_DISCLOSURE)
    if trust_zone in ["Boundary", "Untrusted"]:
        categories.add(StrideCategory.INFO_DISCLOSURE)
    
    # Denial of Service analysis
    if component_type in ["Gateway", "Network"]:
        categories.add(StrideCategory.DENIAL_OF_SERVICE)
    if any(i in ["CAN", "FlexRay", "Ethernet"] for i in interfaces):
        categories.add(StrideCategory.DENIAL_OF_SERVICE)
    
    # Elevation of Privilege analysis
    if any(ap in ["OBD-II", "Debug Port", "USB"] for ap in access_points):
        categories.add(StrideCategory.ELEVATION)
    if trust_zone in ["Critical", "Boundary"]:
        categories.add(StrideCategory.ELEVATION)
    
    return categories

def get_stride_recommendations(categories: Set[StrideCategory], 
                             component_type: str,
                             safety_level: str) -> List[str]:
    """Get security recommendations based on STRIDE categories"""
    recommendations = []
    
    if StrideCategory.SPOOFING in categories:
        recommendations.extend([
            "Implement strong authentication mechanisms",
            "Use secure key storage",
            "Validate message authenticity"
        ])
        if safety_level in ["ASIL C", "ASIL D"]:
            recommendations.append("Implement hardware-based authentication")
    
    if StrideCategory.TAMPERING in categories:
        recommendations.extend([
            "Implement integrity checks",
            "Use secure boot mechanisms",
            "Validate all inputs"
        ])
        if component_type == "ECU":
            recommendations.append("Implement secure firmware update procedures")
    
    if StrideCategory.REPUDIATION in categories:
        recommendations.extend([
            "Implement secure logging",
            "Use cryptographic signatures",
            "Maintain audit trails"
        ])
        if safety_level in ["ASIL C", "ASIL D"]:
            recommendations.append("Use hardware security modules for logging")
    
    if StrideCategory.INFO_DISCLOSURE in categories:
        recommendations.extend([
            "Encrypt sensitive data",
            "Implement access controls",
            "Minimize data exposure"
        ])
        if "Diagnostic Data" in component_type:
            recommendations.append("Implement session-based access control")
    
    if StrideCategory.DENIAL_OF_SERVICE in categories:
        recommendations.extend([
            "Implement rate limiting",
            "Use redundancy mechanisms",
            "Monitor resource usage"
        ])
        if component_type == "Gateway":
            recommendations.append("Implement traffic prioritization")
    
    if StrideCategory.ELEVATION in categories:
        recommendations.extend([
            "Implement principle of least privilege",
            "Use secure session management",
            "Validate authorization for all operations"
        ])
        if safety_level in ["ASIL C", "ASIL D"]:
            recommendations.append("Implement hardware-based access control")
    
    return recommendations

def format_stride_analysis(analysis: StrideAnalysis) -> str:
    """Format STRIDE analysis results for display"""
    result = []
    
    if analysis.categories:
        result.append("STRIDE Categories:")
        for category in analysis.categories:
            result.append(f"- {category.value.replace('_', ' ').title()}")
    
    if analysis.recommendations:
        result.append("\nRecommendations:")
        for rec in analysis.recommendations:
            result.append(f"- {rec}")
    
    return "\n".join(result)
