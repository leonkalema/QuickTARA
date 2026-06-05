"""
Unit tests for the report configuration model and audience presets.

Covers: api/models/report_config.py and api/services/reporting/presets.py
"""
import unittest

from pydantic import ValidationError

from api.models.report_config import (
    ReportAudience,
    ReportClassification,
    ReportConfig,
    ReportDetailLevel,
    ReportMetadata,
    SECTION_ORDER,
    SectionKey,
)
from api.services.reporting.presets import (
    builtin_preset_names,
    default_config_for_audience,
    get_builtin_preset,
)


class TestReportConfigModel(unittest.TestCase):
    """Tests for the ReportConfig pydantic model."""

    def test_defaults(self):
        """A bare config defaults to internal/full/internal with all sections off."""
        config = ReportConfig()
        self.assertEqual(config.audience, ReportAudience.INTERNAL)
        self.assertEqual(config.detail_level, ReportDetailLevel.FULL)
        self.assertEqual(config.classification, ReportClassification.INTERNAL)
        # Validator fills every known section as an explicit False.
        self.assertEqual(set(config.sections.keys()), set(SECTION_ORDER))
        self.assertTrue(all(v is False for v in config.sections.values()))

    def test_metadata_defaults_none(self):
        """Metadata fields default to None."""
        meta = ReportConfig().metadata
        self.assertIsNone(meta.author)
        self.assertIsNone(meta.approver)
        self.assertIsNone(meta.reference)

    def test_fill_missing_sections(self):
        """Partial section dicts are completed with False for missing keys."""
        config = ReportConfig(sections={SectionKey.ISO_COMPLIANCE: True})
        self.assertTrue(config.sections[SectionKey.ISO_COMPLIANCE])
        self.assertFalse(config.sections[SectionKey.TRACEABILITY])
        self.assertEqual(len(config.sections), len(SECTION_ORDER))

    def test_enabled_sections_follows_canonical_order(self):
        """enabled_sections() returns only enabled keys, in SECTION_ORDER."""
        config = ReportConfig(sections={
            SectionKey.CYBERSECURITY_GOALS: True,
            SectionKey.DOCUMENT_CONTROL: True,
            SectionKey.ISO_COMPLIANCE: True,
        })
        enabled = config.enabled_sections()
        # ISO_COMPLIANCE is now near end (after OPEN_ISSUES) per OEM convention
        self.assertEqual(enabled, [
            SectionKey.DOCUMENT_CONTROL,
            SectionKey.CYBERSECURITY_GOALS,
            SectionKey.ISO_COMPLIANCE,
        ])

    def test_is_enabled(self):
        config = ReportConfig(sections={SectionKey.RISK_SUMMARY: True})
        self.assertTrue(config.is_enabled(SectionKey.RISK_SUMMARY))
        self.assertFalse(config.is_enabled(SectionKey.TRACEABILITY))

    def test_invalid_audience_rejected(self):
        with self.assertRaises(ValidationError):
            ReportConfig(audience="marketing")

    def test_roundtrip_serialization(self):
        """Config survives a JSON round-trip with string enum keys."""
        original = default_config_for_audience(ReportAudience.EXTERNAL)
        dumped = original.model_dump(mode="json")
        # Section keys serialize to their string values.
        self.assertIn("iso_compliance", dumped["sections"])
        restored = ReportConfig.model_validate(dumped)
        self.assertEqual(restored.enabled_sections(), original.enabled_sections())
        self.assertEqual(restored.audience, original.audience)


class TestAudiencePresets(unittest.TestCase):
    """Tests for audience default profiles."""

    def test_internal_enables_everything(self):
        config = default_config_for_audience(ReportAudience.INTERNAL)
        self.assertEqual(config.detail_level, ReportDetailLevel.FULL)
        self.assertEqual(config.classification, ReportClassification.INTERNAL)
        # Internal enables all sections except APPENDICES (which is an
        # external-package deliverable, not needed for internal working docs)
        expected = set(SECTION_ORDER) - {SectionKey.APPENDICES}
        self.assertEqual(set(config.enabled_sections()), expected)

    def test_external_hides_traceability_and_is_summary(self):
        config = default_config_for_audience(ReportAudience.EXTERNAL)
        self.assertEqual(config.detail_level, ReportDetailLevel.SUMMARY)
        self.assertEqual(config.classification, ReportClassification.CONFIDENTIAL)
        self.assertFalse(config.is_enabled(SectionKey.TRACEABILITY))
        self.assertTrue(config.is_enabled(SectionKey.CYBERSECURITY_GOALS))

    def test_auditor_enables_traceability_full_detail(self):
        config = default_config_for_audience(ReportAudience.AUDITOR)
        self.assertEqual(config.detail_level, ReportDetailLevel.FULL)
        self.assertTrue(config.is_enabled(SectionKey.TRACEABILITY))
        self.assertTrue(config.is_enabled(SectionKey.ISO_COMPLIANCE))

    def test_all_audiences_include_document_control(self):
        for audience in ReportAudience:
            config = default_config_for_audience(audience)
            self.assertTrue(
                config.is_enabled(SectionKey.DOCUMENT_CONTROL),
                f"{audience} should include document control",
            )


class TestBuiltinPresets(unittest.TestCase):
    """Tests for named built-in presets used as templates."""

    def test_preset_names(self):
        names = builtin_preset_names()
        self.assertEqual(names, [
            "Internal — Full",
            "External — Customer/OEM",
            "Auditor / Regulator",
        ])

    def test_get_builtin_preset_maps_to_audience(self):
        self.assertEqual(
            get_builtin_preset("External — Customer/OEM").audience,
            ReportAudience.EXTERNAL,
        )

    def test_unknown_preset_raises(self):
        with self.assertRaises(ValueError):
            get_builtin_preset("Does Not Exist")


if __name__ == "__main__":
    unittest.main()
