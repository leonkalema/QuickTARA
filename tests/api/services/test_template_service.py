"""
Unit tests for the report template service.

Covers: api/services/reporting/template_service.py and the report_templates
model. Uses an in-memory SQLite database.
"""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.product_asset_models import Base
# Importing the models registers their tables on the shared Base.metadata.
# Organization is needed so the report_templates FK target exists.
from api.models.user import Organization  # noqa: F401
from db.report_template_models import ReportTemplate  # noqa: F401
from api.models.report_config import ReportAudience, ReportConfig, SectionKey
from api.services.reporting.presets import default_config_for_audience
from api.services.reporting import template_service as svc


class TestTemplateService(unittest.TestCase):
    """Tests for built-in resolution and org-template CRUD."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.org_id = "org-1"

    def tearDown(self):
        self.db.close()

    # --- Built-in presets ---

    def test_list_includes_builtins_first(self):
        summaries = svc.list_templates(self.db, self.org_id)
        self.assertTrue(summaries[0].is_builtin)
        names = [s.name for s in summaries]
        self.assertIn("Internal — Full", names)
        self.assertIn("External — Customer/OEM", names)
        self.assertIn("Auditor / Regulator", names)

    def test_resolve_builtin_by_name(self):
        config = svc.resolve_config(self.db, "External — Customer/OEM")
        self.assertEqual(config.audience, ReportAudience.EXTERNAL)

    # --- Create ---

    def test_create_persists_org_template(self):
        config = default_config_for_audience(ReportAudience.INTERNAL)
        row = svc.create_template(self.db, self.org_id, "Acme Standard", config, "user-1")
        self.assertIsNotNone(row.template_id)
        self.assertFalse(row.is_builtin)
        listed = [s.name for s in svc.list_templates(self.db, self.org_id)]
        self.assertIn("Acme Standard", listed)

    def test_create_rejects_blank_name(self):
        config = ReportConfig()
        with self.assertRaises(ValueError):
            svc.create_template(self.db, self.org_id, "   ", config)

    def test_create_rejects_builtin_name(self):
        config = ReportConfig()
        with self.assertRaises(ValueError):
            svc.create_template(self.db, self.org_id, "Internal — Full", config)

    def test_create_rejects_duplicate_name_in_org(self):
        config = ReportConfig()
        svc.create_template(self.db, self.org_id, "Dup", config)
        with self.assertRaises(ValueError):
            svc.create_template(self.db, self.org_id, "Dup", config)

    def test_same_name_allowed_across_orgs(self):
        config = ReportConfig()
        svc.create_template(self.db, "org-a", "Shared", config)
        # Different org, same name should be fine.
        row = svc.create_template(self.db, "org-b", "Shared", config)
        self.assertIsNotNone(row.template_id)

    # --- Resolve / round-trip ---

    def test_resolve_org_template_roundtrips_config(self):
        config = ReportConfig(sections={SectionKey.TRACEABILITY: True})
        row = svc.create_template(self.db, self.org_id, "Trace Only", config)
        resolved = svc.resolve_config(self.db, row.template_id)
        self.assertIn(SectionKey.TRACEABILITY, resolved.enabled_sections())

    def test_resolve_unknown_id_raises(self):
        with self.assertRaises(ValueError):
            svc.resolve_config(self.db, "does-not-exist")

    # --- Update ---

    def test_update_replaces_config(self):
        row = svc.create_template(self.db, self.org_id, "T", ReportConfig())
        new_config = ReportConfig(sections={SectionKey.ISO_COMPLIANCE: True})
        svc.update_template(self.db, row.template_id, new_config)
        resolved = svc.resolve_config(self.db, row.template_id)
        self.assertEqual(resolved.enabled_sections(), [SectionKey.ISO_COMPLIANCE])

    def test_update_unknown_raises(self):
        with self.assertRaises(ValueError):
            svc.update_template(self.db, "nope", ReportConfig())

    # --- Delete ---

    def test_delete_removes_template(self):
        row = svc.create_template(self.db, self.org_id, "Temp", ReportConfig())
        svc.delete_template(self.db, row.template_id)
        with self.assertRaises(ValueError):
            svc.resolve_config(self.db, row.template_id)

    def test_delete_builtin_rejected(self):
        with self.assertRaises(ValueError):
            svc.delete_template(self.db, "Internal — Full")


if __name__ == "__main__":
    unittest.main()
