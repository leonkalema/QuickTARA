#!/usr/bin/env python3
"""
Populate QuickTARA database with realistic automotive ECU data:
- 9 realistic assets
- 50 realistic damage scenarios
- Realistic threat scenarios linked to damage scenarios
"""

import sqlite3
import uuid
from datetime import datetime
import json

def generate_id(prefix=""):
    """Generate a unique ID with optional prefix"""
    return f"{prefix}{str(uuid.uuid4()).upper()[:8]}"

def create_realistic_assets(cursor):
    """Create 9 realistic automotive ECU assets"""
    
    # First, get or create a product scope (ECU)
    scope_id = "ECU-" + str(uuid.uuid4()).upper()[:8]
    cursor.execute("""
        INSERT INTO product_scopes (
            scope_id, name, product_type, description, safety_level, 
            interfaces, access_points, location, trust_zone, boundaries,
            objectives, stakeholders, version, is_current, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scope_id,
        "DCC3 Engine Control Unit",
        "ECU",
        "Main engine control unit responsible for fuel injection, ignition timing, and emissions control",
        "ASIL D",
        json.dumps(["CAN-H", "CAN-L", "OBD-II", "Ethernet", "LIN"]),
        json.dumps(["Diagnostic Port", "CAN Bus", "Flash Programming Interface"]),
        "Engine Bay",
        "Critical",
        json.dumps(["Physical Boundary", "Network Boundary", "Logical Boundary"]),
        json.dumps(["Engine Performance", "Emissions Compliance", "Safety"]),
        json.dumps(["OEM", "Tier1 Supplier", "Service Technician", "End User"]),
        1,
        True,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    assets = [
        {
            "name": "Engine Control Firmware",
            "description": "Core firmware controlling engine operations, fuel injection timing, and ignition control",
            "asset_type": "Firmware",
            "data_types": ["Control Parameters", "Calibration Data", "Executable Code"],
            "storage_location": "Flash Memory",
            "confidentiality": "High",
            "integrity": "High", 
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Diagnostic Software Module",
            "description": "Software module handling OBD-II diagnostics and fault code management",
            "asset_type": "Software",
            "data_types": ["Diagnostic Trouble Codes", "Sensor Data", "Test Results"],
            "storage_location": "EEPROM",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Calibration Parameters",
            "description": "Engine calibration data including fuel maps, timing curves, and emission control parameters",
            "asset_type": "Calibration",
            "data_types": ["Fuel Maps", "Timing Tables", "Emission Parameters"],
            "storage_location": "Calibration Memory",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "CAN Communication Interface",
            "description": "Hardware and software interface for CAN bus communication with other ECUs",
            "asset_type": "Communication",
            "data_types": ["CAN Messages", "Network Data", "Control Signals"],
            "storage_location": "CAN Controller",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": False,
            "authorization_required": False
        },
        {
            "name": "Security Key Storage",
            "description": "Secure storage for cryptographic keys used for authentication and secure communication",
            "asset_type": "Data",
            "data_types": ["Private Keys", "Certificates", "Authentication Tokens"],
            "storage_location": "Hardware Security Module",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Flash Programming Interface",
            "description": "Interface used for firmware updates and reprogramming during manufacturing and service",
            "asset_type": "Interface",
            "data_types": ["Programming Commands", "Firmware Images", "Verification Data"],
            "storage_location": "Programming Port",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "Low",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Sensor Data Processing Unit",
            "description": "Hardware component processing inputs from various engine sensors",
            "asset_type": "Hardware",
            "data_types": ["Sensor Readings", "Processed Values", "Status Information"],
            "storage_location": "Microcontroller",
            "confidentiality": "Low",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": False,
            "authorization_required": False
        },
        {
            "name": "Boot Loader",
            "description": "Initial boot code responsible for system startup and firmware verification",
            "asset_type": "Firmware",
            "data_types": ["Boot Code", "Verification Routines", "System Configuration"],
            "storage_location": "Boot ROM",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Configuration Database",
            "description": "Database storing ECU configuration, variant coding, and personalization data",
            "asset_type": "Configuration",
            "data_types": ["Configuration Parameters", "Variant Data", "Personalization Settings"],
            "storage_location": "Non-volatile Memory",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": False,
            "authorization_required": True
        }
    ]
    
    asset_ids = []
    for asset in assets:
        asset_id = "AS-" + generate_id()
        asset_ids.append(asset_id)
        
        cursor.execute("""
            INSERT INTO assets (
                asset_id, name, description, asset_type, data_types, storage_location,
                scope_id, scope_version, confidentiality, integrity, availability,
                authenticity_required, authorization_required, version, is_current,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_id,
            asset["name"],
            asset["description"],
            asset["asset_type"],
            json.dumps(asset["data_types"]),
            asset["storage_location"],
            scope_id,
            1,
            asset["confidentiality"],
            asset["integrity"],
            asset["availability"],
            asset["authenticity_required"],
            asset["authorization_required"],
            1,
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    print(f"Created {len(assets)} realistic assets for scope: {scope_id}")
    return scope_id, asset_ids

def create_realistic_damage_scenarios(cursor, scope_id, asset_ids):
    """Create 50 realistic damage scenarios"""
    
    damage_scenarios = [
        # Firmware-related scenarios
        {"name": "Malicious Firmware Injection", "description": "Unauthorized firmware modification leading to engine malfunction", "category": "Integrity Violation", "assets": [0, 7], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Firmware Corruption", "description": "Firmware corruption causing engine control failure", "category": "Availability Violation", "assets": [0], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Bootloader Compromise", "description": "Bootloader manipulation allowing persistent malware installation", "category": "Integrity Violation", "assets": [7], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Unauthorized Firmware Access", "description": "Unauthorized reading of proprietary firmware code", "category": "Confidentiality Violation", "assets": [0], "safety": "negligible", "financial": "major", "operational": "minor", "privacy": "negligible"},
        {"name": "Firmware Rollback Attack", "description": "Downgrade to vulnerable firmware version", "category": "Integrity Violation", "assets": [0, 7], "safety": "moderate", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        
        # Calibration-related scenarios  
        {"name": "Calibration Data Theft", "description": "Unauthorized extraction of proprietary calibration parameters", "category": "Confidentiality Violation", "assets": [2], "safety": "negligible", "financial": "major", "operational": "minor", "privacy": "negligible"},
        {"name": "Calibration Tampering", "description": "Modification of calibration data to alter engine performance", "category": "Integrity Violation", "assets": [2], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Emissions Defeat", "description": "Calibration modification to bypass emissions controls", "category": "Integrity Violation", "assets": [2], "safety": "moderate", "financial": "major", "operational": "moderate", "privacy": "negligible"},
        {"name": "Performance Tuning Abuse", "description": "Unauthorized performance enhancement causing engine damage", "category": "Integrity Violation", "assets": [2], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Calibration Data Loss", "description": "Loss of calibration data causing engine malfunction", "category": "Availability Violation", "assets": [2], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        
        # Communication-related scenarios
        {"name": "CAN Bus Message Injection", "description": "Injection of malicious CAN messages causing system malfunction", "category": "Integrity Violation", "assets": [3], "safety": "major", "financial": "minor", "operational": "major", "privacy": "negligible"},
        {"name": "CAN Bus Flooding", "description": "DoS attack flooding CAN bus with messages", "category": "Availability Violation", "assets": [3], "safety": "moderate", "financial": "minor", "operational": "major", "privacy": "negligible"},
        {"name": "Message Replay Attack", "description": "Replay of captured CAN messages at inappropriate times", "category": "Integrity Violation", "assets": [3], "safety": "moderate", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        {"name": "Network Eavesdropping", "description": "Unauthorized monitoring of CAN bus communications", "category": "Confidentiality Violation", "assets": [3], "safety": "negligible", "financial": "minor", "operational": "minor", "privacy": "moderate"},
        {"name": "Communication Jamming", "description": "RF jamming preventing CAN communication", "category": "Availability Violation", "assets": [3], "safety": "moderate", "financial": "minor", "operational": "major", "privacy": "negligible"},
        
        # Security key scenarios
        {"name": "Cryptographic Key Extraction", "description": "Unauthorized extraction of private keys from secure storage", "category": "Confidentiality Violation", "assets": [4], "safety": "minor", "financial": "major", "operational": "moderate", "privacy": "moderate"},
        {"name": "Key Storage Corruption", "description": "Corruption of cryptographic key storage", "category": "Availability Violation", "assets": [4], "safety": "minor", "financial": "moderate", "operational": "major", "privacy": "minor"},
        {"name": "Certificate Forgery", "description": "Creation of fraudulent certificates using compromised keys", "category": "Integrity Violation", "assets": [4], "safety": "minor", "financial": "major", "operational": "moderate", "privacy": "moderate"},
        {"name": "Authentication Bypass", "description": "Bypass of authentication mechanisms", "category": "Integrity Violation", "assets": [4], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "moderate"},
        {"name": "Key Compromise", "description": "Compromise of master encryption keys", "category": "Confidentiality Violation", "assets": [4], "safety": "minor", "financial": "major", "operational": "major", "privacy": "major"},
        
        # Programming interface scenarios
        {"name": "Unauthorized Firmware Update", "description": "Installation of unauthorized firmware via programming interface", "category": "Integrity Violation", "assets": [5, 0], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Programming Interface Abuse", "description": "Misuse of programming interface for unauthorized access", "category": "Integrity Violation", "assets": [5], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "minor"},
        {"name": "Flash Memory Corruption", "description": "Corruption of flash memory during programming", "category": "Availability Violation", "assets": [5, 0], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Programming Tool Compromise", "description": "Compromise of external programming tools", "category": "Integrity Violation", "assets": [5], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "minor"},
        {"name": "Unauthorized Memory Access", "description": "Unauthorized reading of memory contents via programming interface", "category": "Confidentiality Violation", "assets": [5], "safety": "negligible", "financial": "major", "operational": "minor", "privacy": "minor"},
        
        # Sensor data scenarios
        {"name": "Sensor Data Manipulation", "description": "Manipulation of sensor inputs causing incorrect engine control", "category": "Integrity Violation", "assets": [6], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Sensor Spoofing", "description": "Injection of false sensor data", "category": "Integrity Violation", "assets": [6], "safety": "major", "financial": "minor", "operational": "major", "privacy": "negligible"},
        {"name": "Sensor Data Loss", "description": "Loss of critical sensor data causing system failure", "category": "Availability Violation", "assets": [6], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Sensor Calibration Attack", "description": "Manipulation of sensor calibration parameters", "category": "Integrity Violation", "assets": [6], "safety": "moderate", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        {"name": "Sensor Hardware Failure", "description": "Physical damage to sensor processing hardware", "category": "Availability Violation", "assets": [6], "safety": "moderate", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        
        # Diagnostic scenarios
        {"name": "Diagnostic Data Theft", "description": "Unauthorized access to diagnostic data and fault codes", "category": "Confidentiality Violation", "assets": [1], "safety": "negligible", "financial": "minor", "operational": "minor", "privacy": "moderate"},
        {"name": "Fault Code Manipulation", "description": "Modification or deletion of diagnostic fault codes", "category": "Integrity Violation", "assets": [1], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "negligible"},
        {"name": "Diagnostic System Disable", "description": "Disabling of diagnostic monitoring systems", "category": "Availability Violation", "assets": [1], "safety": "moderate", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "False Diagnostic Reports", "description": "Generation of false diagnostic information", "category": "Integrity Violation", "assets": [1], "safety": "minor", "financial": "moderate", "operational": "moderate", "privacy": "negligible"},
        {"name": "Diagnostic Interface Abuse", "description": "Misuse of diagnostic interface for unauthorized access", "category": "Integrity Violation", "assets": [1], "safety": "minor", "financial": "minor", "operational": "moderate", "privacy": "minor"},
        
        # Configuration scenarios
        {"name": "Configuration Tampering", "description": "Unauthorized modification of ECU configuration parameters", "category": "Integrity Violation", "assets": [8], "safety": "moderate", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        {"name": "Variant Coding Abuse", "description": "Unauthorized activation of premium features", "category": "Integrity Violation", "assets": [8], "safety": "minor", "financial": "major", "operational": "minor", "privacy": "negligible"},
        {"name": "Configuration Data Loss", "description": "Loss of configuration data causing system malfunction", "category": "Availability Violation", "assets": [8], "safety": "moderate", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Personalization Data Theft", "description": "Unauthorized access to user personalization data", "category": "Confidentiality Violation", "assets": [8], "safety": "negligible", "financial": "minor", "operational": "minor", "privacy": "major"},
        {"name": "Configuration Rollback", "description": "Unauthorized rollback to previous configuration", "category": "Integrity Violation", "assets": [8], "safety": "minor", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        
        # Multi-asset scenarios
        {"name": "Complete System Compromise", "description": "Full compromise of ECU leading to total control loss", "category": "Multi-Domain Violation", "assets": [0, 1, 2, 3, 4], "safety": "catastrophic", "financial": "major", "operational": "catastrophic", "privacy": "major"},
        {"name": "Supply Chain Attack", "description": "Compromise during manufacturing or supply chain", "category": "Integrity Violation", "assets": [0, 2, 4], "safety": "major", "financial": "major", "operational": "major", "privacy": "moderate"},
        {"name": "Insider Threat", "description": "Malicious actions by authorized personnel", "category": "Multi-Domain Violation", "assets": [0, 2, 5, 8], "safety": "major", "financial": "major", "operational": "major", "privacy": "major"},
        {"name": "Advanced Persistent Threat", "description": "Long-term stealthy compromise of multiple systems", "category": "Multi-Domain Violation", "assets": [0, 1, 3, 4], "safety": "major", "financial": "major", "operational": "major", "privacy": "major"},
        {"name": "Physical Tampering", "description": "Physical access leading to hardware and software compromise", "category": "Multi-Domain Violation", "assets": [0, 4, 5, 6], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "moderate"},
        
        # Additional specific scenarios
        {"name": "Memory Exhaustion Attack", "description": "DoS attack causing memory exhaustion", "category": "Availability Violation", "assets": [0, 1], "safety": "moderate", "financial": "minor", "operational": "major", "privacy": "negligible"},
        {"name": "Timing Attack", "description": "Side-channel attack exploiting timing variations", "category": "Confidentiality Violation", "assets": [4], "safety": "negligible", "financial": "moderate", "operational": "minor", "privacy": "minor"},
        {"name": "Power Analysis Attack", "description": "Side-channel attack using power consumption analysis", "category": "Confidentiality Violation", "assets": [4], "safety": "negligible", "financial": "moderate", "operational": "minor", "privacy": "minor"},
        {"name": "Electromagnetic Interference", "description": "EMI causing system malfunction", "category": "Availability Violation", "assets": [3, 6], "safety": "moderate", "financial": "minor", "operational": "moderate", "privacy": "negligible"},
        {"name": "Temperature Attack", "description": "Extreme temperature causing system failure", "category": "Availability Violation", "assets": [0, 6], "safety": "moderate", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Voltage Glitching", "description": "Power supply manipulation causing security bypass", "category": "Integrity Violation", "assets": [4, 7], "safety": "minor", "financial": "moderate", "operational": "moderate", "privacy": "minor"},
        {"name": "Clock Glitching", "description": "Clock manipulation causing instruction skipping", "category": "Integrity Violation", "assets": [0, 7], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "minor"}
    ]
    
    scenario_ids = []
    for i, scenario in enumerate(damage_scenarios):
        scenario_id = "DS-" + generate_id()
        scenario_ids.append(scenario_id)
        
        # Map affected asset indices to actual asset IDs
        affected_asset_ids = [asset_ids[idx] for idx in scenario["assets"]]
        
        cursor.execute("""
            INSERT INTO damage_scenarios (
                scenario_id, name, description, scope_id, violated_properties,
                category, damage_category, impact_type, severity,
                confidentiality_impact, integrity_impact, availability_impact,
                safety_impact, financial_impact, operational_impact, privacy_impact,
                version, is_current, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scenario_id,
            scenario["name"],
            scenario["description"],
            scope_id,
            json.dumps(["Confidentiality", "Integrity", "Availability"]),
            scenario["category"],
            scenario["category"],  # Legacy field
            "Direct",
            "High",
            "Confidentiality" in scenario["category"],
            "Integrity" in scenario["category"],
            "Availability" in scenario["category"],
            scenario["safety"],
            scenario["financial"],
            scenario["operational"],
            scenario["privacy"],
            1,
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Link damage scenario to affected assets
        for asset_id in affected_asset_ids:
            cursor.execute("""
                INSERT INTO asset_damage_scenario (asset_id, scenario_id)
                VALUES (?, ?)
            """, (asset_id, scenario_id))
    
    print(f"Created {len(damage_scenarios)} realistic damage scenarios")
    return scenario_ids

def create_realistic_threat_scenarios(cursor, scope_id, damage_scenario_ids):
    """Create realistic threat scenarios linked to damage scenarios"""
    
    threat_scenarios = [
        # Remote attacks
        {"name": "Remote Code Execution via OBD-II", "description": "Exploiting OBD-II interface vulnerabilities to execute arbitrary code", "attack_vector": "Network", "damage_scenarios": [0, 1, 20, 21]},
        {"name": "CAN Bus Injection Attack", "description": "Injecting malicious CAN messages from compromised ECU", "attack_vector": "Network", "damage_scenarios": [10, 11, 12]},
        {"name": "Wireless Key Fob Replay", "description": "Capturing and replaying wireless authentication signals", "attack_vector": "Wireless", "damage_scenarios": [15, 18]},
        {"name": "Bluetooth Stack Exploitation", "description": "Exploiting vulnerabilities in Bluetooth communication stack", "attack_vector": "Wireless", "damage_scenarios": [13, 39]},
        {"name": "Cellular Modem Compromise", "description": "Compromising cellular connectivity for remote access", "attack_vector": "Network", "damage_scenarios": [39, 40, 41]},
        
        # Physical attacks
        {"name": "JTAG Interface Exploitation", "description": "Using JTAG debug interface for unauthorized access", "attack_vector": "Physical", "damage_scenarios": [20, 21, 23, 24]},
        {"name": "Flash Memory Extraction", "description": "Physical extraction of firmware from flash memory", "attack_vector": "Physical", "damage_scenarios": [3, 5, 24]},
        {"name": "Hardware Implant Installation", "description": "Installing malicious hardware during manufacturing", "attack_vector": "Physical", "damage_scenarios": [39, 42]},
        {"name": "Side-Channel Analysis", "description": "Using power/timing analysis to extract cryptographic keys", "attack_vector": "Physical", "damage_scenarios": [15, 44, 45]},
        {"name": "Chip Decapping Attack", "description": "Physical decapping of microcontroller for memory access", "attack_vector": "Physical", "damage_scenarios": [3, 15, 24]},
        
        # Software attacks
        {"name": "Buffer Overflow Exploitation", "description": "Exploiting buffer overflow vulnerabilities in firmware", "attack_vector": "Software", "damage_scenarios": [0, 1, 43]},
        {"name": "Return-Oriented Programming", "description": "ROP attack to bypass security controls", "attack_vector": "Software", "damage_scenarios": [0, 18, 39]},
        {"name": "Heap Spray Attack", "description": "Memory corruption attack targeting heap allocation", "attack_vector": "Software", "damage_scenarios": [1, 43]},
        {"name": "Format String Vulnerability", "description": "Exploiting format string bugs for code execution", "attack_vector": "Software", "damage_scenarios": [0, 1]},
        {"name": "Integer Overflow Exploitation", "description": "Exploiting integer overflow for memory corruption", "attack_vector": "Software", "damage_scenarios": [0, 1, 25, 26]},
        
        # Supply chain attacks
        {"name": "Malicious Firmware Update", "description": "Distributing compromised firmware through update mechanism", "attack_vector": "Supply Chain", "damage_scenarios": [0, 4, 40]},
        {"name": "Compromised Development Tools", "description": "Using compromised development environment to inject malware", "attack_vector": "Supply Chain", "damage_scenarios": [0, 40]},
        {"name": "Third-Party Library Compromise", "description": "Exploiting vulnerabilities in third-party software components", "attack_vector": "Supply Chain", "damage_scenarios": [0, 1, 40]},
        {"name": "Hardware Trojan Insertion", "description": "Inserting malicious hardware during chip manufacturing", "attack_vector": "Supply Chain", "damage_scenarios": [39, 42]},
        {"name": "Counterfeit Component Integration", "description": "Using counterfeit components with hidden functionality", "attack_vector": "Supply Chain", "damage_scenarios": [28, 39, 42]},
        
        # Social engineering
        {"name": "Insider Threat Exploitation", "description": "Malicious actions by authorized personnel", "attack_vector": "Social Engineering", "damage_scenarios": [41, 42]},
        {"name": "Phishing Attack on Developers", "description": "Targeting developers to gain access to development systems", "attack_vector": "Social Engineering", "damage_scenarios": [40, 41]},
        {"name": "Service Technician Compromise", "description": "Compromising service tools and procedures", "attack_vector": "Social Engineering", "damage_scenarios": [20, 21, 22, 34]},
        {"name": "Social Engineering for Physical Access", "description": "Gaining unauthorized physical access through deception", "attack_vector": "Social Engineering", "damage_scenarios": [42]},
        
        # Environmental attacks
        {"name": "Electromagnetic Pulse Attack", "description": "Using EMP to disrupt electronic systems", "attack_vector": "Environmental", "damage_scenarios": [46]},
        {"name": "Temperature Manipulation", "description": "Extreme temperature to cause system malfunction", "attack_vector": "Environmental", "damage_scenarios": [47]},
        {"name": "Vibration-Induced Failure", "description": "Using excessive vibration to cause hardware failure", "attack_vector": "Environmental", "damage_scenarios": [28, 47]},
        {"name": "Humidity Attack", "description": "High humidity causing electronic component failure", "attack_vector": "Environmental", "damage_scenarios": [28, 47]},
        
        # Cryptographic attacks
        {"name": "Weak Random Number Generation", "description": "Exploiting predictable random number generation", "attack_vector": "Cryptographic", "damage_scenarios": [15, 17, 19]},
        {"name": "Certificate Authority Compromise", "description": "Compromising trusted certificate authority", "attack_vector": "Cryptographic", "damage_scenarios": [17, 18]},
        {"name": "Quantum Computing Threat", "description": "Future quantum computers breaking current encryption", "attack_vector": "Cryptographic", "damage_scenarios": [15, 19]},
        {"name": "Hash Collision Attack", "description": "Exploiting hash function weaknesses", "attack_vector": "Cryptographic", "damage_scenarios": [17, 18]},
        
        # Protocol attacks
        {"name": "Man-in-the-Middle Attack", "description": "Intercepting and modifying communications", "attack_vector": "Network", "damage_scenarios": [13, 14]},
        {"name": "Session Hijacking", "description": "Taking over authenticated communication sessions", "attack_vector": "Network", "damage_scenarios": [18, 34]},
        {"name": "DNS Spoofing", "description": "Redirecting network traffic through malicious servers", "attack_vector": "Network", "damage_scenarios": [13, 39]},
        {"name": "ARP Poisoning", "description": "Manipulating ARP tables for traffic interception", "attack_vector": "Network", "damage_scenarios": [13, 14]},
        
        # Timing attacks
        {"name": "Race Condition Exploitation", "description": "Exploiting timing-dependent vulnerabilities", "attack_vector": "Software", "damage_scenarios": [0, 1, 18]},
        {"name": "Time-of-Check Time-of-Use", "description": "TOCTOU attack exploiting timing windows", "attack_vector": "Software", "damage_scenarios": [18, 21]},
        
        # Persistence attacks
        {"name": "Bootkit Installation", "description": "Installing malware in boot process for persistence", "attack_vector": "Software", "damage_scenarios": [2, 4]},
        {"name": "Firmware Rootkit", "description": "Deep firmware-level rootkit for persistent access", "attack_vector": "Software", "damage_scenarios": [0, 2, 39]},
        
        # Data exfiltration
        {"name": "Covert Channel Data Exfiltration", "description": "Using covert channels to steal sensitive data", "attack_vector": "Network", "damage_scenarios": [3, 5, 30, 37]},
        {"name": "Steganographic Data Hiding", "description": "Hiding stolen data in legitimate communications", "attack_vector": "Network", "damage_scenarios": [3, 5, 30]},
        
        # Advanced persistent threats
        {"name": "Multi-Stage APT Campaign", "description": "Sophisticated long-term compromise campaign", "attack_vector": "Multi-Vector", "damage_scenarios": [39, 40, 41, 42]},
        {"name": "Living-off-the-Land Attack", "description": "Using legitimate tools for malicious purposes", "attack_vector": "Software", "damage_scenarios": [39, 41]},
        
        # Zero-day exploits
        {"name": "Unknown Firmware Vulnerability", "description": "Exploiting previously unknown firmware vulnerabilities", "attack_vector": "Software", "damage_scenarios": [0, 1, 39]},
        {"name": "Hardware Design Flaw Exploitation", "description": "Exploiting undiscovered hardware design vulnerabilities", "attack_vector": "Hardware", "damage_scenarios": [28, 39, 42]}
    ]
    
    threat_ids = []
    for threat in threat_scenarios:
        threat_id = "TS-" + generate_id()
        threat_ids.append(threat_id)
        
        # Insert threat scenario (using first damage scenario as primary)
        primary_damage_id = damage_scenario_ids[threat["damage_scenarios"][0]]
        
        cursor.execute("""
            INSERT INTO threat_scenarios (
                threat_scenario_id, name, description, attack_vector,
                damage_scenario_id, scope_id, scope_version, is_deleted, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            threat_id,
            threat["name"],
            threat["description"],
            threat["attack_vector"],
            primary_damage_id,
            scope_id,
            1,
            False,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Link to all related damage scenarios via junction table
        for damage_idx in threat["damage_scenarios"]:
            if damage_idx < len(damage_scenario_ids):
                damage_id = damage_scenario_ids[damage_idx]
                cursor.execute("""
                    INSERT INTO threat_damage_links (threat_scenario_id, damage_scenario_id)
                    VALUES (?, ?)
                """, (threat_id, damage_id))
    
    print(f"Created {len(threat_scenarios)} realistic threat scenarios")
    return threat_ids

def main():
    """Main function to populate the database"""
    
    # Connect to database
    conn = sqlite3.connect('/Users/leonkalema/Dev/QuickTARA/quicktara.db')
    cursor = conn.cursor()
    
    try:
        print("Starting realistic data population...")
        
        # Create assets
        print("\n1. Creating realistic assets...")
        scope_id, asset_ids = create_realistic_assets(cursor)
        
        # Create damage scenarios
        print("\n2. Creating realistic damage scenarios...")
        damage_scenario_ids = create_realistic_damage_scenarios(cursor, scope_id, asset_ids)
        
        # Create threat scenarios
        print("\n3. Creating realistic threat scenarios...")
        threat_ids = create_realistic_threat_scenarios(cursor, scope_id, damage_scenario_ids)
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Successfully populated database with:")
        print(f"   - 1 Product Scope (ECU): {scope_id}")
        print(f"   - {len(asset_ids)} Assets")
        print(f"   - {len(damage_scenario_ids)} Damage Scenarios")
        print(f"   - {len(threat_ids)} Threat Scenarios")
        print(f"   - Multiple asset-damage scenario relationships")
        print(f"   - Multiple threat-damage scenario relationships")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
