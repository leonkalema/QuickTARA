"""
Database dependency injector
"""
from typing import Generator
from sqlalchemy.orm import Session

from db.session import get_session_factory

# Create a default session factory
SessionLocal = get_session_factory()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
