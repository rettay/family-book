"""
Demo mode routes — parallel read-only view of seed data, no auth required.

These routes mirror the real app routes but skip authentication entirely.
Templates receive `demo_mode=True` to show the demo banner and hide edit controls.
"""

import os

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.i18n import translate
from app.models.media import Media
from app.models.person import Person, Visibility
from app.models.relationships import ParentChild, Partnership
from app.schemas import (
    ParentChildResponse,
    PartnershipResponse,
    TreeResponse,
    person_to_summary,
)

router = APIRouter(prefix="/demo", tags=["demo"])

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


# ─── Helpers ───────────────────────────────────────────────────────

def _get_locale(request: Request) -> str:
    return request.cookies.get("locale", "en")


def _country_flag(code: str | None) -> str:
    if not code or len(code) != 2:
        return ""
    offset = 127397
    return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)


def _ctx(request: Request, **kwargs):
    """Build template context for demo mode — no current_user, demo_mode=True."""
    locale = _get_locale(request)
    return {
        "request": request,
        "current_user": None,
        "demo_mode": True,
        "url_prefix": "/demo",
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "country_flag": _country_flag,
        **kwargs,
    }


# ─── Demo Landing (redirects to tree) ─────────────────────────────

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def demo_home(request: Request):
    """Demo home — redirects to demo tree."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/demo/tree", status_code=302)


# ─── Demo Tree ────────────────────────────────────────────────────

@router.get("/tree", response_class=HTMLResponse)
async def demo_tree(request: Request):
    return templates.TemplateResponse("tree.html", _ctx(
        request, active_page="tree",
    ))


# ─── Demo Tree API (JSON endpoint for D3) ─────────────────────────

@router.get("/api/tree", response_model=TreeResponse)
async def demo_tree_api(
    db: AsyncSession = Depends(get_db),
):
    """Tree data for demo mode — same shape as /api/tree but no auth."""
    result = await db.execute(select(Person).where(Person.is_root == True))
    root = result.scalar_one_or_none()
    root_id = root.id if root else ""

    result = await db.execute(
        select(Person).where(Person.visibility != Visibility.hidden.value)
    )
    persons = result.scalars().all()
    visible_ids = {p.id for p in persons}

    result = await db.execute(select(ParentChild))
    parent_children = [
        r for r in result.scalars().all()
        if r.parent_id in visible_ids and r.child_id in visible_ids
    ]

    result = await db.execute(select(Partnership))
    partnerships = [
        r for r in result.scalars().all()
        if r.person_a_id in visible_ids and r.person_b_id in visible_ids
    ]

    return TreeResponse(
        root_id=root_id,
        persons=[person_to_summary(p) for p in persons],
        parent_child=[ParentChildResponse.model_validate(pc) for pc in parent_children],
        partnerships=[PartnershipResponse.model_validate(p) for p in partnerships],
    )


# ─── Demo Person Card (sidebar for tree) ──────────────────────────

@router.get("/people/{person_id}/card", response_class=HTMLResponse)
async def demo_person_card(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        return HTMLResponse("<p>Person not found</p>")

    return templates.TemplateResponse("partials/person_sidebar.html", _ctx(
        request, person=person,
    ))


# ─── Demo Partials ────────────────────────────────────────────────

@router.get("/partials/media-gallery", response_class=HTMLResponse)
async def demo_partial_media_gallery(
    request: Request,
    person_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Media).where(Media.person_id == person_id).order_by(Media.created_at.desc())
    )
    media_list = result.scalars().all()

    return templates.TemplateResponse("partials/media_gallery.html", _ctx(
        request, media_list=media_list,
        can_upload=False, person_id=person_id,
    ))


