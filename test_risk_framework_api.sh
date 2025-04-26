#!/bin/bash
# Test script for Risk Calculation Framework API

API_URL="http://127.0.0.1:8080/api/risk"
FRAMEWORK_ID=""

echo "💡 Risk Framework API Test"
echo "=========================="
echo

# Create a new risk framework
echo "📝 Creating a new risk framework..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Automotive TARA Framework",
    "description": "Standard risk framework for automotive threat analysis and risk assessment",
    "version": "1.0.0",
    "impact_definitions": {
      "safety": [
        {
          "category": "safety",
          "level": "negligible",
          "description": "No injuries",
          "numerical_value": 1,
          "examples": ["No safety impact"]
        },
        {
          "category": "safety",
          "level": "minor",
          "description": "Light injuries possible",
          "numerical_value": 2,
          "examples": ["Minor discomfort"]
        },
        {
          "category": "safety",
          "level": "moderate",
          "description": "Injuries requiring medical attention",
          "numerical_value": 3,
          "examples": ["Hospitalization may be required"]
        },
        {
          "category": "safety",
          "level": "major",
          "description": "Severe injuries likely",
          "numerical_value": 4,
          "examples": ["Extended hospital stay required"]
        },
        {
          "category": "safety",
          "level": "critical",
          "description": "Life-threatening or fatal injuries",
          "numerical_value": 5,
          "examples": ["Death or permanent disability"]
        }
      ],
      "financial": [
        {
          "category": "financial",
          "level": "negligible",
          "description": "Minimal financial impact",
          "numerical_value": 1,
          "examples": ["Less than $10,000"]
        },
        {
          "category": "financial",
          "level": "minor",
          "description": "Low financial impact",
          "numerical_value": 2,
          "examples": ["$10,000 - $100,000"]
        },
        {
          "category": "financial",
          "level": "moderate",
          "description": "Moderate financial impact",
          "numerical_value": 3,
          "examples": ["$100,000 - $1,000,000"]
        },
        {
          "category": "financial",
          "level": "major",
          "description": "Significant financial impact",
          "numerical_value": 4,
          "examples": ["$1,000,000 - $10,000,000"]
        },
        {
          "category": "financial",
          "level": "critical",
          "description": "Severe financial impact",
          "numerical_value": 5,
          "examples": ["Greater than $10,000,000"]
        }
      ]
    },
    "likelihood_definitions": [
      {
        "level": "rare",
        "description": "Very unlikely to occur",
        "numerical_value": 1,
        "probability_range": {"min": 0.0, "max": 0.1},
        "examples": ["Highly sophisticated attack requiring nation-state resources"]
      },
      {
        "level": "unlikely",
        "description": "Not likely to occur",
        "numerical_value": 2,
        "probability_range": {"min": 0.1, "max": 0.3},
        "examples": ["Advanced technical skills required"]
      },
      {
        "level": "possible",
        "description": "May occur occasionally",
        "numerical_value": 3,
        "probability_range": {"min": 0.3, "max": 0.5},
        "examples": ["Moderate technical skills required"]
      },
      {
        "level": "likely",
        "description": "Likely to occur",
        "numerical_value": 4,
        "probability_range": {"min": 0.5, "max": 0.7},
        "examples": ["Basic technical skills sufficient"]
      },
      {
        "level": "almost_certain",
        "description": "Almost certain to occur",
        "numerical_value": 5,
        "probability_range": {"min": 0.7, "max": 1.0},
        "examples": ["Trivial attack, script kiddie level"]
      }
    ],
    "risk_matrix": {
      "matrix": [
        {"impact": 1, "likelihood": 1, "risk_level": "low", "numerical_score": 1},
        {"impact": 1, "likelihood": 2, "risk_level": "low", "numerical_score": 2},
        {"impact": 1, "likelihood": 3, "risk_level": "low", "numerical_score": 3},
        {"impact": 1, "likelihood": 4, "risk_level": "medium", "numerical_score": 4},
        {"impact": 1, "likelihood": 5, "risk_level": "medium", "numerical_score": 5},
        {"impact": 2, "likelihood": 1, "risk_level": "low", "numerical_score": 2},
        {"impact": 2, "likelihood": 2, "risk_level": "low", "numerical_score": 4},
        {"impact": 2, "likelihood": 3, "risk_level": "medium", "numerical_score": 6},
        {"impact": 2, "likelihood": 4, "risk_level": "medium", "numerical_score": 8},
        {"impact": 2, "likelihood": 5, "risk_level": "high", "numerical_score": 10},
        {"impact": 3, "likelihood": 1, "risk_level": "low", "numerical_score": 3},
        {"impact": 3, "likelihood": 2, "risk_level": "medium", "numerical_score": 6},
        {"impact": 3, "likelihood": 3, "risk_level": "medium", "numerical_score": 9},
        {"impact": 3, "likelihood": 4, "risk_level": "high", "numerical_score": 12},
        {"impact": 3, "likelihood": 5, "risk_level": "high", "numerical_score": 15},
        {"impact": 4, "likelihood": 1, "risk_level": "medium", "numerical_score": 4},
        {"impact": 4, "likelihood": 2, "risk_level": "medium", "numerical_score": 8},
        {"impact": 4, "likelihood": 3, "risk_level": "high", "numerical_score": 12},
        {"impact": 4, "likelihood": 4, "risk_level": "high", "numerical_score": 16},
        {"impact": 4, "likelihood": 5, "risk_level": "critical", "numerical_score": 20},
        {"impact": 5, "likelihood": 1, "risk_level": "medium", "numerical_score": 5},
        {"impact": 5, "likelihood": 2, "risk_level": "high", "numerical_score": 10},
        {"impact": 5, "likelihood": 3, "risk_level": "high", "numerical_score": 15},
        {"impact": 5, "likelihood": 4, "risk_level": "critical", "numerical_score": 20},
        {"impact": 5, "likelihood": 5, "risk_level": "critical", "numerical_score": 25}
      ],
      "description": "5x5 Risk Matrix for TARA"
    },
    "risk_thresholds": [
      {
        "level": "low",
        "description": "Acceptable risk",
        "requires_approval": false,
        "approvers": [],
        "max_acceptable_score": 4
      },
      {
        "level": "medium",
        "description": "Needs review",
        "requires_approval": true,
        "approvers": ["Security Analyst"],
        "max_acceptable_score": 9
      },
      {
        "level": "high",
        "description": "Requires mitigation",
        "requires_approval": true,
        "approvers": ["Security Analyst", "Security Manager"],
        "max_acceptable_score": 16
      },
      {
        "level": "critical",
        "description": "Unacceptable risk",
        "requires_approval": true,
        "approvers": ["Security Analyst", "Security Manager", "CISO"],
        "max_acceptable_score": 25
      }
    ]
  }')

# Extract the framework_id from the response
FRAMEWORK_ID=$(echo $RESPONSE | grep -o '"framework_id":"[^"]*' | cut -d'"' -f4)

echo "✅ Created risk framework with ID: $FRAMEWORK_ID"
echo

# Get all risk frameworks
echo "📋 Getting all risk frameworks..."
curl -s "$API_URL" | jq '.'
echo

# Get the specific risk framework we just created
echo "🔍 Getting specific risk framework by ID: $FRAMEWORK_ID"
curl -s "$API_URL/$FRAMEWORK_ID" | jq '.'
echo

# Get the active risk framework
echo "✅ Getting active risk framework..."
curl -s "$API_URL/active" | jq '.'
echo

# Update the risk framework
echo "📝 Updating risk framework..."
curl -s -X PUT "$API_URL/$FRAMEWORK_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Automotive TARA Framework",
    "version": "1.0.1"
  }' | jq '.'
echo

echo "🏁 Test completed"
