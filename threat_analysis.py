"""
Threat Analysis Module for QuickTARA
Handles CAPEC threat loading, impact analysis, and threat-component matching
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional
import csv

class ImpactCategory(Enum):
    FINANCIAL = "financial"
    SAFETY = "safety"
    PRIVACY = "privacy"

@dataclass
class ImpactScore:
    financial: int = 0  # 0-5 scale
    safety: int = 0     # 0-5 scale
    privacy: int = 0    # 0-5 scale
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "financial": self.financial,
            "safety": self.safety,
            "privacy": self.privacy
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'ImpactScore':
        return cls(
            financial=data.get('financial', 0),
            safety=data.get('safety', 0),
            privacy=data.get('privacy', 0)
        )

def analyze_impact_categories(description: str, severity: int) -> ImpactScore:
    """Analyze threat description to determine impact categories"""
    impact = ImpactScore()
    desc_lower = description.lower()
    
    # Financial impact indicators
    financial_keywords = {
        'cost', 'financial', 'monetary', 'revenue', 'profit', 'loss', 'business',
        'economic', 'asset', 'theft', 'fraud', 'ransom', 'warranty', 'repair'
    }
    
    # Safety impact indicators
    safety_keywords = {
        'safety', 'life', 'death', 'injury', 'accident', 'crash', 'physical',
        'emergency', 'health', 'medical', 'critical', 'dangerous', 'hazard',
        'airbag', 'brake', 'steering', 'acceleration', 'speed', 'collision'
    }
    
    # Privacy impact indicators
    privacy_keywords = {
        'privacy', 'confidential', 'personal', 'data', 'information', 'leak',
        'disclosure', 'sensitive', 'private', 'identity', 'credential', 'location',
        'tracking', 'telemetry', 'diagnostic', 'profile', 'user', 'owner'
    }
    
    # Calculate normalized impact scores based on keyword matches
    financial_score = sum(1 for word in financial_keywords if word in desc_lower)
    safety_score = sum(1 for word in safety_keywords if word in desc_lower)
    privacy_score = sum(1 for word in privacy_keywords if word in desc_lower)
    
    # Normalize scores to 0-5 scale using the base severity
    max_score = max(financial_score, safety_score, privacy_score, 1)
    impact.financial = min(5, int((financial_score / max_score) * severity))
    impact.safety = min(5, int((safety_score / max_score) * severity))
    impact.privacy = min(5, int((privacy_score / max_score) * severity))
    
    # Ensure at least one category has the base severity
    if max(impact.financial, impact.safety, impact.privacy) < severity:
        if financial_score >= safety_score and financial_score >= privacy_score:
            impact.financial = severity
        elif safety_score >= privacy_score:
            impact.safety = severity
        else:
            impact.privacy = severity
    
    return impact

def parse_related_patterns(related_str: str) -> Set[str]:
    """Parse CAPEC related attack patterns string into IDs"""
    patterns = set()
    if not related_str:
        return patterns
    
    for relation in related_str.split("::"):
        if "CAPEC ID:" in relation:
            try:
                capec_id = relation.split("CAPEC ID:")[1].strip()
                patterns.add(capec_id)
            except IndexError:
                continue
    return patterns

def load_threats_from_capec(capec_files: List[Path]) -> Dict[str, Dict]:
    """Load and merge threats from multiple CAPEC CSV files"""
    threats = {}
    
    severity_map = {
        'Very High': 5,
        'High': 4,
        'Medium': 3,
        'Low': 2,
        'Very Low': 1
    }
    
    likelihood_map = {
        'High': 4,
        'Medium': 3,
        'Low': 2,
        'Very Low': 1
    }
    
    for file in capec_files:
        try:
            with file.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Name') and row.get('Likelihood Of Attack') and row.get('Typical Severity'):
                        likelihood = likelihood_map.get(row['Likelihood Of Attack'], 2)
                        severity = severity_map.get(row['Typical Severity'], 2)
                        
                        # Analyze impact categories
                        impact = analyze_impact_categories(row.get('Description', ''), severity)
                        
                        threats[row['Name']] = {
                            'id': row.get('ID', ''),
                            'impact': impact.to_dict(),
                            'likelihood': likelihood,
                            'description': row.get('Description', ''),
                            'mitigations': row.get('Mitigations', ''),
                            'related_patterns': row.get('Related Attack Patterns', '')
                        }
        except (csv.Error, IOError) as e:
            print(f"Warning: Could not load CAPEC threats from {file}: {e}")
    
    return threats

# Built-in automotive threat database
AUTOMOTIVE_THREATS = {
    "CAN Injection": {
        "id": "AUTO-001",
        "description": "Manipulation of CAN bus messages leading to vehicle malfunction",
        "impact": {
            "financial": 3,
            "safety": 4,
            "privacy": 2
        },
        "likelihood": 3,
        "mitigations": "Implement message authentication, rate limiting, and anomaly detection",
        "related_patterns": "::NATURE:CanPrecede:CAPEC ID:AUTO-002::"
    },
    "ECU Firmware Tampering": {
        "id": "AUTO-002",
        "description": "Unauthorized modification of ECU firmware causing safety issues",
        "impact": {
            "financial": 4,
            "safety": 5,
            "privacy": 3
        },
        "likelihood": 2,
        "mitigations": "Secure boot, firmware signing, and secure update procedures",
        "related_patterns": "::NATURE:CanPrecede:CAPEC ID:AUTO-003::"
    },
    "Sensor Data Manipulation": {
        "id": "AUTO-003",
        "description": "Tampering with sensor data leading to incorrect vehicle behavior",
        "impact": {
            "financial": 3,
            "safety": 4,
            "privacy": 2
        },
        "likelihood": 3,
        "mitigations": "Data validation, plausibility checks, and sensor fusion",
        "related_patterns": "::NATURE:CanPrecede:CAPEC ID:AUTO-004::"
    },
    "Diagnostic Interface Exploit": {
        "id": "AUTO-004",
        "description": "Exploitation of diagnostic interfaces for unauthorized access",
        "impact": {
            "financial": 4,
            "safety": 3,
            "privacy": 4
        },
        "likelihood": 4,
        "mitigations": "Access control, authentication, and session management",
        "related_patterns": "::NATURE:CanPrecede:CAPEC ID:AUTO-001::"
    },
    "Gateway Compromise": {
        "id": "AUTO-005",
        "description": "Compromise of network gateway leading to unauthorized network access",
        "impact": {
            "financial": 4,
            "safety": 4,
            "privacy": 5
        },
        "likelihood": 3,
        "mitigations": "Network segmentation, firewall rules, and intrusion detection",
        "related_patterns": "::NATURE:CanPrecede:CAPEC ID:AUTO-001::"
    }
}
