# QuickTARA

**Threat Analysis and Risk Assessment (TARA) for automotive cybersecurity, with native EU Cyber Resilience Act compliance.**

[![Version](https://img.shields.io/badge/version-2.2.0-brightgreen.svg)](https://github.com/leonkalema/QuickTARA/releases)
[![ISO 21434](https://img.shields.io/badge/ISO%2021434-aligned-blue.svg)](https://www.iso.org/standard/70918.html)
[![UN R155](https://img.shields.io/badge/UN%20R155-aligned-blue.svg)](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security)
[![EU CRA](https://img.shields.io/badge/EU%20CRA-compliance%20module-orange.svg)](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)

Website: **[www.quicktara.com](https://www.quicktara.com)**

---

## What it is

QuickTARA is a web application that guides an automotive cybersecurity team
through the full ISO/SAE 21434 TARA workflow — product scoping, asset
identification, damage and threat scenarios, risk assessment, and risk
treatment — and then produces the compliance artefacts those activities are
supposed to generate: internal traceability reports, customer-facing
compliance summaries, and the seven-section Annex VII technical documentation
required by the EU Cyber Resilience Act (Regulation (EU) 2024/2847).

It is **not** a generic GRC tool with an automotive skin. The data model,
impact categories (SFOP — Safety, Financial, Operational, Privacy), attack
feasibility method, and regulation-to-requirement mappings are all built for
ISO 21434, UN R155, and the CRA specifically.

## What it does

### ISO 21434 / UN R155 TARA workflow

- **Product scoping** — multi-product, per-organization, version-tracked
- **Assets & components** — CIA properties, trust boundaries, component relationships
- **Damage scenarios** — SFOP impact rating (Safety / Financial / Operational / Privacy), severity, regulatory tags
- **Threat scenarios** — STRIDE categorisation, many-to-many linkage to damage scenarios, attack-vector analysis
- **Risk assessment** — attack-feasibility using ISO 21434 Annex G parameters (time, expertise, knowledge, opportunity, equipment), automated risk calculation with manual review
- **Risk treatment** — controls catalog, treatment decisions, residual-risk tracking

### EU Cyber Resilience Act compliance module

Requirements are mapped to exact Annex I section references (§1–§10 Part I, §1–§8 Part II) per Regulation (EU) 2024/2847.

- **Product classification** — wizard determines Default / Class I / Class II / Critical / **Art. 24 open-source steward**; maps to conformity module (A, B+C, H, or security attestation); automotive exclusion per Art. 2(2)(c) flagged as provisional
- **Auto-mapping** — existing TARA artefacts (assets, damage scenarios, controls) are mapped to the **9 Annex I Part I technical requirements** (CRA-01 to CRA-09); CRA-09 covers §1 (no known exploitable vulns) + §10 (update capability); CRA-13 covers §4–§6 (disclosure, CVD policy, contact address). Part II process obligations (CRA-10 to CRA-14: SBOM, VDP, update mechanism, disclosure, reporting) are tracked separately and require organisational documentation, not TARA output — each has a dedicated tab
- **Gap analysis** — per-requirement status, evidence, owner, target date, gap severity, residual risk
- **Compensating controls** — catalog and workflow for legacy products that cannot be redesigned (Art. 5(3))
- **SBOM ingestion (Art. 13(6))** — upload CycloneDX 1.4+/1.5 or SPDX 2.3; parse components, versions, `purl`, supplier, licenses, hashes; auto-map to CRA-10
- **Incident reporting (Art. 14)** — three independent deadline clocks (24h early warning / 72h incident report / 14d final report); structured export ready for the ENISA Single Reporting Platform
- **Annex VII generator** — seven-section technical documentation assembled from the live TARA data, with completeness %, action-required flags, and Markdown export (Pandoc-ready for PDF/DOCX)
- **Conformity workflow (Art. 13)** — seven-step checklist tracking the procedural compliance acts beyond Annex I: conformity assessment module, EU Declaration of Conformity (Annex V), CE marking, EU central database registration (Art. 31), 10-year documentation retention (Art. 23(1)), post-market surveillance plan, and EOSS publication
- **Annex II checklist** — all 9 mandatory user-information items (Art. 13(20) + Annex II); support-period item auto-derived from stored EOSS date; remaining items flagged for manual documentation review
- **Reports** — audit traceability (internal, full requirement × control matrix) and customer compliance summary (external, Annex A with all 18 requirements)
- **Inventory** — SKU, firmware version, units in field/stock, OEM customer, target market

### Platform

- **RBAC** — system admin, organization admin, risk manager, analyst
- **Multi-organization** — users can belong to multiple organizations with different roles
- **Audit trail** — immutable action log, evidence attachments, approval workflows, snapshots
- **Reports** — PDF (ReportLab), Excel, JSON, Text
- **On-premise** — runs in your network, no cloud dependency, SQLite / MySQL / PostgreSQL

---

## Install

### Recommended (review before running)

Download the installer, inspect it, then run it. This is the right pattern
for any install script you don't already trust.

**macOS / Linux:**
```bash
curl -fsSLo office-deploy.sh https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh
less office-deploy.sh    # review what it does
bash office-deploy.sh
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.ps1 -OutFile office-deploy.ps1
Get-Content office-deploy.ps1 | more   # review what it does
.\office-deploy.ps1
```

### One-liner (convenience only)

For demo / throwaway environments. Equivalent trust model to `git clone &&
./install.sh` — you are running unreviewed code from this repository:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh | bash
```

```powershell
# Windows
irm https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.ps1 | iex
```

The script body is wrapped in a `main` function with a single trailing call,
so a partially-downloaded script cannot execute partially.

> **Windows prerequisites:** [Python 3](https://www.python.org/downloads/) (check *Add Python to PATH*), [Node.js LTS](https://nodejs.org/), [Git for Windows](https://git-scm.com/download/win).

### What the installer does

Clones the repo, builds the SvelteKit frontend, starts the FastAPI backend,
runs database migrations, creates an initial System Administrator with a
randomly generated 144-bit password, and writes the credentials to
`quicktara-initial-credentials.txt` (mode `0600`).

**HTTPS is on by default.** The installer generates a self-signed TLS
certificate (valid 2 years) using `openssl` and serves both the frontend
and backend over HTTPS. Browsers will show a one-time warning for the
self-signed cert; accept it, or import `./certs/quicktara.crt` into your
OS trust store, or supply your own cert via `QUICKTARA_SSL_CERTFILE` /
`QUICKTARA_SSL_KEYFILE` before running.

**Default URLs (HTTPS):**

- Frontend: `https://localhost:4173`
- Backend: `https://localhost:8080`
- LAN access: `https://<your-ip>:4173` and `https://<your-ip>:8080`

### Opting out of TLS (NOT recommended)

Only safe behind a reverse proxy that terminates TLS for you, or on a
fully trusted local development machine. **Never use this on a LAN or any
network where credentials could be observed in transit.**

```bash
# macOS/Linux
QUICKTARA_DISABLE_TLS=1 bash office-deploy.sh

# Windows PowerShell
$env:QUICKTARA_DISABLE_TLS = "1"; .\office-deploy.ps1
```

**First login:** open `quicktara-initial-credentials.txt`, sign in, change
the password immediately under *Settings → My Account*, then delete the
file. The bootstrap account exists only to let you create your own admin —
it is never reused or regenerated.

## Production configuration

| Environment variable | Purpose |
|---|---|
| `QUICKTARA_SSL_CERTFILE` | Path to TLS certificate (PEM). Enables HTTPS when paired with key. |
| `QUICKTARA_SSL_KEYFILE` | Path to TLS private key (PEM). |
| `QUICKTARA_JWT_SECRET` | JWT signing secret. Auto-generated to `.quicktara_jwt_secret` (mode `0600`) if unset. |
| `QUICKTARA_CORS_ORIGINS` | Comma-separated allow-list of additional frontend origins. |
| `QUICKTARA_DB_*` | Override the default SQLite database to use MySQL or PostgreSQL. |

Security defaults: CORS is locked to known origins, security headers are
set, the login endpoint is rate-limited to 10/min per IP, and sessions use
JWT with refresh tokens and bcrypt password hashing.

## Requirements

- Python 3.8+
- Node.js 16+ and npm
- Git
- 2 GB RAM minimum (4 GB recommended), 1 GB disk
- macOS 10.15+, Linux, Windows 10+, or any Docker host

---

## Roles and permissions

| Capability | System admin | Org admin | Risk manager | Analyst |
|---|:-:|:-:|:-:|:-:|
| User management | ✓ | ✓ (org scope) | — | — |
| System configuration | ✓ | — | — | — |
| Settings access | ✓ | ✓ | — | — |
| Create assets & scenarios | ✓ | ✓ | ✓ | ✓ |
| Edit / delete assets | ✓ | ✓ | ✓ | — |
| Delete scenarios | ✓ | ✓ | — | — |
| Risk assessment | ✓ | ✓ | ✓ | ✓ (draft) |
| Approve risk treatments | ✓ | ✓ | ✓ | — |
| Generate reports | ✓ | ✓ | ✓ | view-only |

The initial bootstrap account is a System Administrator; rotate its
password, create a per-user admin, and delete the bootstrap credentials
file before opening the instance to others.

---

## Architecture

- **Backend:** FastAPI (Python 3.8+), SQLAlchemy, Alembic migrations
- **Frontend:** SvelteKit (in `tara-web/`)
- **Database:** SQLite (default), MySQL, or PostgreSQL
- **Reports:** ReportLab (PDF), OpenPyXL (Excel)
- **Entry point:** `quicktara_web.py` — called by `office-deploy.sh` (macOS/Linux), `office-deploy.ps1` (Windows), and `Dockerfile`

### Deployment modes

- **Local** — single user, SQLite, self-signed HTTPS
- **LAN** — team within an office network, MySQL or PostgreSQL, self-signed or internal CA
- **Cloud / on-premise server** — bring your own TLS certificate via `QUICKTARA_SSL_*`

---

## Project status

### Shipped

- Full ISO 21434 TARA workflow: products, assets, damage scenarios, threat scenarios, risk assessment, risk treatment
- RBAC with four roles and multi-organization membership
- JWT authentication with refresh tokens, bcrypt, rate-limited login
- Reports: PDF, Excel, JSON, text with ISO 21434 documentation sections
- CRA module: classification wizard (Default / Class I / II / Critical / Art. 24 steward), auto-mapping, gap analysis, compensating controls
- CRA SBOM ingestion (Art. 13(6)) — CycloneDX and SPDX
- CRA incident reporting (Art. 14) — 24h / 72h / 14d deadline tracking with ENISA export
- CRA Annex VII generator — seven-section technical documentation in Markdown
- CRA conformity workflow (Art. 13) — seven-step checklist: DoC, CE marking, EU registration (Art. 31), retention, post-market surveillance
- CRA Annex II checklist — all 9 mandatory user-information items; auto-derives support-period status from EOSS date
- Audit trail — immutable log, evidence attachments, approval workflows, snapshots
- SFOP risk calculator — Safety, Financial, Operational, Privacy
- ISO 21434 requirement traceability

### Planned

- Executive dashboards and C-level summaries
- Custom report templates and branding
- SSO / LDAP integration
- Multi-tenant isolation hardening
- Encryption at rest and managed-cert HTTPS
- Automated periodic compliance re-assessment

### Known limitations

Structural shortcuts and areas under active paydown are tracked in
[`TECH_DEBT.md`](./TECH_DEBT.md).

---

## Contributing

Issues and pull requests are welcome. For substantive changes, open an issue
first so the approach can be discussed before code is written.

## Contact

**Website:** [www.quicktara.com](https://www.quicktara.com)
**Issues:** [github.com/leonkalema/QuickTARA/issues](https://github.com/leonkalema/QuickTARA/issues)

---

© 2025–2026 QuickTARA. All rights reserved.
