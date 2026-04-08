"""Timeline routes — API endpoint and HTML page for family timeline."""

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.models.person import Person
from app.services.timeline_service import get_timeline_events
from app.services.theme_service import get_runtime_theme_from_app
from app.i18n import translate

router = APIRouter(tags=["timeline"])
logger = logging.getLogger(__name__)
_EVENT_TYPE_ALIASES = {
    "": None,
    "all": None,
    "birth": "birth",
    "births": "birth",
    "death": "death",
    "deaths": "death",
    "marriage": "marriage",
    "marriages": "marriage",
}

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


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


async def _resolve_lineage_ids(
    db: AsyncSession,
    lineage_person_id: str | None,
    current_user: Person,
) -> set[str] | None:
    if not lineage_person_id:
        return None
    from app.access_control import get_accessible_person_ids
    accessible = await get_accessible_person_ids(db, current_user)
    if lineage_person_id not in accessible:
        return set()  # inaccessible person → empty result (no events match)
    from app.services.relationship_calculator import get_lineage
    return await get_lineage(db, lineage_person_id)


def _normalize_event_type(raw_event_type: str | None) -> tuple[str | None, str | None]:
    value = (raw_event_type or "").strip().lower()
    if value in _EVENT_TYPE_ALIASES:
        return _EVENT_TYPE_ALIASES[value], None
    return None, f"Unsupported timeline event type: {raw_event_type}"


def _parse_optional_year(raw_year: str | int | None, label: str) -> tuple[int | None, str | None]:
    if raw_year is None or raw_year == "":
        return None, None
    try:
        return int(raw_year), None
    except (TypeError, ValueError):
        return None, f"{label} must be a valid year."


def _normalize_timeline_filters(
    event_type: str | None,
    year_from: str | int | None,
    year_to: str | int | None,
) -> tuple[str | None, int | None, int | None, str | None]:
    normalized_event_type, event_type_error = _normalize_event_type(event_type)
    parsed_year_from, year_from_error = _parse_optional_year(year_from, "From year")
    parsed_year_to, year_to_error = _parse_optional_year(year_to, "To year")
    error = event_type_error or year_from_error or year_to_error
    if parsed_year_from is not None and parsed_year_to is not None and parsed_year_from > parsed_year_to:
        error = "From year must be earlier than to year."
    return normalized_event_type, parsed_year_from, parsed_year_to, error


# ── API ──────────────────────────────────────────────────────────────


class TimelineEvent(BaseModel):
    date: str
    year: int
    type: str
    label: str
    person_id: str | None
    person_name: str
    detail: str


class TimelineResponse(BaseModel):
    events: list[TimelineEvent]
    total: int


@router.get("/api/timeline", response_model=TimelineResponse)
async def api_timeline(
    event_type: str | None = Query(None),
    year_from: str | None = Query(None),
    year_to: str | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    event_type, year_from, year_to, error = _normalize_timeline_filters(event_type, year_from, year_to)
    if error:
        raise HTTPException(status_code=400, detail=error)
    lineage_ids = await _resolve_lineage_ids(db, lineage_person_id, current_user)
    events, total = await get_timeline_events(
        db, current_user,
        event_type=event_type,
        year_from=year_from,
        year_to=year_to,
        branch=branch,
        lineage_person_ids=lineage_ids,
        limit=limit,
        offset=offset,
    )
    return TimelineResponse(
        events=[TimelineEvent(**e) for e in events],
        total=total,
    )


# ── HTML Page ────────────────────────────────────────────────────────


@router.get("/timeline", response_class=HTMLResponse)
async def timeline_page(
    request: Request,
    event_type: str | None = Query(None),
    year_from: str | None = Query(None),
    year_to: str | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    raw_event_type = event_type or ""
    raw_year_from = year_from or ""
    raw_year_to = year_to or ""
    event_type, year_from, year_to, error = _normalize_timeline_filters(event_type, year_from, year_to)
    events = []
    if not error:
        lineage_ids = await _resolve_lineage_ids(db, lineage_person_id, current_user)
        events, _total = await get_timeline_events(
            db, current_user,
            event_type=event_type,
            year_from=year_from,
            year_to=year_to,
            branch=branch,
            lineage_person_ids=lineage_ids,
        )

    # Group events by year for display
    years_seen: list[int] = []
    for ev in events:
        if ev["year"] not in years_seen:
            years_seen.append(ev["year"])

    return templates.TemplateResponse("timeline.html", _ctx(
        request,
        current_user,
        active_page="timeline",
        events=events,
        years=years_seen,
        event_type=event_type or raw_event_type,
        year_from=year_from if year_from is not None else raw_year_from,
        year_to=year_to if year_to is not None else raw_year_to,
        branch=branch or "",
        lineage_person_id=lineage_person_id or "",
        error=error,
    ))


@router.get("/partials/timeline-events", response_class=HTMLResponse)
async def partial_timeline_events(
    request: Request,
    event_type: str | None = Query(None),
    year_from: str | None = Query(None),
    year_to: str | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    event_type, year_from, year_to, error = _normalize_timeline_filters(event_type, year_from, year_to)
    events = []
    if not error:
        lineage_ids = await _resolve_lineage_ids(db, lineage_person_id, current_user)
        events, _total = await get_timeline_events(
            db, current_user,
            event_type=event_type,
            year_from=year_from,
            year_to=year_to,
            branch=branch,
            lineage_person_ids=lineage_ids,
        )

    years_seen: list[int] = []
    for ev in events:
        if ev["year"] not in years_seen:
            years_seen.append(ev["year"])

    return templates.TemplateResponse("partials/timeline_events.html", _ctx(
        request,
        current_user,
        events=events,
        years=years_seen,
        error=error,
    ))
