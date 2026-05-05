#!/bin/bash
set -e

# All logic lives inside main() so a truncated `curl | bash` cannot execute
# partial commands — the trailing `main "$@"` only runs when the entire
# script has been received and parsed successfully.
main() {

echo "🚀 QuickTARA Office Deployment Script"
echo "======================================"

# Configuration
FRONTEND_PORT=${FRONTEND_PORT:-4173}
API_PORT=${API_PORT:-8080}
# TLS is ON by default (CRA Annex I 1(b) — secure by default).
# Set QUICKTARA_DISABLE_TLS=1 only if you intentionally want plain HTTP
# (e.g. behind a reverse proxy that terminates TLS for you).
DISABLE_TLS=${QUICKTARA_DISABLE_TLS:-0}
SSL_DIR="${SSL_DIR:-./certs}"
SSL_CERT="${QUICKTARA_SSL_CERTFILE:-$SSL_DIR/quicktara.crt}"
SSL_KEY="${QUICKTARA_SSL_KEYFILE:-$SSL_DIR/quicktara.key}"

# Get local IP for LAN access
get_lan_ip() {
  if command -v ipconfig >/dev/null 2>&1; then
    ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "0.0.0.0"
  elif command -v hostname >/dev/null 2>&1; then
    hostname -I 2>/dev/null | awk '{print $1}'
  else
    echo "0.0.0.0"
  fi
}
LAN_IP="$(get_lan_ip)"

echo "📍 Detected LAN IP: $LAN_IP"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# ------------------------------------------------------------------
# Admin account setup
# ------------------------------------------------------------------
if [ -z "${QUICKTARA_ADMIN_EMAIL:-}" ]; then
  printf "📧 Enter admin email address [admin@quicktara.local]: "
  read -r QUICKTARA_ADMIN_EMAIL </dev/tty
  QUICKTARA_ADMIN_EMAIL="${QUICKTARA_ADMIN_EMAIL:-admin@quicktara.local}"
fi
# Basic validation
case "$QUICKTARA_ADMIN_EMAIL" in
  *@*.*) ;;
  *) echo "❌ '$QUICKTARA_ADMIN_EMAIL' doesn't look like a valid email. Aborting."; exit 1 ;;
esac
export QUICKTARA_ADMIN_EMAIL
echo "✅ Admin email: $QUICKTARA_ADMIN_EMAIL"
echo ""

# ------------------------------------------------------------------
# TLS certificate — ON by default; set QUICKTARA_DISABLE_TLS=1 to opt out
# ------------------------------------------------------------------
if [ "$DISABLE_TLS" != "1" ]; then
  if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    if command -v openssl >/dev/null 2>&1; then
      echo "🔐 Generating self-signed TLS certificate (valid 2 years)..."
      mkdir -p "$SSL_DIR"
      openssl req -x509 -newkey rsa:4096 -sha256 -days 730 -nodes \
        -keyout "$SSL_KEY" -out "$SSL_CERT" \
        -subj "/CN=quicktara.local" \
        -addext "subjectAltName=IP:127.0.0.1,IP:${LAN_IP},DNS:localhost,DNS:quicktara.local" \
        2>/dev/null
      echo "   Certificate: $SSL_CERT"
      echo "   ⚠️  Self-signed — browsers will show a security warning on first visit."
      echo "      Accept the warning once, or install the cert in your OS trust store,"
      echo "      or supply your own cert via QUICKTARA_SSL_CERTFILE / QUICKTARA_SSL_KEYFILE."
    else
      echo "❌ openssl not found — cannot generate TLS certificate."
      echo "   Install openssl, OR re-run with QUICKTARA_DISABLE_TLS=1 to explicitly"
      echo "   opt out of HTTPS (NOT recommended; only safe behind a reverse proxy"
      echo "   that terminates TLS for you)."
      exit 1
    fi
  else
    echo "🔐 Using existing TLS certificate: $SSL_CERT"
  fi
  # Resolve to absolute paths now — the script changes directory later and relative paths break
  if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
    SSL_CERT="$(cd "$(dirname "$SSL_CERT")" && pwd)/$(basename "$SSL_CERT")"
    SSL_KEY="$(cd "$(dirname "$SSL_KEY")" && pwd)/$(basename "$SSL_KEY")"
  fi
else
  echo "⚠️  QUICKTARA_DISABLE_TLS=1 — running in plain HTTP mode."
  echo "   This is only safe behind a reverse proxy that terminates TLS for you,"
  echo "   or on a fully trusted local development machine. Do NOT use this on a LAN"
  echo "   or any network where credentials could be observed in transit."
  SSL_CERT=""
  SSL_KEY=""
fi
echo ""

# Clone or update repository
if [ -d "QuickTARA" ]; then
    echo "📁 Updating existing QuickTARA..."
    cd QuickTARA
    git pull
else
    echo "📥 Cloning QuickTARA..."
    git clone --depth=1 https://github.com/leonkalema/QuickTARA.git
    cd QuickTARA
    # Remove dev-only files not needed at runtime
    rm -rf tests/ docs/ TECH_DEBT.md CONTRIBUTING.md .github/
fi

echo ""

# Create virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""

# Build and start frontend
echo "🧩 Building QuickTARA frontend..."
if [ -d "tara-web" ]; then
  cd tara-web
  
  # Create .env.local file for frontend API connection (secure, not committed to git)
  echo "⚙️  Configuring frontend environment..."
  _API_SCHEME="http"
  if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then _API_SCHEME="https"; fi
  cat > .env.local << EOF
# Auto-generated by QuickTARA installer
VITE_API_BASE_URL="${_API_SCHEME}://localhost:${API_PORT}/api"
EOF

  # Export TLS paths so vite preview can pick them up (already absolute, set before any cd)
  if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
    export QUICKTARA_SSL_CERTFILE="$SSL_CERT"
    export QUICKTARA_SSL_KEYFILE="$SSL_KEY"
  fi

  npm install --silent
  npm run build --silent
  echo "🌐 Starting QuickTARA frontend..."
  nohup npm run preview -- --host 0.0.0.0 --port "${FRONTEND_PORT}" > "$HOME/quicktara-frontend.log" 2>&1 &
  FRONTEND_PID=$!
  cd ..
  echo "Frontend started with PID: $FRONTEND_PID"
else
  echo "⚠️ 'tara-web' directory not found. Skipping frontend."
  FRONTEND_PID=""
fi

echo ""

# Create default SQLite database (no config needed)
echo "🗄️  Setting up database..."
if [ ! -f "quicktara.db" ]; then
    echo "Creating new database..."
    QUICKTARA_SSL_CERTFILE="" QUICKTARA_SSL_KEYFILE="" python quicktara_web.py --db ./quicktara.db --host 127.0.0.1 --port ${API_PORT} &
    SERVER_PID=$!
    sleep 5
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Database initialized"
else
    echo "✅ Existing database found - preserving data"
fi

# Apply any new schema migrations (safe to re-run; alembic is idempotent)
if [ -f "alembic.ini" ]; then
    echo "🛠️  Applying database migrations..."
    if alembic upgrade head; then
        echo "✅ Migrations up to date"
    else
        echo "⚠️  alembic upgrade head failed — check the log above. Server will still start."
    fi
fi

echo ""
_SCHEME="http"
_SSL_ARGS=""
if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
  _SCHEME="https"
  _SSL_ARGS="--ssl-certfile $SSL_CERT --ssl-keyfile $SSL_KEY"
else
  # Explicitly clear TLS env vars so stale values from a previous HTTPS install
  # don't cause quicktara_web.py to silently re-enable TLS (its argparse defaults
  # to QUICKTARA_SSL_CERTFILE / QUICKTARA_SSL_KEYFILE if set in the environment).
  unset QUICKTARA_SSL_CERTFILE QUICKTARA_SSL_KEYFILE
fi

# Export CORS origins so the backend allows the frontend origin
_FE_SCHEME="http"
if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then _FE_SCHEME="https"; fi
export QUICKTARA_CORS_ORIGINS="${_FE_SCHEME}://localhost:${FRONTEND_PORT},${_FE_SCHEME}://${LAN_IP}:${FRONTEND_PORT}"

if [ -f "./quicktara-initial-credentials.txt" ]; then
  echo ""
  echo "🔐 Initial admin credentials written to:"
  echo "   $(pwd)/quicktara-initial-credentials.txt (mode 0600)"
  echo "   ⚠️  Sign in once, change the password, then DELETE this file."
  echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "🚀 QuickTARA is starting..."
echo "   🖥️  Backend (API):"
echo "      • Local:  ${_SCHEME}://localhost:${API_PORT}"
echo "      • LAN:    ${_SCHEME}://${LAN_IP}:${API_PORT}"
if [ -n "${FRONTEND_PID:-}" ]; then
  echo "   🌐 Frontend (SvelteKit preview):"
  echo "      • Local:  ${_FE_SCHEME}://localhost:${FRONTEND_PORT}"
  echo "      • LAN:    ${_FE_SCHEME}://${LAN_IP}:${FRONTEND_PORT}"
  echo "      (log: $HOME/quicktara-frontend.log)"
else
  echo "   🌐 Frontend: Not started (tara-web missing)"
fi
echo ""
echo "Press Ctrl+C to stop the backend server."
echo ""

# Start server with LAN access
# shellcheck disable=SC2086
python quicktara_web.py --host 0.0.0.0 --port ${API_PORT} ${_SSL_ARGS}

}

# Single trailing call — guarantees the script is fully downloaded before any
# command runs, so a partial `curl | bash` cannot execute partially.
main "$@"
