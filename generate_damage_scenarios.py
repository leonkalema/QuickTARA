#!/usr/bin/env python3
"""
Generate 60 realistic automotive damage scenarios for the Battery Management System (BMS)
"""
import requests
import json
import time

# API configuration
API_BASE = "http://127.0.0.1:8080/api"
BMS_SCOPE_ID = "scope_84049a50"  # Battery Management System

# Realistic automotive damage scenarios for BMS
damage_scenarios = [
    {
        "name": "Battery Cell Voltage Manipulation",
        "description": "Attacker manipulates individual cell voltage readings, causing unbalanced charging and potential thermal runaway.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "Critical",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Temperature Sensor Spoofing",
        "description": "False temperature readings prevent thermal protection mechanisms from activating during overheating conditions.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "Critical",
        "primary_component_id": "BMS001"
    },
    {
        "name": "State of Charge (SoC) Data Corruption",
        "description": "Corrupted SoC data leads to unexpected vehicle shutdown or range miscalculation, stranding drivers.",
        "damage_category": "Operational",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": True,
        "severity": "High",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Charging Current Override",
        "description": "Attacker overrides safe charging current limits, causing battery degradation or fire hazard.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "Critical",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Cell Balancing Disruption",
        "description": "Disruption of cell balancing algorithms leads to uneven cell wear and reduced battery lifespan.",
        "damage_category": "Financial",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "Medium",
        "primary_component_id": "BMS001"
    }
]

# Add 55 more scenarios
additional_scenarios = [
    {
        "name": "BMS Firmware Corruption",
        "description": "Malicious firmware update corrupts BMS control algorithms, affecting all battery operations.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": True,
        "severity": "Critical",
        "primary_component_id": "BMS001"
    },
    {
        "name": "CAN Bus Message Injection",
        "description": "Injection of false CAN messages causes BMS to make incorrect decisions about battery management.",
        "damage_category": "Operational",
        "impact_type": "Cascading",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "High",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Battery History Data Theft",
        "description": "Unauthorized access to battery usage patterns reveals driver behavior and location data.",
        "damage_category": "Privacy",
        "impact_type": "Direct",
        "confidentiality_impact": True,
        "integrity_impact": False,
        "availability_impact": False,
        "severity": "Medium",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Emergency Shutdown Bypass",
        "description": "Attacker bypasses emergency shutdown mechanisms during critical battery faults.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "Critical",
        "primary_component_id": "BMS001"
    },
    {
        "name": "Diagnostic Port Exploitation",
        "description": "Unauthorized access through diagnostic port allows manipulation of BMS parameters.",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "confidentiality_impact": True,
        "integrity_impact": True,
        "availability_impact": False,
        "severity": "High",
        "primary_component_id": "BMS001"
    }
]

# Continue with more scenarios to reach 60 total
def generate_all_scenarios():
    """Generate complete list of 60 damage scenarios"""
    base_scenarios = [
        ("Contactor Control Manipulation", "Attacker controls high-voltage contactors inappropriately, causing electrical hazards.", "Safety", "Critical"),
        ("Battery Authentication Bypass", "Bypassing battery pack authentication allows use of non-certified or damaged batteries.", "Safety", "High"),
        ("Thermal Runaway Detection Failure", "Disabling thermal runaway detection systems prevents early warning of dangerous conditions.", "Safety", "Critical"),
        ("Power Distribution Corruption", "Corrupted power distribution logic causes uneven load distribution and component damage.", "Operational", "High"),
        ("Battery Warranty Data Tampering", "Tampering with battery warranty and maintenance data for fraudulent claims.", "Financial", "Medium"),
        ("Charging Station Communication Hijack", "Hijacking communication with charging stations to overcharge or damage battery.", "Safety", "High"),
        ("Battery Capacity Misreporting", "False reporting of battery capacity affects vehicle performance calculations.", "Operational", "Medium"),
        ("Isolation Monitoring Defeat", "Defeating electrical isolation monitoring creates shock hazards for maintenance personnel.", "Safety", "Critical"),
        ("BMS Calibration Data Corruption", "Corrupting calibration data leads to inaccurate measurements and poor battery management.", "Operational", "High"),
        ("Battery Pack Serial Number Cloning", "Cloning battery pack identifiers for theft or warranty fraud.", "Financial", "Medium"),
        ("Regenerative Braking Interference", "Interfering with regenerative braking energy recovery affects battery charging.", "Operational", "Medium"),
        ("Battery Health Prediction Manipulation", "Manipulating health prediction algorithms to hide battery degradation.", "Safety", "High"),
        ("Charging Profile Modification", "Unauthorized modification of charging profiles damages battery chemistry.", "Safety", "High"),
        ("BMS Communication Jamming", "Jamming BMS communications prevents coordination with other vehicle systems.", "Operational", "High"),
        ("Battery Module Bypass", "Bypassing failed battery modules without proper safety checks creates hazards.", "Safety", "Critical"),
        ("Energy Management Override", "Overriding energy management systems causes inefficient battery usage.", "Operational", "Medium"),
        ("Battery Preconditioning Manipulation", "Manipulating battery preconditioning affects performance in extreme temperatures.", "Operational", "Medium"),
        ("High Voltage Safety Interlock Bypass", "Bypassing safety interlocks exposes personnel to high voltage dangers.", "Safety", "Critical"),
        ("Battery Chemistry Detection Spoofing", "Spoofing battery chemistry detection leads to inappropriate charging algorithms.", "Safety", "High"),
        ("Load Balancing Algorithm Corruption", "Corrupting load balancing algorithms causes uneven battery usage.", "Operational", "Medium"),
        ("Battery Aging Acceleration", "Deliberately accelerating battery aging through improper charge/discharge cycles.", "Financial", "High"),
        ("Fault Code Injection", "Injecting false fault codes triggers unnecessary service actions and costs.", "Financial", "Medium"),
        ("Battery Performance Data Exfiltration", "Stealing battery performance data for competitive intelligence.", "Privacy", "Medium"),
        ("Charging Current Oscillation", "Creating oscillating charging currents damages battery cells.", "Safety", "High"),
        ("Battery Pack Ventilation Control", "Manipulating ventilation systems affects battery thermal management.", "Safety", "High"),
        ("State of Health (SoH) Falsification", "Falsifying SoH data hides battery degradation from users.", "Safety", "High"),
        ("Battery Module Communication Disruption", "Disrupting communication between battery modules affects coordination.", "Operational", "High"),
        ("Charging Time Manipulation", "Manipulating charging time estimates affects user planning and satisfaction.", "Operational", "Low"),
        ("Battery Pack Vibration Monitoring Defeat", "Defeating vibration monitoring prevents detection of mechanical damage.", "Safety", "Medium"),
        ("Energy Recovery System Corruption", "Corrupting energy recovery systems reduces overall vehicle efficiency.", "Operational", "Medium"),
        ("Battery Thermal Model Manipulation", "Manipulating thermal models leads to inappropriate cooling strategies.", "Safety", "High"),
        ("Charging Infrastructure Authentication Bypass", "Bypassing charging infrastructure authentication enables unauthorized charging.", "Financial", "Medium"),
        ("Battery Pack Pressure Monitoring Failure", "Failing to monitor battery pack pressure prevents detection of swelling.", "Safety", "High"),
        ("Power Electronics Control Corruption", "Corrupting power electronics control affects battery charging/discharging.", "Operational", "High"),
        ("Battery Management Algorithm Rollback", "Rolling back BMS algorithms to vulnerable versions creates security gaps.", "Safety", "High"),
        ("Cell Voltage Balancing Circuit Overload", "Overloading balancing circuits causes component failure and fire risk.", "Safety", "Critical"),
        ("Battery Pack Identification Spoofing", "Spoofing battery pack identification bypasses safety and compatibility checks.", "Safety", "High"),
        ("Charging Session Data Manipulation", "Manipulating charging session data affects billing and usage tracking.", "Financial", "Medium"),
        ("Battery Cooling System Override", "Overriding cooling system controls leads to thermal management failures.", "Safety", "High"),
        ("Emergency Response Data Corruption", "Corrupting emergency response data delays proper accident response.", "Safety", "Critical"),
        ("Battery Pack Weight Distribution Spoofing", "Spoofing weight distribution data affects vehicle dynamics calculations.", "Operational", "Medium"),
        ("Charging Cable Authentication Bypass", "Bypassing charging cable authentication allows use of unsafe cables.", "Safety", "High"),
        ("Battery Management Network Segmentation Failure", "Network segmentation failures expose BMS to broader vehicle attacks.", "Safety", "High"),
        ("Power Conversion Efficiency Manipulation", "Manipulating power conversion efficiency affects range calculations.", "Operational", "Medium"),
        ("Battery Pack Mounting Stress Monitoring Defeat", "Defeating stress monitoring prevents detection of mounting failures.", "Safety", "Medium"),
        ("Charging Protocol Downgrade Attack", "Forcing use of less secure charging protocols enables further attacks.", "Safety", "Medium"),
        ("Battery Management Logging Manipulation", "Manipulating BMS logs hides evidence of attacks or malfunctions.", "Safety", "Medium"),
        ("High Voltage Relay Control Corruption", "Corrupting relay control logic creates electrical safety hazards.", "Safety", "Critical"),
        ("Battery Pack Seal Integrity Monitoring Bypass", "Bypassing seal monitoring prevents detection of water ingress.", "Safety", "High"),
        ("Charging Load Scheduling Manipulation", "Manipulating charging schedules affects grid stability and costs.", "Operational", "Medium"),
        ("Battery Management Redundancy Defeat", "Defeating redundant safety systems removes critical backup protections.", "Safety", "Critical"),
        ("Power Quality Monitoring Corruption", "Corrupting power quality monitoring allows harmful electrical conditions.", "Safety", "High"),
        ("Battery Pack Transportation Mode Bypass", "Bypassing transportation safety mode during vehicle shipping.", "Safety", "High"),
        ("Charging Infrastructure Load Balancing Attack", "Attacking load balancing systems affects charging station availability.", "Operational", "Medium"),
        ("Battery Management Secure Boot Bypass", "Bypassing secure boot allows installation of malicious BMS firmware.", "Safety", "Critical"),
        ("Emergency Disconnect System Failure", "Failing emergency disconnect systems prevents safe power isolation.", "Safety", "Critical")
    ]
    
    all_scenarios = damage_scenarios + additional_scenarios
    
    # Add remaining scenarios to reach 60
    for i, (name, desc, category, severity) in enumerate(base_scenarios[:50]):  # Take 50 more to reach 60 total
        scenario = {
            "name": name,
            "description": desc,
            "damage_category": category,
            "impact_type": "Direct",
            "confidentiality_impact": category == "Privacy",
            "integrity_impact": True,
            "availability_impact": category == "Operational" or severity == "Critical",
            "severity": severity,
            "primary_component_id": "BMS001"
        }
        all_scenarios.append(scenario)
    
    return all_scenarios[:60]  # Ensure exactly 60 scenarios

def create_damage_scenario(scenario_data):
    """Create a single damage scenario via API"""
    scenario_data["scope_id"] = BMS_SCOPE_ID
    scenario_data["affected_component_ids"] = [scenario_data["primary_component_id"]]
    
    response = requests.post(f"{API_BASE}/damage-scenarios", json=scenario_data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create scenario '{scenario_data['name']}': {response.status_code} - {response.text}")
        return None

def main():
    """Generate and create all 60 damage scenarios"""
    scenarios = generate_all_scenarios()
    print(f"Generating {len(scenarios)} damage scenarios for BMS...")
    
    created_count = 0
    for i, scenario in enumerate(scenarios, 1):
        print(f"Creating scenario {i}/60: {scenario['name']}")
        result = create_damage_scenario(scenario)
        if result:
            created_count += 1
            print(f"✓ Created: {result['scenario_id']}")
        time.sleep(0.1)  # Small delay to avoid overwhelming the API
    
    print(f"\nCompleted: {created_count}/{len(scenarios)} scenarios created successfully")

if __name__ == "__main__":
    main()
