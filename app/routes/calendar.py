"""Calendar routes — API endpoints and HTML page for family calendar."""

from __future__ import annotations

import logging
import os
from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin, require_auth
from app.config import get_settings
from app.database import get_db
from app.i18n import translate
from app.models.calendar import ExternalCalendarSource
from app.models.person import Person
from app.schemas import (
    ExternalCalendarSourceCreate,
    ExternalCalendarSourceResponse,
    ExternalCalendarSourceUpdate,
)
from app.services.calendar_service import (
    build_calendar_feed_ics,
    build_calendar_feed_url,
    build_feed_name,
    clear_external_calendar_cache,
    get_calendar_events,
    get_person_by_calendar_feed_token,
    get_month_grid,
    list_external_calendar_sources,
    validate_feed_types,
)
from app.services.theme_service import get_runtime_theme_from_app

router = APIRouter(tags=["calendar"])
logger = logging.getLogger(__name__)

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)

MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
DAY_HEADER_KEYS = [
    "calendar.day_mon",
    "calendar.day_tue",
    "calendar.day_wed",
    "calendar.day_thu",
    "calendar.day_fri",
    "calendar.day_sat",
    "calendar.day_sun",
]


def _get_locale(request: Request) -> str:
    return request.cookies.get("locale", "en")


def _ctx(request: Request, current_user: Person | None = None, **kwargs):
    locale = _get_locale(request)
    app_theme = get_runtime_theme_from_app(request.app)
    return {
        "request": request,
        "current_user": current_user,
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "app_theme": app_theme,
        "brand_display_name": app_theme["brand_display_name"],
        "brand_tagline": app_theme["brand_tagline"],
        **kwargs,
    }


def _resolve_year_month(month_value: str | None) -> tuple[int, int]:
    today = date.today()
    if month_value:
        parts = month_value.split("-")
        try:
            year, mon = int(parts[0]), int(parts[1])
            if mon < 1 or mon > 12:
                raise ValueError
            return year, mon
        except (ValueError, IndexError):
            pass
    return today.year, today.month


def _normalize_external_calendar_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("webcal://"):
        return "https://" + normalized[len("webcal://") :]
    return normalized


def _validate_external_calendar_url(url: str) -> str:
    normalized = _normalize_external_calendar_url(url)
    if not normalized.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Calendar URL must start with http://, https://, or webcal://")
    return normalized


async def _get_source_or_404(db: AsyncSession, source_id: str) -> ExternalCalendarSource:
    result = await db.execute(select(ExternalCalendarSource).where(ExternalCalendarSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Calendar source not found")
    return source


def _calendar_redirect(month_value: str | None = None) -> RedirectResponse:
    target = "/calendar"
    if month_value:
        target = f"{target}?month={month_value}"
    return RedirectResponse(target, status_code=303)


class CalendarEvent(BaseModel):
    date: str
    day: int
    type: str
    label: str
    person_id: str | None
    person_name: str | None = None
    name_a: str | None = None
    name_b: str | None = None
    age_turning: int | None = None
    anniversary_years: int | None = None
    year_only: bool = False
    source_name: str | None = None
    source_type: str | None = None


class CalendarResponse(BaseModel):
    year: int
    month: int
    month_name: str
    events: list[CalendarEvent]


_FEED_GROUP_DEFINITIONS = (
    (
        "calendar.feed_group_family",
        "calendar.feed_group_family_copy",
        (
            ("calendar.feed_all", "calendar.feed_all_desc", None),
        ),
    ),
    (
        "calendar.feed_group_event_types",
        "calendar.feed_group_event_types_copy",
        (
            ("calendar.feed_birthdays", "calendar.feed_birthdays_desc", {"birthday"}),
            ("calendar.feed_anniversaries", "calendar.feed_anniversaries_desc", {"anniversary"}),
            ("calendar.feed_remembrances", "calendar.feed_remembrances_desc", {"remembrance"}),
            ("calendar.feed_external", "calendar.feed_external_desc", {"external"}),
        ),
    ),
)

_HOLIDAY_PRESETS = (
    {
        "label_key": "calendar.preset_us_holidays",
        "name": "US Holidays",
        "url": "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics",
        "source_type": "holiday",
    },
    {
        "label_key": "calendar.preset_australia_holidays",
        "name": "Australia Holidays",
        "url": "https://calendar.google.com/calendar/ical/en.australian%23holiday%40group.v.calendar.google.com/public/basic.ics",
        "source_type": "holiday",
    },
    {
        "label_key": "calendar.preset_argentina_holidays",
        "name": "Argentina Holidays",
        "url": "https://calendar.google.com/calendar/ical/en.ar%23holiday%40group.v.calendar.google.com/public/basic.ics",
        "source_type": "holiday",
    },
    {
        "label_key": "calendar.preset_italy_holidays",
        "name": "Italy Holidays",
        "url": "https://calendar.google.com/calendar/ical/en.italian%23holiday%40group.v.calendar.google.com/public/basic.ics",
        "source_type": "holiday",
    },
)


def _ordinal_en(value: int) -> str:
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return f"{value}{suffix}"


def _decorate_calendar_events(events: list[dict], locale: str) -> list[dict]:
    def t(key: str) -> str:
        return translate(key, locale)

    decorated: list[dict] = []
    for event in events:
        item = dict(event)
        item["type_label"] = t(f"calendar.type_{event['type']}")
        item["source_badge"] = None
        if event["type"] == "birthday":
            person_name = event.get("person_name") or event["label"].removesuffix("'s birthday")
            if event.get("age_turning"):
                item["display_label"] = t("calendar.event_birthday_turns").format(
                    name=person_name,
                    age=event["age_turning"],
                )
                item["display_short_label"] = t("calendar.event_turns_short").format(age=event["age_turning"])
            else:
                item["display_label"] = t("calendar.event_birthday").format(name=person_name)
                item["display_short_label"] = person_name
        elif event["type"] == "anniversary":
            name_a = event.get("name_a") or "?"
            name_b = event.get("name_b") or "?"
            if event.get("anniversary_years"):
                years_value = int(event["anniversary_years"])
                if locale == "en":
                    years_label = _ordinal_en(years_value)
                    label_key = "calendar.event_anniversary_years"
                    short_key = "calendar.event_anniversary_short"
                else:
                    years_label = str(years_value)
                    label_key = "calendar.event_anniversary_years_count"
                    short_key = "calendar.event_anniversary_short_count"
                item["display_label"] = t(label_key).format(name_a=name_a, name_b=name_b, years=years_label)
                item["display_short_label"] = t(short_key).format(years=years_label)
            else:
                item["display_label"] = t("calendar.event_anniversary").format(name_a=name_a, name_b=name_b)
                item["display_short_label"] = t("calendar.anniversaries")
        elif event["type"] == "remembrance":
            person_name = event.get("person_name") or event["label"].replace("Remembering ", "", 1)
            item["display_label"] = t("calendar.event_remembrance").format(name=person_name)
            item["display_short_label"] = person_name
        else:
            item["display_label"] = event["label"]
            item["display_short_label"] = event["label"]

        if event.get("source_name"):
            source_type = event.get("source_type") or "other"
            source_key = f"calendar.source_type_{source_type}"
            source_label = translate(source_key, locale)
            item["source_badge"] = source_label if source_label != source_key else source_type

        decorated.append(item)
    return decorated


def _build_feed_groups(current_user: Person, locale: str) -> list[dict]:
    def t(key: str) -> str:
        return translate(key, locale)

    groups: list[dict] = []
    for title_key, copy_key, items in _FEED_GROUP_DEFINITIONS:
        group_items = []
        for label_key, description_key, event_types in items:
            label = t(label_key)
            description = t(description_key)
            group_items.append(
                {
                    "label_key": label_key,
                    "label": label,
                    "description": description,
                    "https_url": build_calendar_feed_url(current_user.calendar_feed_token, event_types=event_types),
                    "webcal_url": build_calendar_feed_url(current_user.calendar_feed_token, event_types=event_types, webcal=True),
                    "search_text": f"{label} {description}".lower(),
                }
            )
        groups.append(
            {
                "title": t(title_key),
                "copy": t(copy_key),
                "items": group_items,
            }
        )
    return groups


def _build_holiday_presets(locale: str) -> list[dict]:
    def t(key: str) -> str:
        return translate(key, locale)

    presets: list[dict] = []
    for preset in _HOLIDAY_PRESETS:
        presets.append(
            {
                **preset,
                "label": t(preset["label_key"]),
                "source_type_label": t("calendar.source_type_holiday"),
            }
        )
    return presets


def _build_calendar_stats(events: list[dict], locale: str) -> list[dict]:
    def t(key: str) -> str:
        return translate(key, locale)

    counts = {"birthday": 0, "anniversary": 0, "remembrance": 0, "external": 0}
    for event in events:
        counts[event["type"]] = counts.get(event["type"], 0) + 1
    return [
        {"label": t("calendar.birthdays"), "value": counts["birthday"], "type": "birthday"},
        {"label": t("calendar.anniversaries"), "value": counts["anniversary"], "type": "anniversary"},
        {"label": t("calendar.remembrances"), "value": counts["remembrance"], "type": "remembrance"},
        {"label": t("calendar.external_events"), "value": counts["external"], "type": "external"},
    ]


def _default_selected_day(events: list[dict], year: int, month: int) -> int | None:
    if not events:
        return None
    today = date.today()
    if today.year == year and today.month == month:
        same_or_future = [event["day"] for event in events if event["day"] >= today.day]
        if same_or_future:
            return same_or_future[0]
    return events[0]["day"]


@router.get("/api/calendar", response_model=CalendarResponse)
async def api_calendar(
    month: str | None = Query(None, description="YYYY-MM format"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    year, mon = _resolve_year_month(month)
    events = await get_calendar_events(db, current_user, year, mon)
    return CalendarResponse(
        year=year,
        month=mon,
        month_name=MONTH_NAMES[mon],
        events=[CalendarEvent(**event) for event in events],
    )


@router.get("/calendar/feed.ics")
async def calendar_feed(
    token: str = Query(..., min_length=1),
    types: str | None = Query(None, description="Comma-separated event types"),
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_person_by_calendar_feed_token(db, token)
    if not current_user:
        return Response(
            content="Invalid calendar feed token",
            media_type="text/plain; charset=utf-8",
            status_code=401,
        )

    requested_types = set(types.split(",")) if types else None
    try:
        normalized_types = validate_feed_types(requested_types)
    except ValueError:
        return Response(
            content="Invalid calendar feed types",
            media_type="text/plain; charset=utf-8",
            status_code=400,
        )
    ical_bytes = await build_calendar_feed_ics(db, current_user, event_types=normalized_types)
    filename = "-".join(build_feed_name(current_user.display_name, normalized_types).lower().split()) + ".ics"
    return Response(
        content=ical_bytes,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, max-age=900",
        },
    )


@router.get("/api/calendar/sources", response_model=list[ExternalCalendarSourceResponse])
async def api_list_calendar_sources(
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    sources = await list_external_calendar_sources(db)
    return [ExternalCalendarSourceResponse.model_validate(source) for source in sources]


@router.post(
    "/api/calendar/sources",
    response_model=ExternalCalendarSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def api_create_calendar_source(
    body: ExternalCalendarSourceCreate,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = ExternalCalendarSource(
        name=body.name.strip(),
        url=_validate_external_calendar_url(body.url),
        source_type=(body.source_type or "holiday").strip() or "holiday",
        enabled=body.enabled,
        created_by=current_user.id,
    )
    db.add(source)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This calendar source already exists")
    clear_external_calendar_cache()
    return ExternalCalendarSourceResponse.model_validate(source)


@router.put("/api/calendar/sources/{source_id}", response_model=ExternalCalendarSourceResponse)
async def api_update_calendar_source(
    source_id: str,
    body: ExternalCalendarSourceUpdate,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = await _get_source_or_404(db, source_id)
    update_data = body.model_dump(exclude_unset=True)
    if "name" in update_data:
        source.name = update_data["name"].strip()
    if "url" in update_data:
        source.url = _validate_external_calendar_url(update_data["url"])
    if "source_type" in update_data:
        source.source_type = (update_data["source_type"] or "holiday").strip() or "holiday"
    if "enabled" in update_data:
        source.enabled = bool(update_data["enabled"])
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This calendar source already exists")
    clear_external_calendar_cache()
    return ExternalCalendarSourceResponse.model_validate(source)


@router.delete("/api/calendar/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_calendar_source(
    source_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = await _get_source_or_404(db, source_id)
    await db.delete(source)
    await db.flush()
    clear_external_calendar_cache()


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    month: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    year, mon = _resolve_year_month(month)
    events = await get_calendar_events(db, current_user, year, mon)
    grid = get_month_grid(year, mon)

    events_by_day: dict[int, list[dict]] = {}
    for event in events:
        events_by_day.setdefault(event["day"], []).append(event)

    if mon == 1:
        prev_month = f"{year - 1:04d}-12"
    else:
        prev_month = f"{year:04d}-{mon - 1:02d}"
    if mon == 12:
        next_month = f"{year + 1:04d}-01"
    else:
        next_month = f"{year:04d}-{mon + 1:02d}"

    locale = _get_locale(request)

    def t(key: str) -> str:
        return translate(key, locale)

    month_name = t(f"calendar.month_{mon}")
    day_headers = [t(key) for key in DAY_HEADER_KEYS]
    rendered_events = _decorate_calendar_events(events, locale)
    external_sources = await list_external_calendar_sources(db) if current_user.is_admin else []
    enabled_external_sources = await list_external_calendar_sources(db, enabled_only=True)
    visible_external_sources = external_sources if current_user.is_admin else enabled_external_sources
    settings = get_settings()

    return templates.TemplateResponse(
        "calendar.html",
        _ctx(
            request,
            current_user,
            active_page="calendar",
            year=year,
            month=mon,
            month_name=month_name,
            grid=grid,
            events=rendered_events,
            events_by_day=events_by_day,
            day_headers=day_headers,
            today_day=date.today().day if date.today().year == year and date.today().month == mon else None,
            today_month=f"{date.today().year:04d}-{date.today().month:02d}",
            prev_month=prev_month,
            next_month=next_month,
            current_month=f"{year:04d}-{mon:02d}",
            external_sources=external_sources,
            enabled_external_sources=enabled_external_sources,
            visible_external_sources=visible_external_sources,
            calendar_feed_groups=_build_feed_groups(current_user, locale),
            holiday_presets=_build_holiday_presets(locale),
            calendar_stats=_build_calendar_stats(rendered_events, locale),
            default_selected_day=_default_selected_day(rendered_events, year, mon),
            sparse_month=len(rendered_events) < 4,
            calendar_feed_token=current_user.calendar_feed_token,
            base_url=settings.BASE_URL.rstrip("/"),
        ),
    )


@router.post("/calendar/sources", response_class=HTMLResponse)
async def create_calendar_source_form(
    name: str = Form(...),
    url: str = Form(...),
    source_type: str = Form("holiday"),
    month: str | None = Form(None),
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = ExternalCalendarSource(
        name=name.strip(),
        url=_validate_external_calendar_url(url),
        source_type=(source_type or "holiday").strip() or "holiday",
        enabled=True,
        created_by=current_user.id,
    )
    db.add(source)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This calendar source already exists")
    clear_external_calendar_cache()
    return _calendar_redirect(month)


@router.post("/calendar/sources/{source_id}/toggle", response_class=HTMLResponse)
async def toggle_calendar_source_form(
    source_id: str,
    month: str | None = Form(None),
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = await _get_source_or_404(db, source_id)
    source.enabled = not source.enabled
    await db.flush()
    clear_external_calendar_cache()
    return _calendar_redirect(month)


@router.post("/calendar/sources/{source_id}/delete", response_class=HTMLResponse)
async def delete_calendar_source_form(
    source_id: str,
    month: str | None = Form(None),
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    source = await _get_source_or_404(db, source_id)
    await db.delete(source)
    await db.flush()
    clear_external_calendar_cache()
    return _calendar_redirect(month)


@router.post("/calendar/feed-token/rotate", response_class=HTMLResponse)
async def rotate_calendar_feed_token(
    month: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    from app.models.base import generate_uuid
    current_user.calendar_feed_token = generate_uuid()
    await db.flush()
    return _calendar_redirect(month)


@router.get("/partials/calendar-grid", response_class=HTMLResponse)
async def partial_calendar_grid(
    request: Request,
    month: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    year, mon = _resolve_year_month(month)
    events = await get_calendar_events(db, current_user, year, mon)
    grid = get_month_grid(year, mon)

    events_by_day: dict[int, list[dict]] = {}
    for event in events:
        events_by_day.setdefault(event["day"], []).append(event)

    if mon == 1:
        prev_month = f"{year - 1:04d}-12"
    else:
        prev_month = f"{year:04d}-{mon - 1:02d}"
    if mon == 12:
        next_month = f"{year + 1:04d}-01"
    else:
        next_month = f"{year:04d}-{mon + 1:02d}"

    locale = _get_locale(request)

    def t(key: str) -> str:
        return translate(key, locale)

    month_name = t(f"calendar.month_{mon}")
    day_headers = [t(key) for key in DAY_HEADER_KEYS]
    rendered_events = _decorate_calendar_events(events, locale)

    return templates.TemplateResponse(
        "partials/calendar_grid.html",
        _ctx(
            request,
            current_user,
            year=year,
            month=mon,
            month_name=month_name,
            grid=grid,
            events=rendered_events,
            events_by_day=events_by_day,
            day_headers=day_headers,
            today_day=date.today().day if date.today().year == year and date.today().month == mon else None,
            today_month=f"{date.today().year:04d}-{date.today().month:02d}",
            prev_month=prev_month,
            next_month=next_month,
            current_month=f"{year:04d}-{mon:02d}",
            default_selected_day=_default_selected_day(rendered_events, year, mon),
        ),
    )
