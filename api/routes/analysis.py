"""
Analysis API routes
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.analysis import Analysis, AnalysisCreate, AnalysisList
from api.services.analysis_service import (
    run_analysis as service_run_analysis,
    list_analyses as service_list_analyses,
    count_analyses as service_count_analyses,
    get_analysis as service_get_analysis,
    get_stride_analysis as service_get_stride_analysis,
    get_attack_paths as service_get_attack_paths
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
async def run_analysis(
    analysis_create: AnalysisCreate,
    db: Session = Depends(get_db)
):
    """
    Run analysis on selected components
    """
    try:
        logger.info(f"Starting analysis for components: {analysis_create.component_ids}")
        analysis = service_run_analysis(db, analysis_create)
        return analysis
    except ValueError as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )


@router.get("", response_model=AnalysisList)
async def list_analyses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all analyses with pagination
    """
    analyses = service_list_analyses(db, skip=skip, limit=limit)
    total = service_count_analyses(db)
    return AnalysisList(analyses=analyses, total=total)


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis results by ID
    """
    analysis = service_get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    return analysis


@router.get("/{analysis_id}/stride")
async def get_stride_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get STRIDE analysis for all components in the analysis
    """
    # Check if analysis exists
    analysis = service_get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Get STRIDE analysis
    stride_results = service_get_stride_analysis(db, analysis_id)
    return stride_results


@router.get("/{analysis_id}/attack-paths")
async def get_attack_paths(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get attack path analysis for all components in the analysis
    """
    # Check if analysis exists
    analysis = service_get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Get attack paths
    attack_paths = service_get_attack_paths(db, analysis_id)
    return attack_paths


@router.post("/{analysis_id}/background", status_code=status.HTTP_202_ACCEPTED)
async def run_background_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run a background analysis task (for long-running analyses)
    """
    # This is a placeholder for future implementation of background tasks
    # Will be useful for very large analyses that take a long time to complete
    return {"status": "Analysis started in background", "analysis_id": analysis_id}


@router.get("/preview-damage-generation/{scope_id}")
async def preview_damage_generation(
    scope_id: str,
    db: Session = Depends(get_db),
):
    """Preview how many damage scenarios would be generated (no DB writes)."""
    try:
        from core.generators.scenario_orchestrator import preview_damage_generation
        return preview_damage_generation(db, scope_id)
    except Exception as e:
        logger.error("Preview failed for %s: %s", scope_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}",
        )


@router.post("/generate-damage-scenarios/{scope_id}")
async def generate_damage_scenarios(
    scope_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Step 1: Auto-generate damage scenarios from assets based on CIA properties.
    Called from the Damage Scenarios page.
    """
    try:
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product
        result = generate_damage_scenarios_for_product(db, scope_id)
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )
        from core.audit_helpers import get_user_from_request, audit_create
        user = get_user_from_request(request)
        count = result.get("created", 0)
        if count:
            audit_create(db, "damage_scenario", f"batch-{scope_id}", user, scope_id=scope_id, summary=f"Auto-generated {count} damage scenarios")
            db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Damage scenario generation failed for %s: %s", scope_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Damage scenario generation failed: {str(e)}",
        )


@router.post("/generate-threat-scenarios/{scope_id}")
async def generate_threat_scenarios(
    scope_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Step 2: Auto-generate threat scenarios from existing damage scenarios
    by matching the MITRE ATT&CK ICS threat catalog. Requires damage
    scenarios to exist first.
    """
    try:
        from core.generators.scenario_orchestrator import generate_threat_scenarios_for_product
        result = generate_threat_scenarios_for_product(db, scope_id)
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )
        from core.audit_helpers import get_user_from_request, audit_create
        user = get_user_from_request(request)
        count = result.get("created", 0)
        if count:
            audit_create(db, "threat_scenario", f"batch-{scope_id}", user, scope_id=scope_id, summary=f"Auto-generated {count} threat scenarios")
            db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Threat scenario generation failed for %s: %s", scope_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat scenario generation failed: {str(e)}",
        )


# ── ISO/SAE 21434 Clause Mapping ─────────────────────────────────────────

@router.get("/iso21434/mappings")
async def get_iso21434_mappings():
    """Return full ISO/SAE 21434 clause mapping for all artifact types."""
    from core.iso21434_mapping import get_all_mappings
    return get_all_mappings()


@router.get("/iso21434/mappings/{artifact_type}")
async def get_iso21434_mapping_for_artifact(artifact_type: str):
    """Return ISO/SAE 21434 clauses for a specific artifact type."""
    from core.iso21434_mapping import ArtifactType, get_clauses_for_artifact
    try:
        at = ArtifactType(artifact_type)
    except ValueError:
        valid = [a.value for a in ArtifactType]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid artifact type '{artifact_type}'. Valid: {valid}",
        )
    clauses = get_clauses_for_artifact(at)
    return [
        {
            "clause_id": c.clause_id,
            "clause_title": c.clause_title,
            "work_product": c.work_product,
            "requirement_summary": c.requirement_summary,
            "section": c.section,
        }
        for c in clauses
    ]


# ── SFOP Risk Calculator ─────────────────────────────────────────────────

@router.post("/risk/calculate-sfop")
async def calculate_sfop_risk(payload: Dict[str, Any]):
    """Calculate risk level from SFOP impact ratings and feasibility.

    Expects JSON body:
      { "safety": "moderate", "financial": "negligible",
        "operational": "major", "privacy": "negligible",
        "feasibility": "high" }
    Returns full risk breakdown including overall_impact and risk_level.
    """
    from core.sfop_risk_calculator import calculate_risk, risk_result_to_dict
    result = calculate_risk(
        safety=payload.get("safety"),
        financial=payload.get("financial"),
        operational=payload.get("operational"),
        privacy=payload.get("privacy"),
        feasibility=payload.get("feasibility"),
    )
    return risk_result_to_dict(result)


@router.post("/risk/calculate-sfop-for-scenario/{scenario_id}")
async def calculate_sfop_risk_for_scenario(
    scenario_id: str,
    feasibility: str = "medium",
    db: Session = Depends(get_db),
):
    """Calculate risk for an existing damage scenario using its SFOP ratings."""
    from core.sfop_risk_calculator import (
        calculate_risk_from_damage_scenario,
        risk_result_to_dict,
    )
    from db.product_asset_models import DamageScenario as ProductDS
    ds = db.query(ProductDS).filter(ProductDS.scenario_id == scenario_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Damage scenario not found")
    scenario_dict = {
        "safety_impact": ds.safety_impact,
        "financial_impact": ds.financial_impact,
        "operational_impact": ds.operational_impact,
        "privacy_impact": ds.privacy_impact,
    }
    result = calculate_risk_from_damage_scenario(scenario_dict, feasibility)
    return risk_result_to_dict(result)
