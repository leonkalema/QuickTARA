"""CRA-10 — Pydantic schemas for SBOM endpoints.

Used by `api/routes/cra_sbom.py`. Mirrors the persistence layer in
`db/cra_sbom_models.py` but exposes only what callers need.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("licenses", mode="before")
    @classmethod
    def _coerce_licenses(cls, value: object) -> Tuple[str, ...]:
        """Persistence stores licenses as comma-separated text (see
        ``db.cra_sbom_models.CraSbomComponent.licenses``). Normalise any of
        ``None`` / ``str`` / list / tuple into a tuple of trimmed IDs so
        the field can be validated regardless of upstream shape."""
        if value is None or value == "":
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, (list, tuple)):
            return tuple(str(v) for v in value)
        return (str(value),)


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
