"""
Database session handling
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
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
        return f"mysql://{user}:{password}@{host}:{port}/{name}"
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
    """
    Initialize database with required tables
    """
    from db.base import Base
    
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)
