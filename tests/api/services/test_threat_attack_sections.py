"""
Unit tests for the threat scenarios and attack paths sections.

Covers the pure helpers (map_threats_to_damages, feasibility_label) and the
builders' empty/non-empty behaviour.
"""
import unittest

from reportlab.platypus import Paragraph

from api.services.reporting.pdf_renderer import create_styles
from api.services.reporting.sections.threat_scenarios_section import (
    build_threat_scenarios_section,
    map_threats_to_damages,
)
from api.services.reporting.sections.attack_paths_section import (
    build_attack_paths_section,
    feasibility_label,
)


class TestMapThreatsToDamages(unittest.TestCase):
    def test_links_resolve_to_damage_names(self):
        threats = [{"threat_scenario_id": "t1", "name": "Spoofing", "description": "d"}]
        damages = [{"scenario_id": "d1", "name": "Loss of control"}]
        links = [{"threat_scenario_id": "t1", "scenario_id": "d1"}]
        rows = map_threats_to_damages(threats, damages, links)
        self.assertEqual(rows[0]["damage_names"], ["Loss of control"])

    def test_threat_without_links_has_empty_damages(self):
        threats = [{"threat_scenario_id": "t1", "name": "X", "description": ""}]
        rows = map_threats_to_damages(threats, [], [])
        self.assertEqual(rows[0]["damage_names"], [])

    def test_unknown_damage_id_is_skipped(self):
        threats = [{"threat_scenario_id": "t1", "name": "X", "description": ""}]
        links = [{"threat_scenario_id": "t1", "scenario_id": "missing"}]
        rows = map_threats_to_damages(threats, [], links)
        self.assertEqual(rows[0]["damage_names"], [])


class TestFeasibilityLabel(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(feasibility_label(5), "High")
        self.assertEqual(feasibility_label(12), "Medium")
        self.assertEqual(feasibility_label(17), "Low")
        self.assertEqual(feasibility_label(25), "Very Low")

    def test_none_is_unknown(self):
        self.assertEqual(feasibility_label(None), "Unknown")


class TestThreatScenariosSection(unittest.TestCase):
    def test_empty_shows_placeholder(self):
        styles = create_styles()
        story = build_threat_scenarios_section([], [], [], styles)
        texts = " ".join(el.text for el in story if isinstance(el, Paragraph))
        self.assertIn("No threat scenarios", texts)

    def test_non_empty_has_heading(self):
        styles = create_styles()
        threats = [{"threat_scenario_id": "t1", "name": "Tamper", "description": "d"}]
        story = build_threat_scenarios_section(threats, [], [], styles)
        texts = " ".join(el.text for el in story if isinstance(el, Paragraph))
        self.assertIn("Threat Scenarios", texts)


class TestAttackPathsSection(unittest.TestCase):
    def test_empty_shows_placeholder(self):
        styles = create_styles()
        story = build_attack_paths_section([], styles)
        texts = " ".join(el.text for el in story if isinstance(el, Paragraph))
        self.assertIn("No attack paths", texts)

    def test_non_empty_has_heading(self):
        styles = create_styles()
        paths = [{
            "attack_path_id": "ap1",
            "name": "Remote takeover",
            "attack_steps": "step1\nstep2",
            "overall_rating": 8.0,
        }]
        story = build_attack_paths_section(paths, styles, include_steps=True)
        texts = " ".join(el.text for el in story if isinstance(el, Paragraph))
        self.assertIn("Attack Paths", texts)


if __name__ == "__main__":
    unittest.main()
