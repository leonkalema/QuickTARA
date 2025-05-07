#!/bin/bash
# Test script for Attack Path Analysis API Endpoints

# Set base URL
BASE_URL="http://localhost:8000/api"

# Define colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}QuickTARA Attack Path Analysis API Test${NC}"
echo "============================================"

# Get an existing analysis ID
echo -e "\n${GREEN}Getting existing analysis ID${NC}"
ANALYSIS_ID=$(sqlite3 ./quicktara.db "SELECT id FROM analyses LIMIT 1;")
echo "Using analysis ID: $ANALYSIS_ID"

# Test 1: Get Attack Paths
echo -e "\n${GREEN}Test 1: Get Attack Paths${NC}"
echo "GET $BASE_URL/attack-paths"

RESPONSE=$(curl -s -X GET "$BASE_URL/attack-paths")

echo "Response:"
echo "$RESPONSE" | jq '.'

# Use the sample path ID we created
PATH_ID="path_sample1"

# Test 2: Get a Specific Attack Path
echo -e "\n${GREEN}Test 3: Get a Specific Attack Path${NC}"
echo "GET $BASE_URL/attack-paths/$PATH_ID"

RESPONSE=$(curl -s -X GET \
  "$BASE_URL/attack-paths/$PATH_ID")

echo "Response:"
echo "$RESPONSE" | jq '.'

# Test 3: Get Attack Chains
echo -e "\n${GREEN}Test 4: Get Attack Chains${NC}"
echo "GET $BASE_URL/attack-paths/chains?analysis_id=$ANALYSIS_ID"

RESPONSE=$(curl -s -X GET "$BASE_URL/attack-paths/chains")

echo "Response:"
echo "$RESPONSE" | jq '.'

# Use the sample chain ID we created
CHAIN_ID="chain_sample1"

# Test 4: Get a Specific Attack Chain
echo -e "\n${GREEN}Test 5: Get a Specific Attack Chain${NC}"
echo "GET $BASE_URL/attack-paths/chains/$CHAIN_ID"

RESPONSE=$(curl -s -X GET \
  "$BASE_URL/attack-paths/chains/$CHAIN_ID")

echo "Response:"
echo "$RESPONSE" | jq '.'

echo -e "\n${BLUE}Test execution completed${NC}"
