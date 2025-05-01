#!/bin/bash

# Test script for enhanced attack path analysis API
# This script tests the new functionality with assumptions, constraints, and threat scenarios

echo "Testing enhanced attack path analysis API..."

# Define the base URL
API_URL="http://localhost:8080/api"

# Test case 1: Basic attack path analysis with primary component
echo -e "\n\033[1mTest Case 1: Basic attack path analysis with primary component\033[0m"
curl -X POST "${API_URL}/attack-paths/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_component_id": "TBOX-001",
    "component_ids": ["TBOX-001", "ECU-002", "CAN-BUS-001", "DISPLAY-001"],
    "include_chains": true,
    "max_depth": 5
  }' | jq .

# Test case 2: Attack path analysis with assumptions
echo -e "\n\033[1mTest Case 2: Attack path analysis with assumptions\033[0m"
curl -X POST "${API_URL}/attack-paths/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_component_id": "TBOX-001",
    "component_ids": ["TBOX-001", "ECU-002", "CAN-BUS-001", "DISPLAY-001"],
    "include_chains": true,
    "max_depth": 5,
    "assumptions": [
      {
        "assumption_id": "assume_1",
        "description": "Attacker has physical access",
        "type": "physical_access"
      },
      {
        "assumption_id": "assume_2",
        "description": "Attacker has local network access",
        "type": "local_network_access"
      }
    ]
  }' | jq .

# Test case 3: Attack path analysis with constraints
echo -e "\n\033[1mTest Case 3: Attack path analysis with constraints\033[0m"
curl -X POST "${API_URL}/attack-paths/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_component_id": "TBOX-001",
    "component_ids": ["TBOX-001", "ECU-002", "CAN-BUS-001", "DISPLAY-001"],
    "include_chains": true,
    "max_depth": 5,
    "constraints": [
      {
        "constraint_id": "constraint_1",
        "description": "Exclude physical access to microcontrollers",
        "type": "exclude_physical_access"
      }
    ]
  }' | jq .

# Test case 4: Attack path analysis with threat scenarios
echo -e "\n\033[1mTest Case 4: Attack path analysis with threat scenarios\033[0m"
curl -X POST "${API_URL}/attack-paths/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_component_id": "TBOX-001",
    "component_ids": ["TBOX-001", "ECU-002", "CAN-BUS-001", "DISPLAY-001"],
    "include_chains": true,
    "max_depth": 5,
    "threat_scenarios": [
      {
        "scenario_id": "threat_s1",
        "name": "Authentication Bypass",
        "description": "Attacker bypasses authentication mechanisms",
        "threat_type": "spoofing",
        "likelihood": 0.7
      },
      {
        "scenario_id": "threat_t1",
        "name": "Firmware Tampering",
        "description": "Attacker modifies firmware to alter component behavior",
        "threat_type": "tampering",
        "likelihood": 0.6
      }
    ]
  }' | jq .

# Test case 5: Full attack path analysis with all parameters
echo -e "\n\033[1mTest Case 5: Full attack path analysis with all parameters\033[0m"
curl -X POST "${API_URL}/attack-paths/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_component_id": "TBOX-001",
    "component_ids": ["TBOX-001", "ECU-002", "CAN-BUS-001", "DISPLAY-001"],
    "include_chains": true,
    "max_depth": 5,
    "entry_point_ids": ["TBOX-001-WIFI", "TBOX-001-4G"],
    "target_ids": ["ECU-002-CAN", "DISPLAY-001-SCREEN"],
    "assumptions": [
      {
        "assumption_id": "assume_1",
        "description": "Attacker has physical access",
        "type": "physical_access"
      }
    ],
    "constraints": [
      {
        "constraint_id": "constraint_1",
        "description": "Exclude physical access to microcontrollers",
        "type": "exclude_physical_access"
      }
    ],
    "threat_scenarios": [
      {
        "scenario_id": "threat_s1",
        "name": "Authentication Bypass",
        "description": "Attacker bypasses authentication mechanisms",
        "threat_type": "spoofing",
        "likelihood": 0.7
      }
    ],
    "vulnerability_ids": ["CVE-2023-1234", "CVE-2023-5678"]
  }' | jq .

echo -e "\n\033[1mTests completed\033[0m"
