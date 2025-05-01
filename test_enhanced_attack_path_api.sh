#!/bin/bash
# Test script for the enhanced attack path analysis API

# Set API base URL
API_BASE="http://localhost:8080/api"

echo "===== Testing Enhanced Attack Path Analysis API ====="

# Create test assumptions
echo "Creating test assumptions..."
cat > test_assumptions.json << EOF
[
  {
    "assumption_id": "assume_1",
    "description": "Attacker has local network access",
    "type": "local_network_access"
  },
  {
    "assumption_id": "assume_2",
    "description": "Attacker has advanced technical skills",
    "type": "skilled_attacker"
  }
]
EOF

# Create test constraints
echo "Creating test constraints..."
cat > test_constraints.json << EOF
[
  {
    "constraint_id": "constraint_1",
    "description": "Exclude physical access to microcontrollers",
    "type": "exclude_physical_access"
  }
]
EOF

# Create test threat scenarios
echo "Creating test threat scenarios..."
cat > test_threat_scenarios.json << EOF
[
  {
    "scenario_id": "threat_1",
    "name": "CAN Bus Spoofing",
    "description": "Attacker spoofs CAN bus messages to inject malicious commands",
    "threat_type": "spoofing",
    "likelihood": 0.8
  },
  {
    "scenario_id": "threat_2",
    "name": "Firmware Tampering",
    "description": "Attacker modifies firmware to alter component behavior",
    "threat_type": "tampering",
    "likelihood": 0.6
  }
]
EOF

# Get the first component from the database to use as primary component
echo "Fetching components to use in test..."
COMPONENTS=$(curl -s -X GET "$API_BASE/components?limit=5")
PRIMARY_COMPONENT=$(echo $COMPONENTS | grep -o '"component_id":"[^"]*"' | head -1 | cut -d'"' -f4)
ALL_COMPONENTS=$(echo $COMPONENTS | grep -o '"component_id":"[^"]*"' | cut -d'"' -f4)

# If no components found, use default values
if [ -z "$PRIMARY_COMPONENT" ]; then
  PRIMARY_COMPONENT="ECU001"
  ALL_COMPONENTS=("ECU001" "ECU002" "ECU003")
fi

# Get some vulnerabilities to include
echo "Fetching vulnerabilities to include in test..."
VULNERABILITIES=$(curl -s -X GET "$API_BASE/vulnerability?limit=3")
VULN_IDS=$(echo $VULNERABILITIES | grep -o '"vulnerability_id":"[^"]*"' | cut -d'"' -f4)

# Create a test request payload
echo "Creating test request payload..."
cat > test_request.json << EOF
{
  "primary_component_id": "$PRIMARY_COMPONENT",
  "component_ids": [$(echo $ALL_COMPONENTS | sed 's/ /","/g' | sed 's/^/"/' | sed 's/$/"/')],
  "entry_point_ids": null,
  "target_ids": null,
  "include_chains": true,
  "max_depth": 5,
  "assumptions": $(cat test_assumptions.json),
  "constraints": $(cat test_constraints.json),
  "threat_scenarios": $(cat test_threat_scenarios.json),
  "vulnerability_ids": [$(echo $VULN_IDS | sed 's/ /","/g' | sed 's/^/"/' | sed 's/$/"/')]
}
EOF

echo "Testing attack path analysis with enhanced parameters..."
echo "Request payload:"
cat test_request.json

# Send the request
echo "Sending request to API..."
RESPONSE=$(curl -s -X POST "$API_BASE/attack-paths" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d @test_request.json)

# Check if response contains the expected fields
echo "Response received:"
echo "$RESPONSE" | python -m json.tool

# Check for key fields in the response
if echo "$RESPONSE" | grep -q "analysis_id"; then
  echo "✅ SUCCESS: Analysis ID found in response"
else
  echo "❌ ERROR: Analysis ID not found in response"
fi

if echo "$RESPONSE" | grep -q "total_paths"; then
  echo "✅ SUCCESS: Total paths found in response"
else
  echo "❌ ERROR: Total paths not found in response"
fi

# Cleanup
echo "Cleaning up temporary files..."
rm test_assumptions.json test_constraints.json test_threat_scenarios.json test_request.json

echo "===== Enhanced Attack Path Analysis API Test Completed ====="
