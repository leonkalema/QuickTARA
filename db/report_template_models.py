"""
Report template database model.

A report template is a saved, reusable ``ReportConfig`` (serialized as JSON)
scoped to an organization. Built-in presets are defined in code
(api/services/reporting/presets.py) and are not stored here; this table only
holds user-created org templates.

See: docs/report-module-redesign.md (section 8b)
"""
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.types import JSON

from db.product_asset_models import Base


class ReportTemplate(Base):
    """A reusable, named report configuration for an organization."""

    __tablename__ = "report_templates"

    template_id = Column(String, primary_key=True, index=True)
    organization_id = Column(
        String,
        ForeignKey("organizations.organization_id"),
        nullable=True,
        index=True,
    )
    name = Column(String(255), nullable=False)
    is_builtin = Column(Boolean, nullable=False, default=False)
    config_json = Column(JSON, nullable=False, default=lambda: {})
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
