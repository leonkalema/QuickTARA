"""
Settings API routes
"""
from fastapi import APIRouter
from api.routes.settings import database

router = APIRouter()

# Include the database settings router
router.include_router(database.router, prefix="/database", tags=["database"])
