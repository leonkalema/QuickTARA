"""
Attack Path Analysis API routes
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from api.models.attack_path import (
    AttackPathRequest, AttackPathAnalysisResult, AttackPathList, 
    AttackChainList, Path, Chain, AttackPathAssumption, AttackPathConstraint,
    ThreatScenario
)
from api.services.attack_path_service import AttackPathService
from api.deps.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=AttackPathAnalysisResult)
async def generate_attack_paths(
    request: AttackPathRequest,
    db: Session = Depends(get_db)
):
    """
    Generate attack paths for the given components with enhanced contextual analysis.
    
    This endpoint performs a comprehensive attack path analysis taking into account:
    - The primary component of interest (focal point for the analysis)
    - Component connections and trust relationships
    - Specific entry points and target components
    - Assumptions about the attacker and environment
    - Constraints that limit the attack scope
    - Relevant threat scenarios from STRIDE or similar methodologies
    - Known vulnerabilities in the components
    
    The analysis identifies feasible attack paths and chains, calculates success likelihood,
    impact scores, and overall risk levels for each path.
    
    Args:
        request: Attack path generation request with the following elements:
            - primary_component_id: ID of the primary component to analyze
            - component_ids: List of component IDs to include in the analysis
            - entry_point_ids: Optional specific entry points
            - target_ids: Optional specific targets
            - assumptions: List of analysis assumptions
            - constraints: List of analysis constraints
            - threat_scenarios: List of relevant threat scenarios
            - vulnerability_ids: List of vulnerability IDs to consider
            - include_chains: Whether to generate attack chains
            - max_depth: Maximum path depth to consider
        
    Returns:
        Analysis result with:
        - Summary information about identified paths and chains
        - Risk metrics and statistics
        - Links to detailed path and chain information
    """
    try:
        service = AttackPathService(db)
        result = await service.generate_attack_paths(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating attack paths: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating attack paths: {str(e)}")


@router.get("", response_model=AttackPathList)
async def get_attack_paths(
    skip: int = 0,
    limit: int = 100,
    analysis_id: Optional[str] = Query(None, description="Filter by analysis ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve attack paths, optionally filtered by analysis ID.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        analysis_id: Optional analysis ID to filter results
        
    Returns:
        List of attack paths with pagination info
    """
    try:
        service = AttackPathService(db)
        db_paths = await service.get_paths(skip=skip, limit=limit, analysis_id=analysis_id)
        
        # Transform paths to ensure steps are included
        api_paths = []
        for db_path in db_paths:
            # Create a complete path object with steps
            path_data = {
                "path_id": db_path.path_id,
                "name": db_path.name,
                "description": db_path.description,
                "path_type": db_path.path_type,
                "complexity": db_path.complexity,
                "entry_point_id": db_path.entry_point_id,
                "target_id": db_path.target_id,
                "success_likelihood": db_path.success_likelihood,
                "impact": db_path.impact,
                "risk_score": db_path.risk_score,
                "analysis_id": db_path.analysis_id,
                "scope_id": db_path.scope_id,
                "created_at": db_path.created_at,
                "updated_at": db_path.updated_at,
                "steps": [{
                    "step_id": s.step_id,
                    "component_id": s.component_id,
                    "step_type": s.step_type,
                    "description": s.description,
                    "prerequisites": s.prerequisites,
                    "vulnerability_ids": s.vulnerability_ids,
                    "threat_ids": s.threat_ids,
                    "order": s.order,
                    "created_at": s.created_at
                } for s in db_path.steps]
            }
            api_paths.append(path_data)
            
        return AttackPathList(
            paths=api_paths,
            total=len(api_paths)
        )
    except Exception as e:
        logger.error(f"Error retrieving attack paths: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack paths: {str(e)}")


@router.get("/chains", response_model=AttackChainList)
async def get_attack_chains(
    skip: int = 0,
    limit: int = 100,
    analysis_id: Optional[str] = Query(None, description="Filter by analysis ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve attack chains, optionally filtered by analysis ID.
    
    Attack chains represent complex attack scenarios consisting of multiple paths
    that share common components or targets.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        analysis_id: Optional analysis ID to filter results
        
    Returns:
        List of attack chains with pagination info
    """
    try:
        service = AttackPathService(db)
        db_chains = await service.get_chains(skip=skip, limit=limit, analysis_id=analysis_id)
        
        # Transform chains to make them compatible with the API model
        api_chains = []
        for db_chain in db_chains:
            # First convert the DB model to a dict
            chain_data = {
                "chain_id": db_chain.chain_id,
                "name": db_chain.name,
                "description": db_chain.description,
                "entry_point_id": db_chain.entry_points[0] if db_chain.entry_points else "",
                "final_target_id": db_chain.targets[0] if db_chain.targets else "",
                "attack_goal": db_chain.attack_goal,
                "total_steps": sum(len(p.steps) for p in db_chain.paths) if db_chain.paths else 0,
                "complexity": db_chain.complexity,
                "success_likelihood": db_chain.success_likelihood,
                "impact": db_chain.impact,
                "risk_score": db_chain.risk_score,
                "analysis_id": db_chain.analysis_id,
                "scope_id": db_chain.scope_id,
                "created_at": db_chain.created_at,
                "updated_at": db_chain.updated_at,
                "paths": [{
                    "path_id": p.path_id,
                    "name": p.name,
                    "description": p.description,
                    "path_type": p.path_type,
                    "complexity": p.complexity,
                    "entry_point_id": p.entry_point_id,
                    "target_id": p.target_id,
                    "success_likelihood": p.success_likelihood,
                    "impact": p.impact,
                    "risk_score": p.risk_score,
                    "analysis_id": p.analysis_id,
                    "scope_id": p.scope_id,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                    "steps": [{
                        "step_id": s.step_id,
                        "component_id": s.component_id,
                        "step_type": s.step_type,
                        "description": s.description,
                        "prerequisites": s.prerequisites,
                        "vulnerability_ids": s.vulnerability_ids,
                        "threat_ids": s.threat_ids,
                        "order": s.order,
                        "created_at": s.created_at
                    } for s in p.steps]
                } for p in db_chain.paths]
            }
            api_chains.append(chain_data)
            
        return AttackChainList(
            chains=api_chains,
            total=len(api_chains)
        )
    except Exception as e:
        logger.error(f"Error retrieving attack chains: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack chains: {str(e)}")


@router.get("/chains/{chain_id}")
async def get_attack_chain(
    chain_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific attack chain by ID.
    
    Args:
        chain_id: Unique identifier of the attack chain
        
    Returns:
        Attack chain details including all associated paths
    """
    try:
        service = AttackPathService(db)
        db_chain = await service.get_chain(chain_id)
        if not db_chain:
            raise HTTPException(status_code=404, detail="Attack chain not found")
        
        # Transform chain to make it compatible with the API model
        chain_data = {
            "chain_id": db_chain.chain_id,
            "name": db_chain.name,
            "description": db_chain.description,
            "entry_point_id": db_chain.entry_points[0] if db_chain.entry_points else "",
            "final_target_id": db_chain.targets[0] if db_chain.targets else "",
            "attack_goal": db_chain.attack_goal,
            "total_steps": sum(len(p.steps) for p in db_chain.paths) if db_chain.paths else 0,
            "complexity": db_chain.complexity,
            "success_likelihood": db_chain.success_likelihood,
            "impact": db_chain.impact,
            "risk_score": db_chain.risk_score,
            "analysis_id": db_chain.analysis_id,
            "scope_id": db_chain.scope_id,
            "created_at": db_chain.created_at,
            "updated_at": db_chain.updated_at,
            "paths": [{
                "path_id": p.path_id,
                "name": p.name,
                "description": p.description,
                "path_type": p.path_type,
                "complexity": p.complexity,
                "entry_point_id": p.entry_point_id,
                "target_id": p.target_id,
                "success_likelihood": p.success_likelihood,
                "impact": p.impact,
                "risk_score": p.risk_score,
                "analysis_id": p.analysis_id,
                "scope_id": p.scope_id,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "steps": [{
                    "step_id": s.step_id,
                    "component_id": s.component_id,
                    "step_type": s.step_type,
                    "description": s.description,
                    "prerequisites": s.prerequisites,
                    "vulnerability_ids": s.vulnerability_ids,
                    "threat_ids": s.threat_ids,
                    "order": s.order,
                    "created_at": s.created_at
                } for s in p.steps]
            } for p in db_chain.paths]
        }
        
        return chain_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving attack chain {chain_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack chain: {str(e)}")


@router.get("/{path_id}", response_model=Path)
async def get_attack_path(
    path_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific attack path by ID.
    
    Args:
        path_id: Unique identifier of the attack path
        
    Returns:
        Attack path details including all steps
    """
    try:
        service = AttackPathService(db)
        path = await service.get_path(path_id)
        if not path:
            raise HTTPException(status_code=404, detail="Attack path not found")
        return path
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving attack path {path_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack path: {str(e)}")
