"""
Settings API routes
"""
from fastapi import APIRouter
from api.routes.settings.database import router as db_router

router = APIRouter()

# Include the database settings router
router.include_router(db_router, prefix="/database", tags=["database"])
