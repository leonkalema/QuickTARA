"""
Clean, modular reports router.
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
import tempfile
from pathlib import Path

from api.deps.db import get_db
from api.services.reporting.report_builder import (
    build_complete_report,
    get_goals_data,
    get_damage_scenarios_data
)
from api.services.report_service import ReportService
from core.export_formats import export_to_json, export_to_excel, export_to_text

router = APIRouter(prefix="/reports", tags=["reports"])


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


@router.get("/{scope_id}/pdf")
async def download_pdf_report(scope_id: str, db: Session = Depends(get_db)):
    """Generate and download PDF report."""
    try:
        import traceback
        print(f"Starting PDF generation for scope: {scope_id}")
        
        pdf_content = build_complete_report(scope_id, db)
        print(f"PDF content generated, size: {len(pdf_content)} bytes")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        # Get scope name for filename
        from api.services.reporting.data_access import get_scope_info
        scope_info = get_scope_info(scope_id, db)
        filename = f"tara_report_{scope_info.get('name', 'unknown') if scope_info else 'unknown'}.pdf"
        print(f"Generated filename: {filename}")
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        print(f"ValueError in PDF generation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Exception in PDF generation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


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
