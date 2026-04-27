"""Shared fixtures for API integration tests.

Spins up the full FastAPI app backed by an ephemeral SQLite database, runs
all Alembic migrations, and overrides authentication so route handlers can
be exercised without real JWTs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT))


@pytest.fixture
def ephemeral_db_url(tmp_path: Path) -> str:
    """Return a `sqlite:///...` URL with schema created via SQLAlchemy.

    `api.deps.db.init_db` runs Alembic then falls back to `create_all` for
    tables not yet covered by migrations. For tests we take the same fallback
    path directly — it is deterministic and fast, and the alembic round-trip
    tests under `tests/db/` cover migration correctness separately.
    """
    db_path = tmp_path / "integration.db"
    url = f"sqlite:///{db_path}"

    # The codebase has two declarative_base() instances:
    #   - `db.base.Base` — legacy models (users, components, ...)
    #   - `db.product_asset_models.Base` — the product-asset family that
    #     CRA tables attach to.
    # Both need `create_all` for a complete test schema.
    from db import base as legacy_base
    from db import cra_incident_models  # noqa: F401
    from db import cra_models  # noqa: F401
    from db import cra_sbom_models  # noqa: F401
    from db import product_asset_models
    from api.models import user as user_models  # noqa: F401

    engine = create_engine(url, connect_args={"check_same_thread": False})
    # Create product-asset tables FIRST. Where table names collide across the
    # two Bases (e.g. `damage_scenarios`), the first-created schema wins and
    # the second `create_all` call skips the existing table. The product-asset
    # family has the newer schema the CRA features target.
    product_asset_models.Base.metadata.create_all(engine)
    legacy_base.Base.metadata.create_all(engine)
    engine.dispose()
    return url


@pytest.fixture
def db_session(ephemeral_db_url: str) -> Generator[Session, None, None]:
    engine = create_engine(ephemeral_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(ephemeral_db_url: str) -> Generator[TestClient, None, None]:
    """Yield a FastAPI TestClient with auth + DB dependencies overridden."""
    from api.app import app
    from api.auth.dependencies import get_current_active_user, get_current_user
    from api.deps.db import get_db

    engine = create_engine(ephemeral_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def _override_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    class _StubUser:
        id = "test-user"
        email = "test@example.com"
        status = "active"
        organization_id = None

    async def _override_user() -> _StubUser:
        return _StubUser()

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_active_user] = _override_user
    app.dependency_overrides[get_current_user] = _override_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()
