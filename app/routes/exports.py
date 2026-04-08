import logging

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_db
from app.models.person import Person
from app.services.audit_service import log_audit
from app.services.export_service import (
    build_archive_export,
    build_gedcom_export,
    cleanup_export_artifact,
)

router = APIRouter(prefix="/api/admin/exports", tags=["exports"])
logger = logging.getLogger(__name__)


def _ephemeral_download_response(
    artifact_path: str,
    media_type: str,
    filename: str,
) -> Response:
    with open(artifact_path, "rb") as handle:
        payload = handle.read()
    cleanup_export_artifact(artifact_path)
    return Response(
        content=payload,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(payload)),
        },
    )


@router.get("/gedcom")
async def download_gedcom_export(
    admin: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    artifact = await build_gedcom_export(db)
    await log_audit(
        db,
        admin.id,
        "export",
        "archive",
        admin.id,
        new_value={"format": "gedcom", "delivery": "ephemeral_download"},
    )
    await db.commit()
    logger.info("GEDCOM export prepared for admin %s", admin.id)
    return _ephemeral_download_response(
        artifact.path,
        media_type="application/octet-stream",
        filename="family-book-export.ged",
    )


@router.get("/archive")
async def download_archive_export(
    admin: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    artifact = await build_archive_export(db)
    await log_audit(
        db,
        admin.id,
        "export",
        "archive",
        admin.id,
        new_value={"format": "archive_zip", "delivery": "ephemeral_download"},
    )
    await db.commit()
    logger.info("Archive export prepared for admin %s", admin.id)
    return _ephemeral_download_response(
        artifact.path,
        media_type="application/zip",
        filename="family-book-archive-export.zip",
    )
