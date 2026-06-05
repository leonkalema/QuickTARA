"""
Unit tests for conditional section assembly in the report builder.

Covers: resolve_sections(), _build_section() dispatch, and build_complete_report()
wiring in api/services/reporting/report_builder.py
"""
import unittest
from unittest import mock

from api.models.report_config import (
    ReportAudience,
    ReportConfig,
    SectionKey,
)
from api.services.reporting import report_builder
from api.services.reporting.presets import default_config_for_audience


class TestResolveSections(unittest.TestCase):
    """Tests for resolve_sections() — ordering and CRA-conditional rule."""

    def test_orders_by_canonical_sequence(self):
        config = ReportConfig(sections={
            SectionKey.TRACEABILITY: True,
            SectionKey.ISO_COMPLIANCE: True,
            SectionKey.ASSET_INVENTORY: True,
        })
        with mock.patch.object(report_builder, "has_cra_assessment", return_value=False):
            resolved = report_builder.resolve_sections(config, "scope-1", db=None)
        # ISO_COMPLIANCE was moved after ASSET_INVENTORY in the canonical order
        self.assertEqual(resolved, [
            SectionKey.ASSET_INVENTORY,
            SectionKey.ISO_COMPLIANCE,
            SectionKey.TRACEABILITY,
        ])

    def test_cra_omitted_when_no_assessment(self):
        config = ReportConfig(sections={SectionKey.CRA_COMPLIANCE: True})
        with mock.patch.object(report_builder, "has_cra_assessment", return_value=False):
            resolved = report_builder.resolve_sections(config, "scope-1", db=None)
        self.assertNotIn(SectionKey.CRA_COMPLIANCE, resolved)

    def test_cra_kept_when_assessment_exists(self):
        config = ReportConfig(sections={SectionKey.CRA_COMPLIANCE: True})
        with mock.patch.object(report_builder, "has_cra_assessment", return_value=True):
            resolved = report_builder.resolve_sections(config, "scope-1", db=None)
        self.assertIn(SectionKey.CRA_COMPLIANCE, resolved)

    def test_disabled_sections_excluded(self):
        config = ReportConfig(sections={SectionKey.ISO_COMPLIANCE: True})
        with mock.patch.object(report_builder, "has_cra_assessment", return_value=True):
            resolved = report_builder.resolve_sections(config, "scope-1", db=None)
        self.assertEqual(resolved, [SectionKey.ISO_COMPLIANCE])

    def test_external_preset_drops_traceability(self):
        config = default_config_for_audience(ReportAudience.EXTERNAL)
        with mock.patch.object(report_builder, "has_cra_assessment", return_value=True):
            resolved = report_builder.resolve_sections(config, "scope-1", db=None)
        self.assertNotIn(SectionKey.TRACEABILITY, resolved)
        self.assertIn(SectionKey.CYBERSECURITY_GOALS, resolved)


class TestBuildSectionDispatch(unittest.TestCase):
    """Tests for _build_section() dispatch."""

    def test_document_control_is_not_a_body_section(self):
        # DOCUMENT_CONTROL renders in the header, so the body builder returns [].
        result = report_builder._build_section(
            SectionKey.DOCUMENT_CONTROL, "scope-1", db=None, styles={},
            config=default_config_for_audience(ReportAudience.INTERNAL),
        )
        self.assertEqual(result, [])

    def test_iso_compliance_dispatches_to_builder(self):
        with mock.patch.object(
            report_builder, "build_compliance_section", return_value=["iso"]
        ) as mocked:
            result = report_builder._build_section(
                SectionKey.ISO_COMPLIANCE, "scope-1", db=None, styles={},
                config=default_config_for_audience(ReportAudience.INTERNAL),
            )
        mocked.assert_called_once()
        self.assertEqual(result, ["iso"])


class TestBuildCompleteReportWiring(unittest.TestCase):
    """Tests for build_complete_report() orchestration (no real DB)."""

    def test_missing_scope_raises(self):
        with mock.patch.object(report_builder, "get_scope_info", return_value=None):
            with self.assertRaises(ValueError):
                report_builder.build_complete_report("missing", db=None)

    def test_defaults_to_internal_profile_when_no_config(self):
        captured = {}

        def fake_render(scope_info, sections, config=None):
            captured["section_count"] = len(sections)
            return b"%PDF-FAKE"

        with mock.patch.object(report_builder, "get_scope_info", return_value={"name": "P"}), \
             mock.patch.object(report_builder, "has_cra_assessment", return_value=False), \
             mock.patch.object(report_builder, "_build_section", return_value=["x"]) as build_sec, \
             mock.patch.object(report_builder, "render_pdf", side_effect=fake_render):
            out = report_builder.build_complete_report("scope-1", db=None)

        self.assertEqual(out, b"%PDF-FAKE")
        # Internal profile enables all 11 sections, minus CRA (no assessment).
        # _build_section is called once per resolved section (mocked to return
        # ["x"]), so count == resolved sections.
        self.assertEqual(build_sec.call_count, 17)  # 18 internal sections - CRA (no assessment)
        self.assertEqual(captured["section_count"], 17)

    def test_empty_sections_are_skipped(self):
        config = ReportConfig(sections={
            SectionKey.ISO_COMPLIANCE: True,
            SectionKey.DOCUMENT_CONTROL: True,
        })

        def fake_build(key, scope_id, db, styles, config):
            return [] if key == SectionKey.DOCUMENT_CONTROL else ["body"]

        captured = {}

        def fake_render(scope_info, sections, config=None):
            captured["sections"] = sections
            return b"%PDF"

        with mock.patch.object(report_builder, "get_scope_info", return_value={"name": "P"}), \
             mock.patch.object(report_builder, "has_cra_assessment", return_value=True), \
             mock.patch.object(report_builder, "_build_section", side_effect=fake_build), \
             mock.patch.object(report_builder, "render_pdf", side_effect=fake_render):
            report_builder.build_complete_report("scope-1", db=None, config=config)

        # Only the non-empty ISO section should reach the renderer.
        self.assertEqual(captured["sections"], [["body"]])


if __name__ == "__main__":
    unittest.main()
