"""CRA-10 — Pydantic schemas for SBOM endpoints.

Used by `api/routes/cra_sbom.py`. Mirrors the persistence layer in
`db/cra_sbom_models.py` but exposes only what callers need.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


class SbomComponentResponse(BaseModel):
    """One component within a stored SBOM."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    bom_ref: str
    name: str
    version: Optional[str] = None
    component_type: Optional[str] = None
    purl: Optional[str] = None
    cpe: Optional[str] = None
    supplier: Optional[str] = None
    licenses: Tuple[str, ...] = Field(default_factory=tuple)


class SbomListItem(BaseModel):
    """One SBOM in a list view (no components)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    sbom_format: str
    spec_version: str
    document_name: Optional[str] = None
    primary_component_name: Optional[str] = None
    primary_component_version: Optional[str] = None
    component_count: int
    raw_size_bytes: int
    uploaded_at: datetime
    uploaded_by: Optional[str] = None


class SbomDetailResponse(SbomListItem):
    """Full SBOM record with components."""

    serial_number: Optional[str] = None
    notes: Optional[str] = None
    components: List[SbomComponentResponse] = Field(default_factory=list)


class SbomUploadResponse(BaseModel):
    """Result of an upload — includes parser warnings for transparency."""

    sbom: SbomListItem
    warnings: List[str] = Field(default_factory=list)
    cra10_status: str
