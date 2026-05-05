#Requires -Version 5.1
<#
.SYNOPSIS
    QuickTARA Office Deployment Script for Windows
.DESCRIPTION
    Deploys QuickTARA on a Windows machine for LAN office use.
    Run from PowerShell as a normal user (no admin required unless installing Python/Node).
.EXAMPLE
    # Basic HTTP deploy (recommended for LAN):
    .\office-deploy.ps1

    # With plain HTTP (NOT recommended; only safe behind a TLS-terminating proxy):
    $env:QUICKTARA_DISABLE_TLS = "1"; .\office-deploy.ps1

    # Pre-set admin email to skip the prompt:
    $env:QUICKTARA_ADMIN_EMAIL = "admin@yourcompany.com"; .\office-deploy.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "QuickTARA Office Deployment Script (Windows)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
$FrontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { "4173" }
$ApiPort      = if ($env:API_PORT)      { $env:API_PORT }      else { "8080"  }
# TLS is ON by default (CRA Annex I 1(b) -- secure by default).
# Set QUICKTARA_DISABLE_TLS=1 only if you intentionally want plain HTTP
# (e.g. behind a reverse proxy that terminates TLS for you).
$DisableTLS   = ($env:QUICKTARA_DISABLE_TLS -eq "1")
$SslDir       = if ($env:SSL_DIR) { $env:SSL_DIR } else { ".\certs" }
$SslCert      = if ($env:QUICKTARA_SSL_CERTFILE) { $env:QUICKTARA_SSL_CERTFILE } else { "$SslDir\quicktara.crt" }
$SslKey       = if ($env:QUICKTARA_SSL_KEYFILE)  { $env:QUICKTARA_SSL_KEYFILE  } else { "$SslDir\quicktara.key" }

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
Write-Host ""

# ---------------------------------------------------------------------------
# TLS certificate -- ON by default; set QUICKTARA_DISABLE_TLS=1 to opt out
# ---------------------------------------------------------------------------
if (-not $DisableTLS) {
    if (-not (Test-Path $SslCert) -or -not (Test-Path $SslKey)) {
        Write-Host "Generating self-signed TLS certificate..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Force -Path $SslDir | Out-Null

        if (Get-Command "openssl" -ErrorAction SilentlyContinue) {
            # Prefer openssl if available (cross-platform cert format)
            $AbsSslDir  = (Resolve-Path $SslDir).Path
            $SslCert    = "$AbsSslDir\quicktara.crt"
            $SslKey     = "$AbsSslDir\quicktara.key"
            openssl req -x509 -newkey rsa:4096 -sha256 -days 730 -nodes `
                -keyout $SslKey -out $SslCert `
                -subj "/CN=quicktara.local" `
                -addext "subjectAltName=IP:127.0.0.1,IP:${LanIP},DNS:localhost,DNS:quicktara.local" 2>$null
        } else {
            # Fall back to PowerShell's built-in cert (Windows only, no separate key file)
            Write-Host "  openssl not found. Using Windows New-SelfSignedCertificate..." -ForegroundColor Yellow
            $cert = New-SelfSignedCertificate `
                -DnsName "quicktara.local","localhost" `
                -CertStoreLocation "Cert:\CurrentUser\My" `
                -NotAfter (Get-Date).AddYears(2)
            $AbsSslDir = (Resolve-Path $SslDir).Path
            $SslCert   = "$AbsSslDir\quicktara.crt"
            $SslKey    = "$AbsSslDir\quicktara.key"
            # Export PEM cert
            $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
            $b64 = [Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
            "-----BEGIN CERTIFICATE-----`n$b64`n-----END CERTIFICATE-----" | Set-Content $SslCert

            # Export PEM private key (requires .NET 5+ or Windows 10 1809+)
            try {
                $rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
                $keyBytes = $rsa.ExportRSAPrivateKey()
                $kb64 = [Convert]::ToBase64String($keyBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
                "-----BEGIN RSA PRIVATE KEY-----`n$kb64`n-----END RSA PRIVATE KEY-----" | Set-Content $SslKey
            } catch {
                Write-Host "  WARNING: Could not export private key. TLS disabled." -ForegroundColor Yellow
                $SslCert = ""; $SslKey = ""
            }
        }

        if ($SslCert -and (Test-Path $SslCert)) {
            Write-Host "  Certificate: $SslCert" -ForegroundColor Green
            Write-Host "  WARNING: Self-signed cert -- browsers will show a security warning." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Using existing TLS certificate: $SslCert" -ForegroundColor Green
        $SslCert = (Resolve-Path $SslCert).Path
        $SslKey  = (Resolve-Path $SslKey).Path
    }
} else {
    Write-Host "WARNING: QUICKTARA_DISABLE_TLS=1 -- running in plain HTTP mode." -ForegroundColor Red
    Write-Host "  This is only safe behind a reverse proxy that terminates TLS for you," -ForegroundColor Red
    Write-Host "  or on a fully trusted local development machine. Do NOT use this on a LAN" -ForegroundColor Red
    Write-Host "  or any network where credentials could be observed in transit." -ForegroundColor Red
    $SslCert = ""; $SslKey = ""
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
# Frontend build + start (background)
# ---------------------------------------------------------------------------
$FrontendPID = $null
if (Test-Path "tara-web") {
    Write-Host "Building QuickTARA frontend..." -ForegroundColor Cyan
    Push-Location "tara-web"

    # Write .env.local
    $ApiScheme = if ($SslCert -and $SslKey) { "https" } else { "http" }
    @"
# Auto-generated by QuickTARA installer
VITE_API_BASE_URL="${ApiScheme}://localhost:${ApiPort}/api"
"@ | Set-Content ".env.local" -Encoding UTF8

    # Set TLS env for vite preview if needed
    if ($SslCert -and $SslKey) {
        $env:QUICKTARA_SSL_CERTFILE = $SslCert
        $env:QUICKTARA_SSL_KEYFILE  = $SslKey
    }

    npm install --silent
    npm run build --silent

    Write-Host "Starting QuickTARA frontend (background)..." -ForegroundColor Cyan
    $FrontendLog = "$env:USERPROFILE\quicktara-frontend.log"
    $FrontendProc = Start-Process -FilePath "npm" `
        -ArgumentList "run", "preview", "--", "--host", "0.0.0.0", "--port", $FrontendPort `
        -NoNewWindow -PassThru `
        -RedirectStandardOutput $FrontendLog `
        -RedirectStandardError  "$env:USERPROFILE\quicktara-frontend-err.log"
    $FrontendPID = $FrontendProc.Id
    Write-Host "  Frontend started (PID $FrontendPID)" -ForegroundColor Green
    Write-Host "  Log: $FrontendLog" -ForegroundColor Gray

    Pop-Location
} else {
    Write-Host "WARNING: 'tara-web' directory not found. Skipping frontend." -ForegroundColor Yellow
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
        -ArgumentList "quicktara_web.py", "--db", ".\quicktara.db", "--host", "127.0.0.1", "--port", $ApiPort `
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
# Summary
# ---------------------------------------------------------------------------
$Scheme   = if ($SslCert -and $SslKey) { "https" } else { "http" }
$FeScheme = if ($SslCert -and $SslKey) { "https" } else { "http" }

$env:QUICKTARA_CORS_ORIGINS = "${FeScheme}://localhost:${FrontendPort},${FeScheme}://${LanIP}:${FrontendPort}"

if (Test-Path "quicktara-initial-credentials.txt") {
    Write-Host "Initial admin credentials written to:" -ForegroundColor Yellow
    Write-Host "  $RepoRoot\quicktara-initial-credentials.txt" -ForegroundColor Yellow
    Write-Host "  Sign in once, change the password, then DELETE this file." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "QuickTARA is starting..." -ForegroundColor Cyan
Write-Host "  Backend (API):"
Write-Host "    Local : ${Scheme}://localhost:${ApiPort}"
Write-Host "    LAN   : ${Scheme}://${LanIP}:${ApiPort}"
if ($FrontendPID) {
    Write-Host "  Frontend (SvelteKit):"
    Write-Host "    Local : ${FeScheme}://localhost:${FrontendPort}"
    Write-Host "    LAN   : ${FeScheme}://${LanIP}:${FrontendPort}"
}
Write-Host ""
Write-Host "Press Ctrl+C to stop the backend server." -ForegroundColor Gray
Write-Host ""

# ---------------------------------------------------------------------------
# Start backend (foreground)
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

& $PythonVenv quicktara_web.py --host 0.0.0.0 --port $ApiPort @SslArgs
