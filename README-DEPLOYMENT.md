# QuickTARA Deployment Guide

This guide covers three deployment scenarios. Pick the one that matches your situation.

---

## Scenario 1: Just Me, On My Laptop

**Time:** 2 minutes | **Audience:** Individual analyst

### Prerequisites

- Python 3.8+ ([download](https://www.python.org/downloads/))
- Node.js 18+ ([download](https://nodejs.org/))
- Git ([download](https://git-scm.com/))

### Steps

```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
pip install -r requirements.txt
cd tara-web && npm install && npm run build && cd ..
python quicktara_web.py
```

Open **http://localhost:8080** in your browser. That's it.

### First login

The installer creates an admin account. Check the terminal output for credentials, or look for `quicktara-initial-credentials.txt` in the project folder. **Change the password immediately** after first login (Settings → Profile), then delete the credentials file.

### What you get

- SQLite database (`quicktara.db`) — no setup needed
- Everything runs on port 8080 (API + frontend)
- HTTP only — safe on localhost, no cert warnings

---

## Scenario 2: My Team, On Our Office Network

**Time:** 5 minutes | **Audience:** Team of 2–20 on a shared LAN

### Option A: Automated installer (macOS / Linux)

```bash
# Review the script first:
curl -sSL https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh -o office-deploy.sh
less office-deploy.sh

# Then run it:
bash office-deploy.sh
```

### Option B: Automated installer (Windows)

```powershell
# Download and review:
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.ps1" -OutFile office-deploy.ps1
Get-Content office-deploy.ps1 | more

# Then run it:
.\office-deploy.ps1
```

The installer will:
1. Ask for your admin email address
2. Clone the repo, install dependencies, build the frontend
3. Initialize the database and start the server
4. Print the URL for your team to use

### What your team sees

Everyone on the LAN opens **http://YOUR-IP:8080** (the installer prints the exact URL). No browser warnings, no TLS issues — it just works.

### Adding team members

1. Log in as admin → **Settings → Users**
2. Click **Add User** — enter their email and assign a role
3. Share the URL and their temporary password
4. They log in and change their password

### Backing up your data

Your entire database is a single file: `quicktara.db`. To back up:

```bash
cp quicktara.db quicktara-backup-$(date +%Y%m%d).db
```

To restore, stop the server, replace `quicktara.db` with your backup, and restart.

### Updating to a new version

```bash
cd QuickTARA
git pull
pip install -r requirements.txt
cd tara-web && npm install && npm run build && cd ..
python quicktara_web.py --host 0.0.0.0 --port 8080
```

Your database is preserved — only code is updated.

---

## Scenario 3: Production / Intranet Server

**Time:** 15 minutes | **Audience:** IT-managed deployment

### Use a real TLS certificate

For production, do **not** use self-signed certificates. Instead:

**Option A — Reverse proxy (recommended)**

Put nginx or Caddy in front of QuickTARA. Caddy auto-provisions certificates from Let's Encrypt:

```
# Caddyfile
quicktara.yourcompany.com {
    reverse_proxy localhost:8080
}
```

QuickTARA runs on HTTP behind the proxy. Caddy handles TLS.

**Option B — Provide your own cert**

If you have a corporate CA or purchased certificate:

```bash
QUICKTARA_SSL_CERTFILE=/path/to/cert.pem \
QUICKTARA_SSL_KEYFILE=/path/to/key.pem \
python quicktara_web.py --host 0.0.0.0 --port 443
```

### Use a production database

For teams larger than 10, or if uptime matters, switch to PostgreSQL or MySQL:

```bash
# PostgreSQL
export QUICKTARA_DB_TYPE=postgresql
export QUICKTARA_DB_HOST=db.internal
export QUICKTARA_DB_NAME=quicktara
export QUICKTARA_DB_USER=quicktara
export QUICKTARA_DB_PASSWORD=<strong-password>
python quicktara_web.py --host 0.0.0.0
```

### Running as a service

**systemd (Linux):**

```ini
[Unit]
Description=QuickTARA
After=network.target

[Service]
WorkingDirectory=/opt/quicktara
ExecStart=/opt/quicktara/.venv/bin/python quicktara_web.py --host 0.0.0.0 --port 8080
Restart=always
User=quicktara

[Install]
WantedBy=multi-user.target
```

### Docker

```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
docker-compose up -d
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `QUICKTARA_PORT` | `8080` | Server port |
| `QUICKTARA_DB_TYPE` | `sqlite` | `sqlite`, `postgresql`, or `mysql` |
| `QUICKTARA_DB_HOST` | `localhost` | Database host (non-SQLite only) |
| `QUICKTARA_DB_PORT` | `5432`/`3306` | Database port |
| `QUICKTARA_DB_NAME` | `quicktara` | Database name |
| `QUICKTARA_DB_USER` | — | Database user |
| `QUICKTARA_DB_PASSWORD` | — | Database password |
| `QUICKTARA_SSL_CERTFILE` | — | Path to TLS certificate |
| `QUICKTARA_SSL_KEYFILE` | — | Path to TLS private key |
| `QUICKTARA_ENABLE_TLS` | `0` | Set to `1` to generate a self-signed cert |
| `QUICKTARA_ADMIN_EMAIL` | prompted | Admin email for initial setup |

## Resource Requirements

| | Minimum | Recommended |
|---|---------|-------------|
| **CPU** | 1 core | 2 cores |
| **RAM** | 512 MB | 2 GB |
| **Disk** | 1 GB | 10 GB SSD |

## Troubleshooting

**Port already in use:**
```bash
QUICKTARA_PORT=9000 python quicktara_web.py
```

**Frontend not loading (API-only mode):**
```bash
cd tara-web && npm install && npm run build && cd ..
# Restart the server — it auto-detects tara-web/build/
```

**Database migration error on startup:**
The server auto-recovers if tables already exist. Check the terminal log for "stamped to head" — this is normal after upgrades.
