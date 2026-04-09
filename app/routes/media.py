import hashlib
import logging
import json
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_edit_media, can_manage_person, can_soft_delete_media, can_view_media, get_person_access
from app.auth import require_admin, require_auth
from app.config import get_settings
from app.database import get_db
from app.models.media import Media
from app.models.media import Album, AlbumMedia
from app.models.person import Person, PersonLifecycleState
from app.roles import is_admin_actor
from app.services.io_limits import SizeLimitExceeded, stream_upload_to_temp
from app.services.hosted_archive_service import (
    archive_allows_writes,
    archive_usage_snapshot,
    get_hosted_archive,
)
from app.services.media_service import (
    ALLOWED_MIME_TYPES,
    IMAGE_MIME_TYPES,
    delete_media_files,
    generate_image_variants,
    get_media_file_path,
    get_media_root,
    get_thumbnail_path,
    get_variant_path,
    save_media_temp_file,
)
from app.services.media_queries import (
    build_tagged_people_payload,
    list_visible_albums,
    list_gallery_media,
    list_media_for_person as query_media_for_person,
    serialize_media_item,
)

router = APIRouter(prefix="/api/media", tags=["media"])
logger = logging.getLogger(__name__)


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


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    person_id: str = Form(...),
    caption: str | None = Form(None),
    title: str | None = Form(None),
    description: str | None = Form(None),
    taken_at: str | None = Form(None),
    tagged_person_ids: str | None = Form(None),
    purpose: str = Form("memory"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a media file. Deduplicates by SHA-256 hash."""
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    valid_purposes = ("memory", "document", "evidence")
    if purpose not in valid_purposes:
        raise HTTPException(status_code=422, detail=f"purpose must be one of: {', '.join(valid_purposes)}")

    # Verify person exists
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
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

    settings = get_settings()
    if settings.hosted_archive_enabled:
        archive = await get_hosted_archive(db)
        writes_allowed, write_denial_reason = archive_allows_writes(archive)
        if not writes_allowed:
            status_code = 402 if "Billing" in (write_denial_reason or "") else 423
            raise HTTPException(status_code=status_code, detail=write_denial_reason)

        usage_snapshot = archive_usage_snapshot(archive)
        quota_bytes = usage_snapshot["quota_bytes"]
        if quota_bytes is not None and (
            usage_snapshot["usage"].total_bytes + streamed_upload.size > quota_bytes
        ):
            raise HTTPException(
                status_code=507,
                detail="Hosted archive storage quota exceeded. Upgrade your plan or free space.",
            )

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
            title=title,
            description=description,
            taken_date=taken_at,
            tagged_person_ids=parsed_tagged_person_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if purpose != "memory":
        media.purpose = purpose
        await db.flush()

    tagged_people = await build_tagged_people_payload(db, media.tagged_person_ids)
    logger.info("Media %s uploaded for person %s by %s", media.id, person_id, current_user.id)
    return {
        "id": media.id,
        "person_id": media.person_id,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "width": media.width,
        "height": media.height,
        "file_size_bytes": media.file_size_bytes,
        "caption": media.caption,
        "title": media.title,
        "description": media.description,
        "taken_date": media.taken_date,
        "purpose": media.purpose,
        "tagged_person_ids": media.tagged_person_ids,
        "tagged_people": tagged_people,
        "is_duplicate": is_duplicate,
        "created_at": str(media.created_at),
    }


@router.get("/gallery")
async def list_gallery_media_api(
    media_type: str | None = Query(None),
    search: str | None = Query(None),
    source: str | None = Query(None),
    album_id: str | None = Query(None),
    person_id: str | None = Query(None),
    uploader_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=96),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    page_result = await list_gallery_media(
        db,
        current_user,
        media_type=media_type,
        search=search,
        source=source,
        album_id=album_id,
        person_id=person_id,
        uploader_id=uploader_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    items = [await serialize_media_item(db, media) for media in page_result.items]
    return {
        "items": items,
        "page": page_result.page,
        "page_size": page_result.page_size,
        "total": page_result.total,
        "has_more": page_result.has_more,
        "next_page": page_result.next_page,
    }


def _can_manage_album(current_user: Person, album: Album) -> bool:
    return is_admin_actor(current_user) or album.created_by == current_user.id


@router.get("/albums")
async def list_gallery_albums_api(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await list_visible_albums(db, current_user)


@router.post("/albums")
async def create_album(
    title: str = Form(...),
    description: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    album = Album(
        title=title.strip(),
        description=(description or "").strip() or None,
        created_by=current_user.id,
    )
    db.add(album)
    await db.flush()
    return RedirectResponse("/gallery", status_code=303)


@router.post("/albums/{album_id}/items")
async def add_media_to_album(
    album_id: str,
    media_id: str = Form(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_album(current_user, album):
        raise HTTPException(status_code=403, detail="Not authorized to edit this album")

    media = await db.get(Media, media_id)
    if media is None or not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=404, detail="Media not found")

    existing = await db.execute(
        select(AlbumMedia).where(
            AlbumMedia.album_id == album.id,
            AlbumMedia.media_id == media.id,
        )
    )
    if existing.scalar_one_or_none() is None:
        db.add(AlbumMedia(album_id=album.id, media_id=media.id, added_by=current_user.id))
        if not album.cover_media_id:
            album.cover_media_id = media.id
        await db.flush()
    return RedirectResponse("/gallery", status_code=303)


@router.post("/albums/{album_id}")
async def edit_album(
    album_id: str,
    title: str = Form(...),
    description: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_album(current_user, album):
        raise HTTPException(status_code=403, detail="Not authorized to edit this album")
    album.title = title.strip()
    album.description = (description or "").strip() or None
    await db.flush()
    return RedirectResponse("/gallery", status_code=303)


@router.post("/albums/{album_id}/items/{media_id}/remove")
async def remove_media_from_album(
    album_id: str,
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_album(current_user, album):
        raise HTTPException(status_code=403, detail="Not authorized to edit this album")

    membership_result = await db.execute(
        select(AlbumMedia).where(
            AlbumMedia.album_id == album.id,
            AlbumMedia.media_id == media_id,
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=404, detail="Album item not found")
    await db.delete(membership)
    if album.cover_media_id == media_id:
        next_item_result = await db.execute(
            select(AlbumMedia).where(AlbumMedia.album_id == album.id).order_by(AlbumMedia.created_at.asc())
        )
        next_item = next_item_result.scalars().first()
        album.cover_media_id = next_item.media_id if next_item else None
    await db.flush()
    return RedirectResponse("/gallery", status_code=303)


@router.post("/albums/{album_id}/delete")
async def delete_album(
    album_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_album(current_user, album):
        raise HTTPException(status_code=403, detail="Not authorized to delete this album")
    await db.delete(album)
    await db.flush()
    return RedirectResponse("/gallery", status_code=303)


@router.get("/moderation/hidden")
async def list_hidden_media(
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: list hidden (soft-deleted) media for moderation."""
    result = await db.execute(
        select(Media).where(Media.visibility == "hidden").order_by(Media.created_at.desc()).limit(100)
    )
    items = result.scalars().all()
    return [
        {
            "id": m.id,
            "person_id": m.person_id,
            "original_filename": m.original_filename,
            "media_type": m.media_type,
            "uploaded_by": m.uploaded_by,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in items
    ]


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
    logger.debug("Media metadata %s requested by %s", media.id, current_user.id)

    tagged_people = await build_tagged_people_payload(db, media.tagged_person_ids)
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
        "title": media.title,
        "description": media.description,
        "taken_date": media.taken_date,
        "purpose": media.purpose,
        "tagged_person_ids": media.tagged_person_ids,
        "tagged_people": tagged_people,
        "created_at": str(media.created_at),
    }
    if is_admin_actor(current_user) or current_user.id == media.person_id:
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
    file_path = get_media_file_path(media.file_path, data_dir)

    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        media_type=media.mime_type,
        filename=media.original_filename,
        headers={"Cache-Control": "private, max-age=3600"},
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
    thumb_path = get_thumbnail_path(media.id, data_dir)

    if not thumb_path or not os.path.isfile(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail not available")

    return FileResponse(
        path=thumb_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.get("/{media_id}/variant/{variant}")
async def serve_variant(
    media_id: str,
    variant: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Serve a media variant (thumb, medium, poster)."""
    if variant not in ("thumb", "medium", "poster"):
        raise HTTPException(status_code=400, detail="Invalid variant. Must be thumb, medium, or poster.")

    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=403, detail="Not visible")

    variant_path = get_variant_path(media.id, variant)
    if not variant_path:
        raise HTTPException(status_code=404, detail="Variant not available")

    return FileResponse(
        path=variant_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.get("", response_model=list)
async def list_media_for_person(
    person_id: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all media for a given person."""
    person, visible_media = await query_media_for_person(db, current_user, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        raise HTTPException(status_code=403, detail="Not visible")
    return [await serialize_media_item(db, media) for media in visible_media]


@router.patch("/{media_id}")
async def update_media(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    caption: str | None = Form(None),
    title: str | None = Form(None),
    description: str | None = Form(None),
    taken_at: str | None = Form(None),
    taken_location: str | None = Form(None),
    person_id: str | None = Form(None),
    purpose: str | None = Form(None),
):
    """Update media metadata (caption/title/description/date/location/person, purpose)."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if not can_edit_media(current_user, media):
        raise HTTPException(status_code=403, detail="Not authorized")

    if purpose is not None:
        valid_purposes = ("memory", "document", "evidence")
        if purpose not in valid_purposes:
            raise HTTPException(status_code=422, detail=f"purpose must be one of: {', '.join(valid_purposes)}")
        media.purpose = purpose

    if caption is not None:
        media.caption = caption
    if title is not None:
        media.title = title
    if description is not None:
        media.description = description
    if taken_at is not None:
        media.taken_date = taken_at
    if taken_location is not None:
        media.taken_location = taken_location
    if person_id is not None:
        person_check = await db.get(Person, person_id)
        if not person_check or person_check.lifecycle_state != PersonLifecycleState.active.value:
            raise HTTPException(status_code=400, detail="Person not found")
        media.person_id = person_id

    await db.flush()
    return {
        "id": media.id,
        "caption": media.caption,
        "title": media.title,
        "description": media.description,
        "taken_date": media.taken_date,
        "taken_location": media.taken_location,
        "person_id": media.person_id,
        "purpose": media.purpose,
    }


@router.get("/{media_id}/tags")
async def get_media_tags(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all persons tagged in a media item."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not await can_view_media(db, current_user, media):
        raise HTTPException(status_code=403, detail="Not visible")
    from app.services.media_queries import build_tagged_people_payload
    tagged_people = await build_tagged_people_payload(db, media.tagged_person_ids)
    return tagged_people


@router.post("/{media_id}/tags", status_code=status.HTTP_200_OK)
async def add_media_tag(
    media_id: str,
    person_id: str = Form(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a person tag to a media item. Idempotent."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not can_edit_media(current_user, media):
        raise HTTPException(status_code=403, detail="Not authorized")
    tagged_person = await db.get(Person, person_id)
    if not tagged_person or tagged_person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Person not found")
    tags = media.tagged_person_ids
    if person_id not in tags:
        tags.append(person_id)
        media.tagged_person_ids = tags
        await db.flush()
    from app.services.media_queries import build_tagged_people_payload
    return await build_tagged_people_payload(db, media.tagged_person_ids)


@router.delete("/{media_id}/tags/{person_id}", status_code=status.HTTP_200_OK)
async def remove_media_tag(
    media_id: str,
    person_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove a person tag from a media item."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not can_edit_media(current_user, media):
        raise HTTPException(status_code=403, detail="Not authorized")
    tags = media.tagged_person_ids
    if person_id not in tags:
        raise HTTPException(status_code=404, detail="Tag not found")
    media.tagged_person_ids = [t for t in tags if t != person_id]
    await db.flush()
    from app.services.media_queries import build_tagged_people_payload
    return await build_tagged_people_payload(db, media.tagged_person_ids)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: str,
    permanent: bool = Query(False),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete for non-admins (sets visibility=hidden). Admin can permanently delete with ?permanent=true."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if not can_soft_delete_media(current_user, media):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Protect primary photos of other people
    if not is_admin_actor(current_user) and media.uploaded_by == current_user.id:
        photo_check = await db.execute(
            select(Person.id).where(
                Person.photo_url == media.id,
                Person.id != current_user.id,
            )
        )
        if photo_check.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="This media is another person's headshot. Unset their headshot first.",
            )

    # Clear photo_url on any person using this media as their headshot
    headshot_persons = await db.execute(
        select(Person).where(Person.photo_url == media_id)
    )
    for person in headshot_persons.scalars().all():
        person.photo_url = None
        await db.flush()

    if is_admin_actor(current_user):
        # Admin delete is permanent by default; use PATCH visibility to soft-delete instead
        delete_media_files(media)
        await db.delete(media)
        await db.flush()
    else:
        # Non-admin: soft delete (hide)
        media.visibility = "hidden"
        await db.flush()


@router.post("/{media_id}/edit-image")
async def edit_image(
    media_id: str,
    file: UploadFile = File(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Replace an existing image with an edited version (cropped/rotated/resized).
    The stored file and its thumb/medium variants are regenerated in place.
    Only the media owner or an admin may call this endpoint."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if media.mime_type not in IMAGE_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only image media can be edited")

    if not (is_admin_actor(current_user) or media.uploaded_by == current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this media")

    if not file.content_type or file.content_type not in IMAGE_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    media_dir = get_media_root(data_dir)

    if not media.file_path:
        raise HTTPException(status_code=409, detail="Media has no stored file to replace")

    dest_path = get_media_file_path(media.file_path, data_dir)
    if not dest_path:
        raise HTTPException(status_code=409, detail="Media has an invalid stored file path")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    # Regenerate thumb and medium variants
    generate_image_variants(data, file.content_type, media_dir, media_id)

    # Update file size and hash
    media.file_size_bytes = len(data)
    media.file_hash = hashlib.sha256(data).hexdigest()
    await db.flush()

    return {
        "id": media.id,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "file_size_bytes": media.file_size_bytes,
        "caption": media.caption,
        "title": media.title,
    }


@router.patch("/{media_id}/visibility")
async def change_media_visibility(
    media_id: str,
    visibility: str = Form(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Change media visibility. Uploader can toggle family↔private. Admin can set anything."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    valid = ("family", "private", "hidden")
    if visibility not in valid:
        raise HTTPException(status_code=422, detail=f"visibility must be one of: {', '.join(valid)}")

    if is_admin_actor(current_user):
        media.visibility = visibility
    elif media.uploaded_by == current_user.id:
        if visibility == "hidden":
            raise HTTPException(status_code=403, detail="Use delete to hide media")
        media.visibility = visibility
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.flush()
    return {"id": media.id, "visibility": media.visibility}


@router.patch("/{media_id}/untag")
async def untag_self(
    media_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove the current user's ID from the tagged person list."""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    tags = media.tagged_person_ids
    if current_user.id not in tags:
        return {"id": media.id, "tagged_person_ids": tags}

    media.tagged_person_ids = [t for t in tags if t != current_user.id]
    await db.flush()
    return {"id": media.id, "tagged_person_ids": media.tagged_person_ids}


def _max_upload_size(content_type: str | None) -> int:
    if not content_type:
        return 10 * 1024 * 1024
    if content_type.startswith("video/"):
        return 250 * 1024 * 1024
    if content_type.startswith("audio/"):
        return 25 * 1024 * 1024
    return 10 * 1024 * 1024
