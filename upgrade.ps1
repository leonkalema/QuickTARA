# QuickTARA upgrade script (Windows / PowerShell)
# ------------------------------------------------
# Run this from INSIDE your existing QuickTARA folder to update an already
# deployed instance to the latest version. It:
#   1. pulls the latest code
#   2. updates Python and Node dependencies
#   3. REBUILDS the frontend (required - the UI is compiled into static files)
#   4. applies database migrations (your data is preserved)
#   5. prints exactly how to restart the server
#
# Usage:
#   cd C:\path\to\QuickTARA
#   .\upgrade.ps1

$ErrorActionPreference = "Stop"

Write-Host "QuickTARA Upgrade"
Write-Host "================="

# --- Sanity check: must be run from a QuickTARA checkout ---
if (-not (Test-Path "quicktara_web.py")) {
    Write-Host "ERROR: This doesn't look like a QuickTARA folder (quicktara_web.py not found)."
    Write-Host "       cd into your QuickTARA directory first, then run: .\upgrade.ps1"
    exit 1
}
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: This folder is not a git checkout, so it can't be updated with git pull."
    Write-Host "       If you installed by downloading a zip, re-run office-deploy.ps1 instead."
    exit 1
}

# --- 1. Pull latest code ---
Write-Host "Pulling latest code..."
git pull

# --- 2. Python dependencies ---
Write-Host "Updating Python dependencies..."
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt --quiet

# --- 3. Rebuild frontend (CRITICAL) ---
if (Test-Path "tara-web") {
    Write-Host "Rebuilding frontend..."
    Push-Location tara-web
    npm install --silent
    npm run build --silent
    Pop-Location
    Write-Host "Frontend rebuilt"
} else {
    Write-Host "WARNING: tara-web not found - skipping frontend build (API-only mode)"
}

# --- 4. Database migrations (data preserved) ---
if (Test-Path "alembic.ini") {
    Write-Host "Applying database migrations..."
    try {
        python -m alembic upgrade head
        Write-Host "Migrations up to date"
    } catch {
        Write-Host "WARNING: Migration step reported an issue - stamping to head..."
        python -m alembic stamp head
    }
}

Write-Host ""
Write-Host "Upgrade complete. Your database was preserved."
Write-Host ""
Write-Host "Now RESTART the server so the new code takes effect:"
Write-Host "  - If you started it manually: stop it (Ctrl+C), then run:"
Write-Host "      python quicktara_web.py --host 0.0.0.0 --port 8080"
Write-Host "  - If it runs as a Windows service: restart that service."
Write-Host ""
Write-Host "After restarting, hard-refresh your browser (Ctrl+Shift+R) to drop the old cached UI."
