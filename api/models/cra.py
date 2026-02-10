"""
CRA Compliance Pydantic models for request/response schemas.

Depends on: core.cra_classifier, core.cra_auto_mapper
Used by: api/routes/cra.py
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CraClassificationEnum(str, Enum):
    """CRA product classification"""
    DEFAULT = "default"
    CLASS_I = "class_i"
    CLASS_II = "class_ii"
    CRITICAL = "critical"


class CraProductTypeEnum(str, Enum):
    """Product lifecycle type"""
    CURRENT = "current"
    LEGACY_A = "legacy_a"
    LEGACY_B = "legacy_b"
    LEGACY_C = "legacy_c"


class CraAssessmentStatusEnum(str, Enum):
    """Assessment workflow status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class CraRequirementStatusEnum(str, Enum):
    """Requirement compliance status"""
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    COMPLIANT = "compliant"
    NOT_APPLICABLE = "not_applicable"


class CompensatingControlStatusEnum(str, Enum):
    """Compensating control implementation status"""
    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"


class GapSeverityEnum(str, Enum):
    """Gap severity / residual risk level"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompliancePathEnum(str, Enum):
    """CRA compliance path per Art. 5(3)"""
    DIRECT_PATCH = "direct_patch"
    COMPENSATING_CONTROL = "compensating_control"
    HYBRID = "hybrid"


# --- Request schemas ---

class CraAssessmentCreate(BaseModel):
    """Create a new CRA assessment for a product"""
    product_id: str = Field(..., description="Product scope ID")
    product_type: CraProductTypeEnum = Field(
        default=CraProductTypeEnum.CURRENT,
        description="Product lifecycle type"
    )
    notes: Optional[str] = Field(None, description="Assessment notes")


MIN_SUPPORT_PERIOD_YEARS: int = 5


class CraAssessmentUpdate(BaseModel):
    """Update an existing CRA assessment"""
    status: Optional[CraAssessmentStatusEnum] = None
    product_type: Optional[CraProductTypeEnum] = None
    support_period_years: Optional[int] = Field(
        None,
        description="Support period in years. CRA minimum is 5 years."
    )
    support_period_justification: Optional[str] = Field(
        None,
        description="Required if support_period_years < 5. Must justify shorter period."
    )
    support_period_end: Optional[str] = None
    eoss_date: Optional[str] = None
    notes: Optional[str] = None


class DataProfileUpdate(BaseModel):
    """Product data classification profile — boolean flags"""
    stores_data_at_rest: Optional[bool] = None
    stores_personal_data: Optional[bool] = None
    collects_telemetry: Optional[bool] = None
    has_network_interfaces: Optional[bool] = None
    has_user_authentication: Optional[bool] = None
    has_physical_interfaces: Optional[bool] = None
    has_updateable_software: Optional[bool] = None
    uses_third_party_components: Optional[bool] = None
    has_crypto_keys: Optional[bool] = None


class ApplicabilityResultResponse(BaseModel):
    """Whether a CRA requirement applies based on data profile"""
    requirement_id: str
    applicable: bool
    justification: str


class DataProfileResponse(BaseModel):
    """Full data profile with computed applicability"""
    profile: Dict[str, bool]
    applicability: List[ApplicabilityResultResponse]
    auto_resolved_count: int


class ClassifyRequest(BaseModel):
    """Classification based on core functionality category selection."""
    category_id: Optional[str] = Field(
        None,
        description="Product category ID from CRA Annexes III/IV catalog. None = Default."
    )
    uses_harmonised_standard: bool = Field(
        default=False,
        description="Whether a harmonised standard will be applied (affects Module A eligibility)"
    )
    is_open_source_public: bool = Field(
        default=False,
        description="Whether product is free/open-source with public technical docs"
    )
    automotive_exception: bool = Field(
        default=False,
        description="Whether UN R155 lex specialis applies"
    )
    answers: Dict[str, bool] = Field(
        default={},
        description="Legacy field — kept for backward compatibility"
    )


class RequirementStatusUpdate(BaseModel):
    """Update a single requirement status"""
    status: Optional[CraRequirementStatusEnum] = None
    owner: Optional[str] = None
    target_date: Optional[str] = None
    evidence_notes: Optional[str] = None
    evidence_links: Optional[List[str]] = None
    gap_description: Optional[str] = None
    remediation_plan: Optional[str] = None
    gap_severity: Optional[GapSeverityEnum] = None
    residual_risk_level: Optional[GapSeverityEnum] = None


class CompensatingControlCreate(BaseModel):
    """Create a compensating control"""
    control_id: str = Field(..., description="Control catalog ID")
    name: str = Field(..., description="Control name")
    description: Optional[str] = None
    implementation_status: CompensatingControlStatusEnum = Field(
        default=CompensatingControlStatusEnum.PLANNED
    )
    supplier_actions: Optional[str] = None
    oem_actions: Optional[str] = None
    residual_risk: Optional[str] = None
    mitigated_requirement_ids: Optional[List[str]] = Field(
        default=[],
        description="List of requirement_status IDs this control mitigates"
    )


class CompensatingControlUpdate(BaseModel):
    """Update a compensating control"""
    name: Optional[str] = None
    description: Optional[str] = None
    implementation_status: Optional[CompensatingControlStatusEnum] = None
    supplier_actions: Optional[str] = None
    oem_actions: Optional[str] = None
    residual_risk: Optional[str] = None
    mitigated_requirement_ids: Optional[List[str]] = None


# --- Response schemas ---

class CraRequirementDefinition(BaseModel):
    """Static definition of a CRA requirement"""
    id: str
    name: str
    article: str
    category: str
    annex_part: str = "Part I"
    obligation_type: str = "risk_based"


class SubRequirementResponse(BaseModel):
    """One checkable sub-item within a CRA requirement"""
    description: str
    check_evidence: str
    typical_gap: str


class RemediationActionResponse(BaseModel):
    """One concrete step to close a gap"""
    action: str
    owner_hint: str
    effort_days: int


class RequirementGuidanceResponse(BaseModel):
    """Per-requirement coaching data — coach AND doer"""
    requirement_id: str
    annex_section: str
    cra_article: str
    priority: str
    deadline_note: str
    explanation: str
    regulatory_text: str
    sub_requirements: List[SubRequirementResponse]
    evidence_checklist: List[str]
    investigation_prompts: List[str]
    common_gaps: List[str]
    remediation_actions: List[RemediationActionResponse]
    effort_estimate: str
    mapped_controls: List[str]
    mapped_standards: List[str]
    tara_link: str


class CraRequirementStatusResponse(BaseModel):
    """Requirement status within an assessment"""
    id: str
    assessment_id: str
    requirement_id: str
    requirement_name: Optional[str] = None
    requirement_article: Optional[str] = None
    requirement_category: Optional[str] = None
    status: str
    auto_mapped: bool
    mapped_artifact_type: Optional[str] = None
    mapped_artifact_count: int = 0
    owner: Optional[str] = None
    target_date: Optional[str] = None
    evidence_notes: Optional[str] = None
    evidence_links: List[str] = []
    gap_description: Optional[str] = None
    remediation_plan: Optional[str] = None
    gap_severity: str = "none"
    residual_risk_level: str = "none"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MitigatedRequirementInfo(BaseModel):
    """Brief info about a mitigated requirement"""
    requirement_status_id: str
    requirement_id: str
    requirement_name: Optional[str] = None


class CompensatingControlResponse(BaseModel):
    """Compensating control response"""
    id: str
    assessment_id: str
    control_id: str
    name: str
    description: Optional[str] = None
    implementation_status: str
    supplier_actions: Optional[str] = None
    oem_actions: Optional[str] = None
    residual_risk: Optional[str] = None
    mitigated_requirements: List[MitigatedRequirementInfo] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConformityModuleResponse(BaseModel):
    """Conformity assessment module recommendation per CRA Art. 32."""
    module_id: str
    name: str
    description: str
    mandatory: bool
    alternatives: List[str]
    rationale: str


class ClassificationResponse(BaseModel):
    """Classification result based on core functionality."""
    classification: str
    category_id: Optional[str] = None
    category_name: str
    conformity_assessment: str
    conformity_module: ConformityModuleResponse
    compliance_deadline: str
    reporting_deadline: str
    cost_estimate_min: int
    cost_estimate_max: int
    automotive_exception: bool
    rationale: str


class CraAssessmentResponse(BaseModel):
    """Full CRA assessment response"""
    id: str
    product_id: str
    product_name: Optional[str] = None
    classification: Optional[str] = None
    classification_answers: Dict[str, Any] = {}
    product_type: str
    compliance_path: str = "direct_patch"
    compliance_deadline: Optional[str] = None
    assessment_date: Optional[datetime] = None
    assessor_id: Optional[str] = None
    status: str
    overall_compliance_pct: int = 0
    support_period_years: Optional[int] = None
    support_period_justification: Optional[str] = None
    support_period_end: Optional[str] = None
    eoss_date: Optional[str] = None
    notes: Optional[str] = None
    automotive_exception: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    requirement_statuses: List[CraRequirementStatusResponse] = []
    compensating_controls: List[CompensatingControlResponse] = []

    class Config:
        from_attributes = True


class CraAssessmentListItem(BaseModel):
    """Lightweight assessment for list views"""
    id: str
    product_id: str
    product_name: Optional[str] = None
    classification: Optional[str] = None
    product_type: str
    status: str
    overall_compliance_pct: int = 0
    compliance_deadline: Optional[str] = None
    updated_at: Optional[datetime] = None


class CraAssessmentListResponse(BaseModel):
    """List of assessments"""
    assessments: List[CraAssessmentListItem]
    total: int


class AutoMapResponse(BaseModel):
    """Result of auto-mapping TARA artifacts to CRA requirements"""
    mapped_count: int
    mappings: List[Dict[str, Any]]


class TargetMarketEnum(str, Enum):
    """Target market for inventory items"""
    EU = "eu"
    NON_EU = "non_eu"
    GLOBAL = "global"


class InventoryItemCreate(BaseModel):
    """Create an inventory item for CRA assessment"""
    assessment_id: str
    sku: str
    firmware_version: Optional[str] = None
    units_in_stock: int = 0
    units_in_field: int = 0
    oem_customer: Optional[str] = None
    target_market: TargetMarketEnum = TargetMarketEnum.EU
    last_production_date: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    """Update an inventory item"""
    sku: Optional[str] = None
    firmware_version: Optional[str] = None
    units_in_stock: Optional[int] = None
    units_in_field: Optional[int] = None
    oem_customer: Optional[str] = None
    target_market: Optional[TargetMarketEnum] = None
    last_production_date: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemResponse(BaseModel):
    """Inventory item response"""
    id: str
    assessment_id: str
    sku: str
    firmware_version: Optional[str] = None
    units_in_stock: int = 0
    units_in_field: int = 0
    oem_customer: Optional[str] = None
    target_market: str = "eu"
    last_production_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventorySummary(BaseModel):
    """Summary of inventory for an assessment"""
    total_skus: int
    total_units_in_stock: int
    total_units_in_field: int
    eu_units: int
    non_eu_units: int
    oems: List[str]
