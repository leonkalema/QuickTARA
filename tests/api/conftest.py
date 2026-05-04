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
    # attack_path (simple) must come BEFORE db.attack_path — uses its own Base and
    # defines attack_paths with attack_path_id PK which risk_treatment FK references.
    from api.models import simple_attack_path  # noqa: F401 — AttackPathDB (own Base)
    from db import attack_path          # noqa: F401 — legacy AttackPath/AttackStep/AttackChain
    from db import risk_treatment       # noqa: F401 — RiskTreatment (FK uses use_alter)
    from db import audit_models         # noqa: F401 — AuditLog/ApprovalWorkflow/Evidence/Snapshot
    from db import cra_incident_models  # noqa: F401
    from db import cra_models           # noqa: F401
    from db import cra_sbom_models      # noqa: F401
    from db import product_asset_models
    from api.models import user as user_models  # noqa: F401

    engine = create_engine(url, connect_args={"check_same_thread": False})

    # Table priority ordering — where two Bases define the same table, the first
    # create wins. The routes use:
    #   threat_scenarios  → LegacyBase schema (has threat_scenario_id + scope_id)
    #   damage_scenarios  → ProductBase schema (has is_current, status, CRA fields)
    #   attack_paths      → simple_attack_path schema (has attack_path_id PK)

    # 1. Create threat_scenarios from LegacyBase FIRST (has scope_id needed by routes).
    from db.threat_scenario import ThreatScenario as _LegacyTS
    _LegacyTS.__table__.create(engine, checkfirst=True)

    # 2. Create attack_paths (with attack_path_id PK) so risk_treatment FK resolves.
    simple_attack_path.Base.metadata.create_all(engine)

    # 3. ProductBase: creates damage_scenarios (newer schema) + product_scopes, assets.
    #    threat_scenarios already exists so it's skipped.
    product_asset_models.Base.metadata.create_all(engine)

    # 4. LegacyBase: fills in analyses, components, risk_treatments, audit tables, etc.
    #    damage_scenarios and threat_scenarios already exist so they're skipped.
    legacy_base.Base.metadata.create_all(engine)

    # 5. UserBase: users, organizations, refresh_tokens.
    user_models.Base.metadata.create_all(engine)

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
    from api.models import simple_attack_path  # noqa: F401 — attack_paths (own Base)
    from db import base as legacy_base
    from db import attack_path          # noqa: F401 — legacy AttackPath/AttackStep/AttackChain
    from db import risk_treatment       # noqa: F401 — RiskTreatment (no FK now)
    from db import audit_models         # noqa: F401 — audit_logs, approval_workflows, etc.
    from db import product_asset_models
    from api.models import user as user_models  # noqa: F401

    engine = create_engine(url, connect_args={"check_same_thread": False})

    # threat_scenarios: routes use db.threat_scenario (LegacyBase) which has
    # threat_scenario_id and scope_id. Create it from LegacyBase FIRST so that
    # ProductBase's create_all skips it (ProductBase has only scenario_id, no scope_id).
    from db.threat_scenario import ThreatScenario as _LegacyTS
    _LegacyTS.__table__.create(engine, checkfirst=True)

    simple_attack_path.Base.metadata.create_all(engine)
    product_asset_models.Base.metadata.create_all(engine)
    legacy_base.Base.metadata.create_all(engine)   # audit_logs, risk_treatments, etc.
    user_models.Base.metadata.create_all(engine)
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
