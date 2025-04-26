"""
Main FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from api.routes import components, analysis, reports, review, settings_routes, scope, risk

logger = logging.getLogger(__name__)

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
            "http://127.0.0.1:5174"      # Additional Vite ports
            # Cannot use wildcard '*' with credentials mode 'include'
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],  # Allows all headers
        expose_headers=["Content-Disposition"],
        max_age=1800  # Cache preflight requests for 30 minutes
    )
    
    # Include all API routers
    app.include_router(scope.router, prefix="/api/scope", tags=["scope"])  # Add scope router first
    app.include_router(components.router, prefix="/api/components", tags=["components"])
    app.include_router(risk.router, prefix="/api/risk", tags=["risk"])  # Add risk framework router
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
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
