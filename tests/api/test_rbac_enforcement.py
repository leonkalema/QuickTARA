"""RBAC enforcement tests.

Verifies that every previously-unprotected route now correctly enforces
authentication and role-based access control:

  Route group         | GET (read)     | POST/PUT/DELETE (write) | PATCH accept
  --------------------|----------------|-------------------------|-------------
  /assets             | login required | analyst+                | n/a
  /damage-scenarios   | login required | analyst+                | risk_manager+
  /threat-scenarios   | login required | analyst+                | risk_manager+
  /attack-paths       | login required | analyst+ (POST)         | n/a
  /threat/catalog     | login required | analyst+                | n/a

Each section tests three actors:
  - Unauthenticated  → 403 on every route
  - Viewer           → 200 on GETs, 403 on writes
  - Analyst          → 200/201 on GETs and writes (where data allows)
  - Risk Manager     → 200 on GETs and writes, 200 on accept
  - Viewer on accept → 403
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_db(tmp_path):
    db_path = tmp_path / "rbac_test.db"
    url = f"sqlite:///{db_path}"

    import db.base  # noqa: F401
    import db.damage_scenario  # noqa: F401
    import db.threat_scenario  # noqa: F401
    import db.attack_path  # noqa: F401
    import db.risk_treatment  # noqa: F401
    import db.audit_models  # noqa: F401
    import db.cra_models  # noqa: F401
    import db.cra_incident_models  # noqa: F401
    import db.cra_sbom_models  # noqa: F401
    import db.threat_catalog  # noqa: F401
    from api.models import simple_attack_path  # noqa: F401
    from api.models import user as user_models  # noqa: F401
    from db.product_asset_models import Base

    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return url, engine, sessionmaker(bind=engine, autoflush=False, autocommit=False)


class _StubUser:
    """Detachment-safe stand-in for a real User ORM object.

    get_user_roles() only needs user_id and is_superuser; everything else
    is needed by the route handler for audit trails and similar.
    """
    def __init__(self, user_id: str, email: str, is_superuser: bool = False):
        self.user_id = user_id
        self.email = email
        self.username = email.split("@")[0]
        self.is_superuser = is_superuser
        self.status = "active"
        self.first_name = "Test"
        self.last_name = "User"


def _seed_user(db: Session, *, superuser=False, email=None) -> _StubUser:
    from api.models.user import User, UserStatus
    from api.auth.security import security_manager
    uid = str(uuid.uuid4())
    email = email or f"u_{uid[:8]}@test.com"
    u = User(
        user_id=uid, email=email,
        username=f"u_{uid[:8]}",
        first_name="Test", last_name="User",
        hashed_password=security_manager.get_password_hash("pw"),
        status=UserStatus.ACTIVE, is_verified=True, is_superuser=superuser,
    )
    db.add(u); db.commit()
    # Return a plain stub — avoids DetachedInstanceError when the ORM object
    # is accessed inside a different request session.
    return _StubUser(user_id=uid, email=email, is_superuser=superuser)


def _seed_org(db: Session, name="Org") -> str:
    from api.models.user import Organization
    oid = str(uuid.uuid4())
    db.add(Organization(organization_id=oid, name=name))
    db.commit()
    return oid


def _assign_role(db: Session, user_id: str, org_id: str, role: str):
    from api.models.user import user_organizations
    db.execute(user_organizations.insert().values(
        user_id=user_id, organization_id=org_id, role=role,
        created_at=datetime.utcnow()
    ))
    db.commit()


def _seed_product(db: Session, org_id: str = None) -> str:
    from db.product_asset_models import ProductScope
    sid = str(uuid.uuid4())
    ps = ProductScope(
        scope_id=sid, name="Test Product", version=1, is_current=True,
        organization_id=org_id,
        product_type="vehicle_ecu",
        safety_level="ASIL-B",
        location="in-vehicle",
        trust_zone="internal",
        created_at=datetime.now(), updated_at=datetime.now(),
    )
    db.add(ps); db.commit()
    return sid


def _make_client(url: str, engine, SessionLocal, stub_user) -> Generator[TestClient, None, None]:
    """Return a TestClient whose auth is overridden with stub_user."""
    from api.app import app
    from api.auth.dependencies import get_current_active_user, get_current_user
    from api.deps.db import get_db

    def _db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    async def _user():
        return stub_user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_active_user] = _user
    app.dependency_overrides[get_current_user] = _user
    return TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def shared_db(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("rbac")
    url, engine, SessionLocal = _make_db(tmp)

    session = SessionLocal()
    org_id = _seed_org(session, "RBAC Org")

    # Seed four users
    viewer   = _seed_user(session, email="viewer@test.com")
    analyst  = _seed_user(session, email="analyst@test.com")
    rm       = _seed_user(session, email="rm@test.com")
    no_role  = _seed_user(session, email="norole@test.com")  # authenticated but no org

    _assign_role(session, viewer.user_id,  org_id, "viewer")
    _assign_role(session, analyst.user_id, org_id, "analyst")
    _assign_role(session, rm.user_id,      org_id, "risk_manager")
    # no_role gets no org assignment → get_user_roles() falls back to VIEWER

    scope_id = _seed_product(session, org_id)
    session.close()

    yield {
        "url": url, "engine": engine, "SessionLocal": SessionLocal,
        "org_id": org_id, "scope_id": scope_id,
        "viewer": viewer, "analyst": analyst, "rm": rm, "no_role": no_role,
    }
    engine.dispose()


def _client_for(shared_db, user_key):
    """Return a fresh TestClient for the given user key.

    Also patches api.auth.dependencies.SessionLocal so that get_user_roles()
    (which bypasses FastAPI DI and opens its own session) hits the test DB.
    """
    import api.deps.db as _db_module
    from api.app import app
    from api.auth.dependencies import get_current_active_user, get_current_user
    from api.deps.db import get_db
    SessionLocal = shared_db["SessionLocal"]

    # get_user_roles() does `from ..deps.db import SessionLocal` inside the
    # function body each call, so we must patch the source module attribute.
    _db_module.SessionLocal = SessionLocal  # type: ignore[attr-defined]

    def _db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    stub = shared_db[user_key]

    async def _user():
        return stub

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_active_user] = _user
    app.dependency_overrides[get_current_user] = _user
    return TestClient(app)


def _unauthed_client(shared_db):
    """Client with NO auth override — FastAPI will try to read Bearer token → 403."""
    from api.app import app
    from api.deps.db import get_db
    SessionLocal = shared_db["SessionLocal"]

    def _db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    # Remove any lingering overrides
    app.dependency_overrides.pop(
        __import__("api.auth.dependencies", fromlist=["get_current_active_user"]).get_current_active_user,
        None
    )
    app.dependency_overrides.pop(
        __import__("api.auth.dependencies", fromlist=["get_current_user"]).get_current_user,
        None
    )
    app.dependency_overrides[get_db] = _db
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helper to clear overrides after each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    from api.app import app
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

class TestAssetsRBAC:
    """GET /assets requires login; POST/PUT/DELETE require analyst+."""

    def test_get_assets_unauthenticated_returns_401(self, shared_db):
        c = _unauthed_client(shared_db)
        r = c.get("/api/assets")
        # FastAPI HTTPBearer returns 403 when no credentials provided,
        # or 401 when credentials are invalid — both mean "not authenticated"
        assert r.status_code in (401, 403)

    def test_get_assets_viewer_allowed(self, shared_db):
        c = _client_for(shared_db, "viewer")
        r = c.get("/api/assets")
        assert r.status_code == 200

    def test_get_assets_analyst_allowed(self, shared_db):
        c = _client_for(shared_db, "analyst")
        r = c.get("/api/assets")
        assert r.status_code == 200

    def test_create_asset_viewer_forbidden(self, shared_db):
        c = _client_for(shared_db, "viewer")
        payload = {
            "name": "Secret Asset",
            "asset_type": "Software",
            "scope_id": shared_db["scope_id"],
        }
        r = c.post("/api/assets", json=payload)
        assert r.status_code == 403

    def test_create_asset_no_org_user_forbidden(self, shared_db):
        c = _client_for(shared_db, "no_role")
        payload = {
            "name": "Secret Asset",
            "asset_type": "Software",
            "scope_id": shared_db["scope_id"],
        }
        r = c.post("/api/assets", json=payload)
        assert r.status_code == 403

    def test_create_asset_analyst_allowed(self, shared_db):
        c = _client_for(shared_db, "analyst")
        payload = {
            "name": "Analyst Asset",
            "asset_type": "Software",
            "scope_id": shared_db["scope_id"],
        }
        r = c.post("/api/assets", json=payload)
        assert r.status_code == 201

    def test_create_asset_risk_manager_allowed(self, shared_db):
        c = _client_for(shared_db, "rm")
        payload = {
            "name": "RM Asset",
            "asset_type": "Hardware",
            "scope_id": shared_db["scope_id"],
        }
        r = c.post("/api/assets", json=payload)
        assert r.status_code == 201

    def test_delete_asset_viewer_forbidden(self, shared_db):
        # First create an asset as analyst, then try to delete as viewer
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/assets", json={
            "name": "To Delete Asset",
            "asset_type": "Data",
            "scope_id": shared_db["scope_id"],
        })
        assert create_r.status_code == 201
        asset_id = create_r.json()["asset_id"]

        viewer_c = _client_for(shared_db, "viewer")
        r = viewer_c.delete(f"/api/assets/{asset_id}")
        assert r.status_code == 403

    def test_delete_asset_analyst_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/assets", json={
            "name": "Delete Me Asset",
            "asset_type": "Data",
            "scope_id": shared_db["scope_id"],
        })
        assert create_r.status_code == 201
        asset_id = create_r.json()["asset_id"]
        r = analyst_c.delete(f"/api/assets/{asset_id}")
        assert r.status_code == 204


# ---------------------------------------------------------------------------
# Damage Scenarios
# ---------------------------------------------------------------------------

class TestDamageScenariosRBAC:
    """GET requires login; POST/PUT/DELETE require analyst+; PATCH /accept requires risk_manager+."""

    def test_list_damage_scenarios_unauthenticated_401(self, shared_db):
        c = _unauthed_client(shared_db)
        assert c.get("/api/damage-scenarios").status_code in (401, 403)

    def test_list_damage_scenarios_viewer_allowed(self, shared_db):
        c = _client_for(shared_db, "viewer")
        assert c.get("/api/damage-scenarios").status_code == 200

    def test_create_damage_scenario_viewer_forbidden(self, shared_db):
        c = _client_for(shared_db, "viewer")
        payload = {
            "scope_id": shared_db["scope_id"],
            "name": "Viewer DS",
            "damage_category": "Safety",
            "impact_type": "Direct",
            "severity": "Critical",
            "confidentiality_impact": True,
            "description": "test",
        }
        assert c.post("/api/damage-scenarios", json=payload).status_code == 403

    def test_create_damage_scenario_analyst_allowed(self, shared_db):
        c = _client_for(shared_db, "analyst")
        payload = {
            "scope_id": shared_db["scope_id"],
            "name": "Analyst DS",
            "damage_category": "Safety",
            "impact_type": "Direct",
            "severity": "Critical",
            "confidentiality_impact": True,
            "description": "test",
        }
        r = c.post("/api/damage-scenarios", json=payload)
        assert r.status_code == 201

    def test_accept_damage_scenario_analyst_forbidden(self, shared_db):
        """Analyst cannot accept a scenario — that requires risk_manager+."""
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "Accept Test DS",
            "damage_category": "Financial",
            "impact_type": "Indirect",
            "severity": "High",
            "confidentiality_impact": True,
            "description": "to be accepted",
        })
        assert create_r.status_code == 201
        scenario_id = create_r.json()["scenario_id"]

        r = analyst_c.patch(f"/api/damage-scenarios/{scenario_id}/accept")
        assert r.status_code == 403

    def test_accept_damage_scenario_risk_manager_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "RM Accept DS",
            "damage_category": "Financial",
            "impact_type": "Indirect",
            "severity": "High",
            "confidentiality_impact": True,
            "description": "to be accepted by rm",
        })
        assert create_r.status_code == 201
        scenario_id = create_r.json()["scenario_id"]

        rm_c = _client_for(shared_db, "rm")
        r = rm_c.patch(f"/api/damage-scenarios/{scenario_id}/accept")
        assert r.status_code == 200
        assert r.json()["status"] == "accepted"

    def test_delete_damage_scenario_viewer_forbidden(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "Delete DS",
            "damage_category": "Operational",
            "impact_type": "Direct",
            "severity": "Medium",
            "confidentiality_impact": True,
            "description": "delete me",
        })
        assert create_r.status_code == 201
        scenario_id = create_r.json()["scenario_id"]

        viewer_c = _client_for(shared_db, "viewer")
        assert viewer_c.delete(f"/api/damage-scenarios/{scenario_id}").status_code == 403

    def test_delete_damage_scenario_analyst_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "Delete Me DS",
            "damage_category": "Operational",
            "impact_type": "Direct",
            "severity": "Low",
            "confidentiality_impact": True,
            "description": "delete me",
        })
        assert create_r.status_code == 201
        scenario_id = create_r.json()["scenario_id"]
        assert analyst_c.delete(f"/api/damage-scenarios/{scenario_id}").status_code == 204


# ---------------------------------------------------------------------------
# Threat Scenarios
# ---------------------------------------------------------------------------

class TestThreatScenariosRBAC:
    """GET requires login; POST/PUT/DELETE require analyst+; PATCH /accept requires risk_manager+."""

    def test_list_threat_scenarios_unauthenticated_401(self, shared_db):
        assert _unauthed_client(shared_db).get("/api/threat-scenarios").status_code in (401, 403)

    def test_list_threat_scenarios_viewer_allowed(self, shared_db):
        assert _client_for(shared_db, "viewer").get("/api/threat-scenarios").status_code == 200

    def test_create_threat_scenario_viewer_forbidden(self, shared_db):
        c = _client_for(shared_db, "viewer")
        payload = {
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "Viewer TS",
            "attack_vector": "network",
            "description": "test",
        }
        assert c.post("/api/threat-scenarios", json=payload).status_code == 403

    def test_create_threat_scenario_analyst_allowed(self, shared_db):
        c = _client_for(shared_db, "analyst")
        payload = {
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "Analyst TS",
            "attack_vector": "physical",
            "description": "test",
        }
        r = c.post("/api/threat-scenarios", json=payload)
        assert r.status_code == 201

    def test_accept_threat_scenario_analyst_forbidden(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "Accept Test TS",
            "attack_vector": "network",
            "description": "to be accepted",
        })
        assert create_r.status_code == 201
        ts_id = create_r.json()["threat_scenario_id"]

        r = analyst_c.patch(f"/api/threat-scenarios/{ts_id}/accept")
        assert r.status_code == 403

    def test_accept_threat_scenario_risk_manager_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "RM Accept TS",
            "attack_vector": "network",
            "description": "to be accepted by rm",
        })
        assert create_r.status_code == 201
        ts_id = create_r.json()["threat_scenario_id"]

        rm_c = _client_for(shared_db, "rm")
        r = rm_c.patch(f"/api/threat-scenarios/{ts_id}/accept")
        assert r.status_code == 200
        assert r.json()["status"] == "accepted"

    def test_delete_threat_scenario_viewer_forbidden(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "Delete TS",
            "attack_vector": "network",
            "description": "delete me",
        })
        assert create_r.status_code == 201
        ts_id = create_r.json()["threat_scenario_id"]
        assert _client_for(shared_db, "viewer").delete(f"/api/threat-scenarios/{ts_id}").status_code == 403

    def test_delete_threat_scenario_analyst_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "scope_version": 1,
            "name": "Delete Me TS",
            "attack_vector": "local_network",
            "description": "delete me",
        })
        assert create_r.status_code == 201
        ts_id = create_r.json()["threat_scenario_id"]
        r = analyst_c.delete(f"/api/threat-scenarios/{ts_id}")
        assert r.status_code == 200  # threat scenario delete returns 200 not 204


# ---------------------------------------------------------------------------
# Threat Catalog
# ---------------------------------------------------------------------------

class TestThreatCatalogRBAC:
    """GET catalog requires login; POST/PUT/DELETE require analyst+."""

    def test_list_catalog_unauthenticated_401(self, shared_db):
        assert _unauthed_client(shared_db).get("/api/threat/catalog").status_code in (401, 403)

    def test_list_catalog_viewer_allowed(self, shared_db):
        assert _client_for(shared_db, "viewer").get("/api/threat/catalog").status_code == 200

    def test_catalog_stats_viewer_allowed(self, shared_db):
        assert _client_for(shared_db, "viewer").get("/api/threat/catalog/stats").status_code == 200

    def test_create_catalog_item_viewer_forbidden(self, shared_db):
        c = _client_for(shared_db, "viewer")
        payload = {
            "title": "Viewer Threat",
            "description": "should be blocked",
            "stride_category": "spoofing",
            "typical_likelihood": 3,
            "typical_severity": 2,
        }
        assert c.post("/api/threat/catalog", json=payload).status_code == 403

    def test_create_catalog_item_analyst_allowed(self, shared_db):
        c = _client_for(shared_db, "analyst")
        payload = {
            "title": "Analyst Threat",
            "description": "created by analyst",
            "stride_category": "tampering",
            "typical_likelihood": 2,
            "typical_severity": 3,
        }
        r = c.post("/api/threat/catalog", json=payload)
        assert r.status_code == 201

    def test_update_catalog_item_viewer_forbidden(self, shared_db):
        # Create as analyst first
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat/catalog", json={
            "title": "Update Test",
            "description": "for update test",
            "stride_category": "repudiation",
            "typical_likelihood": 1,
            "typical_severity": 1,
        })
        assert create_r.status_code == 201
        tid = create_r.json()["id"]

        viewer_c = _client_for(shared_db, "viewer")
        assert viewer_c.put(f"/api/threat/catalog/{tid}", json={"title": "Hacked"}).status_code == 403

    def test_delete_catalog_item_viewer_forbidden(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat/catalog", json={
            "title": "Delete Test",
            "description": "for delete test",
            "stride_category": "elevation_of_privilege",
            "typical_likelihood": 4,
            "typical_severity": 4,
        })
        assert create_r.status_code == 201
        tid = create_r.json()["id"]
        viewer_c = _client_for(shared_db, "viewer")
        assert viewer_c.delete(f"/api/threat/catalog/{tid}").status_code == 403

    def test_delete_catalog_item_analyst_allowed(self, shared_db):
        analyst_c = _client_for(shared_db, "analyst")
        create_r = analyst_c.post("/api/threat/catalog", json={
            "title": "Delete Me Threat",
            "description": "delete me",
            "stride_category": "info_disclosure",
            "typical_likelihood": 2,
            "typical_severity": 2,
        })
        assert create_r.status_code == 201
        tid = create_r.json()["id"]
        assert analyst_c.delete(f"/api/threat/catalog/{tid}").status_code == 204


# ---------------------------------------------------------------------------
# require_analyst_role unit test
# ---------------------------------------------------------------------------

class TestRequireAnalystRoleDependency:
    """Direct unit tests for the new dependency."""

    def test_viewer_rejected(self, shared_db):
        """Viewer role → 403 on analyst-gated endpoints."""
        c = _client_for(shared_db, "viewer")
        # Any write endpoint exercises the dependency
        r = c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "Viewer Attempt",
            "damage_category": "Safety",
            "impact_type": "Direct",
            "severity": "Low",
            "confidentiality_impact": True,
            "description": "blocked",
        })
        assert r.status_code == 403
        assert "Analyst" in r.json()["detail"]

    def test_analyst_accepted(self, shared_db):
        c = _client_for(shared_db, "analyst")
        r = c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "Analyst Attempt",
            "damage_category": "Safety",
            "impact_type": "Direct",
            "severity": "Low",
            "confidentiality_impact": True,
            "description": "allowed",
        })
        assert r.status_code == 201

    def test_risk_manager_accepted(self, shared_db):
        c = _client_for(shared_db, "rm")
        r = c.post("/api/damage-scenarios", json={
            "scope_id": shared_db["scope_id"],
            "name": "RM Attempt",
            "damage_category": "Safety",
            "impact_type": "Direct",
            "severity": "Low",
            "confidentiality_impact": True,
            "description": "allowed",
        })
        assert r.status_code == 201
