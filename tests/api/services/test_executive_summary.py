"""
Unit tests for the executive summary section.

Covers: compute_executive_stats() and build_executive_summary_section() in
api/services/reporting/sections/executive_summary_section.py
"""
import unittest

from reportlab.platypus import Paragraph

from api.services.reporting.pdf_renderer import create_styles
from api.services.reporting.sections.executive_summary_section import (
    build_executive_summary_section,
    compute_executive_stats,
)


def _treatment(risk_level=None, status=None, selected=None):
    return {
        "risk_level": risk_level,
        "treatment_status": status,
        "selected_treatment": selected,
    }


class TestComputeExecutiveStats(unittest.TestCase):
    def test_counts_reflect_inputs(self):
        stats = compute_executive_stats(
            assets=[{"asset_id": "a1"}, {"asset_id": "a2"}],
            damage_scenarios=[{"scenario_id": "d1"}],
            threat_scenarios=[{"threat_scenario_id": "t1"}, {"threat_scenario_id": "t2"}],
            risk_treatments=[_treatment("High"), _treatment("Low")],
        )
        self.assertEqual(stats["asset_count"], 2)
        self.assertEqual(stats["damage_scenario_count"], 1)
        self.assertEqual(stats["threat_scenario_count"], 2)
        self.assertEqual(stats["risk_count"], 2)

    def test_highest_risk_uses_severity_order(self):
        stats = compute_executive_stats(
            [], [], [],
            [_treatment("Low"), _treatment("Critical"), _treatment("Medium")],
        )
        self.assertEqual(stats["highest_risk"], "Critical")

    def test_highest_risk_none_when_empty(self):
        stats = compute_executive_stats([], [], [], [])
        self.assertEqual(stats["highest_risk"], "None")

    def test_coverage_and_approved_counts(self):
        treatments = [
            _treatment("High", "approved", "Mitigate"),
            _treatment("Medium", "draft", "Accept"),
            _treatment("Low", None, None),
        ]
        stats = compute_executive_stats([], [], [], treatments)
        # 2 of 3 have a selected treatment -> 67%
        self.assertEqual(stats["treatment_coverage_pct"], 67)
        self.assertEqual(stats["approved_treatments"], 1)

    def test_coverage_zero_when_no_treatments(self):
        stats = compute_executive_stats([], [], [], [])
        self.assertEqual(stats["treatment_coverage_pct"], 0)
        self.assertEqual(stats["approved_treatments"], 0)

    def test_risk_distribution_groups_levels(self):
        stats = compute_executive_stats(
            [], [], [],
            [_treatment("High"), _treatment("High"), _treatment("Low")],
        )
        self.assertEqual(stats["risk_distribution"]["High"], 2)
        self.assertEqual(stats["risk_distribution"]["Low"], 1)


class TestBuildExecutiveSummarySection(unittest.TestCase):
    def test_section_has_heading_and_narrative(self):
        styles = create_styles()
        story = build_executive_summary_section(
            assets=[{"asset_id": "a1"}],
            damage_scenarios=[{"scenario_id": "d1"}],
            threat_scenarios=[],
            risk_treatments=[_treatment("High", "approved", "Mitigate")],
            styles=styles,
        )
        texts = " ".join(el.text for el in story if isinstance(el, Paragraph))
        self.assertIn("Executive Summary", texts)
        self.assertIn("1 asset(s)", texts)


if __name__ == "__main__":
    unittest.main()
