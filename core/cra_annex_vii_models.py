"""CRA Annex VII — immutable value objects.

Frozen dataclasses returned by `core.cra_annex_vii.build_annex_vii` and
consumed by renderers (`core.cra_annex_vii_markdown`, etc.). No I/O,
no logic — just shapes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple


@dataclass(frozen=True)
class AnnexViiAsset:
    asset_id: str
    name: str
    asset_type: str
    confidentiality: str
    integrity: str
    availability: str


@dataclass(frozen=True)
class AnnexViiDamageScenario:
    scenario_id: str
    name: str
    description: str
    severity: str
    safety_impact: str
    financial_impact: str
    operational_impact: str
    privacy_impact: str
    threat_count: int


@dataclass(frozen=True)
class AnnexViiRequirement:
    requirement_id: str
    name: str
    category: str
    annex_part: str
    status: str
    auto_mapped: bool
    evidence_notes: Optional[str]


@dataclass(frozen=True)
class AnnexViiCompensatingControl:
    control_id: str
    name: str
    description: str
    status: str
    requirement_id: Optional[str]


@dataclass(frozen=True)
class AnnexViiSbomEntry:
    sbom_id: str
    sbom_format: str
    spec_version: str
    component_count: int
    primary_component_name: Optional[str]
    primary_component_version: Optional[str]
    uploaded_at: datetime


@dataclass(frozen=True)
class AnnexViiSection:
    """One Annex VII section. `is_action_required` flags incomplete data."""

    number: str
    title: str
    article_ref: str
    body: str
    is_action_required: bool = False


@dataclass(frozen=True)
class AnnexViiDocument:
    """Complete Annex VII document for one CRA assessment."""

    assessment_id: str
    product_name: str
    product_id: str
    classification: Optional[str]
    conformity_assessment: Optional[str]
    support_period_years: Optional[int]
    support_period_justification: Optional[str]
    compliance_deadline: Optional[str]
    generated_at: datetime

    intended_purpose: Optional[str]
    product_description: Optional[str]
    safety_level: Optional[str]
    interfaces: Tuple[str, ...]
    access_points: Tuple[str, ...]

    assets: Tuple[AnnexViiAsset, ...]
    damage_scenarios: Tuple[AnnexViiDamageScenario, ...]

    requirements: Tuple[AnnexViiRequirement, ...]
    compensating_controls: Tuple[AnnexViiCompensatingControl, ...]

    sboms: Tuple[AnnexViiSbomEntry, ...]

    sections: Tuple[AnnexViiSection, ...] = field(default_factory=tuple)
    completeness_pct: int = 0
