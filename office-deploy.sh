#!/bin/bash
set -e

# All logic lives inside main() so a truncated `curl | bash` cannot execute
# partial commands — the trailing `main "$@"` only runs when the entire
# script has been received and parsed successfully.
main() {

echo "🚀 QuickTARA Office Deployment Script"
echo "======================================"

# Configuration — single port serves both API and frontend
PORT=${QUICKTARA_PORT:-8080}

# TLS is opt-in. For production / internet-facing deployments, provide your own
# certificate via QUICKTARA_SSL_CERTFILE + QUICKTARA_SSL_KEYFILE, or run behind
# a reverse proxy (nginx/caddy) that terminates TLS.
# Set QUICKTARA_ENABLE_TLS=1 to generate a self-signed cert for testing.
ENABLE_TLS=${QUICKTARA_ENABLE_TLS:-0}
SSL_DIR="${SSL_DIR:-./certs}"
SSL_CERT="${QUICKTARA_SSL_CERTFILE:-}"
SSL_KEY="${QUICKTARA_SSL_KEYFILE:-}"

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

# ------------------------------------------------------------------
# Check prerequisites
# ------------------------------------------------------------------
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
case "$QUICKTARA_ADMIN_EMAIL" in
  *@*.*) ;;
  *) echo "❌ '$QUICKTARA_ADMIN_EMAIL' doesn't look like a valid email. Aborting."; exit 1 ;;
esac
export QUICKTARA_ADMIN_EMAIL
echo "✅ Admin email: $QUICKTARA_ADMIN_EMAIL"

if [ -z "${QUICKTARA_ORG_NAME:-}" ]; then
  printf "🏢 Enter organization name [Default Organization]: "
  read -r QUICKTARA_ORG_NAME </dev/tty
  QUICKTARA_ORG_NAME="${QUICKTARA_ORG_NAME:-Default Organization}"
fi
export QUICKTARA_ORG_NAME
echo "✅ Organization: $QUICKTARA_ORG_NAME"
echo ""

# ------------------------------------------------------------------
# TLS — opt-in only; HTTP is the default for local/office use
# ------------------------------------------------------------------
if [ "$ENABLE_TLS" = "1" ] && [ -z "$SSL_CERT" ] && [ -z "$SSL_KEY" ]; then
  SSL_CERT="$SSL_DIR/quicktara.crt"
  SSL_KEY="$SSL_DIR/quicktara.key"
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
    else
      echo "⚠️  openssl not found — falling back to HTTP."
      SSL_CERT=""
      SSL_KEY=""
    fi
  else
    echo "🔐 Using existing TLS certificate: $SSL_CERT"
  fi
fi

# Resolve cert paths to absolute (the script cds later)
if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
  SSL_CERT="$(cd "$(dirname "$SSL_CERT")" && pwd)/$(basename "$SSL_CERT")"
  SSL_KEY="$(cd "$(dirname "$SSL_KEY")" && pwd)/$(basename "$SSL_KEY")"
fi
echo ""

# ------------------------------------------------------------------
# Clone or update repository
# ------------------------------------------------------------------
if [ -d "QuickTARA" ]; then
    echo "📁 Updating existing QuickTARA..."
    cd QuickTARA
    git pull
else
    echo "📥 Cloning QuickTARA..."
    git clone --depth=1 https://github.com/leonkalema/QuickTARA.git
    cd QuickTARA
    rm -rf tests/ docs/ TECH_DEBT.md CONTRIBUTING.md .github/
fi

echo ""

# ------------------------------------------------------------------
# Python environment
# ------------------------------------------------------------------
echo "🐍 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo ""

# ------------------------------------------------------------------
# Build frontend (served by FastAPI on the same port)
# ------------------------------------------------------------------
echo "🧩 Building frontend..."
if [ -d "tara-web" ]; then
  cd tara-web
  npm install --silent
  npm run build --silent
  cd ..
  echo "✅ Frontend built (will be served at /)"
else
  echo "⚠️  tara-web/ not found — API-only mode"
fi

echo ""

# ------------------------------------------------------------------
# Database setup
# ------------------------------------------------------------------
echo "🗄️  Setting up database..."
if [ ! -f "quicktara.db" ]; then
    echo "Creating new database..."
    QUICKTARA_SSL_CERTFILE="" QUICKTARA_SSL_KEYFILE="" \
      python quicktara_web.py --db ./quicktara.db --host 127.0.0.1 --port "${PORT}" &
    SERVER_PID=$!
    sleep 5
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Database initialized"
else
    echo "✅ Existing database found — preserving data"
fi

if [ -f "alembic.ini" ]; then
    echo "🛠️  Applying database migrations..."
    if python -m alembic upgrade head 2>/dev/null; then
        echo "✅ Migrations up to date"
    else
        echo "⚠️  Migration failed — tables may already exist. Stamping to head..."
        python -m alembic stamp head 2>/dev/null || true
    fi
fi

echo ""

# ------------------------------------------------------------------
# Prepare startup
# ------------------------------------------------------------------
_SCHEME="http"
_SSL_ARGS=""
if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
  _SCHEME="https"
  _SSL_ARGS="--ssl-certfile $SSL_CERT --ssl-keyfile $SSL_KEY"
else
  unset QUICKTARA_SSL_CERTFILE QUICKTARA_SSL_KEYFILE 2>/dev/null || true
fi

if [ -f "./quicktara-initial-credentials.txt" ]; then
  echo "🔐 Initial admin credentials written to:"
  echo "   $(pwd)/quicktara-initial-credentials.txt (mode 0600)"
  echo "   ⚠️  Sign in once, change the password, then DELETE this file."
  echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "🚀 QuickTARA is running at:"
echo "   • Local:  ${_SCHEME}://localhost:${PORT}"
echo "   • LAN:    ${_SCHEME}://${LAN_IP}:${PORT}"
echo ""
if [ "$_SCHEME" = "http" ]; then
  echo "   ℹ️  Running over HTTP (fine for localhost and trusted office networks)."
  echo "   For HTTPS, see: https://github.com/leonkalema/QuickTARA#securing-your-deployment"
fi
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# shellcheck disable=SC2086
python quicktara_web.py --host 0.0.0.0 --port "${PORT}" ${_SSL_ARGS}

}

# Single trailing call — guarantees the script is fully downloaded before any
# command runs, so a partial `curl | bash` cannot execute partially.
main "$@"
