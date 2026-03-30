"""
HTML page routes — serves Jinja2 templates for the HTMX frontend.

All data fetching happens server-side. Templates use HTMX for dynamic interactions.
"""

import logging
import os

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import (
    can_manage_person,
    can_view_media,
    get_accessible_person_ids,
    get_person_access,
    redact_person_detail,
    redact_person_summary,
)
from app.auth import get_current_user, require_admin, require_auth
from app.database import get_db
from app.i18n import translate
from app.models.media import Media
from app.models.person import Person, AccountState, PersonLifecycleState
from app.models.revisions import EntityRevision
from app.models.auth import Invite
from app.models.relationships import ParentChild, Partnership
from app.backup.service import get_backup_health
from app.services.revision_service import list_revisions
from app.services.media_queries import (
    can_upload_media_for_person,
    list_gallery_media,
    list_gallery_people,
    list_media_for_person,
    serialize_media_item,
)
from app.services.theme_service import get_runtime_theme_from_app

router = APIRouter(tags=["pages"])
logger = logging.getLogger(__name__)

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


def _ctx(request: Request, current_user: Person | None = None, **kwargs):
    """Build common template context shared by the page-rendering routes."""
    locale = _get_locale(request)
    app_theme = get_runtime_theme_from_app(request.app)
    from app.config import get_settings

    settings = get_settings()
    return {
        "request": request,
        "current_user": current_user,
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "country_flag": _country_flag,
        "app_theme": app_theme,
        "brand_display_name": app_theme["brand_display_name"],
        "brand_tagline": app_theme["brand_tagline"],
        "google_maps_enabled": settings.google_maps_enabled,
        "google_places_enabled": settings.google_places_enabled,
        "google_maps_browser_api_key": settings.google_maps_browser_api_key_value,
        "google_maps_map_id": settings.google_maps_map_id_value,
        **kwargs,
    }


async def _actor_names(
    db: AsyncSession,
    revisions: list[EntityRevision],
) -> dict[str, str]:
    actor_ids = {revision.actor_id for revision in revisions if revision.actor_id}
    if not actor_ids:
        return {}
    result = await db.execute(select(Person).where(Person.id.in_(actor_ids)))
    return {actor.id: actor.display_name for actor in result.scalars().all()}


# ─── Landing / Home ───────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    kind: str | None = Query(None),
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        logger.debug("Anonymous landing page rendered")
        return templates.TemplateResponse("landing.html", _ctx(request))

    return RedirectResponse("/tree", status_code=302)


# ─── Auth Pages ───────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: Person | None = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/tree", status_code=302)
    from app.config import get_settings
    settings = get_settings()
    return templates.TemplateResponse("login.html", _ctx(
        request, google_client_id=settings.GOOGLE_CLIENT_ID,
    ))


@router.get("/invite/{token}", response_class=HTMLResponse)
async def invite_page(
    token: str,
    request: Request,
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user:
        return RedirectResponse("/tree", status_code=302)

    from app.services.auth_service import get_valid_invite

    invite = await get_valid_invite(db, token)
    if not invite:
        return templates.TemplateResponse("invite.html", _ctx(
            request, error="This invite is invalid, expired, or already claimed.", token=token
        ))

    person = await db.get(Person, invite.person_id)
    if not person:
        return templates.TemplateResponse("invite.html", _ctx(
            request, error="This invite no longer points to a valid family member.", token=token
        ))

    return templates.TemplateResponse("invite.html", _ctx(
        request,
        person_name=person.display_name,
        branch=person.branch,
        token=token,
        error=None,
    ))


# ─── Tree ─────────────────────────────────────────────────────────

@router.get("/tree", response_class=HTMLResponse)
async def tree_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("tree.html", _ctx(
        request, current_user, active_page="tree",
    ))


@router.get("/map", response_class=HTMLResponse)
async def map_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("map.html", _ctx(
        request,
        current_user,
        active_page="map",
    ))


@router.get("/gallery", response_class=HTMLResponse)
async def gallery_page(
    request: Request,
    media_type: str | None = Query(None),
    person_id: str | None = Query(None),
    uploader_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    gallery_people = await list_gallery_people(db, current_user)
    gallery_page_result = await list_gallery_media(
        db,
        current_user,
        media_type=media_type,
        person_id=person_id,
        uploader_id=uploader_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
    )
    media_items = [await serialize_media_item(db, media) for media in gallery_page_result.items]
    return templates.TemplateResponse(
        "gallery.html",
        _ctx(
            request,
            current_user,
            active_page="gallery",
            media_list=media_items,
            gallery_page=gallery_page_result,
            render_load_more_oob=False,
            gallery_people=gallery_people,
            gallery_filters={
                "media_type": media_type or "",
                "person_id": person_id or "",
                "uploader_id": uploader_id or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
            },
        ),
    )


# ─── People ───────────────────────────────────────────────────────

@router.get("/people/new", response_class=HTMLResponse)
async def new_person_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("person_new.html", _ctx(
        request, current_user, active_page="people",
    ))


@router.get("/people/{person_id}/edit", response_class=HTMLResponse)
async def person_edit_page(
    person_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        return RedirectResponse("/tree", status_code=302)
    if not can_manage_person(current_user, person):
        return RedirectResponse("/tree", status_code=302)

    return templates.TemplateResponse("person_edit.html", _ctx(
        request, current_user, active_page="people", person=person,
    ))


@router.get("/people/{person_id}/card", response_class=HTMLResponse)
async def person_card(
    person_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Person card fragment for tree sidebar."""
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        return HTMLResponse("<p>Person not found</p>")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        return HTMLResponse("<p>Person not found</p>")

    media_count_query = select(func.count(Media.id)).where(Media.person_id == person.id)

    parent_result = await db.execute(
        select(ParentChild, Person)
        .join(Person, ParentChild.parent_id == Person.id)
        .where(ParentChild.child_id == person_id)
    )
    child_result = await db.execute(
        select(ParentChild, Person)
        .join(Person, ParentChild.child_id == Person.id)
        .where(ParentChild.parent_id == person_id)
    )
    partnership_result = await db.execute(
        select(Partnership).where(
            (Partnership.person_a_id == person_id) | (Partnership.person_b_id == person_id)
        )
    )

    parent_rows = parent_result.all()
    child_rows = child_result.all()
    partnership_rows = partnership_result.scalars().all()
    partner_ids = {
        rel.person_b_id if rel.person_a_id == person_id else rel.person_a_id
        for rel in partnership_rows
    }
    partner_people: list[Person] = []
    if partner_ids:
        partners_result = await db.execute(select(Person).where(Person.id.in_(partner_ids)))
        partner_people = partners_result.scalars().all()

    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    option_result = await db.execute(
        select(Person)
        .where(
            Person.id.in_(accessible_person_ids),
            Person.id != person_id,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    people_options = [
        redact_person_summary(option, await get_person_access(db, current_user, option))
        for option in option_result.scalars().all()
    ]

    metrics = {
        "media_count": (await db.execute(media_count_query)).scalar() or 0,
    }

    visible_parents = []
    for relationship, parent in parent_rows:
        parent_access = await get_person_access(db, current_user, parent)
        if parent_access.can_view:
            summary = redact_person_summary(parent, parent_access)
            visible_parents.append(
                {
                    **summary.model_dump(),
                    "relationship_id": relationship.id,
                    "relationship_kind": relationship.kind,
                    "relationship_confidence": relationship.confidence,
                    "relationship_source": relationship.source,
                    "relationship_source_detail": relationship.source_detail,
                    "relationship_notes": relationship.notes,
                    "relationship_start_date": relationship.start_date,
                    "relationship_end_date": relationship.end_date,
                }
            )

    visible_children = []
    for relationship, child in child_rows:
        child_access = await get_person_access(db, current_user, child)
        if child_access.can_view:
            summary = redact_person_summary(child, child_access)
            visible_children.append(
                {
                    **summary.model_dump(),
                    "relationship_id": relationship.id,
                    "relationship_kind": relationship.kind,
                    "relationship_confidence": relationship.confidence,
                    "relationship_source": relationship.source,
                    "relationship_source_detail": relationship.source_detail,
                    "relationship_notes": relationship.notes,
                    "relationship_start_date": relationship.start_date,
                    "relationship_end_date": relationship.end_date,
                }
            )

    visible_partners = []
    partnerships_by_partner_id = {
        (
            rel.person_b_id if rel.person_a_id == person_id else rel.person_a_id
        ): rel
        for rel in partnership_rows
    }
    for partner in partner_people:
        partner_access = await get_person_access(db, current_user, partner)
        if partner_access.can_view:
            summary = redact_person_summary(partner, partner_access)
            relationship = partnerships_by_partner_id.get(partner.id)
            visible_partners.append(
                {
                    **summary.model_dump(),
                    "relationship_id": relationship.id if relationship else None,
                    "relationship_kind": relationship.kind if relationship else None,
                    "relationship_status": relationship.status if relationship else None,
                    "relationship_start_date": relationship.start_date if relationship else None,
                    "relationship_start_date_precision": relationship.start_date_precision if relationship else None,
                    "relationship_end_date": relationship.end_date if relationship else None,
                    "relationship_end_date_precision": relationship.end_date_precision if relationship else None,
                    "relationship_source": relationship.source if relationship else None,
                    "relationship_notes": relationship.notes if relationship else None,
                }
            )

    return templates.TemplateResponse("partials/person_sidebar.html", _ctx(
        request,
        current_user,
        person=redact_person_detail(person, access),
        person_metrics=metrics,
        can_manage=can_manage_person(current_user, person),
        parent_people=visible_parents,
        child_people=visible_children,
        partner_people=visible_partners,
        people_options=people_options,
    ))


# ─── Admin ────────────────────────────────────────────────────────

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.config import get_settings

    logger.debug("Admin dashboard requested by %s", current_user.id)
    settings = get_settings()
    # Stats
    persons_count = (
        await db.execute(
            select(func.count(Person.id)).where(
                Person.lifecycle_state == PersonLifecycleState.active.value
            )
        )
    ).scalar() or 0
    media_count = (await db.execute(select(func.count(Media.id)))).scalar() or 0
    pending_count = (await db.execute(
        select(func.count(Person.id)).where(Person.account_state == AccountState.pending.value)
    )).scalar() or 0

    stats = {
        "persons": persons_count,
        "media": media_count,
        "pending": pending_count,
    }

    # Pending persons
    result = await db.execute(
        select(Person).where(
            Person.account_state == AccountState.pending.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    pending_persons = result.scalars().all()

    people_result = await db.execute(
        select(Person)
        .where(
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    managed_people = people_result.scalars().all()

    invite_result = await db.execute(select(Invite).order_by(Invite.created_at.desc()).limit(20))
    invites = invite_result.scalars().all()

    invite_people: dict[str, Person] = {}
    for invite in invites:
        person = await db.get(Person, invite.person_id)
        if person:
            invite_people[invite.id] = person

    return templates.TemplateResponse("admin.html", _ctx(
        request, current_user, active_page="admin",
        stats=stats, pending_persons=pending_persons,
        managed_people=managed_people,
        invites=invites,
        invite_people=invite_people,
        backup_health=get_backup_health(),
        resend_enabled=settings.resend_enabled,
        staging_review_url=settings.STAGING_REVIEW_URL.strip() or None,
    ))


@router.get("/admin/people/new", response_class=HTMLResponse)
async def admin_new_person_page(
    request: Request,
    current_user: Person = Depends(require_admin),
):
    return templates.TemplateResponse("person_new.html", _ctx(
        request, current_user, active_page="admin",
    ))


# ─── Settings ─────────────────────────────────────────────────────

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("settings.html", _ctx(
        request, current_user, active_page="settings",
    ))


# ─── HTMX Partials ───────────────────────────────────────────────

@router.get("/partials/media-gallery", response_class=HTMLResponse)
async def partial_media_gallery(
    request: Request,
    person_id: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: media gallery for person page."""
    person, media_list = await list_media_for_person(db, current_user, person_id)
    if not person:
        return HTMLResponse("")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        return HTMLResponse("")
    can_upload = can_upload_media_for_person(current_user, person)

    return templates.TemplateResponse("partials/media_gallery.html", _ctx(
        request, current_user, media_list=media_list,
        can_upload=can_upload, person_id=person_id,
        person_photo_url=person.photo_url,
    ))


@router.get("/partials/global-gallery", response_class=HTMLResponse)
async def partial_global_gallery(
    request: Request,
    media_type: str | None = Query(None),
    person_id: str | None = Query(None),
    uploader_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    gallery_page_result = await list_gallery_media(
        db,
        current_user,
        media_type=media_type,
        person_id=person_id,
        uploader_id=uploader_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
    )
    media_items = [await serialize_media_item(db, media) for media in gallery_page_result.items]
    return templates.TemplateResponse(
        "partials/global_gallery_items.html",
        _ctx(
            request,
            current_user,
            media_list=media_items,
            gallery_page=gallery_page_result,
            render_load_more_oob=True,
            gallery_filters={
                "media_type": media_type or "",
                "person_id": person_id or "",
                "uploader_id": uploader_id or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
            },
        ),
    )


@router.get("/partials/audit-log", response_class=HTMLResponse)
async def partial_audit_log(
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: recent audit log entries."""
    from app.models.audit import AuditLog

    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(50)
    )
    entries_orm = result.scalars().all()

    entries = []
    for e in entries_orm:
        entries.append({
            "action": e.action,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "new_value": e.new_value,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        })

    return templates.TemplateResponse("partials/audit_log.html", _ctx(
        request, current_user, entries=entries,
    ))


@router.get("/partials/person-history", response_class=HTMLResponse)
async def partial_person_history(
    request: Request,
    person_id: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        return HTMLResponse("")

    if person.lifecycle_state == PersonLifecycleState.deleted.value:
        if not current_user.is_admin:
            return HTMLResponse("")
    else:
        access = await get_person_access(db, current_user, person)
        if not access.can_view:
            return HTMLResponse("")

    revisions = await list_revisions(db, entity_type="person", entity_id=person_id, limit=12)
    actor_names = await _actor_names(db, revisions)
    entries = []
    for revision in revisions:
        snapshot = revision.snapshot
        entries.append(
            {
                "id": revision.id,
                "action": revision.action,
                "actor_name": actor_names.get(revision.actor_id or "", "Unknown"),
                "created_at": revision.created_at.isoformat() if revision.created_at else None,
                "display_name": f"{snapshot.get('first_name', '')} {snapshot.get('last_name', '')}".strip(),
                "bio": snapshot.get("bio"),
                "lifecycle_state": snapshot.get("lifecycle_state"),
            }
        )

    return templates.TemplateResponse(
        "partials/person_history.html",
        _ctx(
            request,
            current_user,
            entries=entries,
            person_id=person_id,
            can_revert=current_user.is_admin,
        ),
    )
