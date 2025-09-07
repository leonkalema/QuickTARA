# QuickTARA: Automotive Security Analysis Tool

Enhanced threat and risk assessment tool for automotive systems, incorporating STRIDE analysis, attack chain detection, safety-weighted scoring, attacker feasibility assessment, and formal risk acceptance criteria with human review.

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
- Compliance mapping (ISO 21434, UN R155)

### 3. Risk Assessment
- Component-based risk factors:
  * Exposure (location, trust zone)
  * Complexity (interfaces, connections)
  * Attack surface (access points, data types)
- Trust boundary analysis
- Attack surface calculation
- Safety-weighted scoring

### 4. Attacker Feasibility Assessment
- Technical capability requirements
- Knowledge requirements
- Resource needs assessment
- Time requirements
- Attacker profiles (Hobbyist, Criminal, Hacktivist, Insider, APT)
- Enabling and mitigating factors

### 5. Risk Acceptance Criteria (Clause 14)
- Formal risk treatment decisions (Accept, Accept with Controls, Transfer, Avoid, Mitigate)
- Decision justification
- Residual risk calculation
- Stakeholder approval tracking
- Reassessment scheduling

### 6. Manual Review Workflow
- Human review interface for all risk treatments
- Documentation of review decisions
- Evidence-based justifications
- Traceable decision records
- Compliance with audit requirements

## Installation

1. Clone the repository:
```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Component Data

Create an assets.csv file with your component information:

```csv
component_id,name,type,safety_level,interfaces,access_points,data_types,location,trust_zone,connected_to
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003
```

### 2. Web Interface (Recommended)

The web interface provides a modern, user-friendly experience with a complete workflow:

```bash
# Start the web application (local mode)
python quicktara_web.py
```

Then open your browser to `http://localhost:8080` to access the application.

Web Interface Features:
- Modern user interface built with Svelte and Tailwind CSS
- Component management with import/export
- Interactive analysis dashboard
- Visual STRIDE and attack path analysis
- Complete risk review workflow
- Multiple report formats
- Configurable database backend

Additional options:
```bash
# Custom configuration file
python quicktara_web.py --config my_config.yaml

# Custom database location or connection string
python quicktara_web.py --db ./my_database.db
python quicktara_web.py --db postgresql://user:pass@localhost/quicktara

# Custom host and port
python quicktara_web.py --host 0.0.0.0 --port 9000

# Debug mode
python quicktara_web.py --debug
```

### 3. GUI Workflow (Legacy)

The desktop GUI provides the original interface:

```bash
# Launch the GUI
python quicktara_gui.py
```

GUI Workflow Steps:
1. Click "Open CSV" to load your component data
2. Click "Run Analysis" to perform automatic threat analysis
3. Review the preliminary analysis results
4. Click "Review Risk Treatments" to manually review and approve/modify decisions
5. Click "Generate Final Report" to create the final TARA report with review documentation

### 4. Command Line Usage

For basic analysis without review workflow:

```bash
python quicktara.py -i assets.csv
```

This will generate:
- report.txt: Detailed text report
- report.json: Machine-readable data
- report.xlsx: Excel spreadsheet with multiple analysis sheets
- report.pdf: Formatted PDF report

## Configuration Options

QuickTARA Web can be configured using a YAML configuration file:

```yaml
# Database configuration
database:
  type: sqlite  # sqlite, postgresql, mysql
  path: ./quicktara.db  # For SQLite
  host: localhost  # For other databases
  port: 5432  # For other databases
  name: quicktara  # For other databases
  user: username  # For other databases
  password: password  # For other databases

# Server configuration
server:
  host: 127.0.0.1
  port: 8080
  debug: false

# File storage configuration
storage:
  uploads_dir: ./uploads
  reports_dir: ./reports

# Logging configuration
logging:
  level: info  # debug, info, warning, error
  file: ./quicktara.log
```

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

## Output Reports

### 1. Preliminary Report
- Generated after initial automated analysis
- Contains tool-suggested risk treatments

### 2. Final Report
- Generated after human review process
- Contains justified and traceable risk decisions
- Documents reviewer information and evidence references
- Includes both original and final decisions

### 3. Report Contents

All reports include comprehensive analysis:

- **STRIDE Analysis**: Categorization of threats by type (Spoofing, Tampering, etc.)
- **Impact Categories**: Assessment of financial, safety, and privacy impacts
- **Attack Chains**: Analysis of potential attack paths through connected components
- **Risk Factors**: Calculation of exposure, complexity, and attack surface metrics
- **Attacker Feasibility**: Assessment of attack difficulty and attacker profiles
- **Risk Acceptance Criteria**: Formal justification for treatment decisions
- **Compliance Mappings**: Connections to standards like ISO 21434 and UN R155
- **Cybersecurity Goals**: Alignment with security objectives

## Review Process

The risk treatment review process enables:

1. **Manual Review of All Treatments**: Review each risk decision (Accept, Transfer, Avoid, Mitigate)
2. **Decision Modification**: Change automated treatment decisions based on human judgment
3. **Justification Documentation**: Record reasoning behind each risk decision
4. **Evidence Tracking**: Document references to supporting evidence
5. **Reviewer Attribution**: Track who reviewed and approved each decision
6. **Review Status**: Monitor which risks have been reviewed and which are pending
7. **Audit Compliance**: Generate reports that satisfy regulatory audit requirements

This formal review process ensures that risk treatment decisions are justified, traceable, and properly documented, meeting the requirements of Clause 14 in cybersecurity standards.

## Developer Information

### API Documentation

When running in debug mode, the API documentation is available at:
- OpenAPI UI: http://localhost:8080/docs
- ReDoc UI: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

### Frontend Development

The frontend is built with Svelte, Vite, and Tailwind CSS. To start the frontend development server:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

For production build:
```bash
npm run build
```
