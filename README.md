# QuickTARA: Automotive Security Analysis Tool

Enhanced threat and risk assessment tool for automotive systems, incorporating STRIDE analysis, attack chain detection, and safety-weighted scoring.

## Features

### 1. Enhanced Asset Analysis
- Detailed component attributes
- Safety levels (ASIL A-D)
- Trust zones and connectivity mapping
- Component types: ECU, Sensor, Gateway, Actuator, Network

### 2. Threat Analysis
- STRIDE categorization
- Impact analysis (financial, safety, privacy)
- Attack chain detection
- Compliance mapping (ISO 26262, UN R155)

### 3. Risk Assessment
- Component-based risk factors:
  * Exposure (location, trust zone)
  * Complexity (interfaces, connections)
  * Attack surface (access points, data types)
- Trust boundary analysis
- Attack surface calculation
- Safety-weighted scoring

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

Create an assets.csv file with your component information:

```csv
component_id,name,type,safety_level,interfaces,access_points,data_types,location,trust_zone,connected_to
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003
```

Run the analysis:

```bash
python quicktara.py -i assets.csv
```

This will generate:
- report.txt: Detailed text report
- report.json: Machine-readable data
- report.xlsx: Excel spreadsheet
- report.pdf: Formatted PDF report

## Input Format

### Component Fields
- `component_id`: Unique identifier
- `name`: Human-readable name
- `type`: ECU, Sensor, Gateway, etc.
- `safety_level`: ASIL rating (QM to ASIL D)
- `interfaces`: Communication protocols (|-separated)
- `access_points`: Physical/debug interfaces (|-separated)
- `data_types`: Nature of data handled (|-separated)
- `location`: Physical placement (Internal/External)
- `trust_zone`: Security domain (Critical/Boundary/Standard/Untrusted)
- `connected_to`: Connected component IDs (|-separated)

### Example Components
```csv
# Safety-critical ECU
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003

# External sensor
SNS001,Wheel Speed Sensor,Sensor,ASIL B,CAN,,Sensor Data,External,Untrusted,ECU001

# Network gateway
GWY001,Telematics Gateway,Gateway,ASIL C,CAN|Ethernet|4G,Debug Port|USB,All Traffic|Diagnostic Data,Internal,Boundary,ECU001|ECU004
```

## Output Analysis

### 1. STRIDE Analysis
- Spoofing: Authentication and identity threats
- Tampering: Data/code modification threats
- Repudiation: Audit and logging threats
- Information Disclosure: Data leakage threats
- Denial of Service: Availability threats
- Elevation of Privilege: Authorization threats

### 2. Impact Categories
- Financial: Cost and business impact
- Safety: Physical safety implications
- Privacy: Data protection concerns

### 3. Attack Chains
- Connected component analysis
- Trust boundary crossings
- Attack path identification

### 4. Risk Factors
- Component exposure
- Interface complexity
- Attack surface area
- Safety level weighting