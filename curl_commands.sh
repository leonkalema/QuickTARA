#!/bin/bash

# Ensure the API server is running at http://127.0.0.1:8000

# Add the JWT token threat
echo "Adding JWT session hijacking threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @realistic_threat.json

# Add the automotive threats
echo -e "\n\nAdding CAN Bus Message Injection threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @<(jq '.[0]' automotive_threats.json)

echo -e "\n\nAdding OTA Update System Compromise threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @<(jq '.[1]' automotive_threats.json)

echo -e "\n\nAdding Keyless Entry System Replay Attack threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @<(jq '.[2]' automotive_threats.json)

echo -e "\n\nAdding Information Disclosure via Diagnostic Interface threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @<(jq '.[3]' automotive_threats.json)

echo -e "\n\nAdding V2X Communication DoS Attack threat..."
curl -X POST http://127.0.0.1:8000/api/threat/catalog \
  -H "Content-Type: application/json" \
  -d @<(jq '.[4]' automotive_threats.json)

echo -e "\n\nAll threats have been added to the catalog."
