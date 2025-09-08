FROM node:20-slim as frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY tara-web/package*.json ./
# Install devDependencies too so build tools (vite, svelte-kit) are available
RUN npm ci
COPY tara-web/ ./
RUN npm run build

# Python runtime
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from builder stage (vite default outDir is "dist")
COPY --from=frontend-builder /app/frontend/dist ./tara-web/dist

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run as non-root user
RUN useradd -m -u 1000 quicktara && chown -R quicktara:quicktara /app
USER quicktara

# Default to SQLite in data directory
ENV DATABASE_URL=sqlite:///app/data/quicktara.db

CMD ["python", "quicktara_web.py", "--host", "0.0.0.0", "--port", "8080"]
