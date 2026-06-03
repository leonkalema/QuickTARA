"""Tests for /api/users endpoints — focused on the org-role fix.

Verifies that:
- GET /api/users returns an `organizations` list per user with correct role data.
- POST /api/users creates the user; once an org membership is added the role
  shows up in GET response.
- Tool-admin users surface role="tool_admin" and is_superuser=True.
- Users with no org membership have an empty `organizations` list.
"""
from __future__ import annotations

import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_db(tmp_path):
    """Return (url, engine, SessionLocal) for an ephemeral SQLite DB."""
    db_path = tmp_path / "users_test.db"
    url = f"sqlite:///{db_path}"

    import db.base  # noqa: F401 — registers ORM models on Base
    import db.damage_scenario  # noqa: F401
    import db.threat_scenario  # noqa: F401
    import db.attack_path  # noqa: F401
    import db.risk_treatment  # noqa: F401
    import db.audit_models  # noqa: F401
    import db.cra_models  # noqa: F401
    import db.cra_incident_models  # noqa: F401
    import db.cra_sbom_models  # noqa: F401
    from api.models import simple_attack_path  # noqa: F401
    from api.models import user as user_models  # noqa: F401
    from db.product_asset_models import Base

    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return url, engine, SessionLocal


def _seed_org(db: Session, name: str = "Test Org") -> str:
    """Insert an Organization row and return its ID."""
    from api.models.user import Organization
    org_id = str(uuid.uuid4())
    org = Organization(organization_id=org_id, name=name)
    db.add(org)
    db.commit()
    return org_id


def _seed_user(db: Session, *, superuser: bool = False, email: str | None = None) -> "User":
    from api.models.user import User, UserStatus
    from api.auth.security import security_manager

    uid = str(uuid.uuid4())
    email = email or f"user_{uid[:8]}@example.com"
    user = User(
        user_id=uid,
        email=email,
        username=f"user_{uid[:8]}",
        first_name="Test",
        last_name="User",
        hashed_password=security_manager.get_password_hash("password123"),
        status=UserStatus.ACTIVE,
        is_verified=True,
        is_superuser=superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _assign_org_role(db: Session, user_id: str, org_id: str, role: str) -> None:
    from api.models.user import user_organizations
    from datetime import datetime
    db.execute(
        user_organizations.insert().values(
            user_id=user_id,
            organization_id=org_id,
            role=role,
            created_at=datetime.utcnow(),
        )
    )
    db.commit()


@pytest.fixture
def admin_client(tmp_path):
    """TestClient whose current user is a Tool Admin (is_superuser=True)."""
    url, engine, SessionLocal = _make_db(tmp_path)

    from api.app import app
    from api.auth.dependencies import get_current_active_user, get_current_user
    from api.deps.db import get_db

    def _db() -> Generator[Session, None, None]:
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    # seed the admin user so the DB row exists
    session = SessionLocal()
    admin = _seed_user(session, superuser=True, email="admin@example.com")
    session.close()

    class _AdminStub:
        user_id = admin.user_id
        email = admin.email
        status = "active"
        is_superuser = True

    async def _current_user():
        return _AdminStub()

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_active_user] = _current_user
    app.dependency_overrides[get_current_user] = _current_user

    with TestClient(app) as client:
        # expose helpers on the client object for convenience
        client._SessionLocal = SessionLocal  # type: ignore[attr-defined]
        yield client

    app.dependency_overrides.clear()
    engine.dispose()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetUsersReturnsOrgRoles:
    def test_user_with_org_role_included_in_organizations(self, admin_client):
        """GET /api/users — each user has `organizations` with their role."""
        db: Session = admin_client._SessionLocal()
        try:
            org_id = _seed_org(db)
            user = _seed_user(db, email="analyst@example.com")
            _assign_org_role(db, user.user_id, org_id, "analyst")
        finally:
            db.close()

        resp = admin_client.get("/api/users")
        assert resp.status_code == 200
        users = resp.json()

        # find the analyst user in the response
        match = next((u for u in users if u["email"] == "analyst@example.com"), None)
        assert match is not None, "analyst user not in response"
        assert match["organizations"] != [], "organizations list should not be empty"
        assert match["organizations"][0]["role"] == "analyst"
        assert match["organizations"][0]["organization_id"] == org_id

    def test_user_without_org_has_empty_organizations(self, admin_client):
        """Users with no org membership get an empty `organizations` list."""
        db: Session = admin_client._SessionLocal()
        try:
            user = _seed_user(db, email="noorg@example.com")
        finally:
            db.close()

        resp = admin_client.get("/api/users")
        assert resp.status_code == 200
        users = resp.json()

        match = next((u for u in users if u["email"] == "noorg@example.com"), None)
        assert match is not None
        assert match["organizations"] == []

    def test_role_field_reflects_first_org_role(self, admin_client):
        """Top-level `role` field should equal the user's first org role."""
        db: Session = admin_client._SessionLocal()
        try:
            org_id = _seed_org(db)
            user = _seed_user(db, email="viewer@example.com")
            _assign_org_role(db, user.user_id, org_id, "viewer")
        finally:
            db.close()

        resp = admin_client.get("/api/users")
        assert resp.status_code == 200
        match = next((u for u in resp.json() if u["email"] == "viewer@example.com"), None)
        assert match is not None
        assert match["role"] == "viewer"

    def test_tool_admin_role_and_is_superuser(self, admin_client):
        """Superuser rows expose role='tool_admin' and is_superuser=True."""
        resp = admin_client.get("/api/users")
        assert resp.status_code == 200
        admins = [u for u in resp.json() if u["is_superuser"]]
        assert len(admins) >= 1
        for admin in admins:
            assert admin["role"] == "tool_admin"

    def test_multiple_org_memberships_all_returned(self, admin_client):
        """A user in two orgs should have both entries in `organizations`."""
        db: Session = admin_client._SessionLocal()
        try:
            org1 = _seed_org(db, "Org Alpha")
            org2 = _seed_org(db, "Org Beta")
            user = _seed_user(db, email="multiorg@example.com")
            _assign_org_role(db, user.user_id, org1, "analyst")
            _assign_org_role(db, user.user_id, org2, "risk_manager")
        finally:
            db.close()

        resp = admin_client.get("/api/users")
        assert resp.status_code == 200
        match = next((u for u in resp.json() if u["email"] == "multiorg@example.com"), None)
        assert match is not None
        org_roles = {o["organization_id"]: o["role"] for o in match["organizations"]}
        assert org_roles.get(org1) == "analyst"
        assert org_roles.get(org2) == "risk_manager"


class TestCreateUserOrgRoleResponse:
    def test_create_user_returns_empty_organizations(self, admin_client):
        """POST /api/users — newly created user has no org memberships yet."""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "secure123",
            "role": "analyst",
            "status": "active",
        }
        resp = admin_client.post("/api/users", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        assert "organizations" in data
        assert data["organizations"] == []

    def test_create_tool_admin_sets_is_superuser(self, admin_client):
        """POST with role=tool_admin → is_superuser=True."""
        payload = {
            "email": "newadmin@example.com",
            "username": "newadmin",
            "first_name": "Admin",
            "last_name": "User",
            "password": "secure123",
            "role": "tool_admin",
            "status": "active",
        }
        resp = admin_client.post("/api/users", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_superuser"] is True
        assert data["role"] == "tool_admin"

    def test_create_user_then_assign_org_shows_role_in_get(self, admin_client):
        """After org assignment, GET /api/users shows the role."""
        # Create the user
        payload = {
            "email": "assigned@example.com",
            "username": "assigned",
            "first_name": "Assigned",
            "last_name": "User",
            "password": "secure123",
            "role": "analyst",
            "status": "active",
        }
        create_resp = admin_client.post("/api/users", json=payload)
        assert create_resp.status_code == 200
        user_id = create_resp.json()["user_id"]

        # Assign org role directly in DB
        db: Session = admin_client._SessionLocal()
        try:
            org_id = _seed_org(db, "Assignment Org")
            _assign_org_role(db, user_id, org_id, "risk_manager")
        finally:
            db.close()

        # Now GET should reflect the role
        get_resp = admin_client.get("/api/users")
        assert get_resp.status_code == 200
        match = next((u for u in get_resp.json() if u["user_id"] == user_id), None)
        assert match is not None
        assert match["organizations"][0]["role"] == "risk_manager"
        assert match["role"] == "risk_manager"


class TestGetSingleUserReturnsOrgRole:
    def test_get_user_by_id_includes_organizations(self, admin_client):
        """GET /api/users/{user_id} includes org role data."""
        db: Session = admin_client._SessionLocal()
        try:
            org_id = _seed_org(db, "Single User Org")
            user = _seed_user(db, email="single@example.com")
            _assign_org_role(db, user.user_id, org_id, "auditor")
            user_id = user.user_id
        finally:
            db.close()

        resp = admin_client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["organizations"] != []
        assert data["organizations"][0]["role"] == "auditor"
        assert data["role"] == "auditor"
