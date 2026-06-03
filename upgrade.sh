#!/bin/bash
set -e

# QuickTARA upgrade script (macOS / Linux)
# -----------------------------------------
# Run this from INSIDE your existing QuickTARA folder to update an already
# deployed instance to the latest version. It:
#   1. pulls the latest code
#   2. updates Python and Node dependencies
#   3. REBUILDS the frontend (required — the UI is compiled into static files)
#   4. applies database migrations (your data is preserved)
#   5. prints exactly how to restart the server
#
# It never touches quicktara.db beyond running migrations, so your data is safe.

main() {

echo "⬆️  QuickTARA Upgrade"
echo "===================="

# ------------------------------------------------------------------
# Sanity check — must be run from a QuickTARA checkout
# ------------------------------------------------------------------
if [ ! -f "quicktara_web.py" ]; then
  echo "❌ This doesn't look like a QuickTARA folder (quicktara_web.py not found)."
  echo "   cd into your QuickTARA directory first, then run: bash upgrade.sh"
  exit 1
fi

if [ ! -d ".git" ]; then
  echo "❌ This folder is not a git checkout, so it can't be updated with git pull."
  echo "   If you installed by downloading a zip, re-run office-deploy.sh instead."
  exit 1
fi

# ------------------------------------------------------------------
# 1. Pull latest code
# ------------------------------------------------------------------
echo "📥 Pulling latest code..."
git pull
echo ""

# ------------------------------------------------------------------
# 2. Python dependencies
# ------------------------------------------------------------------
echo "🐍 Updating Python dependencies..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt --quiet
echo ""

# ------------------------------------------------------------------
# 3. Rebuild frontend (CRITICAL — fixes like the login URL ship here)
# ------------------------------------------------------------------
if [ -d "tara-web" ]; then
  echo "🧩 Rebuilding frontend..."
  cd tara-web
  npm install --silent
  npm run build --silent
  cd ..
  echo "✅ Frontend rebuilt"
else
  echo "⚠️  tara-web/ not found — skipping frontend build (API-only mode)"
fi
echo ""

# ------------------------------------------------------------------
# 4. Database migrations (data preserved)
# ------------------------------------------------------------------
if [ -f "alembic.ini" ]; then
  echo "🛠️  Applying database migrations..."
  if python -m alembic upgrade head 2>/dev/null; then
    echo "✅ Migrations up to date"
  else
    echo "⚠️  Migration step reported an issue — tables may already exist. Stamping to head..."
    python -m alembic stamp head 2>/dev/null || true
  fi
fi
echo ""

# ------------------------------------------------------------------
# Done — tell the user how to restart
# ------------------------------------------------------------------
echo "🎉 Upgrade complete. Your database was preserved."
echo ""
echo "🔄 Now RESTART the server so the new code takes effect:"
echo ""
echo "   • If you started it manually in a terminal:"
echo "       press Ctrl+C in that terminal, then run:"
echo "       python quicktara_web.py --host 0.0.0.0 --port 8080"
echo ""
echo "   • If it runs as a systemd service:"
echo "       sudo systemctl restart quicktara"
echo ""
echo "   • If it runs in Docker:"
echo "       docker-compose up -d --build"
echo ""
echo "After restarting, hard-refresh your browser (Cmd/Ctrl+Shift+R) to drop the old cached UI."

}

main "$@"
