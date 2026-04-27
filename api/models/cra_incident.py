"""CRA Art. 14 — Pydantic schemas for incident reporting endpoints.

Used by `api/routes/cra_incident.py`. Phase-specific create/update payloads
mirror Art. 14(2)(a)/(b)/(c).
"""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

IncidentType = Literal["actively_exploited_vulnerability", "severe_incident"]
IncidentStatus = Literal[
    "draft",
    "early_warning_submitted",
    "incident_report_submitted",
    "final_report_submitted",
    "closed",
]
IncidentSeverity = Literal["critical", "high", "medium", "low"]
DeadlinePhaseLiteral = Literal["early_warning", "incident_report", "final_report"]
DeadlineStatusLiteral = Literal["on_track", "approaching", "overdue", "submitted"]


# ──────────────── Create / Update ────────────────


class IncidentCreate(BaseModel):
    """Initial draft — only minimal fields required (Art. 14(2)(a))."""

    title: str = Field(..., min_length=1, max_length=255)
    incident_type: IncidentType
    discovered_at: datetime
    assessment_id: Optional[str] = None
    product_id: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    actively_exploited: bool = False
    member_states_affected: Optional[List[str]] = None  # ISO-3166 alpha-2
    product_description: Optional[str] = None
    cve_id: Optional[str] = None
    notes: Optional[str] = None


class IncidentUpdate(BaseModel):
    """Mutable fields. Only set what's changing."""

    title: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    actively_exploited: Optional[bool] = None
    member_states_affected: Optional[List[str]] = None
    product_description: Optional[str] = None
    vulnerability_nature: Optional[str] = None
    mitigations_taken: Optional[str] = None
    mitigations_recommended: Optional[str] = None
    vulnerability_description: Optional[str] = None
    impact_description: Optional[str] = None
    malicious_actor_info: Optional[str] = None
    fixes_applied: Optional[str] = None
    cve_id: Optional[str] = None
    corrective_measure_available_at: Optional[datetime] = None
    notes: Optional[str] = None


class SubmitPhaseRequest(BaseModel):
    """Mark a phase as submitted to ENISA."""

    phase: DeadlinePhaseLiteral


# ──────────────── Responses ────────────────


class DeadlineResponse(BaseModel):
    """One deadline, computed live."""

    phase: DeadlinePhaseLiteral
    deadline_at: datetime
    seconds_remaining: int
    status: DeadlineStatusLiteral
    submitted_at: Optional[datetime] = None


class IncidentResponse(BaseModel):
    """Full incident record + computed deadlines."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: Optional[str] = None
    product_id: Optional[str] = None
    incident_type: IncidentType
    title: str
    severity: Optional[IncidentSeverity] = None
    status: IncidentStatus
    discovered_at: datetime
    corrective_measure_available_at: Optional[datetime] = None
    early_warning_submitted_at: Optional[datetime] = None
    incident_report_submitted_at: Optional[datetime] = None
    final_report_submitted_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    actively_exploited: bool
    member_states_affected: Optional[List[str]] = None
    product_description: Optional[str] = None

    @field_validator("member_states_affected", mode="before")
    @classmethod
    def _coerce_member_states(cls, value: object) -> Optional[List[str]]:
        """``CraIncident.member_states_affected`` is a JSON-encoded ``TEXT``
        column. Decode it here so callers always see a list."""
        if value is None or value == "":
            return None
        if isinstance(value, list):
            return [str(v) for v in value]
        if isinstance(value, str):
            import json as _json
            try:
                parsed = _json.loads(value)
            except _json.JSONDecodeError:
                return [value]
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
            return [str(parsed)]
        return [str(value)]
    vulnerability_nature: Optional[str] = None
    mitigations_taken: Optional[str] = None
    mitigations_recommended: Optional[str] = None
    vulnerability_description: Optional[str] = None
    impact_description: Optional[str] = None
    malicious_actor_info: Optional[str] = None
    fixes_applied: Optional[str] = None
    cve_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deadlines: List[DeadlineResponse] = Field(default_factory=list)
    overall_overdue: bool = False


class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int


# ──────────────── ENISA export ────────────────


class EnisaExportResponse(BaseModel):
    """Structured export shaped to CRA Art. 14 reporting fields.

    The Single Reporting Platform schema is still being defined by the
    Commission's implementing acts. This payload follows the article text
    and is intended as a portable JSON for manual submission until the
    final schema is published.
    """

    incident_id: str
    phase: DeadlinePhaseLiteral
    generated_at: datetime
    payload: dict
