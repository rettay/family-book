"""Calendar service — aggregates family and external calendar events."""

from __future__ import annotations

import asyncio
import calendar as cal_mod
from datetime import UTC, date, datetime, timedelta
from urllib.parse import urlencode

import httpx
import recurring_ical_events
from icalendar import Calendar, Event
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.access_control import get_accessible_person_ids
from app.models.calendar import ExternalCalendarSource
from app.models.person import Person, PersonLifecycleState, Visibility
from app.models.relationships import Partnership
from app.services.date_parsing import parse_date_raw_to_iso

_EXTERNAL_CALENDAR_CACHE_TTL = timedelta(hours=6)
_external_calendar_cache: dict[str, tuple[datetime, list[dict]]] = {}
_FEED_TYPE_ORDER = ("birthday", "remembrance", "anniversary", "external")


async def get_calendar_events(
    db: AsyncSession,
    current_user: Person,
    year: int,
    month: int,
) -> list[dict]:
    """Return calendar events for the given month."""
    accessible_ids = await get_accessible_person_ids(db, current_user)

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

        birth_date, birth_precision = _resolve_person_event_date(
            iso_value=person.birth_date,
            precision=person.birth_date_precision,
            raw_value=person.birth_date_raw,
        )
        if birth_date and birth_precision in ("exact", "month", None) and birth_date.month == month:
            day = birth_date.day if birth_precision != "month" else 1
            events.append(
                {
                    "date": f"{year:04d}-{month:02d}-{day:02d}",
                    "day": day,
                    "type": "birthday",
                    "label": f"{name}'s birthday",
                    "person_id": person.id,
                    "year_only": birth_precision == "month",
                    "source_name": None,
                    "source_type": None,
                }
            )

        death_date, death_precision = _resolve_person_event_date(
            iso_value=person.death_date,
            precision=person.death_date_precision,
            raw_value=person.death_date_raw,
        )
        if death_date and death_precision in ("exact", "month", None) and death_date.month == month:
            day = death_date.day if death_precision != "month" else 1
            events.append(
                {
                    "date": f"{year:04d}-{month:02d}-{day:02d}",
                    "day": day,
                    "type": "remembrance",
                    "label": f"Remembering {name}",
                    "person_id": person.id,
                    "year_only": death_precision == "month",
                    "source_name": None,
                    "source_type": None,
                }
            )

    person_ids_set = {p.id for p in persons}
    result = await db.execute(select(Partnership))
    partnerships = result.scalars().all()
    names_by_id = {p.id: p.display_name for p in persons}

    for partnership in partnerships:
        if partnership.person_a_id not in person_ids_set or partnership.person_b_id not in person_ids_set:
            continue
        if not partnership.start_date:
            continue
        if partnership.start_date_precision not in ("exact", "month", None):
            continue
        start_date = _parse_date(partnership.start_date)
        if not start_date or start_date.month != month:
            continue
        day = start_date.day if partnership.start_date_precision != "month" else 1
        name_a = names_by_id.get(partnership.person_a_id, "?")
        name_b = names_by_id.get(partnership.person_b_id, "?")
        events.append(
            {
                "date": f"{year:04d}-{month:02d}-{day:02d}",
                "day": day,
                "type": "anniversary",
                "label": f"{name_a} & {name_b} anniversary",
                "person_id": None,
                "year_only": partnership.start_date_precision == "month",
                "source_name": None,
                "source_type": None,
            }
        )

    events.extend(await get_external_calendar_events(db, year, month))
    events.sort(key=lambda e: (e["day"], e["type"], e["label"]))
    return events


async def get_person_by_calendar_feed_token(
    db: AsyncSession,
    token: str,
) -> Person | None:
    if not token:
        return None
    result = await db.execute(
        select(Person).where(
            Person.calendar_feed_token == token,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    return result.scalar_one_or_none()


async def build_calendar_feed_ics(
    db: AsyncSession,
    current_user: Person,
    *,
    event_types: set[str] | None = None,
) -> bytes:
    normalized_types = normalize_feed_types(event_types)
    calendar = Calendar()
    calendar.add("prodid", "-//Family Book//Calendar Feed//EN")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    calendar.add("x-wr-calname", build_feed_name(current_user.display_name, normalized_types))
    calendar.add("x-wr-timezone", "UTC")

    accessible_ids = await get_accessible_person_ids(db, current_user)
    result = await db.execute(
        select(Person).where(
            Person.id.in_(accessible_ids),
            Person.lifecycle_state == PersonLifecycleState.active.value,
            Person.visibility != Visibility.hidden.value,
        )
    )
    persons = result.scalars().all()
    person_ids_set = {person.id for person in persons}
    names_by_id = {person.id: person.display_name for person in persons}

    if "birthday" in normalized_types:
        for person in persons:
            birth_date, birth_precision = _resolve_person_event_date(
                iso_value=person.birth_date,
                precision=person.birth_date_precision,
                raw_value=person.birth_date_raw,
            )
            if birth_date and birth_precision in ("exact", "month", None):
                calendar.add_component(
                    _build_yearly_event(
                        uid=f"birthday-{person.id}@family-book",
                        summary=f"{person.display_name}'s birthday",
                        start_day=birth_date,
                        categories=["birthday"],
                        description=f"Birthday for {person.display_name}",
                    )
                )

    if "remembrance" in normalized_types:
        for person in persons:
            death_date, death_precision = _resolve_person_event_date(
                iso_value=person.death_date,
                precision=person.death_date_precision,
                raw_value=person.death_date_raw,
            )
            if death_date and death_precision in ("exact", "month", None):
                calendar.add_component(
                    _build_yearly_event(
                        uid=f"remembrance-{person.id}@family-book",
                        summary=f"Remembering {person.display_name}",
                        start_day=death_date,
                        categories=["remembrance"],
                        description=f"Remembrance day for {person.display_name}",
                    )
                )

    if "anniversary" in normalized_types:
        result = await db.execute(select(Partnership))
        partnerships = result.scalars().all()
        for partnership in partnerships:
            if partnership.person_a_id not in person_ids_set or partnership.person_b_id not in person_ids_set:
                continue
            if not partnership.start_date or partnership.start_date_precision not in ("exact", "month", None):
                continue
            start_date = _parse_date(partnership.start_date)
            if not start_date:
                continue
            name_a = names_by_id.get(partnership.person_a_id, "?")
            name_b = names_by_id.get(partnership.person_b_id, "?")
            calendar.add_component(
                _build_yearly_event(
                    uid=f"anniversary-{partnership.id}@family-book",
                    summary=f"{name_a} & {name_b} anniversary",
                    start_day=start_date,
                    categories=["anniversary"],
                    description=f"Partnership anniversary for {name_a} and {name_b}",
                )
            )

    if "external" in normalized_types:
        today = date.today()
        horizon_end = _month_add(today.replace(day=1), 18)
        external_events = await _collect_external_feed_events(db, today.replace(day=1), horizon_end)
        for index, event in enumerate(external_events):
            start_day = _parse_date(event["date"])
            if not start_day:
                continue
            source_name = event.get("source_name")
            description = event["label"] if not source_name else f'{event["label"]} ({source_name})'
            calendar.add_component(
                _build_single_event(
                    uid=f"external-{index}-{start_day.isoformat()}-{_slug_uid(event['label'])}@family-book",
                    summary=event["label"],
                    start_day=start_day,
                    categories=["external"],
                    description=description,
                )
            )

    return calendar.to_ical()


async def list_external_calendar_sources(
    db: AsyncSession,
    *,
    enabled_only: bool = False,
) -> list[ExternalCalendarSource]:
    query = select(ExternalCalendarSource).order_by(ExternalCalendarSource.name)
    if enabled_only:
        query = query.where(ExternalCalendarSource.enabled.is_(True))
    result = await db.execute(query)
    return result.scalars().all()


async def get_external_calendar_events(
    db: AsyncSession,
    year: int,
    month: int,
) -> list[dict]:
    sources = await list_external_calendar_sources(db, enabled_only=True)
    if not sources:
        return []

    tasks = [_get_external_source_events(source, year, month) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    events: list[dict] = []
    for result in results:
        if isinstance(result, Exception):
            continue
        events.extend(result)
    return events


def clear_external_calendar_cache() -> None:
    _external_calendar_cache.clear()


def get_month_grid(year: int, month: int) -> list[list[int | None]]:
    """Return a list of weeks, each week a list of 7 day numbers (None for empty cells)."""
    matrix = cal_mod.monthcalendar(year, month)
    return [[d if d != 0 else None for d in week] for week in matrix]


def normalize_feed_types(event_types: set[str] | None) -> set[str]:
    if not event_types:
        return set(_FEED_TYPE_ORDER)
    normalized = {event_type.strip().lower() for event_type in event_types if event_type and event_type.strip()}
    return {event_type for event_type in normalized if event_type in _FEED_TYPE_ORDER}


def validate_feed_types(event_types: set[str] | None) -> set[str]:
    if not event_types:
        return set(_FEED_TYPE_ORDER)
    normalized = {event_type.strip().lower() for event_type in event_types if event_type and event_type.strip()}
    valid = normalize_feed_types(normalized)
    invalid = normalized - set(_FEED_TYPE_ORDER)
    if invalid or not valid:
        raise ValueError("Invalid calendar feed types")
    return valid


def build_feed_name(display_name: str, event_types: set[str]) -> str:
    labels = [event_type for event_type in _FEED_TYPE_ORDER if event_type in event_types]
    if set(labels) == set(_FEED_TYPE_ORDER):
        return f"{display_name} - Family Calendar"
    return f"{display_name} - {' + '.join(label.title() for label in labels)}"


def build_calendar_feed_url(token: str, *, event_types: set[str] | None = None, webcal: bool = False) -> str:
    settings = get_settings()
    base = settings.BASE_URL.rstrip("/")
    if webcal and base.startswith("https://"):
        base = "webcal://" + base[len("https://"):]
    elif webcal and base.startswith("http://"):
        base = "webcal://" + base[len("http://"):]
    params = {"token": token}
    normalized_types = normalize_feed_types(event_types)
    if normalized_types != set(_FEED_TYPE_ORDER):
        params["types"] = ",".join(event_type for event_type in _FEED_TYPE_ORDER if event_type in normalized_types)
    return f"{base}/calendar/feed.ics?{urlencode(params)}"


def _resolve_person_event_date(
    *,
    iso_value: str | None,
    precision: str | None,
    raw_value: str | None,
) -> tuple[date | None, str | None]:
    resolved_iso = iso_value
    resolved_precision = precision
    if not resolved_iso and raw_value:
        resolved_iso, resolved_precision = parse_date_raw_to_iso(raw_value)
    return _parse_date(resolved_iso), resolved_precision


def _parse_date(date_str: str | None) -> date | None:
    """Parse an ISO 8601 date string (YYYY-MM-DD or YYYY-MM or YYYY) to a date object."""
    if not date_str:
        return None
    parts = date_str.split("-")
    try:
        if len(parts) >= 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        if len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
    except (ValueError, IndexError):
        return None
    return None


async def _get_external_source_events(
    source: ExternalCalendarSource,
    year: int,
    month: int,
) -> list[dict]:
    cache_key = f"{source.id}:{source.updated_at.isoformat() if source.updated_at else ''}:{year:04d}-{month:02d}"
    now = datetime.now(UTC)
    cached = _external_calendar_cache.get(cache_key)
    if cached and now - cached[0] < _EXTERNAL_CALENDAR_CACHE_TTL:
        return [dict(event) for event in cached[1]]

    events = await _fetch_external_source_events(source, year, month)
    _external_calendar_cache[cache_key] = (now, [dict(event) for event in events])
    _prune_external_calendar_cache(now)
    return events


async def _fetch_external_source_events(
    source: ExternalCalendarSource,
    year: int,
    month: int,
) -> list[dict]:
    content = await _fetch_calendar_ics(_normalize_calendar_url(source.url))
    calendar = Calendar.from_ical(content)

    month_start = datetime(year, month, 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    month_end = datetime(next_year, next_month, 1)

    events: list[dict] = []
    for component in recurring_ical_events.of(calendar).between(month_start, month_end):
        event_day = _coerce_event_date(component.decoded("DTSTART", None))
        if not event_day or event_day.year != year or event_day.month != month:
            continue

        summary = str(component.get("SUMMARY") or source.name or "Imported event").strip()
        events.append(
            {
                "date": event_day.isoformat(),
                "day": event_day.day,
                "type": "external",
                "label": summary,
                "person_id": None,
                "year_only": False,
                "source_name": source.name,
                "source_type": source.source_type,
            }
        )
    return events


async def _fetch_calendar_ics(url: str) -> bytes:
    headers = {"Accept": "text/calendar, text/plain;q=0.9, */*;q=0.1"}
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.content


def _coerce_event_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return None


def _normalize_calendar_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("webcal://"):
        return "https://" + normalized[len("webcal://"):]
    return normalized


def _prune_external_calendar_cache(now: datetime) -> None:
    stale_keys = [
        key for key, (cached_at, _) in _external_calendar_cache.items()
        if now - cached_at >= _EXTERNAL_CALENDAR_CACHE_TTL
    ]
    for key in stale_keys:
        _external_calendar_cache.pop(key, None)


async def _collect_external_feed_events(
    db: AsyncSession,
    start_month: date,
    end_month: date,
) -> list[dict]:
    cursor = start_month
    events: list[dict] = []
    while cursor < end_month:
        events.extend(await get_external_calendar_events(db, cursor.year, cursor.month))
        cursor = _month_add(cursor, 1)
    seen: set[tuple[str, str, str | None]] = set()
    unique_events: list[dict] = []
    for event in sorted(events, key=lambda entry: (entry["date"], entry["label"], entry.get("source_name") or "")):
        key = (event["date"], event["label"], event.get("source_name"))
        if key in seen:
            continue
        seen.add(key)
        unique_events.append(event)
    return unique_events


def _build_yearly_event(
    *,
    uid: str,
    summary: str,
    start_day: date,
    categories: list[str],
    description: str,
) -> Event:
    event = Event()
    event.add("uid", uid)
    event.add("summary", summary)
    event.add("dtstart", start_day)
    event.add("dtend", start_day + timedelta(days=1))
    event.add("dtstamp", datetime.now(UTC))
    event.add("rrule", {"freq": "yearly"})
    event.add("transp", "TRANSPARENT")
    event.add("categories", categories)
    event.add("description", description)
    return event


def _build_single_event(
    *,
    uid: str,
    summary: str,
    start_day: date,
    categories: list[str],
    description: str,
) -> Event:
    event = Event()
    event.add("uid", uid)
    event.add("summary", summary)
    event.add("dtstart", start_day)
    event.add("dtend", start_day + timedelta(days=1))
    event.add("dtstamp", datetime.now(UTC))
    event.add("transp", "TRANSPARENT")
    event.add("categories", categories)
    event.add("description", description)
    return event


def _month_add(day: date, months: int) -> date:
    year = day.year + ((day.month - 1 + months) // 12)
    month = ((day.month - 1 + months) % 12) + 1
    return date(year, month, 1)


def _slug_uid(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "event"
