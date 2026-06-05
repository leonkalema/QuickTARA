"""
Report configuration model for the redesigned TARA report module.

A ``ReportConfig`` describes *what* a generated report contains and *who* it is
for. It is the single object consumed by the report builder; audience presets
and saved templates are just convenient ways to produce one.

See: docs/report-module-redesign.md
"""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ReportAudience(str, Enum):
    """Intended consumer of the report. Drives the default section profile."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    AUDITOR = "auditor"


class ReportDetailLevel(str, Enum):
    """How much detail each section renders."""

    FULL = "full"
    SUMMARY = "summary"


class ReportClassification(str, Enum):
    """Document classification label shown in the document-control block."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class SectionKey(str, Enum):
    """Toggleable report sections. Each key maps to one section builder."""

    DOCUMENT_CONTROL = "document_control"
    EXECUTIVE_SUMMARY = "executive_summary"
    SCOPE_AND_ASSUMPTIONS = "scope_and_assumptions"
    METHODOLOGY = "methodology"
    ASSESSMENT_STATUS = "assessment_status"
    ISO_COMPLIANCE = "iso_compliance"
    CRA_COMPLIANCE = "cra_compliance"
    ASSET_INVENTORY = "asset_inventory"
    DAMAGE_SCENARIOS = "damage_scenarios"
    THREAT_SCENARIOS = "threat_scenarios"
    ATTACK_PATHS = "attack_paths"
    RISK_SUMMARY = "risk_summary"
    RISK_REGISTER = "risk_register"
    TREATMENT_SUMMARY = "treatment_summary"
    CYBERSECURITY_GOALS = "cybersecurity_goals"
    OPEN_ISSUES = "open_issues"
    TRACEABILITY = "traceability"


# Canonical render order — matches the recommended OEM report structure.
SECTION_ORDER: List[SectionKey] = [
    SectionKey.DOCUMENT_CONTROL,
    SectionKey.EXECUTIVE_SUMMARY,
    SectionKey.SCOPE_AND_ASSUMPTIONS,
    SectionKey.METHODOLOGY,
    SectionKey.ASSESSMENT_STATUS,
    SectionKey.ISO_COMPLIANCE,
    SectionKey.CRA_COMPLIANCE,
    SectionKey.ASSET_INVENTORY,
    SectionKey.DAMAGE_SCENARIOS,
    SectionKey.THREAT_SCENARIOS,
    SectionKey.ATTACK_PATHS,
    SectionKey.RISK_SUMMARY,
    SectionKey.RISK_REGISTER,
    SectionKey.TREATMENT_SUMMARY,
    SectionKey.CYBERSECURITY_GOALS,
    SectionKey.OPEN_ISSUES,
    SectionKey.TRACEABILITY,
]


class ReportMetadata(BaseModel):
    """Free-form document-control metadata (ISO 21434 expects author/approver)."""

    author: Optional[str] = Field(default=None, description="Document author name")
    approver: Optional[str] = Field(default=None, description="Approver name")
    reference: Optional[str] = Field(default=None, description="Document reference / ID")


class ReportConfig(BaseModel):
    """Complete, self-contained description of a report to generate."""

    audience: ReportAudience = Field(default=ReportAudience.INTERNAL)
    detail_level: ReportDetailLevel = Field(default=ReportDetailLevel.FULL)
    classification: ReportClassification = Field(default=ReportClassification.INTERNAL)
    sections: Dict[SectionKey, bool] = Field(default_factory=dict, validate_default=True)
    metadata: ReportMetadata = Field(default_factory=ReportMetadata)

    @field_validator("sections", mode="after")
    @classmethod
    def fill_missing_sections(cls, value: Dict[SectionKey, bool]) -> Dict[SectionKey, bool]:
        """Ensure every known section has an explicit boolean (default off)."""
        return {key: bool(value.get(key, False)) for key in SECTION_ORDER}

    def enabled_sections(self) -> List[SectionKey]:
        """Return enabled sections in canonical render order."""
        return [key for key in SECTION_ORDER if self.sections.get(key, False)]

    def is_enabled(self, key: SectionKey) -> bool:
        """Whether a single section is enabled."""
        return self.sections.get(key, False)
