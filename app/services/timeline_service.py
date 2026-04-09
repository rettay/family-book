"""Timeline service — aggregates family events for chronological timeline view."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_view_media
from app.models.person import Person, PersonLifecycleState, Visibility
from app.models.relationships import Partnership
from app.models.media import AlbumMedia, Media
from app.access_control import get_accessible_person_ids


async def get_timeline_events(
    db: AsyncSession,
    current_user: Person,
    *,
    event_type: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    branch: str | None = None,
    person_id: str | None = None,
    album_id: str | None = None,
    lineage_person_ids: set[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """Return timeline events sorted by date DESC.

    event_type: filter to 'birth', 'death', 'marriage', 'memory'
    year_from/year_to: restrict date range
    branch: filter to a specific branch
    lineage_person_ids: if set, restrict to these person IDs (pre-computed by caller)
    """
    accessible_ids = await get_accessible_person_ids(db, current_user)

    if lineage_person_ids is not None:
        accessible_ids = accessible_ids & lineage_person_ids

    # Load persons
    result = await db.execute(
        select(Person).where(
            Person.id.in_(accessible_ids),
            Person.lifecycle_state == PersonLifecycleState.active.value,
            Person.visibility != Visibility.hidden.value,
        )
    )
    persons = result.scalars().all()

    if branch:
        persons = [p for p in persons if p.branch and p.branch.lower() == branch.lower()]
    if person_id:
        persons = [p for p in persons if p.id == person_id]

    person_ids_set = {p.id for p in persons}
    names_by_id = {p.id: p.display_name for p in persons}

    events: list[dict] = []

    from app.services.date_intelligence_service import compute_age_at_death, compute_current_age

    # Birth events
    if event_type is None or event_type == "birth":
        for person in persons:
            if person.birth_date:
                bd = _parse_date(person.birth_date)
                if bd and _in_year_range(bd.year, year_from, year_to):
                    label = f"{person.display_name} born"
                    if person.is_living:
                        age = compute_current_age(person.birth_date, person.birth_date_precision)
                        if age is not None:
                            label += f" (age {age})"
                    else:
                        age = compute_current_age(person.birth_date, person.birth_date_precision)
                        if age is not None:
                            label += f" (would be {age} today)"
                    events.append({
                        "date": person.birth_date,
                        "year": bd.year,
                        "type": "birth",
                        "label": label,
                        "person_id": person.id,
                        "person_name": person.display_name,
                        "detail": person.birth_place or "",
                    })

    # Death events
    if event_type is None or event_type == "death":
        for person in persons:
            if person.death_date:
                dd = _parse_date(person.death_date)
                if dd and _in_year_range(dd.year, year_from, year_to):
                    label = f"{person.display_name} passed away"
                    age = compute_age_at_death(
                        person.birth_date, person.death_date,
                        person.birth_date_precision, person.death_date_precision,
                    )
                    if age is not None:
                        label += f" (age {age})"
                    events.append({
                        "date": person.death_date,
                        "year": dd.year,
                        "type": "death",
                        "label": label,
                        "person_id": person.id,
                        "person_name": person.display_name,
                        "detail": person.burial_place or "",
                    })

    # Partnership events
    if event_type is None or event_type == "marriage":
        result = await db.execute(
            select(Partnership).where(
                Partnership.person_a_id.in_(person_ids_set),
                Partnership.person_b_id.in_(person_ids_set),
            )
        )
        partnerships = result.scalars().all()
        for p in partnerships:
            if not p.start_date:
                continue
            sd = _parse_date(p.start_date)
            if not sd or not _in_year_range(sd.year, year_from, year_to):
                continue
            # Skip if either partner is not accessible (avoid leaking existence)
            if p.person_a_id not in names_by_id or p.person_b_id not in names_by_id:
                continue
            name_a = names_by_id[p.person_a_id]
            name_b = names_by_id[p.person_b_id]
            events.append({
                "date": p.start_date,
                "year": sd.year,
                "type": "marriage",
                "label": f"{name_a} & {name_b}",
                "person_id": p.person_a_id,
                "person_name": f"{name_a} & {name_b}",
                "detail": p.kind or "",
            })

    if event_type is None or event_type == "memory":
        media_result = await db.execute(select(Media).order_by(Media.created_at.desc()))
        album_media_ids: set[str] | None = None
        if album_id:
            album_result = await db.execute(
                select(AlbumMedia.media_id).where(AlbumMedia.album_id == album_id)
            )
            album_media_ids = {row[0] for row in album_result.all()}
        for media in media_result.scalars().all():
            if album_media_ids is not None and media.id not in album_media_ids:
                continue
            if not await can_view_media(db, current_user, media):
                continue
            if person_id and media.person_id != person_id and person_id not in media.tagged_person_ids:
                continue
            event_date = _parse_date(media.taken_date) if media.taken_date else None
            if event_date is None and media.created_at is not None:
                event_date = media.created_at.date()
            if event_date is None or not _in_year_range(event_date.year, year_from, year_to):
                continue
            owner_name = names_by_id.get(media.person_id)
            if owner_name is None and media.person_id:
                owner = await db.get(Person, media.person_id)
                owner_name = owner.display_name if owner else "Unknown person"
            events.append(
                {
                    "date": event_date.isoformat(),
                    "year": event_date.year,
                    "type": "memory",
                    "label": media.title or media.caption or media.original_filename or "Family memory",
                    "person_id": media.person_id,
                    "person_name": owner_name or "Unknown person",
                    "detail": media.taken_location or owner_name or "",
                }
            )

    # Sort by date DESC
    events.sort(key=lambda e: e["date"], reverse=True)

    # Return total before pagination, then apply pagination
    total = len(events)
    return events[offset:offset + limit], total


def _in_year_range(year: int, year_from: int | None, year_to: int | None) -> bool:
    if year_from and year < year_from:
        return False
    if year_to and year > year_to:
        return False
    return True


def _parse_date(date_str: str) -> date | None:
    if not date_str:
        return None
    parts = date_str.split("-")
    try:
        if len(parts) >= 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        elif len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
        elif len(parts) == 1 and len(parts[0]) == 4:
            return date(int(parts[0]), 1, 1)
    except (ValueError, IndexError):
        return None
    return None
