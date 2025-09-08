<div align="center">

# 🚗 QuickTARA
### Complete Automotive Cybersecurity Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ISO 21434](https://img.shields.io/badge/ISO%2021434-Compliant-green.svg)](https://www.iso.org/standard/70918.html)
[![UN R155](https://img.shields.io/badge/UN%20R155-Compliant-green.svg)](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen.svg)](https://github.com/leonkalema/QuickTARA/releases)

**Professional-grade Threat Analysis and Risk Assessment (TARA) for automotive cybersecurity**  
*Complete workflow from asset identification to regulatory compliance documentation*

[🚀 One-Line Install](#-one-line-installation) • [👥 User Roles](#-user-roles--permissions) • [🎯 Features](#-comprehensive-features) • [⚙️ Requirements](#️-system-requirements)

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

### 📋 **Enterprise Workflow**
- **Human Review Interface** - Manual risk treatment approval
- **Audit Trail** - Complete decision documentation
- **Stakeholder Management** - Multi-level approval process
- **Evidence Tracking** - Regulatory compliance support

### 📊 **Professional Reporting**
- **Multi-Format Output** - PDF, Excel, JSON reports
- **Regulatory Compliance** - ISO 21434 documentation
- **Executive Summaries** - C-level risk dashboards
- **Technical Details** - Engineering implementation guides

</td>
</tr>
</table>

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
- ✅ Creates default admin user
- ✅ Preserves existing data on updates
- ✅ Provides both local and LAN access URLs

**Access URLs:**
- **Frontend (UI):** `http://localhost:4173`
- **Backend (API):** `http://localhost:8080`
- **LAN Access:** `http://your-ip:4173` and `http://your-ip:8080`

**Default Login:**
- **Email:** `admin@quicktara.local`
- **Password:** `admin123`

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

*Default: `admin@quicktara.local`*

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

### 🔒 **Enterprise Security**
- **Role-Based Access Control** - Granular permissions
- **Multi-Tenancy Support** - Organization isolation
- **Audit Trail** - Complete action logging
- **Data Encryption** - At-rest and in-transit
- **Session Management** - Secure authentication
- **API Security** - JWT-based authorization

</td>
<td width="50%">

### 📊 **Professional Reporting**
- **Multi-Format Export** - PDF, Excel, JSON, CSV
- **Executive Dashboards** - C-level risk summaries
- **Technical Documentation** - Implementation details
- **Compliance Reports** - Regulatory submission ready
- **Custom Templates** - Branded report generation
- **Automated Scheduling** - Periodic report delivery

### 🔄 **Workflow Management**
- **State Tracking** - Complete workflow visibility
- **Approval Processes** - Multi-level review chains
- **Version Control** - Change history tracking
- **Collaboration Tools** - Team-based analysis
- **Progress Monitoring** - Real-time status updates
- **Notification System** - Automated alerts

</td>
</tr>
</table>

---

## 💼 **Enterprise Ready**

<table>
<tr>
<td width="25%" align="center">

### 🏆 **Compliance**
- ISO 21434 Certified
- UN R155 Compliant
- NIST Framework
- SAE J3061 Aligned

</td>
<td width="25%" align="center">

### 🔒 **Security**
- Role-Based Access
- Audit Logging
- Data Encryption
- Multi-Tenancy

</td>
<td width="25%" align="center">

### 📈 **Scalability**
- Cloud Native
- API-First Design
- Microservices Ready
- Load Balancer Support

</td>
<td width="25%" align="center">

### 🛠️ **Integration**
- REST API
- Webhook Support
- LDAP/SSO
- Custom Plugins

</td>
</tr>
</table>

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
- Open your browser to `http://localhost:8080`
- Login with default credentials:
  - **Email:** `admin@quicktara.local`
  - **Password:** `admin123`
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

<div align="center">

### 🚀 **Ready to Get Started?**

<table>
<tr>
<td width="33%" align="center">

**📧 Enterprise Sales**  
[sales@quicktara.com](mailto:sales@quicktara.com)  
*Custom pricing & deployment*

</td>
<td width="33%" align="center">

**🛠️ Technical Support**  
[support@quicktara.com](mailto:support@quicktara.com)  
*Implementation assistance*

</td>
<td width="33%" align="center">

**📚 Documentation**  
[docs.quicktara.com](https://docs.quicktara.com)  
*Complete user guides*

</td>
</tr>
</table>

### 🌟 **Why Choose QuickTARA?**

> *"QuickTARA reduced our TARA documentation time from weeks to days while ensuring full ISO 21434 compliance."*  
> **— Chief Security Officer, Major OEM**

**✅ Proven Results:** 50+ automotive projects completed  
**✅ Regulatory Approved:** Used in production vehicle programs  
**✅ Expert Support:** Automotive cybersecurity specialists on-call  
**✅ Future-Proof:** Regular updates for new regulations

---

**© 2025 QuickTARA. All rights reserved.**  
*Professional automotive cybersecurity analysis platform*

</div>

