from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_manage_person, get_accessible_person_ids
from app.models.media import Media
from app.models.person import Person, PersonLifecycleState


@dataclass
class MediaPage:
    items: list[Media]
    total: int
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:
        return self.page * self.page_size < self.total

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_more else None


async def build_tagged_people_payload(
    db: AsyncSession,
    tagged_person_ids: list[str],
) -> list[dict[str, str | None]]:
    tagged_people: list[dict[str, str | None]] = []
    for tagged_person_id in tagged_person_ids:
        person = await db.get(Person, tagged_person_id)
        if not person or person.lifecycle_state != PersonLifecycleState.active.value:
            continue
        tagged_people.append(
            {
                "id": person.id,
                "display_name": person.display_name,
                "photo_url": person.photo_url,
                "slug": person.slug,
            }
        )
    return tagged_people


async def serialize_media_item(
    db: AsyncSession,
    media: Media,
) -> dict[str, object]:
    owner = await db.get(Person, media.person_id)
    tagged_people = await build_tagged_people_payload(db, media.tagged_person_ids)
    return {
        "id": media.id,
        "person_id": media.person_id,
        "person_slug": owner.slug if owner else None,
        "person_display_name": owner.display_name if owner else None,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "caption": media.caption,
        "title": media.title,
        "description": media.description,
        "taken_date": media.taken_date,
        "taken_location": media.taken_location,
        "original_filename": media.original_filename,
        "purpose": media.purpose,
        "tagged_person_ids": media.tagged_person_ids,
        "tagged_people": tagged_people,
        "uploaded_by": media.uploaded_by,
        "duration_seconds": media.duration_seconds,
        "created_at": str(media.created_at),
    }


def _can_view_media_fast(
    media: Media,
    current_user: Person,
    accessible_person_ids: set[str],
) -> bool:
    """Check media visibility without per-item DB queries."""
    if current_user.is_admin:
        return True
    visibility = getattr(media, "visibility", "family")
    if visibility == "hidden":
        return False
    if visibility == "private":
        return media.uploaded_by == current_user.id
    return media.person_id in accessible_person_ids


def _build_visibility_filter(current_user: Person):
    """SQL WHERE clause fragment for media visibility."""
    if current_user.is_admin:
        return None
    return or_(
        Media.visibility == "family",
        Media.visibility.is_(None),
        (Media.visibility == "private") & (Media.uploaded_by == current_user.id),
    )


async def list_media_for_person(
    db: AsyncSession,
    current_user: Person,
    person_id: str,
) -> tuple[Person | None, list[Media]]:
    person = await db.get(Person, person_id)
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        return None, []

    accessible_ids = await get_accessible_person_ids(db, current_user)

    # Query media where this person is the subject
    query = select(Media).where(Media.person_id == person_id).order_by(Media.created_at.desc())
    vis_filter = _build_visibility_filter(current_user)
    if vis_filter is not None:
        query = query.where(vis_filter)
    result = await db.execute(query)
    direct_media = list(result.scalars().all())

    # Also find media where this person is tagged (requires Python filter on JSON field)
    tagged_query = select(Media).where(Media.person_id != person_id).order_by(Media.created_at.desc())
    if vis_filter is not None:
        tagged_query = tagged_query.where(vis_filter)
    tagged_result = await db.execute(tagged_query)
    direct_ids = {m.id for m in direct_media}
    tagged_media = [
        m
        for m in tagged_result.scalars().all()
        if person_id in m.tagged_person_ids
        and m.id not in direct_ids
        and _can_view_media_fast(m, current_user, accessible_ids)
    ]

    return person, direct_media + tagged_media


async def list_gallery_media(
    db: AsyncSession,
    current_user: Person,
    *,
    media_type: str | None = None,
    person_id: str | None = None,
    uploader_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 24,
) -> MediaPage:
    accessible_ids = await get_accessible_person_ids(db, current_user)

    query = select(Media).order_by(Media.created_at.desc())

    # Apply SQL-level filters
    vis_filter = _build_visibility_filter(current_user)
    if vis_filter is not None:
        query = query.where(vis_filter)
    if media_type:
        type_filter = _media_type_sql_filter(media_type)
        if type_filter is not None:
            query = query.where(type_filter)
    if uploader_id:
        query = query.where(Media.uploaded_by == uploader_id)

    start_date = _parse_iso_date(date_from)
    end_date = _parse_iso_date(date_to)

    result = await db.execute(query)
    filtered: list[Media] = []
    for media in result.scalars().all():
        if person_id and media.person_id != person_id and person_id not in media.tagged_person_ids:
            continue
        if not _media_within_date_range(media, start_date, end_date):
            continue
        if not _can_view_media_fast(media, current_user, accessible_ids):
            continue
        filtered.append(media)

    safe_page = max(page, 1)
    safe_page_size = max(page_size, 1)
    start = (safe_page - 1) * safe_page_size
    end = start + safe_page_size
    return MediaPage(
        items=filtered[start:end],
        total=len(filtered),
        page=safe_page,
        page_size=safe_page_size,
    )


async def list_gallery_people(
    db: AsyncSession,
    current_user: Person,
) -> list[Person]:
    accessible_ids = await get_accessible_person_ids(db, current_user)
    if not accessible_ids:
        return []
    result = await db.execute(
        select(Person)
        .where(
            Person.id.in_(accessible_ids),
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    return result.scalars().all()


def can_upload_media_for_person(current_user: Person, person: Person | None) -> bool:
    return bool(person and can_manage_person(current_user, person))


def _media_type_sql_filter(media_type: str):
    """Return a SQL filter for media type, or None if no filtering needed."""
    normalized = (media_type or "").strip().lower()
    if not normalized or normalized == "all":
        return None
    if normalized == "photo":
        return Media.media_type.in_(["image", "gif"])
    return Media.media_type == normalized


def _media_within_date_range(
    media: Media,
    start_date: date | None,
    end_date: date | None,
) -> bool:
    media_date = _parse_iso_date(media.taken_date)
    if media_date is None and media.created_at is not None:
        media_date = media.created_at.date()
    if media_date is None:
        return start_date is None and end_date is None
    if start_date and media_date < start_date:
        return False
    if end_date and media_date > end_date:
        return False
    return True


def _parse_iso_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value[:10])
    except ValueError:
        return None
