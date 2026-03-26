"""Research page — top-level entry point for genealogy record search."""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_manage_person
from app.auth import require_auth
from app.database import get_db
from app.i18n import translate
from app.models.person import Person
from app.models.saved_record import SavedRecord
from app.models.base import generate_uuid
from app.services.research_service import get_available_sources
from app.services.theme_service import get_runtime_theme_from_app

router = APIRouter(tags=["research"])
logger = logging.getLogger(__name__)

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


def _ctx(request: Request, current_user: Person | None = None, **kwargs):
    locale = request.cookies.get("locale", "en")
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


# ── HTML Page ─────────────────────────────────────────────────────────


@router.get("/research", response_class=HTMLResponse)
async def research_index(
    request: Request,
    person_id: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Research index page showing available sources and search entry point."""
    sources = get_available_sources()
    person_context = None
    prefill_query = ""

    if person_id:
        result = await db.execute(
            select(Person).where(
                Person.id == person_id, Person.lifecycle_state == "active"
            )
        )
        person_context = result.scalar_one_or_none()
        if person_context and not person_context.is_root:
            parts = []
            if person_context.first_name:
                parts.append(person_context.first_name)
            if person_context.last_name:
                parts.append(person_context.last_name)
            prefill_query = " ".join(parts)

    return templates.TemplateResponse(
        "research.html",
        _ctx(
            request,
            current_user,
            sources=sources,
            person_context=person_context,
            prefill_query=prefill_query,
            active_page="research",
        ),
    )


# ── Saved Records API ────────────────────────────────────────────────


class SaveRecordRequest(BaseModel):
    person_id: str
    title: str = Field(max_length=500)
    url: str | None = Field(None, max_length=2000)
    source: str = Field(max_length=100)
    snippet: str | None = None


@router.post("/api/research/saved-records")
async def save_record(
    body: SaveRecordRequest,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save an external record to a person."""
    result = await db.execute(
        select(Person).where(
            Person.id == body.person_id, Person.lifecycle_state == "active"
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Access denied")

    record = SavedRecord(
        id=generate_uuid(),
        person_id=body.person_id,
        title=body.title,
        url=body.url,
        source=body.source,
        snippet=body.snippet,
        saved_by=current_user.id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "person_id": record.person_id,
        "title": record.title,
        "url": record.url,
        "source": record.source,
        "snippet": record.snippet,
        "saved_by": record.saved_by,
        "created_at": str(record.created_at),
    }


@router.get("/api/research/saved-records/{person_id}")
async def list_saved_records(
    person_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List saved records for a person."""
    result = await db.execute(
        select(Person).where(
            Person.id == person_id, Person.lifecycle_state == "active"
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    records_result = await db.execute(
        select(SavedRecord)
        .where(SavedRecord.person_id == person_id)
        .order_by(SavedRecord.created_at.desc())
    )
    records = records_result.scalars().all()

    return {
        "records": [
            {
                "id": r.id,
                "person_id": r.person_id,
                "title": r.title,
                "url": r.url,
                "source": r.source,
                "snippet": r.snippet,
                "saved_by": r.saved_by,
                "created_at": str(r.created_at),
            }
            for r in records
        ]
    }


@router.delete("/api/research/saved-records/{record_id}")
async def delete_saved_record(
    record_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved record."""
    result = await db.execute(
        select(SavedRecord).where(SavedRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Saved record not found")

    # Check access to the person this record belongs to
    person_result = await db.execute(
        select(Person).where(Person.id == record.person_id)
    )
    person = person_result.scalar_one_or_none()
    if person and not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Access denied")

    await db.delete(record)
    await db.commit()

    return {"deleted": True}
