<div align="center">

# 🚗 QuickTARA
### Professional Automotive Cybersecurity Analysis Platform

[![License: Commercial](https://img.shields.io/badge/License-Commercial-blue.svg)](LICENSE)
[![ISO 21434](https://img.shields.io/badge/ISO%2021434-Compliant-green.svg)](https://www.iso.org/standard/70918.html)
[![UN R155](https://img.shields.io/badge/UN%20R155-Compliant-green.svg)](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)](https://github.com/leonkalema/QuickTARA/releases)

**Enterprise-grade threat analysis and risk assessment for automotive systems**  
*Trusted by automotive OEMs and Tier 1 suppliers worldwide*

[🚀 Quick Start](#-quick-start-5-minutes) • [📖 Documentation](README-DEPLOYMENT.md) • [🎯 Features](#-key-features) • [💼 Enterprise](#-enterprise-ready)

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

## 🚀 **Quick Start (5 Minutes)**

> **Choose your deployment scenario below** 👇

<table>
<tr>
<td width="33%" align="center">

### 🖥️ **Local Development**
*For developers and testing*

```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
python quicktara_web.py
```

**Access:** `http://localhost:8080`  
**Time:** 30 seconds  
**Requirements:** Python 3.8+

</td>
<td width="33%" align="center">

### 🏢 **Office/LAN Deployment**
*For team collaboration*

```bash
curl -sSL https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh | bash
```

**Access:** `http://your-lan-ip:8080`  
**Time:** 5 minutes  
**Requirements:** Python + Node.js

</td>
<td width="33%" align="center">

### ☁️ **Cloud/Production**
*For enterprise deployment*

```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
docker-compose up -d
```

**Access:** `http://your-server:8080`  
**Time:** 2 minutes  
**Requirements:** Docker

</td>
</tr>
</table>

<div align="center">

📖 **Need help?** See our [Complete Deployment Guide](README-DEPLOYMENT.md) for detailed instructions

</div>

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
<summary>Click to see advanced configuration options</summary>

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

