#Requires -Version 5.1
<#
.SYNOPSIS
    QuickTARA Office Deployment Script for Windows
.DESCRIPTION
    Deploys QuickTARA on a Windows machine for LAN office use.
    Single port serves both API and frontend. HTTP by default.
    Run from PowerShell as a normal user (no admin required unless installing Python/Node).
.EXAMPLE
    # Default HTTP deploy (recommended for localhost / office LAN):
    .\office-deploy.ps1

    # With self-signed TLS for testing:
    $env:QUICKTARA_ENABLE_TLS = "1"; .\office-deploy.ps1

    # With your own TLS cert:
    $env:QUICKTARA_SSL_CERTFILE = "C:\certs\my.crt"
    $env:QUICKTARA_SSL_KEYFILE  = "C:\certs\my.key"
    .\office-deploy.ps1

    # Pre-set admin email to skip the prompt:
    $env:QUICKTARA_ADMIN_EMAIL = "admin@yourcompany.com"; .\office-deploy.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "QuickTARA Office Deployment Script (Windows)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Configuration — single port serves both API and frontend
# ---------------------------------------------------------------------------
$Port = if ($env:QUICKTARA_PORT) { $env:QUICKTARA_PORT } else { "8080" }

# TLS is opt-in. For production, provide your own cert or use a reverse proxy.
# Set QUICKTARA_ENABLE_TLS=1 to generate a self-signed cert for testing.
$EnableTLS = ($env:QUICKTARA_ENABLE_TLS -eq "1")
$SslDir    = if ($env:SSL_DIR) { $env:SSL_DIR } else { ".\certs" }
$SslCert   = if ($env:QUICKTARA_SSL_CERTFILE) { $env:QUICKTARA_SSL_CERTFILE } else { "" }
$SslKey    = if ($env:QUICKTARA_SSL_KEYFILE)  { $env:QUICKTARA_SSL_KEYFILE  } else { "" }

# ---------------------------------------------------------------------------
# Helper: get LAN IPv4 address (first non-loopback, non-APIPA)
# ---------------------------------------------------------------------------
function Get-LanIP {
    try {
        $ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
               Where-Object { $_.IPAddress -notmatch "^127\." -and
                               $_.IPAddress -notmatch "^169\.254\." -and
                               $_.PrefixOrigin -ne "WellKnown" } |
               Sort-Object InterfaceMetric |
               Select-Object -First 1).IPAddress
        if ($ip) { return $ip }
    } catch {}
    return "0.0.0.0"
}

$LanIP = Get-LanIP
Write-Host "Detected LAN IP: $LanIP" -ForegroundColor Yellow
Write-Host ""

# ---------------------------------------------------------------------------
# Helper: find Python executable
# ---------------------------------------------------------------------------
function Find-Python {
    foreach ($cmd in @("python", "python3", "py")) {
        $p = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($p) {
            # Make sure it's Python 3
            $ver = & $cmd --version 2>&1
            if ($ver -match "Python 3\.") { return $cmd }
        }
    }
    return $null
}

# ---------------------------------------------------------------------------
# Prerequisites check
# ---------------------------------------------------------------------------
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

$Python = Find-Python
if (-not $Python) {
    Write-Host "ERROR: Python 3 not found. Download from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "       Make sure to check 'Add Python to PATH' during install." -ForegroundColor Red
    exit 1
}
Write-Host "  Python : OK  ($Python)" -ForegroundColor Green

if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found. Download from https://nodejs.org/ (LTS version)" -ForegroundColor Red
    exit 1
}
Write-Host "  Node   : OK" -ForegroundColor Green

if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: npm not found. It should come with Node.js." -ForegroundColor Red
    exit 1
}
Write-Host "  npm    : OK" -ForegroundColor Green

if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: git not found. Download from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}
Write-Host "  git    : OK" -ForegroundColor Green
Write-Host ""

# ---------------------------------------------------------------------------
# Admin email
# ---------------------------------------------------------------------------
if (-not $env:QUICKTARA_ADMIN_EMAIL) {
    $input = Read-Host "Enter admin email address [admin@quicktara.local]"
    if ([string]::IsNullOrWhiteSpace($input)) { $input = "admin@quicktara.local" }
    $env:QUICKTARA_ADMIN_EMAIL = $input
}
if ($env:QUICKTARA_ADMIN_EMAIL -notmatch "^[^@]+@[^@]+\.[^@]+$") {
    Write-Host "ERROR: '$($env:QUICKTARA_ADMIN_EMAIL)' does not look like a valid email." -ForegroundColor Red
    exit 1
}
Write-Host "Admin email: $($env:QUICKTARA_ADMIN_EMAIL)" -ForegroundColor Green

if (-not $env:QUICKTARA_ORG_NAME) {
    $orgInput = Read-Host "Enter organization name [Default Organization]"
    if ([string]::IsNullOrWhiteSpace($orgInput)) { $orgInput = "Default Organization" }
    $env:QUICKTARA_ORG_NAME = $orgInput
}
Write-Host "Organization: $($env:QUICKTARA_ORG_NAME)" -ForegroundColor Green
Write-Host ""

# ---------------------------------------------------------------------------
# TLS — opt-in; HTTP is the default for local/office use
# ---------------------------------------------------------------------------
if ($EnableTLS -and (-not $SslCert) -and (-not $SslKey)) {
    $SslCert = "$SslDir\quicktara.crt"
    $SslKey  = "$SslDir\quicktara.key"
    if (-not (Test-Path $SslCert) -or -not (Test-Path $SslKey)) {
        New-Item -ItemType Directory -Force -Path $SslDir | Out-Null
        if (Get-Command "openssl" -ErrorAction SilentlyContinue) {
            Write-Host "Generating self-signed TLS certificate..." -ForegroundColor Cyan
            $AbsSslDir = (Resolve-Path $SslDir).Path
            $SslCert   = "$AbsSslDir\quicktara.crt"
            $SslKey    = "$AbsSslDir\quicktara.key"
            openssl req -x509 -newkey rsa:4096 -sha256 -days 730 -nodes `
                -keyout $SslKey -out $SslCert `
                -subj "/CN=quicktara.local" `
                -addext "subjectAltName=IP:127.0.0.1,IP:${LanIP},DNS:localhost,DNS:quicktara.local" 2>$null
            Write-Host "  Certificate: $SslCert" -ForegroundColor Green
            Write-Host "  Self-signed — browsers will show a security warning." -ForegroundColor Yellow
        } else {
            Write-Host "  openssl not found — falling back to HTTP." -ForegroundColor Yellow
            $SslCert = ""; $SslKey = ""
        }
    } else {
        Write-Host "Using existing TLS certificate: $SslCert" -ForegroundColor Green
        $SslCert = (Resolve-Path $SslCert).Path
        $SslKey  = (Resolve-Path $SslKey).Path
    }
}
if ($SslCert -and $SslKey -and (Test-Path $SslCert) -and (Test-Path $SslKey)) {
    $SslCert = (Resolve-Path $SslCert).Path
    $SslKey  = (Resolve-Path $SslKey).Path
}
Write-Host ""

# ---------------------------------------------------------------------------
# Clone or update repository
# ---------------------------------------------------------------------------
if (Test-Path "QuickTARA") {
    Write-Host "Updating existing QuickTARA..." -ForegroundColor Cyan
    Push-Location "QuickTARA"
    git pull
} else {
    Write-Host "Cloning QuickTARA..." -ForegroundColor Cyan
    git clone --depth=1 https://github.com/leonkalema/QuickTARA.git
    Push-Location "QuickTARA"
    # Remove dev-only files not needed at runtime
    @("tests", "docs", "TECH_DEBT.md", "CONTRIBUTING.md", ".github") | ForEach-Object {
        if (Test-Path $_) { Remove-Item $_ -Recurse -Force }
    }
}
$RepoRoot = (Get-Location).Path
Write-Host ""

# ---------------------------------------------------------------------------
# Python virtual environment
# ---------------------------------------------------------------------------
Write-Host "Setting up Python virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    & $Python -m venv .venv
}
$PythonVenv = "$RepoRoot\.venv\Scripts\python.exe"
$PipVenv    = "$RepoRoot\.venv\Scripts\pip.exe"
$AlembicVenv = "$RepoRoot\.venv\Scripts\alembic.exe"

Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
& $PipVenv install -r requirements.txt --quiet
Write-Host "  Python deps installed" -ForegroundColor Green
Write-Host ""

# ---------------------------------------------------------------------------
# Build frontend (served by FastAPI on the same port)
# ---------------------------------------------------------------------------
if (Test-Path "tara-web") {
    Write-Host "Building frontend..." -ForegroundColor Cyan
    Push-Location "tara-web"
    npm install --silent
    npm run build --silent
    Pop-Location
    Write-Host "  Frontend built (will be served at /)" -ForegroundColor Green
} else {
    Write-Host "WARNING: tara-web/ not found — API-only mode" -ForegroundColor Yellow
}
Write-Host ""

# ---------------------------------------------------------------------------
# Database init + migrations
# ---------------------------------------------------------------------------
Write-Host "Setting up database..." -ForegroundColor Cyan
if (-not (Test-Path "quicktara.db")) {
    Write-Host "  Creating new database..."
    # Start briefly to trigger init_db(), then stop
    $env:QUICKTARA_SSL_CERTFILE = ""
    $env:QUICKTARA_SSL_KEYFILE  = ""
    $initProc = Start-Process -FilePath $PythonVenv `
        -ArgumentList "quicktara_web.py", "--db", ".\quicktara.db", "--host", "127.0.0.1", "--port", $Port `
        -NoNewWindow -PassThru
    Start-Sleep -Seconds 6
    $initProc | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  Database initialized" -ForegroundColor Green
} else {
    Write-Host "  Existing database found — preserving data" -ForegroundColor Green
}

if (Test-Path "alembic.ini") {
    Write-Host "  Applying database migrations..." -ForegroundColor Cyan
    try {
        & $AlembicVenv upgrade head
        Write-Host "  Migrations up to date" -ForegroundColor Green
    } catch {
        Write-Host "  WARNING: alembic upgrade head failed. Server will still start." -ForegroundColor Yellow
    }
}
Write-Host ""

# ---------------------------------------------------------------------------
# Summary and startup
# ---------------------------------------------------------------------------
$Scheme = if ($SslCert -and $SslKey) { "https" } else { "http" }

if (Test-Path "quicktara-initial-credentials.txt") {
    Write-Host "Initial admin credentials written to:" -ForegroundColor Yellow
    Write-Host "  $RepoRoot\quicktara-initial-credentials.txt" -ForegroundColor Yellow
    Write-Host "  Sign in once, change the password, then DELETE this file." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "QuickTARA is running at:" -ForegroundColor Cyan
Write-Host "    Local : ${Scheme}://localhost:${Port}"
Write-Host "    LAN   : ${Scheme}://${LanIP}:${Port}"
Write-Host ""
if ($Scheme -eq "http") {
    Write-Host "  Running over HTTP (fine for localhost and trusted office networks)." -ForegroundColor Gray
    Write-Host "  For HTTPS, see: https://github.com/leonkalema/QuickTARA#securing-your-deployment" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""

# ---------------------------------------------------------------------------
# Start server (foreground — single port serves API + frontend)
# ---------------------------------------------------------------------------
$SslArgs = @()
if ($SslCert -and $SslKey) {
    $env:QUICKTARA_SSL_CERTFILE = $SslCert
    $env:QUICKTARA_SSL_KEYFILE  = $SslKey
    $SslArgs = @("--ssl-certfile", $SslCert, "--ssl-keyfile", $SslKey)
} else {
    $env:QUICKTARA_SSL_CERTFILE = ""
    $env:QUICKTARA_SSL_KEYFILE  = ""
}

& $PythonVenv quicktara_web.py --host 0.0.0.0 --port $Port @SslArgs
