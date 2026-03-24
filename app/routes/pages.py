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
    can_view_moment,
    get_accessible_person_ids,
    get_person_access,
    redact_person_detail,
    redact_person_summary,
)
from app.auth import get_current_user, require_admin, require_auth
from app.database import get_db
from app.i18n import translate
from app.models.media import Media
from app.models.moments import Moment, MomentComment, MomentLifecycleState
from app.models.person import Person, AccountState, PersonLifecycleState, Visibility
from app.models.revisions import EntityRevision
from app.models.auth import Invite
from app.models.relationships import ParentChild, Partnership
from app.schemas import PersonSummary
from app.backup.service import get_backup_health
from app.services.moment_service import (
    build_moment_cards,
    build_moments_path,
    list_visible_moments,
)
from app.services.revision_service import list_revisions
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
    return {
        "request": request,
        "current_user": current_user,
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "country_flag": _country_flag,
        "app_theme": app_theme,
        "brand_display_name": app_theme["brand_display_name"],
        "brand_tagline": app_theme["brand_tagline"],
        **kwargs,
    }


async def _moment_people(
    db: AsyncSession, current_user: Person
) -> list[PersonSummary]:
    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    result = await db.execute(
        select(Person)
        .where(
            Person.visibility != Visibility.hidden.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
            Person.id.in_(accessible_person_ids),
        )
        .order_by(Person.last_name, Person.first_name)
    )

    people: list[PersonSummary] = []
    for person in result.scalars().all():
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            people.append(redact_person_summary(person, access))
    return people


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


@router.get("/moments", response_class=HTMLResponse)
async def moments_page(
    request: Request,
    kind: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    moments_orm = await list_visible_moments(
        db, current_user, kind=kind, limit=20
    )
    moments = await build_moment_cards(db, moments_orm, current_user)
    moment_people = await _moment_people(db, current_user)

    return templates.TemplateResponse("home.html", _ctx(
        request,
        current_user,
        active_page="home",
        moments=moments,
        moment_people=moment_people,
        moment_filter=kind,
        load_more_url=build_moments_path(
            "/partials/moments",
            before=moments[-1]["id"] if moments else None,
            kind=kind,
            limit=20,
        ),
    ))


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
        request, current_user, active_page="map",
    ))


# ─── People ───────────────────────────────────────────────────────

@router.get("/people", response_class=HTMLResponse)
async def people_page(
    request: Request,
    branch: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    branch_filter = branch
    query = select(Person).where(
        Person.visibility != Visibility.hidden.value,
        Person.lifecycle_state == PersonLifecycleState.active.value,
        Person.id.in_(accessible_person_ids),
    )
    if branch_filter:
        query = query.where(Person.branch == branch_filter)
    query = query.order_by(Person.last_name, Person.first_name)
    result = await db.execute(query)
    persons = result.scalars().all()

    branch_result = await db.execute(
        select(Person.branch)
        .where(Person.branch.isnot(None), Person.id.in_(accessible_person_ids))
        .distinct()
    )
    branches = sorted([row[0] for row in branch_result.all() if row[0]])

    summaries: list[PersonSummary] = []
    for person in persons:
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            summaries.append(redact_person_summary(person, access))

    return templates.TemplateResponse("people.html", _ctx(
        request, current_user, active_page="people",
        persons=summaries,
        branches=branches, branch_filter=branch_filter,
    ))


@router.get("/people/new", response_class=HTMLResponse)
async def new_person_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("person_new.html", _ctx(
        request, current_user, active_page="people",
    ))


@router.get("/people/{person_id}", response_class=HTMLResponse)
async def person_detail_page(
    person_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        return RedirectResponse("/people", status_code=302)
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        return RedirectResponse("/people", status_code=302)

    # Parents
    result = await db.execute(
        select(Person).join(ParentChild, ParentChild.parent_id == Person.id)
        .where(ParentChild.child_id == person_id)
    )
    parent_people = result.scalars().all()

    # Children
    result = await db.execute(
        select(Person).join(ParentChild, ParentChild.child_id == Person.id)
        .where(ParentChild.parent_id == person_id)
    )
    child_people = result.scalars().all()

    # Partners
    result = await db.execute(
        select(Partnership).where(
            (Partnership.person_a_id == person_id) | (Partnership.person_b_id == person_id)
        )
    )
    partnerships = result.scalars().all()
    partner_ids = set()
    for p in partnerships:
        pid = p.person_b_id if p.person_a_id == person_id else p.person_a_id
        partner_ids.add(pid)
    partners = []
    for pid in partner_ids:
        result = await db.execute(select(Person).where(Person.id == pid))
        partner = result.scalar_one_or_none()
        if partner:
            partners.append(partner)

    # Siblings (share a parent)
    parent_ids = [p.id for p in parent_people]
    siblings = []
    if parent_ids:
        result = await db.execute(
            select(Person).join(ParentChild, ParentChild.child_id == Person.id)
            .where(ParentChild.parent_id.in_(parent_ids), Person.id != person_id)
        )
        siblings = list({s.id: s for s in result.scalars().all()}.values())

    can_edit = can_manage_person(current_user, person)
    visible_parents = []
    for parent in parent_people:
        parent_access = await get_person_access(db, current_user, parent)
        if parent_access.can_view:
            visible_parents.append(redact_person_summary(parent, parent_access))

    visible_children = []
    for child in child_people:
        child_access = await get_person_access(db, current_user, child)
        if child_access.can_view:
            visible_children.append(redact_person_summary(child, child_access))

    visible_partners = []
    for partner in partners:
        partner_access = await get_person_access(db, current_user, partner)
        if partner_access.can_view:
            visible_partners.append(redact_person_summary(partner, partner_access))

    visible_siblings = []
    for sibling in siblings:
        sibling_access = await get_person_access(db, current_user, sibling)
        if sibling_access.can_view:
            visible_siblings.append(redact_person_summary(sibling, sibling_access))
    person_view = redact_person_detail(person, access)
    moment_people = await _moment_people(db, current_user)

    return templates.TemplateResponse("person.html", _ctx(
        request, current_user, active_page="people",
        person=person_view, parents=visible_parents, children=visible_children,
        partners=visible_partners, siblings=visible_siblings, can_edit=can_edit,
        moment_people=moment_people,
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
        return RedirectResponse("/people", status_code=302)
    if not can_manage_person(current_user, person):
        return RedirectResponse("/people", status_code=302)

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

    moment_count_query = select(func.count(Moment.id)).where(
        Moment.person_id == person.id,
        Moment.lifecycle_state == MomentLifecycleState.active.value,
    )
    story_count_query = select(func.count(Moment.id)).where(
        Moment.person_id == person.id,
        Moment.lifecycle_state == MomentLifecycleState.active.value,
        Moment.kind == "story",
    )
    if not current_user.is_admin:
        moment_count_query = moment_count_query.where(Moment.visibility == "members")
        story_count_query = story_count_query.where(Moment.visibility == "members")
    media_count_query = select(func.count(Media.id)).where(Media.person_id == person.id)

    parent_result = await db.execute(
        select(Person).join(ParentChild, ParentChild.parent_id == Person.id).where(ParentChild.child_id == person_id)
    )
    child_result = await db.execute(
        select(Person).join(ParentChild, ParentChild.child_id == Person.id).where(ParentChild.parent_id == person_id)
    )
    partnership_result = await db.execute(
        select(Partnership).where(
            (Partnership.person_a_id == person_id) | (Partnership.person_b_id == person_id)
        )
    )

    parent_people = parent_result.scalars().all()
    child_people = child_result.scalars().all()
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
        "moment_count": (await db.execute(moment_count_query)).scalar() or 0,
        "story_count": (await db.execute(story_count_query)).scalar() or 0,
        "media_count": (await db.execute(media_count_query)).scalar() or 0,
    }

    visible_parents = []
    for parent in parent_people:
        parent_access = await get_person_access(db, current_user, parent)
        if parent_access.can_view:
            visible_parents.append(redact_person_summary(parent, parent_access))

    visible_children = []
    for child in child_people:
        child_access = await get_person_access(db, current_user, child)
        if child_access.can_view:
            visible_children.append(redact_person_summary(child, child_access))

    visible_partners = []
    for partner in partner_people:
        partner_access = await get_person_access(db, current_user, partner)
        if partner_access.can_view:
            visible_partners.append(redact_person_summary(partner, partner_access))

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
    moments_count = (
        await db.execute(
            select(func.count(Moment.id)).where(Moment.lifecycle_state != "deleted")
        )
    ).scalar() or 0
    media_count = (await db.execute(select(func.count(Media.id)))).scalar() or 0
    pending_count = (await db.execute(
        select(func.count(Person.id)).where(Person.account_state == AccountState.pending.value)
    )).scalar() or 0

    stats = {
        "persons": persons_count,
        "moments": moments_count,
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

@router.get("/partials/moments", response_class=HTMLResponse)
async def partial_moments(
    request: Request,
    before: str | None = Query(None),
    person: str | None = Query(None),
    kind: str | None = Query(None),
    limit: int = Query(20),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: render moment cards for infinite scroll."""
    if person:
        person_result = await db.execute(select(Person).where(Person.id == person))
        target_person = person_result.scalar_one_or_none()
        if not target_person:
            return HTMLResponse("")
        access = await get_person_access(db, current_user, target_person)
        if not access.can_view:
            return HTMLResponse("")

    moments_orm = await list_visible_moments(
        db,
        current_user,
        before=before,
        person_id=person,
        kind=kind,
        limit=limit,
    )
    moments = await build_moment_cards(db, moments_orm, current_user)

    # Build HTML from moment cards
    html_parts = []
    for m in moments:
        html_parts.append(
            templates.get_template("partials/moment_card.html").render(
                _ctx(request, current_user, m=m)
            )
        )

    # Add next load-more trigger if we got a full page
    if len(moments) >= limit:
        last_id = moments[-1]["id"]
        load_more_url = build_moments_path(
            "/partials/moments",
            before=last_id,
            person_id=person,
            kind=kind,
            limit=limit,
        )
        html_parts.append(
            f'<div hx-get="{load_more_url}" '
            f'hx-trigger="revealed" hx-swap="afterend">'
            f'<div style="text-align:center;padding:20px;">'
            f'<div class="spinner" style="margin:0 auto;"></div></div></div>'
        )

    return HTMLResponse("".join(html_parts))


@router.get("/partials/people-grid", response_class=HTMLResponse)
async def partial_people_grid(
    request: Request,
    search: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: people grid for live search."""
    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    query = select(Person).where(
        Person.visibility != Visibility.hidden.value,
        Person.lifecycle_state == PersonLifecycleState.active.value,
        Person.id.in_(accessible_person_ids),
    )
    if search:
        like = f"%{search}%"
        query = query.where(
            (Person.first_name.ilike(like))
            | (Person.last_name.ilike(like))
            | (Person.nickname.ilike(like))
        )
    query = query.order_by(Person.last_name, Person.first_name)
    result = await db.execute(query)
    persons = result.scalars().all()

    summaries: list[PersonSummary] = []
    for person in persons:
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            summaries.append(redact_person_summary(person, access))

    return templates.TemplateResponse("partials/people_grid.html", _ctx(
        request, current_user, persons=summaries,
    ))


@router.get("/partials/media-gallery", response_class=HTMLResponse)
async def partial_media_gallery(
    request: Request,
    person_id: str = Query(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: media gallery for person page."""
    person_result = await db.execute(select(Person).where(Person.id == person_id))
    person = person_result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        return HTMLResponse("")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        return HTMLResponse("")

    result = await db.execute(
        select(Media).order_by(Media.created_at.desc())
    )
    media_list = []
    for media in result.scalars().all():
        if media.person_id != person_id and person_id not in media.tagged_person_ids:
            continue
        if not await can_view_media(db, current_user, media):
            continue
        media_list.append(media)
    can_upload = can_manage_person(current_user, person)

    return templates.TemplateResponse("partials/media_gallery.html", _ctx(
        request, current_user, media_list=media_list,
        can_upload=can_upload, person_id=person_id,
    ))


@router.get("/partials/comments/{moment_id}", response_class=HTMLResponse)
async def partial_comments(
    moment_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """HTMX partial: comment thread for a moment."""
    moment_result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = moment_result.scalar_one_or_none()
    if not moment or not await can_view_moment(db, current_user, moment):
        return HTMLResponse("")

    result = await db.execute(
        select(MomentComment)
        .where(MomentComment.moment_id == moment_id)
        .order_by(MomentComment.created_at.asc())
        .limit(50)
    )
    comments_orm = result.scalars().all()

    comments = []
    for c in comments_orm:
        person_result = await db.execute(select(Person).where(Person.id == c.person_id))
        person = person_result.scalar_one_or_none()
        comments.append({
            "id": c.id,
            "person_name": person.display_name if person else "Unknown",
            "body": c.body,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return templates.TemplateResponse("partials/comments.html", _ctx(
        request, current_user, comments=comments, moment_id=moment_id,
    ))


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
