"""Calendar routes — API endpoint and HTML page for family calendar."""

import logging
import os
from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.models.person import Person
from app.services.calendar_service import get_calendar_events, get_month_grid
from app.services.theme_service import get_runtime_theme_from_app
from app.i18n import translate

router = APIRouter(tags=["calendar"])
logger = logging.getLogger(__name__)

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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


# ── API ──────────────────────────────────────────────────────────────


class CalendarEvent(BaseModel):
    date: str
    day: int
    type: str
    label: str
    person_id: str | None
    year_only: bool = False


class CalendarResponse(BaseModel):
    year: int
    month: int
    month_name: str
    events: list[CalendarEvent]


@router.get("/api/calendar", response_model=CalendarResponse)
async def api_calendar(
    month: str | None = Query(None, description="YYYY-MM format"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    if month:
        parts = month.split("-")
        try:
            year, mon = int(parts[0]), int(parts[1])
            if mon < 1 or mon > 12:
                raise ValueError
        except (ValueError, IndexError):
            year, mon = today.year, today.month
    else:
        year, mon = today.year, today.month

    events = await get_calendar_events(db, current_user, year, mon)
    return CalendarResponse(
        year=year,
        month=mon,
        month_name=MONTH_NAMES[mon],
        events=[CalendarEvent(**e) for e in events],
    )


# ── HTML Page ────────────────────────────────────────────────────────


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    month: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    if month:
        parts = month.split("-")
        try:
            year, mon = int(parts[0]), int(parts[1])
            if mon < 1 or mon > 12:
                raise ValueError
        except (ValueError, IndexError):
            year, mon = today.year, today.month
    else:
        year, mon = today.year, today.month

    events = await get_calendar_events(db, current_user, year, mon)
    grid = get_month_grid(year, mon)

    # Build events-by-day lookup
    events_by_day: dict[int, list[dict]] = {}
    for ev in events:
        events_by_day.setdefault(ev["day"], []).append(ev)

    # Prev/next month
    if mon == 1:
        prev_month = f"{year - 1:04d}-12"
    else:
        prev_month = f"{year:04d}-{mon - 1:02d}"
    if mon == 12:
        next_month = f"{year + 1:04d}-01"
    else:
        next_month = f"{year:04d}-{mon + 1:02d}"

    return templates.TemplateResponse("calendar.html", _ctx(
        request,
        current_user,
        active_page="calendar",
        year=year,
        month=mon,
        month_name=MONTH_NAMES[mon],
        grid=grid,
        events=events,
        events_by_day=events_by_day,
        day_headers=DAY_HEADERS,
        today_day=today.day if today.year == year and today.month == mon else None,
        prev_month=prev_month,
        next_month=next_month,
        current_month=f"{year:04d}-{mon:02d}",
    ))


@router.get("/partials/calendar-grid", response_class=HTMLResponse)
async def partial_calendar_grid(
    request: Request,
    month: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: return just the calendar grid for month navigation."""
    today = date.today()
    parts = month.split("-")
    try:
        year, mon = int(parts[0]), int(parts[1])
        if mon < 1 or mon > 12:
            raise ValueError
    except (ValueError, IndexError):
        year, mon = today.year, today.month

    events = await get_calendar_events(db, current_user, year, mon)
    grid = get_month_grid(year, mon)

    events_by_day: dict[int, list[dict]] = {}
    for ev in events:
        events_by_day.setdefault(ev["day"], []).append(ev)

    if mon == 1:
        prev_month = f"{year - 1:04d}-12"
    else:
        prev_month = f"{year:04d}-{mon - 1:02d}"
    if mon == 12:
        next_month = f"{year + 1:04d}-01"
    else:
        next_month = f"{year:04d}-{mon + 1:02d}"

    return templates.TemplateResponse("partials/calendar_grid.html", _ctx(
        request,
        current_user,
        year=year,
        month=mon,
        month_name=MONTH_NAMES[mon],
        grid=grid,
        events=events,
        events_by_day=events_by_day,
        day_headers=DAY_HEADERS,
        today_day=today.day if today.year == year and today.month == mon else None,
        prev_month=prev_month,
        next_month=next_month,
        current_month=f"{year:04d}-{mon:02d}",
    ))
