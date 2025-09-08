# QuickTARA Deployment Guide

## 🚀 Three Ways to Deploy QuickTARA

### 1. **Local Development** (You - 30 seconds)
```bash
python quicktara_web.py
# Access: http://localhost:8080
```

### 2. **Office/LAN Deployment** (Colleagues - 5 minutes)
```bash
# One command - downloads, installs, builds, runs
curl -sSL https://raw.githubusercontent.com/leonkalema/QuickTARA/main/office-deploy.sh | bash

# OR clone first:
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
./office-deploy.sh
```
**Result**: Runs on their LAN IP, accessible to office network

### 3. **Cloud Deployment** (Production - 2 minutes)

#### Option A: Docker (Recommended)
```bash
git clone https://github.com/leonkalema/QuickTARA.git
cd QuickTARA
docker-compose up -d
```

#### Option B: With MySQL (Production)
```bash
docker-compose --profile mysql up -d
```

#### Option C: Cloud Platforms

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
docker build -t quicktara .
docker tag quicktara:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/quicktara:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/quicktara:latest
```

**Google Cloud Run:**
```bash
gcloud run deploy quicktara --source . --platform managed --region us-central1 --allow-unauthenticated
```

**Azure Container Instances:**
```bash
az container create --resource-group myResourceGroup --name quicktara --image quicktara:latest --ports 8080
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
QUICKTARA_DB_TYPE=sqlite|mysql|postgresql
QUICKTARA_DB_HOST=localhost
QUICKTARA_DB_PORT=3306
QUICKTARA_DB_NAME=quicktara
QUICKTARA_DB_USER=username
QUICKTARA_DB_PASSWORD=password

# Server
QUICKTARA_SERVER_HOST=0.0.0.0
QUICKTARA_SERVER_PORT=8080
QUICKTARA_SERVER_DEBUG=false

# Storage
QUICKTARA_UPLOADS_DIR=./uploads
QUICKTARA_REPORTS_DIR=./reports
```

### Default Behavior
- **Database**: SQLite (no config needed)
- **Host**: 127.0.0.1 (local only)
- **Port**: 8080
- **Data**: Stored in `./quicktara.db`
- **Default Login**: 
  - Email: `admin@quicktara.local`
  - Password: `admin123`

## 🌐 Network Access

### Local Only
```bash
python quicktara_web.py
# Access: http://localhost:8080
```

### LAN Access
```bash
python quicktara_web.py --host 0.0.0.0
# Access: http://YOUR-IP:8080
```

### Custom Port
```bash
python quicktara_web.py --host 0.0.0.0 --port 9000
# Access: http://YOUR-IP:9000
```

## 🔒 Security Notes

### For Office/LAN:
- Uses SQLite (single file database)
- No external dependencies
- Data stays local

### For Cloud:
- Use MySQL/PostgreSQL for production
- Set strong passwords
- Enable HTTPS (reverse proxy required)
- Consider VPN for sensitive data

## 📊 Resource Requirements

### Minimum:
- **CPU**: 1 core
- **RAM**: 512MB
- **Disk**: 1GB
- **Network**: 10Mbps

### Recommended:
- **CPU**: 2 cores
- **RAM**: 2GB
- **Disk**: 10GB SSD
- **Network**: 100Mbps

## 🆘 Troubleshooting

### Common Issues:

**Port already in use:**
```bash
python quicktara_web.py --port 8081
```

**Permission denied:**
```bash
sudo python quicktara_web.py --host 0.0.0.0 --port 80
```

**Database connection failed:**
```bash
# Check database config or use SQLite default
python quicktara_web.py --db ./backup.db
```

**Frontend not loading:**
```bash
cd tara-web
npm run build
cd ..
python quicktara_web.py
```

## 🌱 Frontend Environment Configuration (tara-web)

The frontend reads its API base URL from an environment variable. If not set, it defaults to `window.location.origin + /api` via `tara-web/src/lib/config.ts`.

1) Local development (same-origin, no env needed)
- If your backend is available at the same origin under `/api`, no configuration is necessary.

2) Local development (different API origin)
- Create `tara-web/.env.local` with:

```
VITE_API_BASE_URL="http://127.0.0.1:8080/api"
```

- Restart Vite dev server after changing envs.

3) Production hosting (Netlify/Vercel/etc.)
- Set `VITE_API_BASE_URL` in the platform's environment variables to point to your API, for example:

```
VITE_API_BASE_URL="https://quicktara.fly.dev/api"
```

4) Version control
- `tara-web/.gitignore` already ignores `.env` and `.env.*` (except `.env.example`).
- Use `tara-web/.env.example` as a template for environment variables.
