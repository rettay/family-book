from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import (
    can_create_moment_for_person,
    can_manage_moment,
    can_view_media,
    can_view_moment,
    get_person_access,
)
from app.auth import require_auth
from app.database import get_db
from app.models.media import Media
from app.models.moments import Moment, MomentComment, MomentReaction, MomentVisibility
from app.models.person import Person
from app.services.moment_service import (
    build_moment_card,
    build_moment_cards,
    list_visible_moments,
)

router = APIRouter(prefix="/api/moments", tags=["moments"])


# --- Schemas ---

class MomentCreate(BaseModel):
    kind: str
    person_id: str | None = None
    tagged_person_ids: list[str] = []
    body: str | None = Field(None, max_length=5000)
    title: str | None = Field(None, max_length=300)
    media_ids: list[str] = []
    milestone_type: str | None = None
    occurred_at: datetime | None = None
    visibility: str = "members"


class MomentUpdate(BaseModel):
    body: str | None = Field(None, max_length=5000)
    title: str | None = Field(None, max_length=300)
    person_id: str | None = None
    tagged_person_ids: list[str] | None = None
    media_ids: list[str] | None = None
    milestone_type: str | None = None
    occurred_at: datetime | None = None
    visibility: str | None = None


class PersonBrief(BaseModel):
    id: str
    display_name: str
    photo_url: str | None


class MediaBrief(BaseModel):
    id: str
    url: str
    width: int | None
    height: int | None
    media_type: str | None = None
    caption: str | None = None


class MomentCard(BaseModel):
    id: str
    kind: str
    poster: PersonBrief | None
    about: PersonBrief | None
    tagged_people: list[PersonBrief]
    title: str | None
    body: str | None
    media: list[MediaBrief]
    milestone_type: str | None
    occurred_at: str
    source: str | None = None
    reactions: dict[str, int]
    my_reaction: str | None
    comment_count: int
    created_at: str


class CommentCreate(BaseModel):
    body: str = Field(max_length=2000)


class CommentResponse(BaseModel):
    id: str
    moment_id: str
    person_id: str
    person_name: str
    body: str
    created_at: str


class ReactionCreate(BaseModel):
    emoji: str = Field(max_length=10)


ALLOWED_MOMENT_VISIBILITIES = {
    MomentVisibility.members.value,
    MomentVisibility.admins.value,
    MomentVisibility.hidden.value,
}


def _has_moment_content(
    *,
    title: str | None,
    body: str | None,
    media_ids: list[str],
    milestone_type: str | None,
) -> bool:
    return any(
        [
            title and title.strip(),
            body and body.strip(),
            media_ids,
            milestone_type,
        ]
    )


async def _validate_person(
    db: AsyncSession,
    current_user: Person,
    person_id: str,
    *,
    require_manage: bool,
) -> Person:
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=400, detail="Person not found")

    if require_manage:
        if not can_create_moment_for_person(current_user, person):
            raise HTTPException(
                status_code=403, detail="Not authorized to post for this profile"
            )
    else:
        access = await get_person_access(db, current_user, person)
        if not access.can_view:
            raise HTTPException(
                status_code=403, detail="Not authorized to tag this person"
            )

    return person


async def _approved_media_ids(
    db: AsyncSession, current_user: Person, media_ids: list[str]
) -> list[str]:
    approved_media_ids: list[str] = []
    for media_id in media_ids:
        media_result = await db.execute(select(Media).where(Media.id == media_id))
        media = media_result.scalar_one_or_none()
        if not media:
            continue
        if not await can_view_media(db, current_user, media):
            raise HTTPException(
                status_code=403, detail="Not authorized to attach this media"
            )
        approved_media_ids.append(media.id)
    return approved_media_ids


async def _approved_tagged_person_ids(
    db: AsyncSession, current_user: Person, tagged_person_ids: list[str]
) -> list[str]:
    approved_ids: list[str] = []
    for tagged_person_id in tagged_person_ids:
        person = await _validate_person(
            db,
            current_user,
            tagged_person_id,
            require_manage=False,
        )
        approved_ids.append(person.id)
    return approved_ids


def _validated_visibility(value: str | None) -> str:
    visibility = value or MomentVisibility.members.value
    if visibility not in ALLOWED_MOMENT_VISIBILITIES:
        raise HTTPException(status_code=400, detail="Invalid visibility")
    return visibility


# --- Routes ---

@router.get("")
async def list_moments(
    before: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    person: str | None = Query(None),
    branch: str | None = Query(None),
    kind: str | None = Query(None),
    year: int | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List moments feed, reverse-chronological, paginated."""
    if person:
        person_result = await db.execute(select(Person).where(Person.id == person))
        target_person = person_result.scalar_one_or_none()
        if target_person:
            access = await get_person_access(db, current_user, target_person)
            if not access.can_view:
                raise HTTPException(status_code=403, detail="Not visible")

    moments = await list_visible_moments(
        db,
        current_user,
        before=before,
        limit=limit,
        person_id=person,
        branch=branch,
        kind=kind,
        year=year,
    )
    return await build_moment_cards(db, moments, current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_moment(
    body: MomentCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a new moment."""
    person_id = body.person_id or current_user.id

    await _validate_person(db, current_user, person_id, require_manage=True)
    visibility = _validated_visibility(body.visibility)
    if visibility == MomentVisibility.admins.value and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin visibility is restricted")
    if visibility == MomentVisibility.hidden.value and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Hidden visibility is restricted")
    approved_media_ids = await _approved_media_ids(db, current_user, body.media_ids)
    approved_tagged_person_ids = await _approved_tagged_person_ids(
        db, current_user, body.tagged_person_ids
    )
    if not _has_moment_content(
        title=body.title,
        body=body.body,
        media_ids=approved_media_ids,
        milestone_type=body.milestone_type,
    ):
        raise HTTPException(status_code=400, detail="Moment content is required")

    moment = Moment(
        person_id=person_id,
        kind=body.kind,
        title=body.title,
        body=body.body,
        milestone_type=body.milestone_type,
        occurred_at=body.occurred_at or datetime.now(timezone.utc),
        visibility=visibility,
        posted_by=current_user.id,
    )
    moment.media_ids = approved_media_ids
    moment.tagged_person_ids = approved_tagged_person_ids

    db.add(moment)
    await db.flush()

    return await build_moment_card(db, moment, current_user)


@router.get("/{moment_id}")
async def get_moment(
    moment_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a single moment detail."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    if not await can_view_moment(db, current_user, moment):
        raise HTTPException(status_code=403, detail="Not visible")

    return await build_moment_card(db, moment, current_user)


@router.put("/{moment_id}")
async def update_moment(
    moment_id: str,
    body: MomentUpdate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a moment (author only, or admin)."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")

    if not can_manage_moment(current_user, moment):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = body.model_dump(exclude_unset=True)
    if "visibility" in update_data:
        update_data["visibility"] = _validated_visibility(update_data["visibility"])
        if (
            update_data["visibility"] in {MomentVisibility.hidden.value, MomentVisibility.admins.value}
            and not current_user.is_admin
        ):
            raise HTTPException(status_code=403, detail="Restricted visibility")
    if "person_id" in update_data and update_data["person_id"]:
        await _validate_person(
            db, current_user, update_data["person_id"], require_manage=True
        )
    if "tagged_person_ids" in update_data and update_data["tagged_person_ids"] is not None:
        moment.tagged_person_ids = await _approved_tagged_person_ids(
            db, current_user, update_data.pop("tagged_person_ids")
        )
    if "media_ids" in update_data and update_data["media_ids"] is not None:
        moment.media_ids = await _approved_media_ids(
            db, current_user, update_data.pop("media_ids")
        )
    for field, value in update_data.items():
        setattr(moment, field, value)
    if not _has_moment_content(
        title=moment.title,
        body=moment.body,
        media_ids=moment.media_ids,
        milestone_type=moment.milestone_type,
    ):
        raise HTTPException(status_code=400, detail="Moment content is required")

    await db.flush()
    return await build_moment_card(db, moment, current_user)


@router.delete("/{moment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_moment(
    moment_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a moment (admin or poster only)."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")

    if not can_manage_moment(current_user, moment):
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(moment)
    await db.flush()


# --- Comments ---

@router.get("/{moment_id}/comments")
async def list_comments(
    moment_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List comments on a moment."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    if not await can_view_moment(db, current_user, moment):
        raise HTTPException(status_code=403, detail="Not visible")

    result = await db.execute(
        select(MomentComment)
        .where(MomentComment.moment_id == moment_id)
        .order_by(MomentComment.created_at.asc())
        .limit(limit)
    )
    comments = result.scalars().all()

    response = []
    for c in comments:
        person_result = await db.execute(select(Person).where(Person.id == c.person_id))
        person = person_result.scalar_one_or_none()
        response.append({
            "id": c.id,
            "moment_id": c.moment_id,
            "person_id": c.person_id,
            "person_name": person.display_name if person else "Unknown",
            "body": c.body,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return response


@router.post("/{moment_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    moment_id: str,
    body: CommentCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to a moment."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    if not await can_view_moment(db, current_user, moment):
        raise HTTPException(status_code=403, detail="Not visible")

    comment = MomentComment(
        moment_id=moment_id,
        person_id=current_user.id,
        body=body.body,
    )
    db.add(comment)
    await db.flush()

    return {
        "id": comment.id,
        "moment_id": comment.moment_id,
        "person_id": comment.person_id,
        "person_name": current_user.display_name,
        "body": comment.body,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment (admin or author only)."""
    result = await db.execute(
        select(MomentComment).where(MomentComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    moment_result = await db.execute(select(Moment).where(Moment.id == comment.moment_id))
    moment = moment_result.scalar_one_or_none()
    if moment and not await can_view_moment(db, current_user, moment) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not visible")

    if comment.person_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(comment)
    await db.flush()


# --- Reactions ---

@router.post("/{moment_id}/reactions")
async def add_reaction(
    moment_id: str,
    body: ReactionCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add or replace a reaction on a moment. One per person."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    if not await can_view_moment(db, current_user, moment):
        raise HTTPException(status_code=403, detail="Not visible")

    # Check for existing reaction
    result = await db.execute(
        select(MomentReaction).where(
            MomentReaction.moment_id == moment_id,
            MomentReaction.person_id == current_user.id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.emoji = body.emoji
        await db.flush()
    else:
        reaction = MomentReaction(
            moment_id=moment_id,
            person_id=current_user.id,
            emoji=body.emoji,
        )
        db.add(reaction)
        await db.flush()

    # Return aggregated count for this emoji
    result = await db.execute(
        select(func.count(MomentReaction.id)).where(
            MomentReaction.moment_id == moment_id,
            MomentReaction.emoji == body.emoji,
        )
    )
    count = result.scalar()

    return {"emoji": body.emoji, "count": count}


@router.delete("/{moment_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    moment_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove the current user's reaction from a moment."""
    result = await db.execute(select(Moment).where(Moment.id == moment_id))
    moment = result.scalar_one_or_none()
    if not moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    if not await can_view_moment(db, current_user, moment):
        raise HTTPException(status_code=403, detail="Not visible")

    result = await db.execute(
        select(MomentReaction).where(
            MomentReaction.moment_id == moment_id,
            MomentReaction.person_id == current_user.id,
        )
    )
    reaction = result.scalar_one_or_none()
    if not reaction:
        raise HTTPException(status_code=404, detail="No reaction to remove")

    await db.delete(reaction)
    await db.flush()
