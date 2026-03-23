import json
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_manage_person, can_view_media, get_person_access
from app.auth import require_auth
from app.config import get_settings
from app.database import get_db
from app.models.media import Media
from app.models.person import Person
from app.services.io_limits import SizeLimitExceeded, stream_upload_to_temp
from app.services.media_service import (
    ALLOWED_MIME_TYPES,
    delete_media_files,
    save_media_temp_file,
)

router = APIRouter(prefix="/api/media", tags=["media"])


def _parse_tagged_person_ids(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in raw_value.split(",") if item.strip()]


async def _build_tagged_people(db: AsyncSession, tagged_person_ids: list[str]) -> list[dict[str, str | None]]:
    tagged_people: list[dict[str, str | None]] = []
    for tagged_person_id in tagged_person_ids:
        person = await db.get(Person, tagged_person_id)
        if not person:
            continue
        tagged_people.append(
            {
                "id": person.id,
                "display_name": person.display_name,
                "photo_url": person.photo_url,
            }
        )
    return tagged_people


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    person_id: str = Form(...),
    caption: str | None = Form(None),
    tagged_person_ids: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a media file. Deduplicates by SHA-256 hash."""
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    # Verify person exists
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=400, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized to upload for this profile")

    parsed_tagged_person_ids = _parse_tagged_person_ids(tagged_person_ids)
    for tagged_person_id in parsed_tagged_person_ids:
        tagged_person = await db.get(Person, tagged_person_id)
        if not tagged_person:
            raise HTTPException(status_code=400, detail=f"Tagged person not found: {tagged_person_id}")
        tagged_person_access = await get_person_access(db, current_user, tagged_person)
        if not tagged_person_access.can_view:
            raise HTTPException(status_code=403, detail="Not authorized to tag this person")

    max_size = _max_upload_size(file.content_type)
    try:
        streamed_upload = await stream_upload_to_temp(file, max_size)
    except SizeLimitExceeded:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        media, is_duplicate = await save_media_temp_file(
            db=db,
            temp_path=streamed_upload.path,
            file_size=streamed_upload.size,
            file_hash=streamed_upload.sha256,
            filename=file.filename or "upload",
            mime_type=file.content_type,
            person_id=person_id,
            uploaded_by=current_user.id,
            caption=caption,
            tagged_person_ids=parsed_tagged_person_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tagged_people = await _build_tagged_people(db, media.tagged_person_ids)
    return {
        "id": media.id,
        "person_id": media.person_id,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "width": media.width,
        "height": media.height,
        "file_size_bytes": media.file_size_bytes,
        "caption": media.caption,
        "tagged_person_ids": media.tagged_person_ids,
        "tagged_people": tagged_people,
        "is_duplicate": is_duplicate,
        "created_at": str(media.created_at),
    }


@router.get("/{media_id}")
async def get_media_metadata(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get media metadata."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=403, detail="Not visible")

    tagged_people = await _build_tagged_people(db, media.tagged_person_ids)
    body = {
        "id": media.id,
        "person_id": media.person_id,
        "original_filename": media.original_filename,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "width": media.width,
        "height": media.height,
        "file_size_bytes": media.file_size_bytes,
        "caption": media.caption,
        "tagged_person_ids": media.tagged_person_ids,
        "tagged_people": tagged_people,
        "created_at": str(media.created_at),
    }
    if current_user.is_admin or current_user.id == media.person_id:
        body["source"] = media.source
        body["uploaded_by"] = media.uploaded_by
    return body


@router.get("/{media_id}/file")
async def serve_media_file(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Serve the actual media file through an authenticated endpoint."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=403, detail="Not visible")

    if not media.file_path:
        raise HTTPException(status_code=404, detail="No file associated with this media")

    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    file_path = os.path.join(data_dir, "media", media.file_path)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        media_type=media.mime_type,
        filename=media.original_filename,
    )


@router.get("/{media_id}/thumbnail")
async def serve_thumbnail(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Serve a thumbnail for image media."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=403, detail="Not visible")

    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    thumb_path = os.path.join(data_dir, "media", "thumbnails", f"{media.id}.jpg")

    if not os.path.isfile(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail not available")

    return FileResponse(path=thumb_path, media_type="image/jpeg")


@router.get("", response_model=list)
async def list_media_for_person(
    person_id: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all media for a given person."""
    person_result = await db.execute(select(Person).where(Person.id == person_id))
    person = person_result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        raise HTTPException(status_code=403, detail="Not visible")

    result = await db.execute(
        select(Media).order_by(Media.created_at.desc())
    )
    visible_media = []
    for media in result.scalars().all():
        if media.person_id != person_id and person_id not in media.tagged_person_ids:
            continue
        if not await can_view_media(db, current_user, media):
            continue
        visible_media.append(media)
    response = []
    for media in visible_media:
        response.append(
            {
                "id": media.id,
                "person_id": media.person_id,
                "media_type": media.media_type,
                "mime_type": media.mime_type,
                "caption": media.caption,
                "tagged_person_ids": media.tagged_person_ids,
                "tagged_people": await _build_tagged_people(db, media.tagged_person_ids),
                "created_at": str(media.created_at),
            }
        )
    return response


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete media owned by the uploader or an admin."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if not current_user.is_admin and media.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    delete_media_files(media)
    await db.delete(media)
    await db.flush()


def _max_upload_size(content_type: str | None) -> int:
    if not content_type:
        return 10 * 1024 * 1024
    if content_type.startswith("video/"):
        return 100 * 1024 * 1024
    if content_type.startswith("audio/"):
        return 25 * 1024 * 1024
    return 10 * 1024 * 1024
