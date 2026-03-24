"""
Backup admin API routes.

POST /api/admin/backup       — trigger immediate backup
GET  /api/admin/backup/download — download latest backup as .zip
GET  /api/admin/backup/status  — backup health info
"""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse

from app.auth import require_admin
from app.backup.service import (
    create_download_zip,
    get_backup_health,
    run_backup,
    verify_backup_restore,
)
from app.models.person import Person

router = APIRouter(prefix="/api/admin/backup", tags=["backup"])
logger = logging.getLogger(__name__)


@router.post("")
async def trigger_backup(admin: Person = Depends(require_admin)) -> JSONResponse:
    """Trigger an immediate backup."""
    path = run_backup()
    logger.info("Backup triggered by admin %s: %s", admin.id, path)
    return JSONResponse({"status": "ok", "path": path})


@router.get("/download")
async def download_backup(admin: Person = Depends(require_admin)) -> FileResponse:
    """Download latest backup as .zip (DB + media)."""
    zip_path = create_download_zip()
    logger.info("Backup download prepared for admin %s: %s", admin.id, zip_path)
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="family-book-backup.zip",
    )


@router.get("/status")
async def backup_status(admin: Person = Depends(require_admin)) -> JSONResponse:
    """Return backup freshness info."""
    logger.debug("Backup status requested by admin %s", admin.id)
    return JSONResponse(get_backup_health())


@router.post("/verify")
async def backup_verify(admin: Person = Depends(require_admin)) -> JSONResponse:
    """Verify that the latest backup can restore into a usable temporary state."""
    result = verify_backup_restore()
    logger.info("Backup restore verification completed for admin %s", admin.id)
    return JSONResponse(result)
