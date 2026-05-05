"""
Database session handling
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Default to SQLite but can be configured
DEFAULT_DATABASE_URL = "sqlite:///./quicktara.db"


def get_database_url(settings=None):
    """
    Get database URL from settings or environment
    """
    if not settings:
        # Try to load from database.json config file
        try:
            import json
            import os
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "database.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    db_config = json.load(f)
                
                if db_config.get("type") == "mysql":
                    host = db_config.get("host", "localhost")
                    port = db_config.get("port", 3306)
                    name = db_config.get("name", "quicktara")
                    user = db_config.get("user", "root")
                    password = db_config.get("password", "")
                    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
                elif db_config.get("type") == "postgresql":
                    host = db_config.get("host", "localhost")
                    port = db_config.get("port", 5432)
                    name = db_config.get("name", "quicktara")
                    user = db_config.get("user", "postgres")
                    password = db_config.get("password", "")
                    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        except Exception:
            pass
        
        return DEFAULT_DATABASE_URL
    
    db_type = settings.get("database", {}).get("type", "sqlite")
    
    if db_type == "sqlite":
        db_path = settings.get("database", {}).get("path", "./quicktara.db")
        return f"sqlite:///{db_path}"
    elif db_type == "postgresql":
        host = settings.get("database", {}).get("host", "localhost")
        port = settings.get("database", {}).get("port", 5432)
        name = settings.get("database", {}).get("name", "quicktara")
        user = settings.get("database", {}).get("user", "postgres")
        password = settings.get("database", {}).get("password", "")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    elif db_type == "mysql":
        host = settings.get("database", {}).get("host", "localhost")
        port = settings.get("database", {}).get("port", 3306)
        name = settings.get("database", {}).get("name", "quicktara")
        user = settings.get("database", {}).get("user", "root")
        password = settings.get("database", {}).get("password", "")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    else:
        logger.warning(f"Unsupported database type: {db_type}, using SQLite")
        return DEFAULT_DATABASE_URL


def get_engine(settings=None):
    """
    Create SQLAlchemy engine
    """
    database_url = get_database_url(settings)
    
    # Special handling for SQLite
    if database_url.startswith("sqlite"):
        # Ensure directory exists
        db_path = database_url.split("///")[1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            database_url, 
            connect_args={"check_same_thread": False}
        )
    
    return create_engine(database_url)


def get_session_factory(settings=None):
    """
    Create session factory for dependency injection
    """
    engine = get_engine(settings)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)



def init_db(settings=None):
    """Initialize database by running Alembic migrations to head."""
    import subprocess
    import sys
    from pathlib import Path

    project_dir = Path(__file__).parent.parent.absolute()

    logger.info("Running database migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
        else:
            logger.error(f"Migration failed:\n{result.stderr}")
            raise RuntimeError(f"alembic upgrade head failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise
