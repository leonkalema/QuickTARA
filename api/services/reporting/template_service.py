"""
Report template service: resolves built-in presets and org-saved templates
into ``ReportConfig`` objects, and provides CRUD for org templates.

Built-in presets live in code (presets.py); org templates live in the
``report_templates`` table. Listing merges both, built-ins first.
"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from api.models.report_config import ReportConfig
from db.report_template_models import ReportTemplate
from .presets import builtin_preset_names, get_builtin_preset


class TemplateSummary:
    """Lightweight view of a template for listing (built-in or org)."""

    def __init__(self, template_id: str, name: str, is_builtin: bool) -> None:
        self.template_id = template_id
        self.name = name
        self.is_builtin = is_builtin


def _generate_id() -> str:
    return str(uuid.uuid4())


def list_templates(db: Session, organization_id: Optional[str]) -> List[TemplateSummary]:
    """List built-in presets followed by the organization's saved templates."""
    summaries: List[TemplateSummary] = [
        TemplateSummary(template_id=name, name=name, is_builtin=True)
        for name in builtin_preset_names()
    ]
    rows = (
        db.query(ReportTemplate)
        .filter(ReportTemplate.organization_id == organization_id)
        .order_by(ReportTemplate.name)
        .all()
    )
    summaries.extend(
        TemplateSummary(template_id=row.template_id, name=row.name, is_builtin=False)
        for row in rows
    )
    return summaries


def resolve_config(db: Session, template_id: str) -> ReportConfig:
    """Resolve a template id to a ``ReportConfig``.

    Built-in presets are keyed by their display name; org templates by their
    generated id. Built-ins are checked first.
    """
    if template_id in set(builtin_preset_names()):
        return get_builtin_preset(template_id)
    row = db.query(ReportTemplate).filter(
        ReportTemplate.template_id == template_id
    ).first()
    if row is None:
        raise ValueError(f"Template not found: {template_id}")
    return ReportConfig.model_validate(row.config_json)


def create_template(
    db: Session,
    organization_id: Optional[str],
    name: str,
    config: ReportConfig,
    created_by: Optional[str] = None,
) -> ReportTemplate:
    """Create and persist a new org template from a config."""
    if not name or not name.strip():
        raise ValueError("Template name is required")
    if name in set(builtin_preset_names()):
        raise ValueError(f"'{name}' is a reserved built-in preset name")
    existing = (
        db.query(ReportTemplate)
        .filter(
            ReportTemplate.organization_id == organization_id,
            ReportTemplate.name == name,
        )
        .first()
    )
    if existing is not None:
        raise ValueError(f"A template named '{name}' already exists")
    row = ReportTemplate(
        template_id=_generate_id(),
        organization_id=organization_id,
        name=name,
        is_builtin=False,
        config_json=config.model_dump(mode="json"),
        created_by=created_by,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_template(
    db: Session,
    template_id: str,
    config: ReportConfig,
) -> ReportTemplate:
    """Replace the config of an existing org template."""
    row = db.query(ReportTemplate).filter(
        ReportTemplate.template_id == template_id
    ).first()
    if row is None:
        raise ValueError(f"Template not found: {template_id}")
    row.config_json = config.model_dump(mode="json")
    db.commit()
    db.refresh(row)
    return row


def delete_template(db: Session, template_id: str) -> None:
    """Delete an org template. Raises if the id matches a built-in preset."""
    if template_id in set(builtin_preset_names()):
        raise ValueError("Built-in presets cannot be deleted")
    row = db.query(ReportTemplate).filter(
        ReportTemplate.template_id == template_id
    ).first()
    if row is None:
        raise ValueError(f"Template not found: {template_id}")
    db.delete(row)
    db.commit()
