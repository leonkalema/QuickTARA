"""CRA Annex VII — technical documentation generator endpoints.

Mounts under /api/cra. Endpoints:

  GET /assessments/{id}/annex-vii            structured JSON document
  GET /assessments/{id}/annex-vii/markdown   downloadable Markdown

Both endpoints rebuild the document on every call from current QuickTARA
data — no caching. Re-uploading an SBOM or marking a requirement compliant
is reflected immediately.
"""
from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_active_user
from api.deps.db import get_db
from api.models.cra_annex_vii import AnnexViiDocumentResponse
from api.models.user import User
from core.cra_annex_vii import build_annex_vii
from core.cra_annex_vii_markdown import render_markdown

logger = logging.getLogger(__name__)
router = APIRouter()


def _to_response(doc) -> AnnexViiDocumentResponse:
    """Convert frozen dataclass tree → Pydantic response.

    `dataclasses.asdict` walks the tree, including nested tuples, and
    Pydantic accepts the resulting dict via standard validation.
    """
    raw: Dict[str, Any] = asdict(doc)
    return AnnexViiDocumentResponse(**raw)


@router.get(
    "/assessments/{assessment_id}/annex-vii",
    response_model=AnnexViiDocumentResponse,
)
async def get_annex_vii(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnnexViiDocumentResponse:
    """CRA Annex VII — return the structured document for the assessment."""
    doc = build_annex_vii(db, assessment_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRA assessment not found",
        )
    return _to_response(doc)


@router.get(
    "/assessments/{assessment_id}/annex-vii/markdown",
    response_class=Response,
    responses={
        200: {
            "content": {"text/markdown": {}},
            "description": "Markdown document",
        },
    },
)
async def get_annex_vii_markdown(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    """CRA Annex VII — return the document rendered as Markdown."""
    doc = build_annex_vii(db, assessment_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRA assessment not found",
        )
    md = render_markdown(doc)
    safe_name = "".join(
        c if c.isalnum() or c in {"-", "_"} else "_" for c in doc.product_name
    ) or "product"
    filename = f"annex-vii-{safe_name}.md"
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
