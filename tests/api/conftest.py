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

    from db.product_asset_models import Base
    import db.base          # noqa: F401
    import db.damage_scenario  # noqa: F401
    import db.threat_scenario  # noqa: F401
    import db.attack_path   # noqa: F401
    import db.risk_treatment  # noqa: F401
    import db.audit_models  # noqa: F401
    import db.cra_models    # noqa: F401
    import db.cra_incident_models  # noqa: F401
    import db.cra_sbom_models  # noqa: F401
    from api.models import simple_attack_path  # noqa: F401
    from api.models import user as user_models  # noqa: F401

    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    engine.dispose()
    return url


@pytest.fixture
def alembic_db_url(tmp_path: Path) -> str:
    """Return an SQLite URL whose schema was built by Alembic + create_all.

    Mirrors the production init_db() flow:
      1. Alembic upgrade head  (creates tables that have migrations)
      2. create_all for ORM-only tables (product_scopes, assets, attack_paths, …)

    Use this fixture (via `alembic_client`) for tests that exercise routes which
    depend on the Alembic schema — especially damage_scenarios and threat_scenarios
    where the legacy and product bases define conflicting schemas.
    """
    db_path = tmp_path / "alembic_integration.db"
    url = f"sqlite:///{db_path}"

    # Step 1 — run Alembic to create all migrated tables with the correct schema.
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    # warm sys.modules so alembic env.py can import db.base
    import db.base  # noqa: F401
    command.upgrade(cfg, "head")

    # Step 2 — create ORM-only tables (not covered by migrations).
    from db.product_asset_models import Base
    import db.base          # noqa: F401
    import db.damage_scenario  # noqa: F401
    import db.threat_scenario  # noqa: F401
    import db.attack_path   # noqa: F401
    import db.risk_treatment  # noqa: F401
    import db.audit_models  # noqa: F401
    import db.cra_models    # noqa: F401
    import db.cra_incident_models  # noqa: F401
    import db.cra_sbom_models  # noqa: F401
    from api.models import simple_attack_path  # noqa: F401
    from api.models import user as user_models  # noqa: F401

    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    engine.dispose()
    return url


@pytest.fixture
def alembic_client(alembic_db_url: str) -> Generator[TestClient, None, None]:
    """TestClient backed by a fully migrated ephemeral DB — use for TARA flow tests."""
    from api.app import app
    from api.auth.dependencies import get_current_active_user, get_current_user
    from api.deps.db import get_db

    engine = create_engine(alembic_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def _override_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    class _StubUser:
        id = "test-user"
        user_id = "test-user"
        email = "test@example.com"
        status = "active"
        organization_id = None
        is_superuser = False

    async def _override_user() -> _StubUser:
        return _StubUser()

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_active_user] = _override_user
    app.dependency_overrides[get_current_user] = _override_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def alembic_db_session(alembic_db_url: str) -> Generator[Session, None, None]:
    engine = create_engine(alembic_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


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
        user_id = "test-user"
        email = "test@example.com"
        status = "active"
        organization_id = None
        is_superuser = False

    async def _override_user() -> _StubUser:
        return _StubUser()

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_active_user] = _override_user
    app.dependency_overrides[get_current_user] = _override_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()
