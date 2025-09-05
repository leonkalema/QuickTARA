#!/usr/bin/env python3
"""
Populate QuickTARA database with realistic automotive data for product_c8833c81:
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

def create_realistic_assets_for_product(cursor, scope_id):
    """Create 9 realistic automotive assets for the existing product"""
    
    assets = [
        {
            "name": "Telematics Control Unit Firmware",
            "description": "Core firmware managing cellular connectivity, GPS navigation, and remote services",
            "asset_type": "Firmware",
            "data_types": ["Control Logic", "Communication Protocols", "Navigation Data"],
            "storage_location": "Flash Memory",
            "confidentiality": "High",
            "integrity": "High", 
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Vehicle Data Gateway",
            "description": "Central gateway processing and routing vehicle data between ECUs and external services",
            "asset_type": "Software",
            "data_types": ["Vehicle Telemetry", "Diagnostic Data", "Usage Statistics"],
            "storage_location": "Secure Processor",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Over-the-Air Update System",
            "description": "System managing secure download and installation of software updates",
            "asset_type": "Software",
            "data_types": ["Update Packages", "Verification Signatures", "Installation Scripts"],
            "storage_location": "Secure Storage",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Infotainment System Database",
            "description": "Database storing user preferences, media content, and application data",
            "asset_type": "Data",
            "data_types": ["User Profiles", "Media Files", "Application Data", "Contact Lists"],
            "storage_location": "Internal Storage",
            "confidentiality": "High",
            "integrity": "Medium",
            "availability": "Medium",
            "authenticity_required": False,
            "authorization_required": True
        },
        {
            "name": "Cellular Communication Module",
            "description": "Hardware and software for 4G/5G cellular connectivity and emergency services",
            "asset_type": "Communication",
            "data_types": ["Network Traffic", "Emergency Calls", "Remote Commands"],
            "storage_location": "Cellular Modem",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "High",
            "authenticity_required": True,
            "authorization_required": False
        },
        {
            "name": "GPS Navigation System",
            "description": "GPS receiver and navigation software providing location services",
            "asset_type": "Hardware",
            "data_types": ["Location Data", "Route Information", "POI Database"],
            "storage_location": "GPS Module",
            "confidentiality": "Medium",
            "integrity": "Medium",
            "availability": "High",
            "authenticity_required": False,
            "authorization_required": False
        },
        {
            "name": "Vehicle Identity Certificate",
            "description": "Digital certificates and keys for vehicle authentication and secure communication",
            "asset_type": "Data",
            "data_types": ["Digital Certificates", "Private Keys", "Vehicle ID"],
            "storage_location": "Hardware Security Module",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "Remote Diagnostic Interface",
            "description": "Interface enabling remote diagnostic access and vehicle health monitoring",
            "asset_type": "Interface",
            "data_types": ["Diagnostic Commands", "Health Reports", "Error Logs"],
            "storage_location": "Diagnostic Port",
            "confidentiality": "Medium",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
            "authorization_required": True
        },
        {
            "name": "User Authentication System",
            "description": "System managing user authentication, profiles, and access control",
            "asset_type": "Software",
            "data_types": ["User Credentials", "Biometric Data", "Access Tokens"],
            "storage_location": "Secure Element",
            "confidentiality": "High",
            "integrity": "High",
            "availability": "Medium",
            "authenticity_required": True,
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
    return asset_ids

def create_realistic_damage_scenarios_for_product(cursor, scope_id, asset_ids):
    """Create 50 realistic damage scenarios for telematics/infotainment system"""
    
    damage_scenarios = [
        # Telematics firmware scenarios
        {"name": "Telematics Firmware Compromise", "description": "Unauthorized modification of telematics control firmware", "category": "Integrity Violation", "assets": [0], "safety": "moderate", "financial": "major", "operational": "major", "privacy": "major"},
        {"name": "Remote Command Injection", "description": "Injection of malicious commands via telematics interface", "category": "Integrity Violation", "assets": [0, 4], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "moderate"},
        {"name": "Telematics Service Disruption", "description": "Denial of service attack on telematics functionality", "category": "Availability Violation", "assets": [0, 4], "safety": "negligible", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Firmware Rollback Attack", "description": "Downgrade to vulnerable telematics firmware version", "category": "Integrity Violation", "assets": [0], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "moderate"},
        {"name": "Telematics Memory Corruption", "description": "Memory corruption causing system instability", "category": "Availability Violation", "assets": [0], "safety": "moderate", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        
        # Vehicle data gateway scenarios
        {"name": "Vehicle Data Interception", "description": "Unauthorized access to vehicle telemetry and diagnostic data", "category": "Confidentiality Violation", "assets": [1], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "major"},
        {"name": "Data Gateway Manipulation", "description": "Modification of vehicle data in transit", "category": "Integrity Violation", "assets": [1], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "moderate"},
        {"name": "Gateway Flooding Attack", "description": "Overwhelming data gateway with excessive traffic", "category": "Availability Violation", "assets": [1], "safety": "negligible", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        {"name": "Telemetry Data Theft", "description": "Unauthorized extraction of sensitive vehicle usage data", "category": "Confidentiality Violation", "assets": [1], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "major"},
        {"name": "Data Routing Manipulation", "description": "Redirecting vehicle data to unauthorized destinations", "category": "Integrity Violation", "assets": [1], "safety": "negligible", "financial": "moderate", "operational": "moderate", "privacy": "major"},
        
        # OTA update system scenarios
        {"name": "Malicious OTA Update", "description": "Installation of compromised software via OTA update", "category": "Integrity Violation", "assets": [2], "safety": "major", "financial": "major", "operational": "major", "privacy": "moderate"},
        {"name": "OTA Update Interception", "description": "Man-in-the-middle attack on update process", "category": "Integrity Violation", "assets": [2], "safety": "major", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Update Verification Bypass", "description": "Bypassing signature verification for updates", "category": "Integrity Violation", "assets": [2], "safety": "major", "financial": "major", "operational": "major", "privacy": "moderate"},
        {"name": "OTA Service Disruption", "description": "Preventing legitimate software updates", "category": "Availability Violation", "assets": [2], "safety": "negligible", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Update Rollback Attack", "description": "Forcing rollback to vulnerable software versions", "category": "Integrity Violation", "assets": [2], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "negligible"},
        
        # Infotainment database scenarios
        {"name": "Personal Data Theft", "description": "Unauthorized access to user personal information", "category": "Confidentiality Violation", "assets": [3], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "severe"},
        {"name": "Media Content Manipulation", "description": "Modification or deletion of user media files", "category": "Integrity Violation", "assets": [3], "safety": "negligible", "financial": "negligible", "operational": "negligible", "privacy": "moderate"},
        {"name": "Contact List Exposure", "description": "Unauthorized access to user contact information", "category": "Confidentiality Violation", "assets": [3], "safety": "negligible", "financial": "negligible", "operational": "negligible", "privacy": "major"},
        {"name": "User Profile Manipulation", "description": "Unauthorized modification of user preferences and settings", "category": "Integrity Violation", "assets": [3], "safety": "negligible", "financial": "negligible", "operational": "moderate", "privacy": "moderate"},
        {"name": "Database Corruption", "description": "Corruption of infotainment database causing data loss", "category": "Availability Violation", "assets": [3], "safety": "negligible", "financial": "negligible", "operational": "moderate", "privacy": "moderate"},
        
        # Cellular communication scenarios
        {"name": "Cellular Network Hijacking", "description": "Redirecting cellular traffic through malicious base stations", "category": "Integrity Violation", "assets": [4], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "major"},
        {"name": "Emergency Call Disruption", "description": "Preventing or manipulating emergency service calls", "category": "Availability Violation", "assets": [4], "safety": "severe", "financial": "major", "operational": "major", "privacy": "negligible"},
        {"name": "Cellular Eavesdropping", "description": "Unauthorized monitoring of cellular communications", "category": "Confidentiality Violation", "assets": [4], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "major"},
        {"name": "SIM Card Cloning", "description": "Cloning vehicle SIM card for unauthorized access", "category": "Integrity Violation", "assets": [4], "safety": "moderate", "financial": "major", "operational": "moderate", "privacy": "major"},
        {"name": "Cellular Jamming Attack", "description": "RF jamming preventing cellular connectivity", "category": "Availability Violation", "assets": [4], "safety": "moderate", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        
        # GPS navigation scenarios
        {"name": "GPS Spoofing Attack", "description": "Providing false GPS signals to mislead navigation", "category": "Integrity Violation", "assets": [5], "safety": "major", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        {"name": "Location Data Theft", "description": "Unauthorized access to vehicle location history", "category": "Confidentiality Violation", "assets": [5], "safety": "negligible", "financial": "negligible", "operational": "negligible", "privacy": "major"},
        {"name": "Navigation System Disruption", "description": "Jamming GPS signals to disable navigation", "category": "Availability Violation", "assets": [5], "safety": "moderate", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        {"name": "Route Manipulation", "description": "Altering navigation routes for malicious purposes", "category": "Integrity Violation", "assets": [5], "safety": "moderate", "financial": "negligible", "operational": "moderate", "privacy": "negligible"},
        {"name": "POI Database Poisoning", "description": "Injecting malicious points of interest into navigation database", "category": "Integrity Violation", "assets": [5], "safety": "negligible", "financial": "negligible", "operational": "negligible", "privacy": "negligible"},
        
        # Vehicle identity certificate scenarios
        {"name": "Vehicle Identity Theft", "description": "Theft of vehicle digital identity certificates", "category": "Confidentiality Violation", "assets": [6], "safety": "negligible", "financial": "major", "operational": "moderate", "privacy": "major"},
        {"name": "Certificate Forgery", "description": "Creation of fraudulent vehicle certificates", "category": "Integrity Violation", "assets": [6], "safety": "moderate", "financial": "major", "operational": "moderate", "privacy": "moderate"},
        {"name": "Key Extraction Attack", "description": "Extraction of private keys from secure storage", "category": "Confidentiality Violation", "assets": [6], "safety": "negligible", "financial": "major", "operational": "moderate", "privacy": "major"},
        {"name": "Certificate Revocation Attack", "description": "Unauthorized revocation of valid certificates", "category": "Availability Violation", "assets": [6], "safety": "negligible", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Identity Spoofing", "description": "Impersonating legitimate vehicle identity", "category": "Integrity Violation", "assets": [6], "safety": "moderate", "financial": "major", "operational": "moderate", "privacy": "moderate"},
        
        # Remote diagnostic scenarios
        {"name": "Unauthorized Remote Access", "description": "Gaining unauthorized access via diagnostic interface", "category": "Integrity Violation", "assets": [7], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "moderate"},
        {"name": "Diagnostic Data Manipulation", "description": "Altering diagnostic reports and error logs", "category": "Integrity Violation", "assets": [7], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "negligible"},
        {"name": "Remote Diagnostic Abuse", "description": "Misusing diagnostic capabilities for malicious purposes", "category": "Integrity Violation", "assets": [7], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "moderate"},
        {"name": "Diagnostic Service Disruption", "description": "Preventing legitimate diagnostic operations", "category": "Availability Violation", "assets": [7], "safety": "negligible", "financial": "moderate", "operational": "major", "privacy": "negligible"},
        {"name": "Health Report Falsification", "description": "Generating false vehicle health reports", "category": "Integrity Violation", "assets": [7], "safety": "moderate", "financial": "moderate", "operational": "moderate", "privacy": "negligible"},
        
        # User authentication scenarios
        {"name": "Authentication Bypass", "description": "Bypassing user authentication mechanisms", "category": "Integrity Violation", "assets": [8], "safety": "negligible", "financial": "moderate", "operational": "moderate", "privacy": "major"},
        {"name": "Biometric Data Theft", "description": "Unauthorized access to user biometric information", "category": "Confidentiality Violation", "assets": [8], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "severe"},
        {"name": "Credential Stuffing Attack", "description": "Using stolen credentials to gain unauthorized access", "category": "Integrity Violation", "assets": [8], "safety": "negligible", "financial": "moderate", "operational": "moderate", "privacy": "major"},
        {"name": "Session Hijacking", "description": "Taking over authenticated user sessions", "category": "Integrity Violation", "assets": [8], "safety": "negligible", "financial": "moderate", "operational": "moderate", "privacy": "major"},
        {"name": "Authentication Service Failure", "description": "Failure of authentication system causing access issues", "category": "Availability Violation", "assets": [8], "safety": "negligible", "financial": "negligible", "operational": "major", "privacy": "negligible"},
        
        # Multi-asset scenarios
        {"name": "Complete Telematics Compromise", "description": "Full compromise of telematics and connectivity systems", "category": "Multi-Domain Violation", "assets": [0, 1, 4, 6], "safety": "major", "financial": "major", "operational": "severe", "privacy": "severe"},
        {"name": "Connected Car Ransomware", "description": "Ransomware attack targeting connected vehicle systems", "category": "Availability Violation", "assets": [0, 2, 3, 8], "safety": "moderate", "financial": "major", "operational": "severe", "privacy": "major"},
        {"name": "Privacy Invasion Campaign", "description": "Coordinated attack to extract all personal data", "category": "Confidentiality Violation", "assets": [1, 3, 5, 8], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "severe"},
        {"name": "Vehicle Tracking Stalking", "description": "Unauthorized tracking and surveillance of vehicle", "category": "Confidentiality Violation", "assets": [1, 4, 5], "safety": "negligible", "financial": "negligible", "operational": "negligible", "privacy": "severe"},
        {"name": "Remote Vehicle Control", "description": "Gaining remote control over vehicle functions", "category": "Integrity Violation", "assets": [0, 1, 4], "safety": "severe", "financial": "major", "operational": "major", "privacy": "moderate"},
        
        # Advanced scenarios
        {"name": "Supply Chain Infiltration", "description": "Compromise during manufacturing or software supply chain", "category": "Integrity Violation", "assets": [0, 2, 6], "safety": "major", "financial": "major", "operational": "major", "privacy": "major"},
        {"name": "Insider Threat Attack", "description": "Malicious actions by authorized service personnel", "category": "Multi-Domain Violation", "assets": [2, 6, 7, 8], "safety": "moderate", "financial": "major", "operational": "major", "privacy": "major"},
        {"name": "State-Sponsored Surveillance", "description": "Government-level surveillance and data collection", "category": "Confidentiality Violation", "assets": [1, 4, 5, 8], "safety": "negligible", "financial": "moderate", "operational": "negligible", "privacy": "severe"}
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

def create_realistic_threat_scenarios_for_product(cursor, scope_id, damage_scenario_ids):
    """Create realistic threat scenarios for telematics/infotainment system"""
    
    threat_scenarios = [
        # Remote network attacks
        {"name": "Cellular Network Man-in-the-Middle", "description": "Intercepting cellular communications via rogue base station", "attack_vector": "Network", "damage_scenarios": [20, 22, 23]},
        {"name": "WiFi Hotspot Exploitation", "description": "Compromising vehicle via malicious WiFi access points", "attack_vector": "Wireless", "damage_scenarios": [0, 1, 15]},
        {"name": "Bluetooth Stack Buffer Overflow", "description": "Exploiting Bluetooth vulnerabilities for code execution", "attack_vector": "Wireless", "damage_scenarios": [0, 44]},
        {"name": "V2X Communication Spoofing", "description": "Spoofing vehicle-to-everything communication messages", "attack_vector": "Wireless", "damage_scenarios": [1, 25, 28]},
        {"name": "Remote API Exploitation", "description": "Exploiting vulnerabilities in remote service APIs", "attack_vector": "Network", "damage_scenarios": [1, 6, 35]},
        
        # OTA and update attacks
        {"name": "Compromised Update Server", "description": "Distributing malicious updates from compromised servers", "attack_vector": "Supply Chain", "damage_scenarios": [10, 11]},
        {"name": "Update Package Manipulation", "description": "Modifying update packages in transit", "attack_vector": "Network", "damage_scenarios": [10, 12]},
        {"name": "Signature Verification Bypass", "description": "Bypassing cryptographic signature checks", "attack_vector": "Software", "damage_scenarios": [12, 13]},
        {"name": "Rollback Attack via Replay", "description": "Replaying old update commands to downgrade software", "attack_vector": "Network", "damage_scenarios": [14, 3]},
        {"name": "Delta Update Poisoning", "description": "Injecting malicious code via differential updates", "attack_vector": "Software", "damage_scenarios": [10, 11]},
        
        # GPS and navigation attacks
        {"name": "GPS Signal Spoofing", "description": "Transmitting false GPS signals to mislead navigation", "attack_vector": "Wireless", "damage_scenarios": [25, 28]},
        {"name": "GNSS Jamming Attack", "description": "Jamming GPS/GNSS signals to disable positioning", "attack_vector": "Wireless", "damage_scenarios": [27, 24]},
        {"name": "Map Data Injection", "description": "Injecting malicious data into navigation maps", "attack_vector": "Network", "damage_scenarios": [29, 28]},
        {"name": "Dead Reckoning Manipulation", "description": "Manipulating inertial navigation when GPS unavailable", "attack_vector": "Physical", "damage_scenarios": [25, 28]},
        
        # Cellular and communication attacks
        {"name": "IMSI Catcher Deployment", "description": "Using fake cell towers to intercept communications", "attack_vector": "Wireless", "damage_scenarios": [20, 22]},
        {"name": "SIM Swapping Attack", "description": "Transferring vehicle SIM to attacker-controlled device", "attack_vector": "Social Engineering", "damage_scenarios": [23, 20]},
        {"name": "Baseband Processor Exploitation", "description": "Exploiting vulnerabilities in cellular modem firmware", "attack_vector": "Wireless", "damage_scenarios": [0, 20, 44]},
        {"name": "Emergency Services Hijacking", "description": "Redirecting emergency calls to malicious services", "attack_vector": "Network", "damage_scenarios": [21, 20]},
        
        # Physical and hardware attacks
        {"name": "Telematics Unit Physical Access", "description": "Direct physical access to telematics hardware", "attack_vector": "Physical", "damage_scenarios": [0, 30, 32]},
        {"name": "Antenna Tampering", "description": "Physical manipulation of communication antennas", "attack_vector": "Physical", "damage_scenarios": [24, 27]},
        {"name": "Hardware Implant Installation", "description": "Installing malicious hardware during service", "attack_vector": "Physical", "damage_scenarios": [44, 49]},
        {"name": "Side-Channel Key Extraction", "description": "Extracting cryptographic keys via power analysis", "attack_vector": "Physical", "damage_scenarios": [30, 32]},
        
        # Software and application attacks
        {"name": "Infotainment App Exploitation", "description": "Exploiting vulnerabilities in third-party applications", "attack_vector": "Software", "damage_scenarios": [15, 16, 19]},
        {"name": "Media File Malware", "description": "Embedding malware in media files", "attack_vector": "Software", "damage_scenarios": [16, 19]},
        {"name": "Voice Command Injection", "description": "Injecting malicious commands via voice interface", "attack_vector": "Software", "damage_scenarios": [39, 42]},
        {"name": "USB Port Exploitation", "description": "Exploiting USB connectivity for malware delivery", "attack_vector": "Physical", "damage_scenarios": [0, 15, 44]},
        
        # Authentication and access control attacks
        {"name": "Biometric Spoofing", "description": "Spoofing fingerprint or facial recognition systems", "attack_vector": "Physical", "damage_scenarios": [39, 40]},
        {"name": "Key Fob Relay Attack", "description": "Relaying key fob signals to gain unauthorized access", "attack_vector": "Wireless", "damage_scenarios": [39, 42]},
        {"name": "PIN Brute Force Attack", "description": "Brute forcing user authentication PINs", "attack_vector": "Software", "damage_scenarios": [39, 42]},
        {"name": "Session Token Theft", "description": "Stealing authentication tokens from memory", "attack_vector": "Software", "damage_scenarios": [42, 43]},
        
        # Privacy and surveillance attacks
        {"name": "Covert Location Tracking", "description": "Secretly tracking vehicle location without consent", "attack_vector": "Software", "damage_scenarios": [26, 47]},
        {"name": "Microphone Eavesdropping", "description": "Unauthorized activation of vehicle microphones", "attack_vector": "Software", "damage_scenarios": [15, 46]},
        {"name": "Camera System Hijacking", "description": "Taking control of vehicle cameras for surveillance", "attack_vector": "Software", "damage_scenarios": [46, 48]},
        {"name": "Contact List Harvesting", "description": "Extracting user contact information", "attack_vector": "Software", "damage_scenarios": [17, 46]},
        
        # Advanced persistent threats
        {"name": "State-Sponsored Implant", "description": "Government-level persistent surveillance implant", "attack_vector": "Supply Chain", "damage_scenarios": [48, 49, 46]},
        {"name": "Multi-Stage APT Campaign", "description": "Sophisticated long-term compromise of vehicle systems", "attack_vector": "Multi-Vector", "damage_scenarios": [44, 45, 46]},
        {"name": "Living-off-the-Land Attack", "description": "Using legitimate vehicle functions for malicious purposes", "attack_vector": "Software", "damage_scenarios": [44, 47]},
        
        # Ransomware and extortion
        {"name": "Vehicle Ransomware Attack", "description": "Encrypting vehicle systems and demanding ransom", "attack_vector": "Software", "damage_scenarios": [45, 44]},
        {"name": "Data Exfiltration for Extortion", "description": "Stealing personal data for blackmail purposes", "attack_vector": "Network", "damage_scenarios": [15, 40, 46]},
        {"name": "Service Disruption Extortion", "description": "Threatening to disable vehicle services", "attack_vector": "Network", "damage_scenarios": [2, 13, 24]},
        
        # Supply chain and insider threats
        {"name": "Malicious Service Technician", "description": "Service personnel installing malicious software", "attack_vector": "Social Engineering", "damage_scenarios": [49, 35, 36]},
        {"name": "Compromised Development Environment", "description": "Injecting malware during software development", "attack_vector": "Supply Chain", "damage_scenarios": [48, 10]},
        {"name": "Third-Party Component Compromise", "description": "Exploiting vulnerabilities in third-party libraries", "attack_vector": "Supply Chain", "damage_scenarios": [0, 44]},
        
        # Environmental and jamming attacks
        {"name": "RF Interference Attack", "description": "Using RF interference to disrupt communications", "attack_vector": "Environmental", "damage_scenarios": [24, 27, 2]},
        {"name": "EMP Attack on Electronics", "description": "Electromagnetic pulse targeting vehicle electronics", "attack_vector": "Environmental", "damage_scenarios": [2, 13, 43]},
        
        # Protocol and cryptographic attacks
        {"name": "Certificate Authority Compromise", "description": "Compromising trusted certificate authorities", "attack_vector": "Cryptographic", "damage_scenarios": [31, 34]},
        {"name": "Weak Encryption Exploitation", "description": "Exploiting weak cryptographic implementations", "attack_vector": "Cryptographic", "damage_scenarios": [30, 32, 22]},
        {"name": "Quantum Computing Threat", "description": "Future quantum computers breaking current encryption", "attack_vector": "Cryptographic", "damage_scenarios": [30, 32]},
        
        # Social engineering attacks
        {"name": "Phishing for Vehicle Credentials", "description": "Tricking users into revealing vehicle access credentials", "attack_vector": "Social Engineering", "damage_scenarios": [39, 42]},
        {"name": "Vishing for Remote Access", "description": "Voice phishing to gain remote diagnostic access", "attack_vector": "Social Engineering", "damage_scenarios": [35, 36]},
        {"name": "Pretexting for Physical Access", "description": "Impersonating service personnel for physical access", "attack_vector": "Social Engineering", "damage_scenarios": [49, 35]}
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
    """Main function to populate the database for product_c8833c81"""
    
    # Connect to database
    conn = sqlite3.connect('/Users/leonkalema/Dev/QuickTARA/quicktara.db')
    cursor = conn.cursor()
    
    try:
        print("Starting realistic data population for product_c8833c81...")
        
        # Use existing product scope
        scope_id = "product_c8833c81"
        
        # Verify the product exists
        cursor.execute("SELECT name FROM product_scopes WHERE scope_id = ?", (scope_id,))
        result = cursor.fetchone()
        if not result:
            print(f"❌ Error: Product {scope_id} not found in database")
            return
        
        product_name = result[0]
        print(f"Found existing product: {product_name}")
        
        # Create assets
        print("\n1. Creating realistic assets...")
        asset_ids = create_realistic_assets_for_product(cursor, scope_id)
        
        # Create damage scenarios
        print("\n2. Creating realistic damage scenarios...")
        damage_scenario_ids = create_realistic_damage_scenarios_for_product(cursor, scope_id, asset_ids)
        
        # Create threat scenarios
        print("\n3. Creating realistic threat scenarios...")
        threat_ids = create_realistic_threat_scenarios_for_product(cursor, scope_id, damage_scenario_ids)
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Successfully populated {scope_id} ({product_name}) with:")
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
