"""GEDCOM import upload and status endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.importers.gedcom_parser import parse_gedcom
from app.models.imports import GedcomImportBatch, ImportStatus
from app.models.person import Person
from app.roles import is_admin_actor, is_staff_actor
from app.services.import_service import (
    build_gedcom_import_summary,
    detect_unsupported_gedcom_items,
    find_duplicates,
    import_gedcom,
    rollback_gedcom_batch,
)
from app.models.base import utcnow

router = APIRouter(prefix="/api/import", tags=["import"])
logger = logging.getLogger(__name__)

MAX_GEDCOM_SIZE = 10 * 1024 * 1024  # 10MB


def _require_import_staff(current_user: Person) -> None:
    if not is_staff_actor(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to manage GEDCOM imports")


def _validate_and_parse(content: bytes, filename: str):
    """Validate file and parse GEDCOM content. Returns parsed result or raises."""
    if not filename or not filename.lower().endswith((".ged", ".gedcom")):
        raise HTTPException(status_code=400, detail="File must be a .ged or .gedcom file")
    if len(content) > MAX_GEDCOM_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {MAX_GEDCOM_SIZE // (1024*1024)}MB",
        )
    parsed = parse_gedcom(content, max_size_bytes=MAX_GEDCOM_SIZE)
    if parsed.errors:
        raise HTTPException(status_code=400, detail=parsed.errors[0])
    if not parsed.individuals:
        raise HTTPException(status_code=400, detail="No individual records found in GEDCOM file")
    return parsed


@router.post("/gedcom/preview")
async def preview_gedcom(
    file: UploadFile = File(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Parse a GEDCOM file and return a preview with duplicate candidates.

    Does NOT import anything — allows the user to review duplicates
    before confirming the import.
    """
    _require_import_staff(current_user)
    content = await file.read()
    parsed = _validate_and_parse(content, file.filename)

    duplicates = await find_duplicates(db, parsed.individuals)
    unsupported_items = detect_unsupported_gedcom_items(content)

    individuals_preview = []
    for indi in parsed.individuals:
        entry = {
            "xref": indi.xref,
            "name": f"{indi.first_name} {indi.last_name}".strip(),
            "birth_date": indi.birth.date if indi.birth else "",
            "birth_place": indi.birth.place if indi.birth else "",
            "is_duplicate": indi.xref in duplicates,
        }
        if indi.xref in duplicates:
            d = duplicates[indi.xref]
            entry["duplicate_match"] = {
                "existing_person_id": d.existing_person_id,
                "existing_name": d.existing_name,
                "match_reason": d.match_reason,
            }
        individuals_preview.append(entry)

    return {
        "ok": True,
        "individuals_count": len(parsed.individuals),
        "families_count": len(parsed.families),
        "duplicates_count": len(duplicates),
        "unsupported_items": unsupported_items,
        "individuals": individuals_preview,
    }


@router.post("/gedcom")
async def upload_gedcom(
    file: UploadFile = File(...),
    skip_xrefs: str = Query("", description="Comma-separated xrefs to skip (duplicates confirmed by user)"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload and import a GEDCOM file."""
    _require_import_staff(current_user)
    content = await file.read()
    parsed = _validate_and_parse(content, file.filename)

    # Create import batch record
    batch = GedcomImportBatch(
        filename=file.filename or "unknown.ged",
        status=ImportStatus.importing.value,
        imported_by=current_user.id,
    )
    db.add(batch)
    await db.flush()

    # Import
    skip_duplicate_xrefs = {
        xref.strip()
        for xref in skip_xrefs.split(",")
        if xref.strip()
    }
    result = await import_gedcom(
        db,
        parsed,
        actor_id=current_user.id,
        skip_duplicate_xrefs=skip_duplicate_xrefs,
        batch_id=batch.id,
    )
    summary = build_gedcom_import_summary(
        parsed=parsed,
        result=result,
        unsupported_items=detect_unsupported_gedcom_items(content),
    )

    # Finalize batch record
    batch.status = ImportStatus.completed.value
    batch.persons_created = result.persons_created
    batch.relationships_created = result.relationships_created
    batch.duplicates_skipped = result.duplicates_skipped
    batch.stats = summary
    batch.completed_at = utcnow()
    await db.flush()

    return {
        "ok": True,
        "batch_id": batch.id,
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
        "unsupported_items": summary["unsupported_items"],
    }


@router.get("/gedcom/{batch_id}")
async def get_gedcom_batch(
    batch_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    _require_import_staff(current_user)
    batch = await db.get(GedcomImportBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")
    if batch.imported_by != current_user.id and not is_admin_actor(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view this import batch")

    return {
        "id": batch.id,
        "filename": batch.filename,
        "status": batch.status,
        "persons_created": batch.persons_created,
        "relationships_created": batch.relationships_created,
        "duplicates_skipped": batch.duplicates_skipped,
        "created_at": batch.created_at.isoformat() if batch.created_at else None,
        "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
        "summary": batch.stats,
    }


@router.post("/gedcom/{batch_id}/rollback")
async def rollback_batch(
    batch_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    _require_import_staff(current_user)
    batch = await db.get(GedcomImportBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")
    if batch.imported_by != current_user.id and not is_admin_actor(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to roll back this import batch")

    result = await rollback_gedcom_batch(
        db,
        batch=batch,
        actor_id=current_user.id,
    )
    return {
        "ok": True,
        "batch_id": batch.id,
        "status": batch.status,
        **result,
    }
