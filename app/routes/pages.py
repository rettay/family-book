"""
HTML page routes — serves Jinja2 templates for the HTMX frontend.

All data fetching happens server-side. Templates use HTMX for dynamic interactions.
"""

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
from app.i18n import t as translate
from app.models.media import Media
from app.models.moments import Moment, MomentComment
from app.models.person import Person, AccountState, Visibility
from app.models.auth import Invite
from app.models.relationships import ParentChild, Partnership
from app.schemas import PersonSummary

router = APIRouter(tags=["pages"])

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
    """Build common template context."""
    locale = _get_locale(request)
    return {
        "request": request,
        "current_user": current_user,
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "country_flag": _country_flag,
        **kwargs,
    }


async def _build_moment_card_simple(db: AsyncSession, moment: Moment, current_user_id: str) -> dict:
    """Lightweight moment card builder for template rendering."""
    from app.models.moments import MomentReaction

    # Poster
    poster = None
    if moment.posted_by:
        result = await db.execute(select(Person).where(Person.id == moment.posted_by))
        p = result.scalar_one_or_none()
        if p:
            poster = {"id": p.id, "display_name": p.display_name, "photo_url": p.photo_url}

    # About person
    about = None
    result = await db.execute(select(Person).where(Person.id == moment.person_id))
    p = result.scalar_one_or_none()
    if p:
        about = {"id": p.id, "display_name": p.display_name, "photo_url": p.photo_url}

    tagged_people = []
    for tagged_person_id in moment.tagged_person_ids:
        result = await db.execute(select(Person).where(Person.id == tagged_person_id))
        tagged_person = result.scalar_one_or_none()
        if tagged_person:
            tagged_people.append(
                {
                    "id": tagged_person.id,
                    "display_name": tagged_person.display_name,
                    "photo_url": tagged_person.photo_url,
                }
            )

    # Media
    media_list = []
    if moment.media_ids:
        for mid in moment.media_ids:
            result = await db.execute(select(Media).where(Media.id == mid))
            m = result.scalar_one_or_none()
            if m:
                media_list.append({"id": m.id, "url": f"/api/media/{m.id}/file", "width": m.width, "height": m.height})

    # Reactions
    result = await db.execute(
        select(MomentReaction.emoji, func.count(MomentReaction.id))
        .where(MomentReaction.moment_id == moment.id)
        .group_by(MomentReaction.emoji)
    )
    reactions = {row[0]: row[1] for row in result.all()}

    # My reaction
    result = await db.execute(
        select(MomentReaction.emoji).where(
            MomentReaction.moment_id == moment.id,
            MomentReaction.person_id == current_user_id,
        )
    )
    my_reaction = result.scalar_one_or_none()

    # Comment count
    result = await db.execute(
        select(func.count(MomentComment.id)).where(MomentComment.moment_id == moment.id)
    )
    comment_count = result.scalar() or 0

    return {
        "id": moment.id,
        "kind": moment.kind,
        "poster": poster,
        "about": about,
        "tagged_people": tagged_people,
        "title": moment.title,
        "body": moment.body,
        "media": media_list,
        "milestone_type": moment.milestone_type,
        "occurred_at": moment.occurred_at.isoformat() if moment.occurred_at else None,
        "source": moment.source if hasattr(moment, "source") else None,
        "reactions": reactions,
        "my_reaction": my_reaction,
        "comment_count": comment_count,
        "created_at": moment.created_at.isoformat() if moment.created_at else None,
    }


# ─── Landing / Home ───────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    kind: str | None = Query(None),
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        return templates.TemplateResponse("landing.html", _ctx(request))

    accessible_person_ids = await get_accessible_person_ids(db, current_user)

    # Build moments feed
    query = select(Moment).where(Moment.person_id.in_(accessible_person_ids))
    if kind:
        query = query.where(Moment.kind == kind)
    if not current_user.is_admin:
        query = query.where(Moment.visibility == "members")
    query = query.order_by(Moment.occurred_at.desc()).limit(20)
    result = await db.execute(query)
    moments_orm = result.scalars().all()

    moments = []
    for m in moments_orm:
        card = await _build_moment_card_simple(db, m, current_user.id)
        moments.append(card)

    return templates.TemplateResponse("home.html", _ctx(
        request, current_user, active_page="home", moments=moments,
    ))


# ─── Auth Pages ───────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: Person | None = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/", status_code=302)
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
        return RedirectResponse("/", status_code=302)

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


@router.get("/people/{person_id}", response_class=HTMLResponse)
async def person_detail_page(
    person_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
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

    return templates.TemplateResponse("person.html", _ctx(
        request, current_user, active_page="people",
        person=person_view, parents=visible_parents, children=visible_children,
        partners=visible_partners, siblings=visible_siblings, can_edit=can_edit,
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
    if not person:
        return RedirectResponse("/people", status_code=302)
    if not can_manage_person(current_user, person):
        return RedirectResponse("/people", status_code=302)

    return templates.TemplateResponse("person_edit.html", _ctx(
        request, current_user, active_page="people", person=person,
    ))


@router.get("/people/new", response_class=HTMLResponse)
async def new_person_page(
    request: Request,
    current_user: Person = Depends(require_auth),
):
    return templates.TemplateResponse("person_new.html", _ctx(
        request, current_user, active_page="people",
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
    if not person:
        return HTMLResponse("<p>Person not found</p>")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        return HTMLResponse("<p>Person not found</p>")

    return templates.TemplateResponse("partials/person_sidebar.html", _ctx(
        request, current_user, person=redact_person_detail(person, access),
    ))


# ─── Admin ────────────────────────────────────────────────────────

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Stats
    persons_count = (await db.execute(select(func.count(Person.id)))).scalar() or 0
    moments_count = (await db.execute(select(func.count(Moment.id)))).scalar() or 0
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
        select(Person).where(Person.account_state == AccountState.pending.value)
    )
    pending_persons = result.scalars().all()

    people_result = await db.execute(
        select(Person).where(Person.is_root.is_(False)).order_by(Person.last_name, Person.first_name)
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

    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    query = select(Moment).where(Moment.person_id.in_(accessible_person_ids))
    if before:
        result = await db.execute(select(Moment.occurred_at).where(Moment.id == before))
        cursor_time = result.scalar_one_or_none()
        if cursor_time:
            query = query.where(Moment.occurred_at < cursor_time)
    if person:
        if person not in accessible_person_ids:
            return HTMLResponse("")
    if kind:
        query = query.where(Moment.kind == kind)
    if not current_user.is_admin:
        query = query.where(Moment.visibility == "members")
    query = query.order_by(Moment.occurred_at.desc())
    if not person:
        query = query.limit(limit)
    result = await db.execute(query)
    moments_orm = result.scalars().all()
    if person:
        moments_orm = [m for m in moments_orm if m.person_id == person or person in m.tagged_person_ids]
        moments_orm = moments_orm[:limit]

    moments = []
    for m in moments_orm:
        card = await _build_moment_card_simple(db, m, current_user.id)
        moments.append(card)

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
        html_parts.append(
            f'<div hx-get="/partials/moments?before={last_id}" '
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
    if not person:
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
