"""CRA Annex VII — Pydantic response schemas.

Used by `api/routes/cra_annex_vii.py`. Mirrors the value objects in
`core.cra_annex_vii_models`.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AnnexViiAssetResponse(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    confidentiality: str
    integrity: str
    availability: str


class AnnexViiDamageScenarioResponse(BaseModel):
    scenario_id: str
    name: str
    description: str
    severity: str
    safety_impact: str
    financial_impact: str
    operational_impact: str
    privacy_impact: str
    threat_count: int


class AnnexViiRequirementResponse(BaseModel):
    requirement_id: str
    name: str
    category: str
    annex_part: str
    status: str
    auto_mapped: bool
    evidence_notes: Optional[str] = None


class AnnexViiCompensatingControlResponse(BaseModel):
    control_id: str
    name: str
    description: str
    status: str
    requirement_id: Optional[str] = None


class AnnexViiSbomEntryResponse(BaseModel):
    sbom_id: str
    sbom_format: str
    spec_version: str
    component_count: int
    primary_component_name: Optional[str] = None
    primary_component_version: Optional[str] = None
    uploaded_at: datetime


class AnnexViiSectionResponse(BaseModel):
    number: str
    title: str
    article_ref: str
    body: str
    is_action_required: bool


class AnnexViiDocumentResponse(BaseModel):
    assessment_id: str
    product_name: str
    product_id: str
    classification: Optional[str] = None
    conformity_assessment: Optional[str] = None
    support_period_years: Optional[int] = None
    support_period_justification: Optional[str] = None
    compliance_deadline: Optional[str] = None
    generated_at: datetime
    intended_purpose: Optional[str] = None
    product_description: Optional[str] = None
    safety_level: Optional[str] = None
    interfaces: List[str] = Field(default_factory=list)
    access_points: List[str] = Field(default_factory=list)
    assets: List[AnnexViiAssetResponse] = Field(default_factory=list)
    damage_scenarios: List[AnnexViiDamageScenarioResponse] = Field(default_factory=list)
    requirements: List[AnnexViiRequirementResponse] = Field(default_factory=list)
    compensating_controls: List[AnnexViiCompensatingControlResponse] = Field(default_factory=list)
    sboms: List[AnnexViiSbomEntryResponse] = Field(default_factory=list)
    sections: List[AnnexViiSectionResponse] = Field(default_factory=list)
    completeness_pct: int = 0
