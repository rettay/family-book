"""Wiki routes — index page and person wiki pages."""

import json
import logging
import os
import re

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Form
from app.auth import require_auth
from app.database import get_db
from app.models.person import Person, PersonLifecycleState, Visibility
from app.access_control import get_person_access, can_manage_person
from app.services.wiki_service import assemble_wiki_sections
from app.services.revision_service import serialize_person_snapshot, record_revision
from app.services.sanitization import RICH_TEXT_FIELDS as _RICH_TEXT_FIELDS, sanitize_html
from app.services.media_queries import can_upload_media_for_person, list_media_for_person
from app.services.theme_service import get_runtime_theme_from_app
from pydantic import ValidationError
from app.schemas import EducationEntry, CareerEntry, OrganizationEntry
from app.i18n import translate

router = APIRouter(tags=["wiki"])
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


# ── Wiki Index ────────────────────────────────────────────────────────


@router.get("/wiki", response_class=HTMLResponse)
async def wiki_index(
    request: Request,
    search: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Render wiki index page with alphabetical person list."""
    query = select(Person).where(
        Person.lifecycle_state == PersonLifecycleState.active.value,
    )
    if not current_user.is_admin:
        query = query.where(Person.visibility != Visibility.hidden.value)

    result = await db.execute(query.order_by(Person.first_name, Person.last_name))
    persons = result.scalars().all()

    if search:
        search_lower = search.lower()
        persons = [
            p for p in persons
            if search_lower in (p.first_name or "").lower()
            or search_lower in (p.last_name or "").lower()
            or search_lower in p.display_name.lower()
        ]

    return templates.TemplateResponse("wiki_index.html", _ctx(
        request,
        current_user,
        active_page="wiki",
        persons=persons,
        search=search or "",
    ))


# ── Person Wiki Page ──────────────────────────────────────────────────


@router.get("/wiki/{slug}", response_class=HTMLResponse)
async def wiki_person(
    request: Request,
    slug: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Render Wikipedia-style person page."""
    result = await db.execute(
        select(Person).where(
            Person.slug == slug,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        raise HTTPException(status_code=403, detail="Not visible")

    sections = await assemble_wiki_sections(db, person, current_user)
    can_edit = access.can_manage
    _, media_list = await list_media_for_person(db, current_user, person.id)

    return templates.TemplateResponse("wiki_person.html", _ctx(
        request,
        current_user,
        active_page="wiki",
        person=person,
        sections=sections,
        can_edit=can_edit,
        media_list=media_list,
        person_id=person.id,
        can_upload=can_upload_media_for_person(current_user, person),
        person_photo_url=person.photo_url,
    ))


# ── API ───────────────────────────────────────────────────────────────


@router.get("/api/wiki/{slug}")
async def wiki_person_api(
    slug: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """JSON API for wiki page data (section assembly)."""
    result = await db.execute(
        select(Person).where(
            Person.slug == slug,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        raise HTTPException(status_code=403, detail="Not visible")

    sections = await assemble_wiki_sections(db, person, current_user)
    return {
        "person_id": person.id,
        "slug": person.slug,
        "display_name": person.display_name,
        "sections": sections,
    }


# ── Section Editing ──────────────────────────────────────────────────

# Map section IDs to person fields
SECTION_FIELD_MAP = {
    "summary": ["bio"],
    "early-life": ["birth_place", "birth_country_code", "birth_date_raw", "birth_last_name"],
    "education": ["education"],
    "career": ["career"],
    "personal-life": ["residence_place", "residence_country_code"],
    "organizations": ["organizations"],
    "physical-description": ["height", "weight", "eye_color", "hair_color", "blood_type"],
    "death-legacy": ["death_date_raw", "burial_place", "burial_cemetery_name",
                      "burial_country_code", "burial_plot_number", "obituary", "obituary_source"],
    "sources": ["source_detail", "confidence"],
    "research-notes": ["research_notes"],
}

# JSON array fields that need special handling
_JSON_ARRAY_FIELDS = {"education", "career", "organizations"}

# Pydantic models for validation of array entries
_ARRAY_ENTRY_MODELS = {
    "education": EducationEntry,
    "career": CareerEntry,
    "organizations": OrganizationEntry,
}


def _parse_indexed_form_fields(form, field_name: str) -> list[dict] | None:
    """Parse indexed form fields like education[0].institution into a list of dicts.

    Returns None if no matching keys found (allows fallback to raw JSON).
    """
    pattern = re.compile(rf"^{re.escape(field_name)}\[(\d+)\]\.(\w+)$")
    entries: dict[int, dict] = {}
    found = False
    for key in form:
        m = pattern.match(key)
        if m:
            found = True
            idx = int(m.group(1))
            subfield = m.group(2)
            value = form[key].strip() if form[key] else ""
            if idx not in entries:
                entries[idx] = {}
            if value:
                entries[idx][subfield] = value
    if not found:
        return None
    # Return entries sorted by index, filtering out empty entries
    return [entries[i] for i in sorted(entries.keys()) if entries[i]]


def _validate_array_entries(field_name: str, entries: list[dict]) -> list[dict]:
    """Validate and whitelist array entries through Pydantic models.

    Raises HTTPException(422) if validation fails (e.g. max_length exceeded).
    """
    model_cls = _ARRAY_ENTRY_MODELS.get(field_name)
    if not model_cls:
        return entries
    validated = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        try:
            obj = model_cls.model_validate(entry)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        validated.append(obj.model_dump(exclude_none=True))
    return validated


async def _get_person_for_edit(slug: str, current_user: Person, db: AsyncSession) -> Person:
    """Load person by slug and verify edit permissions."""
    result = await db.execute(
        select(Person).where(
            Person.slug == slug,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized")
    return person


@router.get("/wiki/{slug}/edit/{section}", response_class=HTMLResponse)
async def wiki_edit_section(
    request: Request,
    slug: str,
    section: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return HTMX partial with edit form for a wiki section."""
    person = await _get_person_for_edit(slug, current_user, db)
    fields = SECTION_FIELD_MAP.get(section, [])
    if not fields:
        raise HTTPException(status_code=404, detail="Unknown section")

    return templates.TemplateResponse("partials/wiki_edit_section.html", _ctx(
        request,
        current_user,
        person=person,
        section=section,
        fields=fields,
    ))


@router.post("/wiki/{slug}/edit/{section}", response_class=HTMLResponse)
async def wiki_save_section(
    request: Request,
    slug: str,
    section: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save section edits back to person structured fields."""
    person = await _get_person_for_edit(slug, current_user, db)
    fields = SECTION_FIELD_MAP.get(section, [])
    if not fields:
        raise HTTPException(status_code=404, detail="Unknown section")

    old_snapshot = serialize_person_snapshot(person)
    form = await request.form()

    for field in fields:
        if field in _JSON_ARRAY_FIELDS:
            # Parse structured form fields: fieldname[idx].key = value
            parsed = _parse_indexed_form_fields(form, field)
            if parsed is not None:
                validated = _validate_array_entries(field, parsed)
                setattr(person, field, validated)
            elif field in form:
                # Fallback: try raw JSON (backward compat)
                value = form[field].strip() if form[field] else None
                try:
                    value = json.loads(value) if value else []
                except json.JSONDecodeError:
                    value = getattr(person, field, [])
                if isinstance(value, list):
                    value = _validate_array_entries(field, value)
                setattr(person, field, value)
            else:
                # No indexed fields and no raw JSON — user removed all entries
                setattr(person, field, [])
        elif field in form:
            value = form[field].strip() if form[field] else None
            if field in _RICH_TEXT_FIELDS and value:
                setattr(person, field, sanitize_html(value))
            else:
                setattr(person, field, value if value else None)

    await db.flush()
    await record_revision(
        db,
        entity_type="person",
        entity_id=person.id,
        actor_id=current_user.id,
        action="update",
        snapshot=serialize_person_snapshot(person),
    )

    # Re-render the wiki page (redirect back)
    sections = await assemble_wiki_sections(db, person, current_user)
    can_edit = True  # Already verified above

    return templates.TemplateResponse("wiki_person.html", _ctx(
        request,
        current_user,
        active_page="wiki",
        person=person,
        sections=sections,
        can_edit=can_edit,
    ))
