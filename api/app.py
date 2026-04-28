"""
Main FastAPI application factory
"""
import os
import traceback
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

# Set up logger
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiting (SlowAPI — optional, gracefully skipped if not installed)
# ---------------------------------------------------------------------------
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
    HAS_LIMITER = True
except ImportError:
    _limiter = None
    HAS_LIMITER = False
    logger.warning("slowapi not installed — rate limiting disabled. Run: pip install slowapi")

# Import all routers
from api.routers import (
    attack_path, 
    risk_treatment, reports as reports_router, auth, users, 
    settings as settings_router, organizations, organization_members
)

def create_app(settings=None):
    """
    Create FastAPI application with all routes and middleware
    """
    app = FastAPI(
        title="QuickTARA API",
        description="REST API for automotive security threat analysis and risk assessment",
        version="2.1.0",
    )

    # ------------------------------------------------------------------
    # Rate limiter (login brute-force protection)
    # ------------------------------------------------------------------
    if HAS_LIMITER:
        app.state.limiter = _limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ------------------------------------------------------------------
    # Security headers middleware
    # ------------------------------------------------------------------
    _tls_active: bool = bool(
        os.environ.get("QUICKTARA_SSL_CERTFILE") and os.environ.get("QUICKTARA_SSL_KEYFILE")
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next) -> Response:
        origin = request.headers.get("origin", "")
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # HSTS — only advertise on TLS deployments, otherwise misleading
        if _tls_active:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        # Safety net: Starlette's CORSMiddleware doesn't add CORS headers to
        # unhandled 500 responses (ServerErrorMiddleware runs outside CORS).
        # Re-add them here for any allowed origin so the browser can read the error.
        if origin and "access-control-allow-origin" not in response.headers:
            if origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # ------------------------------------------------------------------
    # CORS — locked to known origins; extend via QUICKTARA_CORS_ORIGINS
    # ------------------------------------------------------------------
    _default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    _env_origins = [
        o.strip()
        for o in os.environ.get("QUICKTARA_CORS_ORIGINS", "").split(",")
        if o.strip()
    ]
    allowed_origins = list(dict.fromkeys(_default_origins + _env_origins))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        expose_headers=["Content-Disposition"],
        max_age=600,
    )

    # Global handler: converts unhandled exceptions into JSON 500s *before*
    # the response leaves ExceptionMiddleware, so CORSMiddleware (which wraps it)
    # can still add the Access-Control-Allow-Origin header.  Without this the
    # exception propagates all the way to ServerErrorMiddleware (outermost),
    # which returns a bare 500 with no CORS headers and the browser blocks it.
    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path,
                     traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": str(exc) or "Internal server error"})

    # Include all API routers
    
    # Authentication routes (no auth required)
    app.include_router(auth.router, prefix="/api", tags=["authentication"])
    
    # User management routes (admin auth required)
    app.include_router(users.router, tags=["users"])
    
    # Import and include legacy routes from api.routes
    from api.routes import scope, components, damage_scenarios, threat_scenarios, impact_ratings, risk, threat, vulnerability, analysis, simple_attack_path, products, assets, reports, review
    
    # New product-centric model routes (takes precedence)
    app.include_router(products.router, prefix="/api/products", tags=["products"])  # Product (scope) routes
    app.include_router(assets.router, prefix="/api/assets", tags=["assets"])      # Asset (component) routes
    
    # Legacy routes (kept for backward compatibility)
    app.include_router(scope.router, prefix="/api/scope", tags=["scope"])
    app.include_router(components.router, prefix="/api/components", tags=["components"])
    app.include_router(damage_scenarios.router, prefix="/api/damage-scenarios", tags=["damage-scenarios"])
    app.include_router(threat_scenarios.router, prefix="/api/threat-scenarios", tags=["threat-scenarios"])
    app.include_router(impact_ratings.router, prefix="/api/impact-ratings", tags=["impact-ratings"])
    app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
    app.include_router(threat.router, prefix="/api/threat", tags=["threat"])
    app.include_router(vulnerability.router, prefix="/api/vulnerability", tags=["vulnerability"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    
    # Add attack path analysis router
    app.include_router(simple_attack_path.router, prefix="/api/attack-paths", tags=["attack-paths"])
    app.include_router(attack_path.router, prefix="/api/attack-paths-analysis", tags=["attack-paths-analysis"])
    app.include_router(risk_treatment.router, prefix="/api", tags=["risk-treatment"])
    app.include_router(reports_router.router, prefix="/api", tags=["reports-pdf"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    app.include_router(review.router, prefix="/api/review", tags=["review"])
    
    # Audit trail, approval workflows, evidence, and TARA snapshots
    from api.routes import audit as audit_routes
    app.include_router(audit_routes.router, prefix="/api/audit", tags=["audit"])
    
    # CRA compliance module
    from api.routes import cra as cra_routes
    from api.routes import cra_sbom as cra_sbom_routes
    from api.routes import cra_incident as cra_incident_routes
    from api.routes import cra_annex_vii as cra_annex_vii_routes
    app.include_router(cra_routes.router, prefix="/api/cra", tags=["cra"])
    app.include_router(cra_sbom_routes.router, prefix="/api/cra", tags=["cra-sbom"])
    app.include_router(cra_incident_routes.router, prefix="/api/cra", tags=["cra-incident"])
    app.include_router(cra_annex_vii_routes.router, prefix="/api/cra", tags=["cra-annex-vii"])
    
    app.include_router(settings_router.router, tags=["settings"])
    app.include_router(organizations.router, tags=["organizations"])
    app.include_router(organization_members.router, tags=["organization-members"])
    
    # Serve static files (for production when frontend is built)
    frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    
    @app.get("/api/health")
    async def health_check():
        """Simple health check endpoint"""
        return {"status": "ok"}
    
    @app.on_event("startup")
    async def seed_threat_catalog_on_startup():
        """Auto-seed threat catalog from bundled data if empty. No internet needed."""
        try:
            from core.threat_catalog.startup_seed import auto_seed_catalog
            from api.deps.db import SessionLocal
            db = SessionLocal()
            try:
                result = auto_seed_catalog(db)
                if result.get("created", 0) > 0:
                    logger.info("Auto-seeded %d threats into catalog", result["created"])
            finally:
                db.close()
        except Exception as e:
            logger.warning("Threat catalog auto-seed skipped: %s", str(e))
    
    return app

# Create the app instance for uvicorn
app = create_app()
