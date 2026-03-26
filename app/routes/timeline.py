"""Timeline routes — API endpoint and HTML page for family timeline."""

import logging
import os

from fastapi import APIRouter, Depends, Query, Request
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


async def _resolve_lineage_ids(db: AsyncSession, lineage_person_id: str | None) -> set[str] | None:
    if not lineage_person_id:
        return None
    from app.services.relationship_calculator import get_lineage
    return await get_lineage(db, lineage_person_id)


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
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    lineage_ids = await _resolve_lineage_ids(db, lineage_person_id)
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
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    lineage_ids = await _resolve_lineage_ids(db, lineage_person_id)
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
        event_type=event_type or "",
        year_from=year_from or "",
        year_to=year_to or "",
        branch=branch or "",
        lineage_person_id=lineage_person_id or "",
    ))


@router.get("/partials/timeline-events", response_class=HTMLResponse)
async def partial_timeline_events(
    request: Request,
    event_type: str | None = Query(None),
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    branch: str | None = Query(None),
    lineage_person_id: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    lineage_ids = await _resolve_lineage_ids(db, lineage_person_id)
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
    ))
