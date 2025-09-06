"""
Main FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

# Set up logger
logger = logging.getLogger(__name__)

# Import all routers
from api.routes import components, analysis, reports, review, settings_routes, scope, risk, threat, vulnerability, attack_path, damage_scenarios, impact_ratings, threat_scenarios, simple_attack_path

# Import new product-centric model routers
from api.routes import products, assets

# Import risk treatment router
from api.routers import risk_treatment

def create_app(settings=None):
    """
    Create FastAPI application with all routes and middleware
    """
    app = FastAPI(
        title="QuickTARA API",
        description="REST API for automotive security threat analysis and risk assessment",
        version="1.0.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",     # Vite dev server
            "http://127.0.0.1:5173",     # Vite dev server alternative
            "http://localhost:4173",     # Vite preview
            "http://127.0.0.1:4173",     # Vite preview alternative
            "http://localhost:3000",     # Alternative development port
            "http://127.0.0.1:3000",     # Alternative development port IP
            "http://localhost",          # Generic localhost
            "http://127.0.0.1",         # Generic local IP
            "http://localhost:8080",     # If frontend is served by the same backend
            "http://127.0.0.1:8080",     # Backend local IP
            "http://localhost:5174",     # Additional Vite ports
            "http://127.0.0.1:5174",      # Additional Vite ports
            "*"                         # Allow all origins (for development only)
            # In production, replace this with specific allowed origins
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],  # Allows all headers
        expose_headers=["Content-Disposition"],
        max_age=1800  # Cache preflight requests for 30 minutes
    )
    
    # Include all API routers
    
    # New product-centric model routes (takes precedence)
    app.include_router(products.router, prefix="/api/products", tags=["products"])  # Product (scope) routes
    app.include_router(assets.router, prefix="/api/assets", tags=["assets"])      # Asset (component) routes
    
    # Legacy routes (kept for backward compatibility)
    app.include_router(scope.router, prefix="/api/scope", tags=["scope"])        # Legacy scope router
    app.include_router(components.router, prefix="/api/components", tags=["components"])  # Legacy components router
    app.include_router(damage_scenarios.router, prefix="/api/damage-scenarios", tags=["damage-scenarios"])  # Add damage scenarios router
    app.include_router(threat_scenarios.router, prefix="/api/threat-scenarios", tags=["threat-scenarios"])  # Add threat scenarios router
    app.include_router(impact_ratings.router, prefix="/api/impact-ratings", tags=["impact-ratings"])  # Add impact ratings router
    app.include_router(risk.router, prefix="/api/risk", tags=["risk"])  # Add risk framework router
    app.include_router(threat.router, prefix="/api/threat", tags=["threat"])  # Add threat analysis router
    app.include_router(vulnerability.router, prefix="/api/vulnerability", tags=["vulnerability"])  # Add vulnerability assessment router
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    
    # Add attack path analysis router
    app.include_router(simple_attack_path.router, prefix="/api/attack-paths", tags=["attack-paths"])
    app.include_router(attack_path.router, prefix="/api/attack-paths-analysis", tags=["attack-paths-analysis"])
    app.include_router(risk_treatment.router, prefix="/api", tags=["risk-treatment"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    app.include_router(review.router, prefix="/api/review", tags=["review"])
    app.include_router(settings_routes.router, prefix="/api/settings", tags=["settings"])
    
    # Serve static files (for production when frontend is built)
    frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    
    @app.get("/api/health")
    async def health_check():
        """Simple health check endpoint"""
        return {"status": "ok"}
    
    return app
