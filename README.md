<div align="center">

# 🚗 QuickTARA
### Complete Automotive Cybersecurity Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ISO 21434](https://img.shields.io/badge/ISO%2021434-Compliant-green.svg)](https://www.iso.org/standard/70918.html)
[![UN R155](https://img.shields.io/badge/UN%20R155-Compliant-green.svg)](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security)
[![Version](https://img.shields.io/badge/Version-2.1.0-brightgreen.svg)](https://github.com/leonkalema/QuickTARA/releases)
[![CRA](https://img.shields.io/badge/EU%20CRA-Compliance%20Module-orange.svg)](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)

**Professional-grade Threat Analysis and Risk Assessment (TARA) for automotive cybersecurity**  
*Complete workflow from asset identification to CRA compliance — ISO 21434, UN R155, and EU Cyber Resilience Act*

[🚀 One-Line Install](#-one-line-installation) • [🇪🇺 CRA Module](#-cra-compliance-module) • [👥 User Roles](#-user-roles--permissions) • [🎯 Features](#-comprehensive-features) • [⚙️ Requirements](#️-system-requirements)

</div>

---

<table>
<tr>
<td width="50%">

### 🔍 **Advanced Threat Analysis**
- **STRIDE Framework** - Complete threat categorization
- **Attack Chain Detection** - Multi-hop attack path analysis
- **Impact Assessment** - Financial, safety, and privacy impacts
- **Compliance Mapping** - ISO 21434 & UN R155 alignment

### 🛡️ **Risk Assessment Engine**
- **Component-Based Scoring** - Exposure, complexity, attack surface
- **Safety-Weighted Analysis** - ASIL-aware risk calculations
- **Trust Boundary Mapping** - Security domain analysis
- **Attacker Feasibility** - Capability and resource assessment

</td>
<td width="50%">

### 📋 **Workflow UI**
- Guided 6-step TARA navigation
- CRUD for products, assets, damage and threat scenarios
- Organization and user management (RBAC)

### 📊 **Report Generation**
- Multi-format output: PDF, Excel, JSON, Text
- ISO 21434 documentation sections
- Technical details and traceability

</td>
</tr>
</table>

---

## 🇪🇺 **CRA Compliance Module**

QuickTARA is the first TARA tool with **native EU Cyber Resilience Act (CRA) compliance** built in — no plugins, no add-ons.

<table>
<tr>
<td width="50%">

### 📋 **Classification & Gap Analysis**
- **Product Classification** — 6-question wizard determines Default, Class I, Class II, or Critical
- **Auto-Mapping** — Existing TARA artifacts (assets, damage scenarios, controls) automatically map to CRA requirements
- **Gap Analysis** — All **18 CRA requirements** (9 Part I risk-based, 5 Part II mandatory, 4 documentation) tracked with risk-level scoring; risk-based vs mandatory remain visually distinct in the UI and reports
- **Legacy Product Support** — Compensating controls catalog for products that can't be redesigned
- **Risk-Driven Workflow** — Apply a suggested control directly from a gap → control is created + linked → risk drops

</td>
<td width="50%">

### 📊 **Reports & Compliance Evidence**
- **Audit Traceability Report** — Full requirement × control matrix with residual risk, status definitions, justification notes (print + CSV)
- **Customer Compliance Summary** — External-safe report with classification, methodology, assurance statement, and Annex A (all 18 requirements with status)
- **Auto-Generated Milestones** — Quarterly roadmap derived from requirement target dates
- **Inventory Tracking** — SKU, firmware version, units in field/stock, OEM customer, target market
- **Classification Impact Panel** — Conformity path, deadline urgency, cost estimate, and regulatory obligations

</td>
</tr>
</table>

### � **SBOM Ingestion (CRA Art. 13(6))**
Upload **CycloneDX 1.4+/1.5** or **SPDX 2.3** SBOMs per assessment. The parser
extracts components, versions, `purl`, supplier, license IDs and hashes;
storage is keyed by assessment so revisions form an audit trail. Each upload
auto-maps to **CRA-10** (component identification) and is surfaced as evidence
in the Annex VII technical-documentation export. Backed by `core/cra_sbom_*`
and the `cra_sboms` / `cra_sbom_components` tables (Alembic
`a1c2d3e4f5g6`).

### 🚨 **ENISA 24h / 72h / 14d Incident Reporting (CRA Art. 14)**
Every incident drives three independent deadline clocks computed from the
discovery timestamp (and, for the final report, the corrective-measure
availability). Phase status (`pending` / `approaching` / `overdue` /
`submitted`) is recomputed on every read so dashboards never lie. The
**Single Reporting Platform export** produces a structured payload per phase
ready to paste into the ENISA portal. Naive (timezone-less) timestamps are
rejected at the API boundary — Art. 14 windows are absolute, not local.
Backed by `core/cra_incident_*` and the `cra_incidents` table (Alembic
`b2d3e4f5g6h7`).

### 📑 **Annex VII Technical Documentation Generator**
One click produces the full **seven-section Annex VII document** — product
description, vulnerability handling, risk assessment, harmonised standards,
test reports, declaration of conformity, and SBOM appendix — assembled from
the live TARA artefacts, requirement statuses, compensating controls, and
SBOMs. The UI shows a **completeness percentage**, flags which sections still
need manual input ("Action required"), and exports a Markdown file ready for
notified-body submission or Pandoc conversion to PDF/DOCX. Read-only —
regenerates on every refresh from the source of truth. Backed by
`core/cra_annex_vii*`.

### �� **Validation & Integrity**
- N/A status requires documented justification — form blocks save without it
- Residual risk labels accurately reflect control status (planned ≠ implemented ≠ verified)
- Single source of truth — gap analysis reads from requirement statuses, not parallel data
- SBOM and incident persistence are covered by **alembic upgrade + downgrade round-trip tests** under `tests/db/`
- API surfaces (SBOM, incidents, Annex VII) have **end-to-end integration tests** under `tests/api/test_cra_integration.py`

---

## 🚀 **One-Line Installation**

**Get QuickTARA running in 5 minutes with zero configuration:**

```bash
curl -sSL https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh | bash
```

**What this does:**
- ✅ Downloads and installs QuickTARA
- ✅ Sets up Python backend (FastAPI + SQLite)
- ✅ Builds and starts SvelteKit frontend
- ✅ Creates initial admin user with a randomly generated password (written to `quicktara-initial-credentials.txt`, mode `0600`, in the project root)
- ✅ Generates a self-signed TLS certificate (HTTPS by default when `openssl` is available)
- ✅ Locks CORS to known origins, adds security headers, and rate-limits the login endpoint (10/min per IP)
- ✅ Preserves existing data on updates
- ✅ Provides both local and LAN access URLs

**Access URLs (HTTPS by default):**
- **Frontend (UI):** `https://localhost:4173`
- **Backend (API):** `https://localhost:8080`
- **LAN Access:** `https://your-ip:4173` and `https://your-ip:8080`

> Browsers will warn about the self-signed certificate on first visit. Accept the warning, or import `./certs/quicktara.crt` into your OS trust store. To use a real cert, set `QUICKTARA_SSL_CERTFILE` and `QUICKTARA_SSL_KEYFILE` to point at your own files before running the script.

**First Login:**
The first-run database migration creates a **System Administrator** account with a randomly generated 144-bit password and writes the credentials to `quicktara-initial-credentials.txt` in the project root with file mode `0600` (owner read/write only). Open the file, sign in, **change the password immediately** under *Settings → My Account*, then **delete the file**. The bootstrap account exists only to let you create your own admin user — it is never reused or regenerated and must not be left in place on shared or production deployments.

**Production environment variables:**

| Variable                   | Purpose                                                                                  |
|----------------------------|------------------------------------------------------------------------------------------|
| `QUICKTARA_SSL_CERTFILE`   | Path to TLS certificate (PEM). Enables HTTPS when paired with key.                       |
| `QUICKTARA_SSL_KEYFILE`    | Path to TLS private key (PEM).                                                           |
| `QUICKTARA_JWT_SECRET`     | JWT signing secret. Auto-generated to `.quicktara_jwt_secret` (mode `0600`) if not set.  |
| `QUICKTARA_CORS_ORIGINS`   | Comma-separated allow-list of additional frontend origins.                               |
| `QUICKTARA_DB_*`           | Override the default SQLite database (see *Advanced Configuration*).                     |

---

## ⚙️ **System Requirements**

<table>
<tr>
<td width="50%">

### 🖥️ **Required Software**
- **Python 3.8+** - Backend API server
- **Node.js 16+** - Frontend build system
- **npm** - Package manager (comes with Node.js)
- **Git** - Version control (for installation)

### 💾 **System Resources**
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 1GB for application + data
- **CPU:** Any modern processor (x64/ARM64)
- **Network:** Internet for initial download

</td>
<td width="50%">

### 🌐 **Supported Platforms**
- **macOS** 10.15+ (Intel/Apple Silicon)
- **Linux** (Ubuntu 18.04+, CentOS 7+, etc.)
- **Windows** 10+ (WSL2 recommended)
- **Docker** (any platform with Docker support)

### 🔧 **Installation Methods**
- **One-liner** (recommended) - Automated setup
- **Manual** - Step-by-step installation
- **Docker** - Containerized deployment
- **Development** - Local development setup

</td>
</tr>
</table>

### 📦 **Quick Prerequisites Check**

```bash
# Check if you have the required tools
python3 --version    # Should be 3.8+
node --version       # Should be 16+
npm --version        # Should be 6+
git --version        # Any recent version
```

**Missing tools?** Install them:
- **Python:** [python.org/downloads](https://python.org/downloads)
- **Node.js:** [nodejs.org](https://nodejs.org) (includes npm)
- **Git:** [git-scm.com](https://git-scm.com)

## 👥 **User Roles & Permissions**

QuickTARA implements comprehensive role-based access control (RBAC) for enterprise security and workflow management:

<table>
<tr>
<td width="25%">

### 🔧 **System Administrator**
**Full system control**
- ✅ User management
- ✅ System configuration
- ✅ Database administration
- ✅ All TARA operations
- ✅ Settings access
- ✅ Audit logs

*Initial bootstrap account is created by the installer; rotate the password immediately and create a per-user admin account.*

</td>
<td width="25%">

### 🏢 **Organization Admin**
**Organization-wide management**
- ✅ User management (org scope)
- ✅ Project oversight
- ✅ All TARA operations
- ✅ Settings access
- ✅ Compliance reporting
- ❌ System configuration

*Manages organizational users*

</td>
<td width="25%">

### 🛡️ **Risk Manager**
**Risk assessment authority**
- ✅ All TARA operations
- ✅ Risk treatment approval
- ✅ Compliance validation
- ✅ Report generation
- ❌ User management
- ❌ Settings access

*Approves risk treatments*

</td>
<td width="25%">

### 📊 **Analyst**
**Day-to-day TARA work**
- ✅ Asset management
- ✅ Threat/damage scenarios
- ✅ Risk assessment (draft)
- ✅ Report viewing
- ❌ Risk treatment approval
- ❌ User management

*Creates and analyzes scenarios*

</td>
</tr>
</table>

### 🔐 **Permission Matrix**

| Feature | System Admin | Org Admin | Risk Manager | Analyst |
|---------|:------------:|:---------:|:------------:|:-------:|
| **User Management** | ✅ | ✅ (org) | ❌ | ❌ |
| **Settings Access** | ✅ | ✅ | ❌ | ❌ |
| **Create Assets** | ✅ | ✅ | ✅ | ✅ |
| **Edit/Delete Assets** | ✅ | ✅ | ✅ | ❌ |
| **Create Scenarios** | ✅ | ✅ | ✅ | ✅ |
| **Delete Scenarios** | ✅ | ✅ | ❌ | ❌ |
| **Risk Assessment** | ✅ | ✅ | ✅ | ✅ (draft) |
| **Approve Treatments** | ✅ | ✅ | ✅ | ❌ |
| **Generate Reports** | ✅ | ✅ | ✅ | ✅ (view) |
| **System Configuration** | ✅ | ❌ | ❌ | ❌ |

---

## 🎯 **Comprehensive Features**

### 📋 **Complete TARA Workflow**

<table>
<tr>
<td width="33%">

#### 1️⃣ **Product Scope Definition**
- Multi-product management
- Global product selection
- Scope versioning
- Asset categorization

#### 2️⃣ **Asset & Component Management**
- Interactive asset creation
- CIA property assignment
- Component relationships
- Trust boundary mapping

</td>
<td width="33%">

#### 3️⃣ **Damage Scenario Analysis**
- Asset-specific scenarios
- SFOP impact rating (Safety, Financial, Operational, Privacy)
- Severity classification
- Regulatory compliance mapping

#### 4️⃣ **Threat Scenario Modeling**
- Many-to-many threat-damage linking
- Attack vector analysis
- STRIDE categorization
- Attack path visualization

</td>
<td width="33%">

#### 5️⃣ **Risk Assessment & Treatment**
- Automated risk calculation
- Manual review workflow
- Treatment approval process
- Mitigation strategy documentation

#### 6️⃣ **Compliance & Reporting**
- ISO 21434 documentation
- UN R155 compliance
- Executive summaries
- Technical implementation guides

</td>
</tr>
</table>

### 🔧 **Advanced Capabilities**

<table>
<tr>
<td width="50%">

### 🧠 **Intelligent Analysis**
- **Automated Threat Detection** - STRIDE-based analysis
- **Risk Scoring Engine** - Multi-factor risk calculation  
- **Impact Assessment** - SFOP methodology
- **Compliance Mapping** - Regulatory requirement tracking
- **Attack Path Analysis** - Multi-hop threat chains
- **Feasibility Assessment** - Attacker capability modeling

### 🔒 **Security Features**
- **Role-Based Access Control** - 4-tier user roles with permission hierarchy
- **Organization Management** - Multi-organization user assignment
- **Secure Authentication** - JWT tokens with refresh mechanism
- **Password Security** - bcrypt hashing with salt
- **Session Management** - Automatic token refresh and expiry
- **API Security** - JWT-based endpoint protection

</td>
<td width="50%">

### 📊 **Report Generation**
- **Multi-Format Export** - PDF, Excel, JSON, Text formats
- **Compliance Documentation** - ISO 21434 regulatory reports
- **Technical Analysis** - Detailed threat and risk documentation
- **Structured Sections** - Assets, damage scenarios, risk summaries
- **Professional Layout** - ReportLab-based PDF generation
- **Data Export** - Machine-readable formats for integration

### 🔄 **Basic Workflow**
- **TARA Process Flow** - 6-step guided workflow
- **Data Management** - Create, read, update operations
- **User Interface** - Web-based forms and tables
- **Simple Notifications** - Basic UI feedback messages

</td>
</tr>
</table>

---

## 🔎 **Project Status & Roadmap**

### Implemented
- **TARA Workflow** — Products, assets, damage scenarios, threat scenarios, risk assessment, risk treatment
- **RBAC** — System admin, org admin, risk manager, analyst with permission matrix
- **Authentication** — JWT with refresh tokens, bcrypt password hashing, session management
- **Organization Management** — Multi-org support, membership assignment, settings UI
- **Reports** — PDF (ReportLab), Excel, JSON, Text with ISO 21434 documentation sections
- **CRA Compliance Module** — Classification wizard, auto-mapping, gap analysis, compensating controls
- **CRA Reports** — Audit traceability report (internal) and customer compliance summary (external)
- **CRA Inventory** — SKU tracking, firmware versions, units in field/stock, OEM customers
- **CRA SBOM Ingestion (Art. 13(6))** — CycloneDX 1.4+/1.5 and SPDX 2.3 upload, parse, and storage; auto-maps to CRA-10
- **CRA Incident Reporting (Art. 14)** — 24h / 72h / 14d deadline tracking with structured ENISA Single Reporting Platform export
- **CRA Annex VII Generator** — Seven-section technical documentation with completeness %, action-required flags, Markdown export
- **Audit Trail** — Immutable action logging, evidence attachments, approval workflows, snapshots
- **SFOP Risk Calculator** — Safety, Financial, Operational, Privacy impact scoring
- **ISO 21434 Mapping** — Requirement traceability to standard clauses
- **On-Premise Deployment** — Private instances, no cloud dependency

### Planned
- Executive dashboards and C-level summaries
- Custom report templates and branding
- SSO/LDAP integration
- Multi-tenant isolation hardening
- Encryption at rest and default HTTPS deployment
- Automated periodic compliance re-assessment

### Known limitations & technical debt
A running register of structural shortcuts (dual `Base` metadatas, partial
Alembic coverage, mixed Pydantic v1/v2, no PDF golden-file tests, no
Playwright E2E) is tracked in [`TECH_DEBT.md`](./TECH_DEBT.md). Reference
entries by number in PRs that interact with them.

---

## 🔧 **Manual Installation** *(Advanced Users)*

<details>
<summary>Click to expand manual installation steps</summary>

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

4. Build frontend:
```bash
cd tara-web
npm install && npm run build
cd ..
```

5. Run:
```bash
python quicktara_web.py
```

</details>

---

## 📚 **Usage Guide**

### 🎯 **Getting Started**

<table>
<tr>
<td width="50%">

#### 1️⃣ **Access the Platform**
- Open your browser to `https://localhost:4173` (or `http://` if TLS was disabled)
- Sign in with the bootstrap admin credentials printed by the installer
- **Change the password immediately** under *Settings → My Account*
- Navigate to the dashboard

#### 2️⃣ **Create Your Project**
- Click "New Project" 
- Enter vehicle/system details
- Define security scope

</td>
<td width="50%">

#### 3️⃣ **Import Assets**
- Use the web interface to add components
- Or upload CSV file with asset data
- Review and validate imported data

#### 4️⃣ **Run Analysis**
- Execute automated threat analysis
- Review generated risk assessments
- Approve or modify treatment decisions

</td>
</tr>
</table>

### 📄 **Asset Data Format**

<details>
<summary>Click to see CSV format specification</summary>

```csv
component_id,name,type,safety_level,interfaces,access_points,data_types,location,trust_zone,connected_to
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003
SNS001,Wheel Speed Sensor,Sensor,ASIL B,CAN,,Sensor Data,External,Untrusted,ECU001
GWY001,Telematics Gateway,Gateway,ASIL C,CAN|Ethernet|4G,Debug Port|USB,All Traffic|Diagnostic Data,Internal,Boundary,ECU001|ECU004
```

**Field Descriptions:**
- `component_id`: Unique identifier (e.g., ECU001)
- `name`: Human-readable component name
- `type`: ECU, Sensor, Gateway, Actuator, Network
- `safety_level`: QM, ASIL A, ASIL B, ASIL C, ASIL D
- `interfaces`: Communication protocols (pipe-separated)
- `access_points`: Physical/debug interfaces (pipe-separated)
- `data_types`: Nature of data handled (pipe-separated)
- `location`: Internal or External
- `trust_zone`: Critical, Boundary, Standard, Untrusted
- `connected_to`: Connected component IDs (pipe-separated)

</details>

---

## ⚙️ **Advanced Configuration**

<details>
<summary>Click settings to see advanced configuration options</summary>

### 🔧 **Command Line Options**

```bash
# Custom configuration file
python quicktara_web.py --config my_config.yaml

# Custom database location
python quicktara_web.py --db ./my_database.db
python quicktara_web.py --db postgresql://user:pass@localhost/quicktara

# Network configuration
python quicktara_web.py --host 0.0.0.0 --port 9000

# Debug mode
python quicktara_web.py --debug
```

### 📊 **Database Options**
- **SQLite** (Default) - Single file, no setup required
- **MySQL** - Production-ready, multi-user support
- **PostgreSQL** - Advanced features, enterprise scale

### 🌐 **Deployment Modes**
- **Local** - Single user development
- **LAN** - Team collaboration within office network
- **Cloud** - Internet-accessible, enterprise deployment

</details>

### 🖥️ **Command Line Interface**

<details>
<summary>For automated/batch processing</summary>

```bash
# Basic analysis
python quicktara.py -i assets.csv

# Custom output directory
python quicktara.py -i assets.csv -o ./reports/

# Specific report formats
python quicktara.py -i assets.csv --pdf --excel --json
```

**Generated Reports:**
- 📄 `report.pdf` - Executive summary and technical details
- 📊 `report.xlsx` - Spreadsheet with multiple analysis sheets
- 🔧 `report.json` - Machine-readable data for integrations
- 📝 `report.txt` - Plain text detailed report

</details>

---

## 📞 **Support & Contact**

For questions or contributions, please open an issue on GitHub.

---

**© 2025–2026 QuickTARA. All rights reserved.**

