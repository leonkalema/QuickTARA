"""
Integration tests for the reports router endpoints.

Covers: POST /reports/{scope_id}/pdf (config-driven) and the report template
management endpoints in api/routers/reports.py. Uses FastAPI dependency
overrides and an in-memory SQLite database.
"""
import unittest
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.product_asset_models import Base
from api.models.user import Organization  # noqa: F401  (registers table)
from db.report_template_models import ReportTemplate  # noqa: F401
from api.deps.db import get_db
from api.auth.dependencies import get_current_active_user
from api.routers import reports as reports_router


class _FakeOrg:
    organization_id = "org-1"


class _FakeUser:
    user_id = "user-1"
    organizations = [_FakeOrg()]


class TestReportsRouter(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        self.app = FastAPI()
        self.app.include_router(reports_router.router)

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        self.app.dependency_overrides[get_db] = override_get_db
        self.app.dependency_overrides[get_current_active_user] = lambda: _FakeUser()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    # --- PDF POST ---

    def test_post_pdf_passes_config_through(self):
        captured = {}

        def fake_build(scope_id, db, config=None):
            captured["scope_id"] = scope_id
            captured["audience"] = config.audience.value if config else None
            return b"%PDF-1.4 fake"

        with mock.patch.object(reports_router, "build_complete_report", side_effect=fake_build), \
             mock.patch(
                 "api.services.reporting.data_access.get_scope_info",
                 return_value={"name": "Widget"},
             ):
            resp = self.client.post(
                "/reports/scope-9/pdf",
                json={"audience": "external", "sections": {"iso_compliance": True}},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "application/pdf")
        self.assertEqual(captured["scope_id"], "scope-9")
        self.assertEqual(captured["audience"], "external")

    def test_post_pdf_without_body_uses_default(self):
        def fake_build(scope_id, db, config=None):
            # No body -> FastAPI passes None -> builder applies internal default.
            self.assertIsNone(config)
            return b"%PDF"

        with mock.patch.object(reports_router, "build_complete_report", side_effect=fake_build), \
             mock.patch(
                 "api.services.reporting.data_access.get_scope_info",
                 return_value={"name": "Widget"},
             ):
            resp = self.client.post("/reports/scope-1/pdf")
        self.assertEqual(resp.status_code, 200)

    # --- Templates ---

    def test_list_templates_returns_builtins(self):
        resp = self.client.get("/reports/templates")
        self.assertEqual(resp.status_code, 200)
        names = [t["name"] for t in resp.json()["templates"]]
        self.assertIn("Internal — Full", names)
        self.assertTrue(any(t["is_builtin"] for t in resp.json()["templates"]))

    def test_create_then_list_and_delete_template(self):
        create = self.client.post(
            "/reports/templates",
            json={"name": "Acme Standard", "config": {"audience": "external"}},
        )
        self.assertEqual(create.status_code, 201)
        template_id = create.json()["template_id"]
        self.assertFalse(create.json()["is_builtin"])

        listed = self.client.get("/reports/templates").json()["templates"]
        self.assertIn("Acme Standard", [t["name"] for t in listed])

        deleted = self.client.delete(f"/reports/templates/{template_id}")
        self.assertEqual(deleted.status_code, 204)

    def test_create_duplicate_returns_400(self):
        body = {"name": "Dup", "config": {"audience": "internal"}}
        self.client.post("/reports/templates", json=body)
        second = self.client.post("/reports/templates", json=body)
        self.assertEqual(second.status_code, 400)

    def test_delete_builtin_returns_400(self):
        resp = self.client.delete("/reports/templates/Internal — Full")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
