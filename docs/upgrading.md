# How to Upgrade QuickTARA

This guide covers upgrading any running QuickTARA installation to a newer version. Follow the section that matches how you originally installed it.

Before you start, check your current version. Open the app and look at the footer, or call the API:

```bash
curl -s http://localhost:8080/api/health
# Check /docs at the same address for the version string
```

---

## Office / Direct Install (office-deploy.sh)

This applies if you ran `office-deploy.sh` or started the app with `python quicktara_web.py`.

### Step 1: Back up your database

```bash
cp quicktara.db quicktara.db.bak-$(date +%Y%m%d)
```

Keep this file until you have confirmed the upgrade works. If you use MySQL or PostgreSQL, take a dump instead:

```bash
# MySQL
mysqldump -u quicktara -p quicktara > quicktara_backup_$(date +%Y%m%d).sql

# PostgreSQL
pg_dump quicktara > quicktara_backup_$(date +%Y%m%d).sql
```

### Step 2: Stop the running process

```bash
pkill -f quicktara_web.py
```

### Step 3: Pull the new code

```bash
cd /path/to/QuickTARA

# Latest on main
git pull origin main

# Or a specific release tag
git fetch --tags
git checkout v2.2.0
```

### Step 4: Update Python dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Rebuild the frontend

```bash
cd tara-web
npm install
npm run build
cd ..
```

### Step 6: Start the app

```bash
python quicktara_web.py
```

Database migrations run automatically on startup. Watch the log output for:

```
INFO - Running database migrations...
INFO - Database migrations completed successfully
```

If migrations fail, the app will not start. See the Rollback section below.

### Step 7: Verify

Open the app. Check the version number in the footer. It should match the release you checked out.

---

## Docker

This applies if you run QuickTARA with `docker compose`.

### Step 1: Back up your data volume

```bash
# SQLite — copy the database file out of the volume
docker run --rm \
  -v quicktara_quicktara_data:/data \
  -v $(pwd):/backup \
  busybox cp /data/quicktara.db /backup/quicktara.db.bak-$(date +%Y%m%d)
```

If you use MySQL, take a dump from the mysql container before proceeding.

### Step 2: Pull the new code

```bash
cd /path/to/QuickTARA
git pull origin main
```

### Step 3: Rebuild and restart

```bash
docker compose build
docker compose up -d
```

Migrations run automatically when the container starts. Check the logs:

```bash
docker compose logs -f quicktara
```

Look for `Database migrations completed successfully` before the app starts accepting requests.

### Step 4: Verify

```bash
curl -s http://localhost:8080/api/health
```

Open the app and check the version in the footer.

---

## Rollback

If the upgrade fails, revert in this order.

**1. Revert the database migration (if migrations ran)**

```bash
source .venv/bin/activate
alembic downgrade -1
```

Run this once per migration that was applied. Each release lists its migrations in the release notes under `docs/`.

**2. Revert the code**

```bash
git checkout v2.1.0   # replace with the previous version
```

**3. Restart**

```bash
python quicktara_web.py
```

For Docker:

```bash
git checkout v2.1.0
docker compose build
docker compose up -d
```

**4. Restore from backup (if needed)**

```bash
# SQLite
cp quicktara.db.bak-YYYYMMDD quicktara.db
python quicktara_web.py
```

Only restore from backup if the migration itself corrupted data, which is rare. The migration down-path is the correct first step.

---

## Checking migration status

To see which migration your database is currently on:

```bash
source .venv/bin/activate
alembic current
```

To see the full migration history:

```bash
alembic history --verbose
```

---

## Release notes

Each release has a document in `docs/` that lists what changed and any steps specific to that version. Read the release notes before upgrading across multiple versions. For example, `docs/upgrade-2.2.0.md` covers the changes in v2.2.0.
