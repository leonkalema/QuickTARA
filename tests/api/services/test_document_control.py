"""
Unit tests for the document-control block in the PDF renderer.

Covers: build_document_control_lines() and build_document_header() in
api/services/reporting/pdf_renderer.py
"""
import unittest

from reportlab.platypus import Paragraph

from api.models.report_config import (
    ReportClassification,
    ReportConfig,
    ReportMetadata,
)
from api.services.reporting.pdf_renderer import (
    build_document_control_lines,
    build_document_header,
    create_styles,
)


class TestDocumentControlLines(unittest.TestCase):
    """Tests for the pure document-control line builder."""

    def test_none_config_returns_empty(self):
        self.assertEqual(build_document_control_lines(None), [])

    def test_classification_always_present(self):
        config = ReportConfig(classification=ReportClassification.CONFIDENTIAL)
        lines = build_document_control_lines(config)
        self.assertEqual(lines[0], "Classification: Confidential")

    def test_optional_metadata_included_when_present(self):
        config = ReportConfig(
            classification=ReportClassification.INTERNAL,
            metadata=ReportMetadata(
                author="Jane Doe",
                approver="John Smith",
                reference="DOC-001",
            ),
        )
        lines = build_document_control_lines(config)
        self.assertIn("Author: Jane Doe", lines)
        self.assertIn("Approver: John Smith", lines)
        self.assertIn("Reference: DOC-001", lines)

    def test_absent_metadata_omitted(self):
        config = ReportConfig(metadata=ReportMetadata(author="Only Author"))
        lines = build_document_control_lines(config)
        self.assertIn("Author: Only Author", lines)
        self.assertFalse(any(line.startswith("Approver") for line in lines))
        self.assertFalse(any(line.startswith("Reference") for line in lines))


class TestDocumentHeaderRendering(unittest.TestCase):
    """Tests that the header actually renders the document-control block."""

    def _header_texts(self, config):
        styles = create_styles()
        story = build_document_header({"name": "Widget", "version": "2.0"}, styles, config)
        return [el.text for el in story if isinstance(el, Paragraph)]

    def test_header_includes_classification_and_approver(self):
        config = ReportConfig(
            classification=ReportClassification.CONFIDENTIAL,
            metadata=ReportMetadata(approver="Alice"),
        )
        texts = self._header_texts(config)
        joined = " ".join(texts)
        self.assertIn("Classification:", joined)
        self.assertIn("Confidential", joined)
        self.assertIn("Approver:", joined)
        self.assertIn("Alice", joined)

    def test_header_without_config_has_no_classification(self):
        texts = self._header_texts(None)
        joined = " ".join(texts)
        self.assertNotIn("Classification:", joined)
        # Core product info still renders.
        self.assertIn("Widget", joined)


if __name__ == "__main__":
    unittest.main()
