"""Tests for `core.cra_annex_vii` builder and renderer.

The builder is exercised through a stubbed SQLAlchemy `query()` chain so
tests stay hermetic; the renderer is exercised against synthetic value
objects without touching SQLAlchemy at all.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List

from core.cra_annex_vii import build_annex_vii
from core.cra_annex_vii_markdown import render_markdown
from core.cra_annex_vii_models import (
    AnnexViiAsset,
    AnnexViiCompensatingControl,
    AnnexViiDamageScenario,
    AnnexViiDocument,
    AnnexViiRequirement,
    AnnexViiSbomEntry,
    AnnexViiSection,
)


# ──────────────── Stubs ────────────────


class _StubAssessment:
    def __init__(self) -> None:
        self.id = "assess-1"
        self.product_id = "prod-1"
        self.classification = "class_i"
        self.compliance_path = "Module B+C"
        self.support_period_years = 7
        self.support_period_justification = None
        self.compliance_deadline = "2027-12-11"


class _StubProduct:
    def __init__(self) -> None:
        self.scope_id = "prod-1"
        self.name = "ECU-Brake-Controller"
        self.product_type = "ECU"
        self.description = "Brake controller for passenger vehicles"
        self.safety_level = "ASIL-D"
        self.interfaces = ["CAN", "Ethernet"]
        self.access_points = ["OBD-II"]


class _StubRequirement:
    def __init__(
        self,
        *,
        requirement_id: str,
        name: str,
        category: str,
        annex_part: str,
        status: str,
        auto_mapped: bool = False,
    ) -> None:
        self.requirement_id = requirement_id
        self.requirement_name = name
        self.requirement_category = category
        self.annex_part = annex_part
        self.status = status
        self.auto_mapped = auto_mapped
        self.evidence_notes = None


class _StubAsset:
    def __init__(self, name: str) -> None:
        self.asset_id = f"asset-{name}"
        self.name = name
        self.asset_type = "Software"
        self.confidentiality = "High"
        self.integrity = "High"
        self.availability = "Medium"


class _StubDamageScenario:
    def __init__(self, name: str) -> None:
        self.scenario_id = f"ds-{name}"
        self.name = name
        self.description = f"Damage to {name}"
        self.severity = "High"
        self.safety_impact = "high"
        self.financial_impact = "medium"
        self.operational_impact = "high"
        self.privacy_impact = "negligible"
        self.is_current = True


class _StubSbom:
    def __init__(self) -> None:
        self.id = "sbom-1"
        self.assessment_id = "assess-1"
        self.sbom_format = "cyclonedx"
        self.spec_version = "1.5"
        self.component_count = 42
        self.primary_component_name = "ECU-Brake-Controller"
        self.primary_component_version = "2.4.1"
        self.uploaded_at = datetime(2026, 5, 1, 10, 0, 0, tzinfo=timezone.utc)


class _StubFilter:
    def __init__(self, rows: List[Any]) -> None:
        self._rows = rows

    def filter(self, *args: Any, **kwargs: Any) -> "_StubFilter":
        return self

    def order_by(self, *args: Any) -> "_StubFilter":
        return self

    def first(self) -> Any:
        return self._rows[0] if self._rows else None

    def all(self) -> List[Any]:
        return list(self._rows)

    def count(self) -> int:
        return len(self._rows)


class _StubSession:
    """Minimal Session that routes `db.query(Model)` to a row list per model."""

    def __init__(self, mapping: dict) -> None:
        self._mapping = mapping

    def query(self, model: Any) -> _StubFilter:
        return _StubFilter(self._mapping.get(model.__name__, []))


# ──────────────── Builder ────────────────


def _make_session(**overrides: List[Any]) -> _StubSession:
    from db.cra_models import (
        CraAssessment,
        CraCompensatingControl,
        CraRequirementStatusRecord,
    )
    from db.cra_sbom_models import CraSbom
    from db.product_asset_models import (
        Asset,
        DamageScenario,
        ProductScope,
        ThreatScenario,
    )

    base = {
        CraAssessment.__name__: [_StubAssessment()],
        ProductScope.__name__: [_StubProduct()],
        Asset.__name__: [_StubAsset("Firmware"), _StubAsset("Bootloader")],
        DamageScenario.__name__: [_StubDamageScenario("Loss of brake")],
        ThreatScenario.__name__: [object(), object()],  # count = 2
        CraRequirementStatusRecord.__name__: [
            _StubRequirement(
                requirement_id="CRA-01", name="Secure by default",
                category="technical", annex_part="Part I", status="compliant",
            ),
            _StubRequirement(
                requirement_id="CRA-10", name="SBOM",
                category="documentation", annex_part="Part II", status="partial",
                auto_mapped=True,
            ),
        ],
        CraCompensatingControl.__name__: [],
        CraSbom.__name__: [_StubSbom()],
    }
    base.update(overrides)
    return _StubSession(base)


def test_build_returns_none_when_assessment_missing() -> None:
    from db.cra_models import CraAssessment

    db = _make_session(**{CraAssessment.__name__: []})
    assert build_annex_vii(db, "missing") is None  # type: ignore[arg-type]


def test_build_populates_metadata() -> None:
    db = _make_session()
    doc = build_annex_vii(db, "assess-1")  # type: ignore[arg-type]

    assert doc is not None
    assert doc.product_name == "ECU-Brake-Controller"
    assert doc.classification == "class_i"
    assert doc.conformity_assessment == "Module B+C"
    assert doc.support_period_years == 7
    assert doc.safety_level == "ASIL-D"
    assert doc.interfaces == ("CAN", "Ethernet")


def test_build_pulls_assets_and_scenarios() -> None:
    db = _make_session()
    doc = build_annex_vii(db, "assess-1")  # type: ignore[arg-type]

    assert doc is not None
    assert len(doc.assets) == 2
    assert doc.assets[0].name == "Firmware"
    assert len(doc.damage_scenarios) == 1
    assert doc.damage_scenarios[0].threat_count == 2


def test_build_emits_seven_sections_with_correct_action_flags() -> None:
    db = _make_session()
    doc = build_annex_vii(db, "assess-1")  # type: ignore[arg-type]

    assert doc is not None
    assert len(doc.sections) == 7

    by_number = {s.number: s for s in doc.sections}

    # §1 — has product, classification, support period → done
    assert by_number["1"].is_action_required is False
    # §2 — has Part II partial → done
    assert by_number["2"].is_action_required is False
    # §3 — has assets + scenarios → done
    assert by_number["3"].is_action_required is False
    # §4 — standards always action-required for now
    assert by_number["4"].is_action_required is True
    # §5 — has both Part I & Part II evidence → done
    assert by_number["5"].is_action_required is False
    # §6 — DoC always action-required for now
    assert by_number["6"].is_action_required is True
    # §7 — SBOM uploaded → done
    assert by_number["7"].is_action_required is False


def test_completeness_pct_excludes_action_required() -> None:
    db = _make_session()
    doc = build_annex_vii(db, "assess-1")  # type: ignore[arg-type]
    assert doc is not None
    # 5/7 sections done = 71 %
    assert doc.completeness_pct == 71


def test_section_7_action_required_when_no_sbom() -> None:
    from db.cra_sbom_models import CraSbom

    db = _make_session(**{CraSbom.__name__: []})
    doc = build_annex_vii(db, "assess-1")  # type: ignore[arg-type]
    assert doc is not None
    section_7 = next(s for s in doc.sections if s.number == "7")
    assert section_7.is_action_required is True
    assert "No SBOM uploaded" in section_7.body


# ──────────────── Renderer ────────────────


def _make_doc() -> AnnexViiDocument:
    return AnnexViiDocument(
        assessment_id="A",
        product_name="ECU",
        product_id="P",
        classification="class_i",
        conformity_assessment="Module B+C",
        support_period_years=7,
        support_period_justification=None,
        compliance_deadline="2027-12-11",
        generated_at=datetime(2026, 5, 1, 10, 0, 0, tzinfo=timezone.utc),
        intended_purpose="Braking",
        product_description="Braking",
        safety_level="ASIL-D",
        interfaces=("CAN",),
        access_points=("OBD-II",),
        assets=(
            AnnexViiAsset("a1", "Firmware", "Software", "High", "High", "Medium"),
        ),
        damage_scenarios=(
            AnnexViiDamageScenario(
                "ds1", "Loss of brake", "desc", "High",
                "high", "medium", "high", "negligible", 2,
            ),
        ),
        requirements=(
            AnnexViiRequirement(
                "CRA-01", "Secure by default", "technical", "Part I",
                "compliant", False, None,
            ),
        ),
        compensating_controls=(
            AnnexViiCompensatingControl(
                "c1", "Network segmentation", "Isolate CAN", "implemented", "CRA-04",
            ),
        ),
        sboms=(
            AnnexViiSbomEntry(
                "s1", "cyclonedx", "1.5", 42, "ECU", "2.4.1",
                datetime(2026, 5, 1, 10, 0, 0, tzinfo=timezone.utc),
            ),
        ),
        sections=(
            AnnexViiSection("1", "General", "§1", "body 1", False),
            AnnexViiSection("4", "Standards", "§4", "body 4", True),
        ),
        completeness_pct=50,
    )


def test_render_includes_title_and_metadata() -> None:
    md = render_markdown(_make_doc())
    assert "# CRA Annex VII — Technical Documentation: ECU" in md
    assert "Module B+C" in md
    assert "Completeness: 50%" in md


def test_render_marks_action_required_sections() -> None:
    md = render_markdown(_make_doc())
    assert "**Action required.**" in md
    # §1 should not have the warning, §4 should
    assert md.index("§4 — Standards") > md.index("§1 — General")


def test_render_includes_appendices() -> None:
    md = render_markdown(_make_doc())
    assert "Appendix A — Risk assessment artefacts" in md
    assert "Appendix B — Annex I requirement matrix" in md
    assert "Appendix C — Compensating controls" in md
    assert "Appendix D — Software Bill of Materials" in md


def test_render_assets_table_contains_data() -> None:
    md = render_markdown(_make_doc())
    assert "| Firmware | Software | High | High | Medium |" in md


def test_render_sbom_table_contains_data() -> None:
    md = render_markdown(_make_doc())
    assert "cyclonedx" in md and "1.5" in md and "42" in md
