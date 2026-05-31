"""
Request/response models for report template endpoints.
"""
from typing import List

from pydantic import BaseModel, Field

from api.models.report_config import ReportConfig


class TemplateCreateRequest(BaseModel):
    """Payload to save a new org report template."""

    name: str = Field(..., min_length=1, description="Unique template name within the org")
    config: ReportConfig = Field(..., description="The report configuration to store")


class TemplateSummaryResponse(BaseModel):
    """A template entry for listings (built-in preset or org template)."""

    template_id: str = Field(..., description="Built-in preset name or org template id")
    name: str = Field(..., description="Display name")
    is_builtin: bool = Field(..., description="Whether this is a read-only built-in preset")


class TemplateListResponse(BaseModel):
    """List of available templates for the current org."""

    templates: List[TemplateSummaryResponse] = Field(default_factory=list)
