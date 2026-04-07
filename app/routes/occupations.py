"""Occupation routes — REST JSON API + HTMX partials for occupation history."""

import os
import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.i18n import translate
from app.models.occupation import PersonOccupation
from app.models.person import Person, PersonLifecycleState
from app.services.theme_service import get_runtime_theme_from_app

router = APIRouter(tags=["occupations"])
logger = logging.getLogger(__name__)

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


# ── Helpers ───────────────────────────────────────────────────────────


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


def _t(request: Request, key: str) -> str:
    return translate(key, _get_locale(request))


def _serialize(occ: PersonOccupation) -> dict:
    return {
        "id": occ.id,
        "title": occ.title,
        "employer": occ.employer,
        "start_date": occ.start_date,
        "end_date": occ.end_date,
        "added_by_person_id": occ.added_by_person_id,
    }


async def _get_person_by_slug(slug: str, db: AsyncSession) -> Person:
    result = await db.execute(
        select(Person).where(
            Person.slug == slug,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


async def load_occupations(db: AsyncSession, person_id: str) -> list[dict]:
    """Load occupations for a person. Current roles (end_date IS NULL) first, then start_date desc."""
    result = await db.execute(
        select(PersonOccupation)
        .where(PersonOccupation.person_id == person_id)
        .order_by(
            case((PersonOccupation.end_date.is_(None), 0), else_=1),
            PersonOccupation.start_date.desc(),
        )
    )
    return [_serialize(occ) for occ in result.scalars().all()]


async def _check_conflict(db: AsyncSession, person_id: str, exclude_id: str | None = None) -> bool:
    """Return True if another current role (end_date IS NULL) already exists."""
    q = select(PersonOccupation).where(
        PersonOccupation.person_id == person_id,
        PersonOccupation.end_date.is_(None),
    )
    if exclude_id:
        q = q.where(PersonOccupation.id != exclude_id)
    existing = await db.execute(q)
    return existing.scalar_one_or_none() is not None


async def _do_create(
    db: AsyncSession,
    person_id: str,
    *,
    title: str,
    employer: str,
    start_date: str,
    end_date: str,
    currently_in_role: str,
    added_by_person_id: str,
) -> tuple[PersonOccupation, bool]:
    """Create an occupation record. Returns (occ, conflict)."""
    normalized_end = None if currently_in_role else (end_date.strip() or None)
    conflict = False
    if normalized_end is None:
        conflict = await _check_conflict(db, person_id)
    occ = PersonOccupation(
        person_id=person_id,
        title=title.strip(),
        employer=employer.strip() or None,
        start_date=start_date.strip() or None,
        end_date=normalized_end,
        added_by_person_id=added_by_person_id,
        source=f"user:{added_by_person_id}",
    )
    db.add(occ)
    await db.flush()
    return occ, conflict


async def _do_update(
    db: AsyncSession,
    occ: PersonOccupation,
    *,
    title: str,
    employer: str,
    start_date: str,
    end_date: str,
    currently_in_role: str,
) -> tuple[PersonOccupation, bool]:
    """Update an occupation record. Returns (occ, conflict)."""
    normalized_end = None if currently_in_role else (end_date.strip() or None)
    conflict = False
    if normalized_end is None and occ.end_date is not None:
        conflict = await _check_conflict(db, occ.person_id, exclude_id=occ.id)
    occ.title = title.strip()
    occ.employer = employer.strip() or None
    occ.start_date = start_date.strip() or None
    occ.end_date = normalized_end
    await db.flush()
    return occ, conflict


# ── REST JSON API ─────────────────────────────────────────────────────


@router.get("/api/persons/{person_id}/occupations")
async def list_occupations_api(
    person_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List occupation history for a person (JSON)."""
    return await load_occupations(db, person_id)


@router.post("/api/persons/{person_id}/occupations", status_code=201)
async def create_occupation_api(
    person_id: str,
    title: str = Form(...),
    employer: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    currently_in_role: str = Form(""),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create an occupation record (JSON)."""
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    occ, conflict = await _do_create(
        db, person_id,
        title=title, employer=employer,
        start_date=start_date, end_date=end_date,
        currently_in_role=currently_in_role,
        added_by_person_id=current_user.id,
    )
    data = _serialize(occ)
    if conflict:
        data["conflict"] = True
        data["conflict_message"] = "Another role is already marked as current. Update it with an end date."
    return data


@router.put("/api/persons/{person_id}/occupations/{occ_id}")
async def update_occupation_api(
    person_id: str,
    occ_id: str,
    title: str = Form(...),
    employer: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    currently_in_role: str = Form(""),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update an occupation record (JSON)."""
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person_id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    occ, conflict = await _do_update(
        db, occ,
        title=title, employer=employer,
        start_date=start_date, end_date=end_date,
        currently_in_role=currently_in_role,
    )
    data = _serialize(occ)
    if conflict:
        data["conflict"] = True
        data["conflict_message"] = "Another role is already marked as current. Update it with an end date."
    return data


@router.delete("/api/persons/{person_id}/occupations/{occ_id}", status_code=204)
async def delete_occupation_api(
    person_id: str,
    occ_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete an occupation record — adder or admin only (JSON)."""
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person_id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    if occ.added_by_person_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(occ)
    return Response(status_code=204)


# ── HTMX Wiki Partials ────────────────────────────────────────────────


@router.get("/api/wiki/{slug}/occupations/new-form", response_class=HTMLResponse)
async def occupation_new_form(
    slug: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return the occupation add form partial."""
    person = await _get_person_by_slug(slug, db)
    return templates.TemplateResponse("partials/wiki_occupation_form.html", _ctx(
        request, current_user,
        occ=None,
        edit_mode=False,
        person=person,
        slug=slug,
    ))


@router.post("/api/wiki/{slug}/occupations", response_class=HTMLResponse)
async def create_occupation_htmx(
    slug: str,
    request: Request,
    title: str = Form(...),
    employer: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    currently_in_role: str = Form(""),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create an occupation record and return the card partial."""
    person = await _get_person_by_slug(slug, db)
    occ, conflict = await _do_create(
        db, person.id,
        title=title, employer=employer,
        start_date=start_date, end_date=end_date,
        currently_in_role=currently_in_role,
        added_by_person_id=current_user.id,
    )
    return templates.TemplateResponse("partials/wiki_occupation_card.html", _ctx(
        request, current_user,
        occ=_serialize(occ),
        conflict=conflict,
        person=person,
        slug=slug,
    ))


@router.get("/api/wiki/{slug}/occupations/{occ_id}/edit", response_class=HTMLResponse)
async def occupation_edit_form(
    slug: str,
    occ_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return the occupation edit form partial (prefilled)."""
    person = await _get_person_by_slug(slug, db)
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person.id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    return templates.TemplateResponse("partials/wiki_occupation_form.html", _ctx(
        request, current_user,
        occ=_serialize(occ),
        edit_mode=True,
        person=person,
        slug=slug,
    ))


@router.put("/api/wiki/{slug}/occupations/{occ_id}", response_class=HTMLResponse)
async def update_occupation_htmx(
    slug: str,
    occ_id: str,
    request: Request,
    title: str = Form(...),
    employer: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    currently_in_role: str = Form(""),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update an occupation record and return the updated card partial."""
    person = await _get_person_by_slug(slug, db)
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person.id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    occ, conflict = await _do_update(
        db, occ,
        title=title, employer=employer,
        start_date=start_date, end_date=end_date,
        currently_in_role=currently_in_role,
    )
    return templates.TemplateResponse("partials/wiki_occupation_card.html", _ctx(
        request, current_user,
        occ=_serialize(occ),
        conflict=conflict,
        person=person,
        slug=slug,
    ))


@router.get("/api/wiki/{slug}/occupations/{occ_id}/card", response_class=HTMLResponse)
async def occupation_card(
    slug: str,
    occ_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return the card partial for a single occupation (cancel-edit restore)."""
    person = await _get_person_by_slug(slug, db)
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person.id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    return templates.TemplateResponse("partials/wiki_occupation_card.html", _ctx(
        request, current_user,
        occ=_serialize(occ),
        conflict=False,
        person=person,
        slug=slug,
    ))


@router.get("/api/wiki/{slug}/occupations/{occ_id}/confirm-delete", response_class=HTMLResponse)
async def confirm_delete_occupation(
    slug: str,
    occ_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return inline confirm/cancel buttons for deleting an occupation."""
    person = await _get_person_by_slug(slug, db)
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person.id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    if occ.added_by_person_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    html = f"""
<span id="occupation-{occ_id}-delete-wrap" style="display:inline-flex;gap:.5rem;align-items:center;">
  <span style="font-size:.875rem">{_t(request, 'occupation.delete_confirm')}</span>
  <button class="btn btn--sm btn--danger"
          hx-delete="/api/wiki/{slug}/occupations/{occ_id}"
          hx-target="#occupation-{occ_id}"
          hx-swap="outerHTML swap:300ms">{_t(request, 'occupation.delete_occupation')}</button>
  <button class="btn btn--sm btn--outline"
          hx-get="/api/wiki/{slug}/occupations/{occ_id}/card"
          hx-target="#occupation-{occ_id}-delete-wrap"
          hx-swap="outerHTML">{_t(request, 'occupation.cancel')}</button>
</span>"""
    return HTMLResponse(html)


@router.delete("/api/wiki/{slug}/occupations/{occ_id}")
async def delete_occupation_htmx(
    slug: str,
    occ_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete an occupation record — adder or admin only."""
    person = await _get_person_by_slug(slug, db)
    result = await db.execute(
        select(PersonOccupation).where(
            PersonOccupation.id == occ_id,
            PersonOccupation.person_id == person.id,
        )
    )
    occ = result.scalar_one_or_none()
    if not occ:
        raise HTTPException(status_code=404, detail="Occupation not found")
    if occ.added_by_person_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(occ)
    return Response(status_code=204)
