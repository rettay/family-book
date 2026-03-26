"""Timeline service — aggregates family events for chronological timeline view."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moments import Moment, MomentLifecycleState, MomentVisibility
from app.models.person import Person, PersonLifecycleState, Visibility
from app.models.relationships import Partnership
from app.access_control import get_accessible_person_ids


async def get_timeline_events(
    db: AsyncSession,
    current_user: Person,
    *,
    event_type: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    branch: str | None = None,
    lineage_person_ids: set[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """Return timeline events sorted by date DESC.

    event_type: filter to 'birth', 'death', 'marriage', 'moment'
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

    # Moment events
    if event_type is None or event_type == "moment":
        moment_query = select(Moment).where(
            Moment.lifecycle_state == MomentLifecycleState.active.value,
        )
        if not current_user.is_admin:
            moment_query = moment_query.where(Moment.visibility == MomentVisibility.members.value)
        result = await db.execute(moment_query)
        moments = result.scalars().all()
        for moment in moments:
            if not moment.occurred_at:
                continue
            if moment.person_id not in person_ids_set:
                continue
            occ = moment.occurred_at
            if not _in_year_range(occ.year, year_from, year_to):
                continue
            events.append({
                "date": occ.strftime("%Y-%m-%d"),
                "year": occ.year,
                "type": "moment",
                "label": moment.title or moment.kind,
                "person_id": moment.person_id,
                "person_name": names_by_id.get(moment.person_id, "?"),
                "detail": (moment.body or "")[:120],
            })

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
