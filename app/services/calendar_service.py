"""Calendar service — aggregates family events from Person, Partnership, and Moment data."""

import calendar as cal_mod
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moments import Moment, MomentLifecycleState, MomentVisibility
from app.models.person import Person, PersonLifecycleState, Visibility
from app.models.relationships import Partnership
from app.access_control import get_accessible_person_ids


async def get_calendar_events(
    db: AsyncSession,
    current_user: Person,
    year: int,
    month: int,
) -> list[dict]:
    """Return calendar events for the given month.

    Events are sourced from:
    - Person birth_date (recurring annual — birthday)
    - Person death_date (recurring annual — remembrance)
    - Partnership start_date (recurring annual — anniversary)
    - Moment occurred_at (one-time on specific date)
    """
    accessible_ids = await get_accessible_person_ids(db, current_user)

    # Persons with dates
    result = await db.execute(
        select(Person).where(
            Person.id.in_(accessible_ids),
            Person.lifecycle_state == PersonLifecycleState.active.value,
            Person.visibility != Visibility.hidden.value,
        )
    )
    persons = result.scalars().all()

    events: list[dict] = []

    for person in persons:
        name = person.display_name

        # Birthday (recurring — match month/day regardless of year)
        if person.birth_date and person.birth_date_precision in ("exact", "month", None):
            bd = _parse_date(person.birth_date)
            if bd and bd.month == month:
                day = bd.day if person.birth_date_precision != "month" else 1
                events.append({
                    "date": f"{year:04d}-{month:02d}-{day:02d}",
                    "day": day,
                    "type": "birthday",
                    "label": f"{name}'s birthday",
                    "person_id": person.id,
                    "year_only": person.birth_date_precision == "month",
                })

        # Remembrance (recurring — death date anniversary)
        if person.death_date and person.death_date_precision in ("exact", "month", None):
            dd = _parse_date(person.death_date)
            if dd and dd.month == month:
                day = dd.day if person.death_date_precision != "month" else 1
                events.append({
                    "date": f"{year:04d}-{month:02d}-{day:02d}",
                    "day": day,
                    "type": "remembrance",
                    "label": f"Remembering {name}",
                    "person_id": person.id,
                    "year_only": person.death_date_precision == "month",
                })

    # Partnership anniversaries
    person_ids_set = {p.id for p in persons}
    result = await db.execute(select(Partnership))
    partnerships = result.scalars().all()

    # Build name lookup
    names_by_id = {p.id: p.display_name for p in persons}

    for partnership in partnerships:
        if partnership.person_a_id not in person_ids_set or partnership.person_b_id not in person_ids_set:
            continue
        if not partnership.start_date:
            continue
        if partnership.start_date_precision not in ("exact", "month", None):
            continue
        sd = _parse_date(partnership.start_date)
        if not sd or sd.month != month:
            continue
        day = sd.day if partnership.start_date_precision != "month" else 1
        name_a = names_by_id.get(partnership.person_a_id, "?")
        name_b = names_by_id.get(partnership.person_b_id, "?")
        events.append({
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "day": day,
            "type": "anniversary",
            "label": f"{name_a} & {name_b} anniversary",
            "person_id": None,
            "year_only": partnership.start_date_precision == "month",
        })

    # Moments with occurred_at in this specific month/year
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
        occ = moment.occurred_at
        if occ.year == year and occ.month == month:
            events.append({
                "date": f"{year:04d}-{month:02d}-{occ.day:02d}",
                "day": occ.day,
                "type": "moment",
                "label": moment.title or moment.kind,
                "person_id": moment.person_id,
                "year_only": False,
            })

    events.sort(key=lambda e: (e["day"], e["type"], e["label"]))
    return events


def get_month_grid(year: int, month: int) -> list[list[int | None]]:
    """Return a list of weeks, each week a list of 7 day numbers (None for empty cells)."""
    matrix = cal_mod.monthcalendar(year, month)
    return [[d if d != 0 else None for d in week] for week in matrix]


def _parse_date(date_str: str) -> date | None:
    """Parse an ISO 8601 date string (YYYY-MM-DD or YYYY-MM or YYYY) to a date object."""
    if not date_str:
        return None
    parts = date_str.split("-")
    try:
        if len(parts) >= 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        elif len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
    except (ValueError, IndexError):
        return None
    return None
