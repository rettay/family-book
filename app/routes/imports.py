"""GEDCOM import upload and status endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.importers.gedcom_parser import parse_gedcom
from app.models.person import Person
from app.services.import_service import import_gedcom

router = APIRouter(prefix="/api/import", tags=["import"])
logger = logging.getLogger(__name__)

MAX_GEDCOM_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/gedcom")
async def upload_gedcom(
    file: UploadFile = File(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload and import a GEDCOM file."""
    if not file.filename or not file.filename.lower().endswith((".ged", ".gedcom")):
        raise HTTPException(status_code=400, detail="File must be a .ged or .gedcom file")

    content = await file.read()
    if len(content) > MAX_GEDCOM_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {MAX_GEDCOM_SIZE // (1024*1024)}MB",
        )

    # Parse
    parsed = parse_gedcom(content, max_size_bytes=MAX_GEDCOM_SIZE)
    if parsed.errors:
        raise HTTPException(status_code=400, detail=parsed.errors[0])

    if not parsed.individuals:
        raise HTTPException(status_code=400, detail="No individual records found in GEDCOM file")

    # Import
    result = await import_gedcom(db, parsed, actor_id=current_user.id)

    return {
        "ok": True,
        "persons_created": result.persons_created,
        "relationships_created": result.relationships_created,
        "duplicates_skipped": result.duplicates_skipped,
        "duplicate_candidates": [
            {
                "existing_person_id": d.existing_person_id,
                "existing_name": d.existing_name,
                "gedcom_name": d.gedcom_name,
                "match_reason": d.match_reason,
            }
            for d in result.duplicate_candidates
        ],
        "errors": result.errors,
    }
