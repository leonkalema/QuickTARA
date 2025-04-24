"""
Database settings API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Union
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
import sys
import json
from enum import Enum

from db.session import get_engine, get_database_url, get_session_factory, init_db
from api.deps.db import get_db
from config.settings import load_settings, update_settings

router = APIRouter()


class DatabaseType(str, Enum):
    """Database type enum"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class DatabaseConfig(BaseModel):
    """Database configuration model"""
    type: DatabaseType
    path: Optional[str] = None  # For SQLite
    host: Optional[str] = None  # For PostgreSQL/MySQL
    port: Optional[int] = None  # For PostgreSQL/MySQL
    name: Optional[str] = None  # Database name for PostgreSQL/MySQL
    user: Optional[str] = None  # For PostgreSQL/MySQL
    password: Optional[str] = None  # For PostgreSQL/MySQL


class MigrationInfo(BaseModel):
    """Database migration information"""
    current_revision: str
    latest_revision: str
    is_latest: bool
    pending_migrations: List[str]


class ConnectionTestResult(BaseModel):
    """Result of a database connection test"""
    success: bool
    message: str


class MigrationResult(BaseModel):
    """Result of a database migration operation"""
    success: bool
    message: str
    migrations_applied: Optional[List[str]] = None


class DatabaseInitResult(BaseModel):
    """Result of a database initialization operation"""
    success: bool
    message: str


@router.get("/")
async def get_database_config() -> DatabaseConfig:
    """
    Get the current database configuration
    """
    settings = load_settings()
    db_config = settings.get("database", {})
    
    return DatabaseConfig(
        type=db_config.get("type", "sqlite"),
        path=db_config.get("path", "./quicktara.db"),
        host=db_config.get("host"),
        port=db_config.get("port"),
        name=db_config.get("name"),
        user=db_config.get("user"),
        password=db_config.get("password"),
    )


@router.post("/")
async def update_database_config(config: Dict) -> DatabaseConfig:
    """
    Update the database configuration
    """
    settings = load_settings()
    
    # Update database settings
    if "database" not in settings:
        settings["database"] = {}
    
    # Update only the provided fields
    for key, value in config.items():
        if value is not None:  # Only update non-None values
            settings["database"][key] = value
    
    # Ensure required fields exist
    if "type" not in settings["database"]:
        settings["database"]["type"] = "sqlite"
    
    # For SQLite, ensure path exists
    if settings["database"]["type"] == "sqlite" and "path" not in settings["database"]:
        settings["database"]["path"] = "./quicktara.db"
    
    # Save settings
    update_settings(settings)
    
    return DatabaseConfig(
        type=settings["database"].get("type", "sqlite"),
        path=settings["database"].get("path", "./quicktara.db"),
        host=settings["database"].get("host"),
        port=settings["database"].get("port"),
        name=settings["database"].get("name"),
        user=settings["database"].get("user"),
        password=settings["database"].get("password"),
    )


@router.post("/test")
async def test_database_connection(config: Dict) -> ConnectionTestResult:
    """
    Test the database connection with provided configuration
    """
    try:
        # Create a temporary settings dict
        temp_settings = {"database": config}
        
        # Try to create an engine with the settings
        engine = get_engine(temp_settings)
        
        # Try to connect
        with engine.connect() as conn:
            # Execute a simple query to verify connection
            conn.execute(text("SELECT 1"))
        
        return ConnectionTestResult(success=True, message="Connection successful")
    except Exception as e:
        return ConnectionTestResult(success=False, message=f"Connection failed: {str(e)}")


@router.get("/migrations")
async def get_migration_status() -> MigrationInfo:
    """
    Get the status of database migrations
    """
    try:
        # Get project root
        project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        
        # Run 'alembic current' to get current revision
        current_proc = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=False
        )
        
        current_revision = "Not initialized"
        if current_proc.returncode == 0 and current_proc.stdout:
            # Extract revision from output (format: "Current revision: abc123 (head)")
            current_revision = current_proc.stdout.strip().split(" ")[2]
            # Handle case where no revision exists
            if current_revision == "None":
                current_revision = "Not initialized"
        
        # Run 'alembic history' to get latest revision and pending migrations
        history_proc = subprocess.run(
            [sys.executable, "-m", "alembic", "history", "--verbose"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=False
        )
        
        latest_revision = "Unknown"
        pending_migrations = []
        
        if history_proc.returncode == 0 and history_proc.stdout:
            # Parse history output
            history_lines = history_proc.stdout.strip().split("\n")
            if history_lines:
                # The most recent revision is first in output
                if ":" in history_lines[0]:
                    latest_revision = history_lines[0].split(":")[0].strip()
                
                # Find pending migrations
                is_current = False
                for line in history_lines:
                    if current_revision != "Not initialized" and current_revision in line:
                        is_current = True
                        continue
                    
                    if not is_current and ":" in line:
                        revision_id = line.split(":")[0].strip()
                        revision_desc = line.split(":", 1)[1].strip()
                        pending_migrations.append(f"{revision_id}: {revision_desc}")
        
        # Determine if latest
        is_latest = (current_revision == latest_revision) or (current_revision != "Not initialized" and not pending_migrations)
        
        return MigrationInfo(
            current_revision=current_revision,
            latest_revision=latest_revision,
            is_latest=is_latest,
            pending_migrations=pending_migrations
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get migration status: {str(e)}"
        )


@router.post("/migrations/upgrade")
async def run_migrations() -> MigrationResult:
    """
    Run database migrations
    """
    try:
        # Get project root
        project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        
        # Run 'alembic upgrade head'
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # Get list of applied migrations from output
            migrations_applied = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if "Running upgrade" in line:
                        migrations_applied.append(line.strip())
            
            return MigrationResult(
                success=True,
                message="Migrations applied successfully",
                migrations_applied=migrations_applied
            )
        else:
            return MigrationResult(
                success=False,
                message=f"Failed to apply migrations: {result.stderr}"
            )
    except Exception as e:
        return MigrationResult(
            success=False,
            message=f"Error running migrations: {str(e)}"
        )


@router.post("/initialize")
async def initialize_database() -> DatabaseInitResult:
    """
    Initialize the database (create tables directly)
    """
    try:
        # Get settings
        settings = load_settings()
        
        # Initialize the database
        try:
            init_db(settings)
            return DatabaseInitResult(
                success=True,
                message="Database initialized successfully"
            )
        except Exception as e:
            # Check if the error is just because tables already exist
            if "table already exists" in str(e):
                return DatabaseInitResult(
                    success=True,
                    message="Database tables already exist, initialization skipped"
                )
            return DatabaseInitResult(
                success=False,
                message=f"Failed to initialize database: {str(e)}"
            )
    except Exception as e:
        return DatabaseInitResult(
            success=False,
            message=f"Failed to initialize database: {str(e)}"
        )
