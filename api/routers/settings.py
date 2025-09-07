"""
Settings API Router
Handles database configuration and system settings
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Database configuration models
class DatabaseConfig(BaseModel):
    type: str  # sqlite, postgresql, mysql
    path: Optional[str] = None  # For SQLite
    host: Optional[str] = None  # For PostgreSQL/MySQL
    port: Optional[int] = None  # For PostgreSQL/MySQL
    name: Optional[str] = None  # Database name
    user: Optional[str] = None  # Username
    password: Optional[str] = None  # Password

class MigrationInfo(BaseModel):
    current_revision: str
    latest_revision: str
    is_latest: bool
    pending_migrations: List[str]

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Configuration file path
CONFIG_FILE = "config/database.json"

def load_db_config() -> DatabaseConfig:
    """Load database configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                return DatabaseConfig(**config_data)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
    
    # Return default SQLite config
    return DatabaseConfig(
        type="sqlite",
        path="./quicktara.db"
    )

def save_db_config(config: DatabaseConfig) -> None:
    """Save database configuration to file"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config.model_dump(exclude_none=True), f, indent=2)

def build_connection_string(config: DatabaseConfig) -> str:
    """Build SQLAlchemy connection string from config"""
    if config.type == "sqlite":
        return f"sqlite:///{config.path}"
    elif config.type == "postgresql":
        port = config.port or 5432
        return f"postgresql://{config.user}:{config.password}@{config.host}:{port}/{config.name}"
    elif config.type == "mysql":
        port = config.port or 3306
        return f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{port}/{config.name}"
    else:
        raise ValueError(f"Unsupported database type: {config.type}")

def get_alembic_config() -> Config:
    """Get Alembic configuration"""
    alembic_cfg = Config("alembic.ini")
    
    # Update connection string with current database config
    db_config = load_db_config()
    connection_string = build_connection_string(db_config)
    
    # Debug logging
    logger.info(f"Database config type: {db_config.type}")
    logger.info(f"Connection string: {connection_string}")
    
    alembic_cfg.set_main_option("sqlalchemy.url", connection_string)
    
    # Also set the script location to use the correct migrations directory
    alembic_cfg.set_main_option("script_location", "db/migrations")
    
    return alembic_cfg

def get_migration_info_real() -> MigrationInfo:
    """Get real migration status from Alembic"""
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get current revision from database
        db_config = load_db_config()
        engine = create_engine(build_connection_string(db_config))
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
        
        # Get latest revision from scripts
        latest_rev = script.get_current_head()
        
        # Get pending migrations
        pending = []
        if current_rev != latest_rev:
            for rev in script.walk_revisions(current_rev, latest_rev):
                if rev.revision != current_rev:
                    pending.append(f"{rev.revision[:8]}_{rev.doc or 'migration'}")
        
        return MigrationInfo(
            current_revision=current_rev or "Not initialized",
            latest_revision=latest_rev or "No migrations",
            is_latest=(current_rev == latest_rev),
            pending_migrations=pending
        )
    except Exception as e:
        logger.error(f"Failed to get real migration info: {e}")
        # Fallback to basic info
        return MigrationInfo(
            current_revision="Unknown",
            latest_revision="Unknown", 
            is_latest=True,
            pending_migrations=[]
        )

@router.get("/database", response_model=DatabaseConfig)
async def get_database_config():
    """Get current database configuration"""
    try:
        config = load_db_config()
        # Don't return password in response
        if config.password:
            config.password = "***"
        return config
    except Exception as e:
        logger.error(f"Failed to get database config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database", response_model=DatabaseConfig)
async def update_database_config(config: DatabaseConfig):
    """Update database configuration"""
    try:
        # Validate configuration
        if config.type not in ["sqlite", "postgresql", "mysql"]:
            raise ValueError("Invalid database type")
        
        if config.type != "sqlite":
            if not all([config.host, config.port, config.name, config.user]):
                raise ValueError("Host, port, name, and user are required for non-SQLite databases")
        
        # Save configuration
        save_db_config(config)
        
        # Return config without password
        response_config = config.model_copy()
        if response_config.password:
            response_config.password = "***"
        
        return response_config
    except Exception as e:
        logger.error(f"Failed to update database config: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/database/test", response_model=ApiResponse)
async def test_database_connection(config: DatabaseConfig):
    """Test database connection"""
    try:
        connection_string = build_connection_string(config)
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return ApiResponse(
            success=True,
            message="Database connection successful"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return ApiResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error testing connection: {e}")
        return ApiResponse(
            success=False,
            message=f"Test failed: {str(e)}"
        )

@router.get("/database/migrations", response_model=MigrationInfo)
async def get_migration_status():
    """Get database migration status"""
    try:
        return get_migration_info_real()
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/migrations/upgrade", response_model=ApiResponse)
async def run_migrations():
    """Run database migrations"""
    try:
        alembic_cfg = get_alembic_config()
        
        # Get current migration info before upgrade
        before_info = get_migration_info_real()
        
        # Run the upgrade
        command.upgrade(alembic_cfg, "head")
        
        # Get migration info after upgrade
        after_info = get_migration_info_real()
        
        migrations_applied = before_info.pending_migrations
        
        return ApiResponse(
            success=True,
            message=f"Successfully applied {len(migrations_applied)} migration(s)",
            data={"migrations_applied": migrations_applied}
        )
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        return ApiResponse(
            success=False,
            message=f"Migration failed: {str(e)}"
        )

@router.post("/database/initialize", response_model=ApiResponse)
async def initialize_database():
    """Initialize a new database"""
    try:
        # Test connection first
        config = load_db_config()
        connection_string = build_connection_string(config)
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Get Alembic config with correct connection string
        alembic_cfg = get_alembic_config()
        
        # Create all tables from scratch using Alembic
        command.upgrade(alembic_cfg, "head")
        
        return ApiResponse(
            success=True,
            message="Database initialized and schema created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return ApiResponse(
            success=False,
            message=f"Initialization failed: {str(e)}"
        )
