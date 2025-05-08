#!/bin/bash
# Test script for SFOP Impact Rating API endpoints

# Set base URL
BASE_URL="http://127.0.0.1:8080/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing SFOP Impact Rating API Endpoints ===${NC}\n"

# Function to check API response
check_response() {
  local response=$1
  local step=$2
  
  if [[ $response == *"error"* ]] || [[ $response == *"detail"* ]]; then
    echo -e "${RED}Error in step $step: $response${NC}"
    return 1
  else
    echo -e "${GREEN}Step $step successful!${NC}"
    return 0
  fi
}

# 1. Get a list of existing damage scenarios to work with
echo -e "${BLUE}1. Getting list of damage scenarios...${NC}"
SCENARIOS_RESPONSE=$(curl -s "$BASE_URL/damage-scenarios?limit=5")
echo "$SCENARIOS_RESPONSE" | grep -o '"scenario_id":"[^"]*"' | head -1 > /tmp/scenario_id.txt
SCENARIO_ID=$(cat /tmp/scenario_id.txt | cut -d '"' -f 4)

if [ -z "$SCENARIO_ID" ]; then
  echo -e "${YELLOW}No existing damage scenarios found. Creating a test scenario...${NC}"
  
  # Create a test damage scenario if none exists
  CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/damage-scenarios" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Scenario for SFOP Ratings",
      "description": "This is a test scenario created for testing SFOP impact ratings",
      "damage_category": "Operational",
      "impact_type": "Direct",
      "confidentiality_impact": true,
      "integrity_impact": false,
      "availability_impact": true,
      "severity": "Medium",
      "scope_id": "scope-1",
      "primary_component_id": "comp-1",
      "affected_component_ids": ["comp-1"]
    }')
  
  echo "$CREATE_RESPONSE" | grep -o '"scenario_id":"[^"]*"' > /tmp/scenario_id.txt
  SCENARIO_ID=$(cat /tmp/scenario_id.txt | cut -d '"' -f 4)
  
  if [ -z "$SCENARIO_ID" ]; then
    echo -e "${RED}Failed to create test scenario. Please check if the API is running and the database is properly set up.${NC}"
    exit 1
  else
    echo -e "${GREEN}Created test scenario with ID: $SCENARIO_ID${NC}"
  fi
else
  echo -e "${GREEN}Found existing scenario with ID: $SCENARIO_ID${NC}"
fi

# First, let's check if we can get the damage scenario directly
echo -e "\n${BLUE}2. Getting damage scenario $SCENARIO_ID directly...${NC}"
GET_RESPONSE=$(curl -s "$BASE_URL/damage-scenarios/$SCENARIO_ID")
echo "$GET_RESPONSE" | jq '.'
check_response "$GET_RESPONSE" "2"

echo -e "\n${BLUE}3. Getting impact ratings for scenario $SCENARIO_ID...${NC}"
RATINGS_RESPONSE=$(curl -s "$BASE_URL/impact-ratings/scenarios/$SCENARIO_ID/impact-ratings")
echo "$RATINGS_RESPONSE" | jq '.'
check_response "$RATINGS_RESPONSE" "3"

echo -e "\n${BLUE}4. Getting suggested SFOP ratings...${NC}"
SUGGESTIONS_RESPONSE=$(curl -s "$BASE_URL/impact-ratings/suggest-ratings?component_id=comp-1&damage_category=Operational&confidentiality_impact=true&availability_impact=true")
echo "$SUGGESTIONS_RESPONSE" | jq '.'
check_response "$SUGGESTIONS_RESPONSE" "4"

echo -e "\n${BLUE}5. Updating impact ratings for scenario $SCENARIO_ID...${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/impact-ratings/scenarios/$SCENARIO_ID/impact-ratings" \
  -H "Content-Type: application/json" \
  -d '{
    "safety_impact": "Low",
    "financial_impact": "Medium",
    "operational_impact": "High",
    "privacy_impact": "Low",
    "impact_rating_notes": "These ratings were manually set during testing",
    "sfop_rating_override_reason": "Testing the API endpoints"
  }')
echo "$UPDATE_RESPONSE" | jq '.'
check_response "$UPDATE_RESPONSE" "5"

echo -e "\n${BLUE}6. Verifying updated impact ratings...${NC}"
VERIFY_RESPONSE=$(curl -s "$BASE_URL/impact-ratings/scenarios/$SCENARIO_ID/impact-ratings")
echo "$VERIFY_RESPONSE" | jq '.'
check_response "$VERIFY_RESPONSE" "6"

echo -e "\n${BLUE}7. Listing all scenarios with impact ratings...${NC}"
LIST_RESPONSE=$(curl -s "$BASE_URL/impact-ratings/list?limit=5")
echo "$LIST_RESPONSE" | jq '.'
check_response "$LIST_RESPONSE" "7"

echo -e "\n${BLUE}8. Filtering scenarios by impact rating...${NC}"
FILTER_RESPONSE=$(curl -s "$BASE_URL/impact-ratings/list?operational_impact=High")
echo "$FILTER_RESPONSE" | jq '.'
check_response "$FILTER_RESPONSE" "8"

echo -e "\n${GREEN}=== Testing complete! ===${NC}"
