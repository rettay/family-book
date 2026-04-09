"""
PWA routes — service worker registration, share target endpoint.

POST /api/share — receives shared photos from mobile share sheet
"""

import logging
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.media import MediaInboxItem, MediaInboxStatus
from app.models.person import Person
from app.services.io_limits import SizeLimitExceeded, stream_upload_to_temp
from app.services.media_service import _media_type_for_mime
from app.services.theme_service import get_runtime_theme_from_app
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(tags=["pwa"])

ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4", "video/webm"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/static/manifest.json")
async def manifest(request: Request):
    runtime_theme = get_runtime_theme_from_app(request.app)
    return JSONResponse(
        runtime_theme["manifest"],
        media_type="application/manifest+json",
    )


@router.post("/api/share")
async def share_target(
    title: str = Form(default=""),
    text: str = Form(default=""),
    media: UploadFile | None = File(default=None),
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Receive shared content from PWA share sheet.

    If not logged in, redirect to login with return_to.
    """
    if current_user is None:
        return RedirectResponse(url="/login?return_to=/api/share", status_code=302)

    if media is None:
        return RedirectResponse(url="/?toast=shared", status_code=302)

    # Validate file type
    if media.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {media.content_type}")

    # Read and validate size
    try:
        streamed_upload = await stream_upload_to_temp(media, MAX_FILE_SIZE)
    except SizeLimitExceeded:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # Dedup by hash
    file_hash = streamed_upload.sha256

    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    media_dir = os.path.join(data_dir, "media")
    inbox_dir = os.path.join(media_dir, "inbox")
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(inbox_dir, exist_ok=True)

    ext = _ext_from_content_type(media.content_type)
    filename = f"{uuid.uuid4()}{ext}"
    relative_path = os.path.join("inbox", filename)
    file_path = os.path.join(inbox_dir, filename)
    shutil.move(streamed_upload.path, file_path)

    inbox_item = MediaInboxItem(
        file_path=relative_path,
        original_filename=media.filename or filename,
        mime_type=media.content_type,
        file_size_bytes=streamed_upload.size,
        file_hash=file_hash,
        media_type=_media_type_for_mime(media.content_type),
        status=MediaInboxStatus.pending.value,
        uploaded_by=current_user.id,
        source_title=title.strip() or None,
        source_text=text.strip() or None,
        title=title.strip() or None,
        caption=text.strip() or None,
    )
    db.add(inbox_item)
    await db.flush()

    logger.info(
        "Share target: user=%s inbox_item=%s file=%s size=%d hash=%s",
        current_user.id[:8], inbox_item.id, filename, streamed_upload.size, file_hash[:12],
    )
    return RedirectResponse(url="/media/inbox?shared=1", status_code=302)


def _ext_from_content_type(ct: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
    }.get(ct, ".bin")
