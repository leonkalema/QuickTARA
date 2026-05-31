"""
Clean, modular reports router.
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile
from pathlib import Path

from api.deps.db import get_db
from api.auth.dependencies import get_current_active_user
from api.models.user import User
from api.models.report_config import ReportConfig
from api.models.report_template import (
    TemplateCreateRequest,
    TemplateListResponse,
    TemplateSummaryResponse,
)
from api.services.reporting.report_builder import (
    build_complete_report,
    get_goals_data,
    get_damage_scenarios_data
)
from api.services.reporting import template_service
from api.services.report_service import ReportService
from core.export_formats import export_to_json, export_to_excel, export_to_text

router = APIRouter(prefix="/reports", tags=["reports"])


def _current_org_id(current_user: User) -> Optional[str]:
    """Resolve the active organization id for the user, if any."""
    orgs = getattr(current_user, "organizations", None) or []
    if not orgs:
        return None
    return orgs[0].organization_id


@router.get("/{scope_id}/goals")
async def get_cybersecurity_goals(scope_id: str, db: Session = Depends(get_db)):
    """Get cybersecurity goals data for validation."""
    try:
        return get_goals_data(scope_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch goals: {str(e)}")


@router.get("/{scope_id}/damage-scenarios")
async def get_damage_scenarios_summary(scope_id: str, db: Session = Depends(get_db)):
    """Get damage scenarios data for validation."""
    try:
        return get_damage_scenarios_data(scope_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch damage scenarios: {str(e)}")


def _generate_pdf_response(
    scope_id: str,
    db: Session,
    config: Optional[ReportConfig] = None,
) -> FileResponse:
    """Build a TARA PDF and wrap it in a FileResponse."""
    import traceback
    try:
        pdf_content = build_complete_report(scope_id, db, config)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name

        from api.services.reporting.data_access import get_scope_info
        scope_info = get_scope_info(scope_id, db)
        name = scope_info.get('name', 'unknown') if scope_info else 'unknown'
        filename = f"tara_report_{name}.pdf"

        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Exception in PDF generation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/{scope_id}/pdf")
async def download_pdf_report(scope_id: str, db: Session = Depends(get_db)):
    """Generate and download a PDF report using the default (internal/full) profile."""
    return _generate_pdf_response(scope_id, db, config=None)


@router.post("/{scope_id}/pdf")
async def generate_pdf_report(
    scope_id: str,
    config: Optional[ReportConfig] = None,
    db: Session = Depends(get_db),
):
    """Generate a PDF report from a supplied ReportConfig.

    When no config is provided the default internal/full profile is used,
    matching the GET endpoint.
    """
    return _generate_pdf_response(scope_id, db, config=config)


# --- Report template management ---

@router.get("/templates", response_model=TemplateListResponse)
async def list_report_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List built-in presets and the current org's saved templates."""
    org_id = _current_org_id(current_user)
    summaries = template_service.list_templates(db, org_id)
    return TemplateListResponse(templates=[
        TemplateSummaryResponse(
            template_id=s.template_id, name=s.name, is_builtin=s.is_builtin
        )
        for s in summaries
    ])


@router.post("/templates", response_model=TemplateSummaryResponse, status_code=201)
async def create_report_template(
    payload: TemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save a new reusable report template for the current org."""
    org_id = _current_org_id(current_user)
    try:
        row = template_service.create_template(
            db, org_id, payload.name, payload.config, getattr(current_user, "user_id", None)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TemplateSummaryResponse(
        template_id=row.template_id, name=row.name, is_builtin=False
    )


@router.delete("/templates/{template_id}", status_code=204)
async def delete_report_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an org template (built-in presets cannot be deleted)."""
    try:
        template_service.delete_template(db, template_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(status_code=204)


@router.get("/{scope_id}/export/{format}")
async def export_report(scope_id: str, format: str, db: Session = Depends(get_db)):
    """Export report in various formats (json, excel, text)."""
    try:
        # Get data for export
        from api.services.reporting.data_access import (
            get_scope_info, get_damage_scenarios, get_risk_treatments
        )
        
        scope_info = get_scope_info(scope_id, db)
        if not scope_info:
            raise HTTPException(status_code=404, detail=f"Scope {scope_id} not found")
        
        damage_scenarios = get_damage_scenarios(scope_id, db)
        risk_treatments = get_risk_treatments(scope_id, db)
        goals_data = get_goals_data(scope_id, db)
        
        export_data = {
            "scope": scope_info,
            "damage_scenarios": damage_scenarios,
            "risk_treatments": risk_treatments,
            "cybersecurity_goals": goals_data["goals"],
            "generated_at": datetime.now().isoformat()
        }
        
        if format.lower() == "json":
            content = export_to_json(export_data)
            media_type = "application/json"
            filename = f"tara_report_{scope_info['name']}.json"
        elif format.lower() == "excel":
            content = export_to_excel(export_data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"tara_report_{scope_info['name']}.xlsx"
        elif format.lower() == "text":
            content = export_to_text(export_data)
            media_type = "text/plain"
            filename = f"tara_report_{scope_info['name']}.txt"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use json, excel, or text.")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            if isinstance(content, str):
                tmp_file.write(content.encode('utf-8'))
            else:
                tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Legacy endpoints for backward compatibility
@router.post("/{scope_id}/generate")
async def generate_report_legacy(scope_id: str, db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to PDF generation."""
    return await download_pdf_report(scope_id, db)


@router.get("/{scope_id}/download")
async def download_report_legacy(scope_id: str, db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to PDF download."""
    return await download_pdf_report(scope_id, db)


@router.get("/tara-pdf/{scope_id}")
async def download_tara_pdf_legacy(scope_id: str, db: Session = Depends(get_db)):
    """Legacy endpoint for frontend - redirects to PDF download."""
    try:
        return await download_pdf_report(scope_id, db)
    except Exception as e:
        import traceback
        print(f"Error in tara-pdf endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
