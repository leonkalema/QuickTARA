"""
Main FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from api.routes import components, analysis, reports, review

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
        allow_origins=["*"],  # Allows all origins in development
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    
    # Include all API routers
    app.include_router(components.router, prefix="/api/components", tags=["components"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    app.include_router(review.router, prefix="/api/review", tags=["review"])
    
    # Serve static files (for production when frontend is built)
    frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    
    @app.get("/api/health")
    async def health_check():
        """Simple health check endpoint"""
        return {"status": "ok"}
    
    return app
