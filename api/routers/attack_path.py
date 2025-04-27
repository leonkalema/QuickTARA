"""
API Routes for Attack Path Analysis
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.models.attack_path import (
    AttackPathRequest, AttackPathAnalysisResult, AttackPathList, 
    AttackChainList, Path, Chain
)
from api.services.attack_path_service import AttackPathService
from api.deps.db import get_db

router = APIRouter(
    prefix="/analysis",
    tags=["attack-path-analysis"],
    responses={404: {"description": "Resource not found"}},
)


@router.post("/attack-paths", response_model=AttackPathAnalysisResult)
async def generate_attack_paths(
    request: AttackPathRequest,
    db: Session = Depends(get_db)
):
    """
    Generate attack paths for the given components.
    
    This endpoint analyzes the component connections, trust zones, and vulnerabilities
    to identify potential attack paths and chains.
    
    Args:
        request: Attack path generation request with component IDs
        
    Returns:
        Analysis result with summary information about identified paths and chains
    """
    try:
        service = AttackPathService(db)
        result = await service.generate_attack_paths(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating attack paths: {str(e)}")


@router.get("/attack-paths", response_model=AttackPathList)
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
    service = AttackPathService(db)
    paths = await service.get_paths(skip=skip, limit=limit, analysis_id=analysis_id)
    return AttackPathList(
        paths=paths,
        total=len(paths)  # In a real implementation, this would use a count query
    )


@router.get("/attack-paths/{path_id}", response_model=Path)
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
    service = AttackPathService(db)
    path = await service.get_path(path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Attack path not found")
    return path


@router.get("/attack-chains", response_model=AttackChainList)
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
    service = AttackPathService(db)
    chains = await service.get_chains(skip=skip, limit=limit, analysis_id=analysis_id)
    return AttackChainList(
        chains=chains,
        total=len(chains)  # In a real implementation, this would use a count query
    )


@router.get("/attack-chains/{chain_id}", response_model=Chain)
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
        chain = await service.get_chain(chain_id)
        if not chain:
            raise HTTPException(status_code=404, detail="Attack chain not found")
        return chain
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error retrieving attack chain {chain_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving attack chain: {str(e)}")
