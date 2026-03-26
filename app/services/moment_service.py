from collections import defaultdict
from urllib.parse import urlencode

from sqlalchemy import and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_view_media, get_accessible_person_ids
from app.models.media import Media
from app.models.moments import Moment, MomentComment, MomentLifecycleState, MomentReaction
from app.models.person import Person, PersonLifecycleState


def _moment_order(query):
    return query.order_by(
        Moment.occurred_at.desc(),
        Moment.created_at.desc(),
        Moment.id.desc(),
    )


def _tagged_person_match(person_id: str):
    return Moment._tagged_person_ids.like(f'%"{person_id}"%')


async def list_visible_moments(
    db: AsyncSession,
    current_user: Person,
    *,
    before: str | None = None,
    limit: int = 20,
    person_id: str | None = None,
    branch: str | None = None,
    kind: str | None = None,
    tagged_only: bool = False,
    year: int | None = None,
) -> list[Moment]:
    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    query = select(Moment).where(Moment.person_id.in_(accessible_person_ids))
    if current_user.is_admin:
        query = query.where(
            Moment.lifecycle_state.in_(
                [
                    MomentLifecycleState.active.value,
                    MomentLifecycleState.moderated.value,
                ]
            )
        )
    else:
        query = query.where(Moment.lifecycle_state == MomentLifecycleState.active.value)

    if person_id:
        if person_id not in accessible_person_ids:
            return []
        query = query.where(
            or_(Moment.person_id == person_id, _tagged_person_match(person_id))
        )

    if before:
        cursor = await db.get(Moment, before)
        if cursor:
            query = query.where(
                or_(
                    Moment.occurred_at < cursor.occurred_at,
                    and_(
                        Moment.occurred_at == cursor.occurred_at,
                        Moment.created_at < cursor.created_at,
                    ),
                    and_(
                        Moment.occurred_at == cursor.occurred_at,
                        Moment.created_at == cursor.created_at,
                        Moment.id < cursor.id,
                    ),
                )
            )

    if branch:
        query = query.join(Person, Moment.person_id == Person.id).where(
            Person.branch == branch
        )

    if kind:
        query = query.where(Moment.kind == kind)

    if tagged_only:
        query = query.where(Moment._tagged_person_ids != "[]")

    if year:
        query = query.where(extract("year", Moment.occurred_at) == year)

    if not current_user.is_admin:
        query = query.where(Moment.visibility == "members")

    result = await db.execute(_moment_order(query).limit(limit))
    return list(result.scalars().all())


async def build_moment_cards(
    db: AsyncSession,
    moments: list[Moment],
    current_user: Person,
) -> list[dict]:
    if not moments:
        return []

    person_ids = {
        person_id
        for moment in moments
        for person_id in [moment.posted_by, moment.person_id, *moment.tagged_person_ids]
        if person_id
    }
    persons_by_id: dict[str, Person] = {}
    if person_ids:
        person_result = await db.execute(
            select(Person).where(
                Person.id.in_(person_ids),
                Person.lifecycle_state == PersonLifecycleState.active.value,
            )
        )
        persons_by_id = {person.id: person for person in person_result.scalars().all()}

    media_ids = {
        media_id
        for moment in moments
        for media_id in moment.media_ids
        if media_id
    }
    media_by_id: dict[str, Media] = {}
    if media_ids:
        media_result = await db.execute(select(Media).where(Media.id.in_(media_ids)))
        media_by_id = {media.id: media for media in media_result.scalars().all()}

    moment_ids = [moment.id for moment in moments]

    reactions_by_moment: dict[str, dict[str, int]] = defaultdict(dict)
    reaction_rows = await db.execute(
        select(
            MomentReaction.moment_id,
            MomentReaction.emoji,
            func.count(MomentReaction.id),
        )
        .where(MomentReaction.moment_id.in_(moment_ids))
        .group_by(MomentReaction.moment_id, MomentReaction.emoji)
    )
    for moment_id, emoji, count in reaction_rows.all():
        reactions_by_moment[moment_id][emoji] = count

    my_reactions: dict[str, str] = {}
    my_reaction_rows = await db.execute(
        select(MomentReaction.moment_id, MomentReaction.emoji).where(
            MomentReaction.moment_id.in_(moment_ids),
            MomentReaction.person_id == current_user.id,
        )
    )
    for moment_id, emoji in my_reaction_rows.all():
        my_reactions[moment_id] = emoji

    comment_counts: dict[str, int] = defaultdict(int)
    comment_rows = await db.execute(
        select(MomentComment.moment_id, func.count(MomentComment.id))
        .where(MomentComment.moment_id.in_(moment_ids))
        .group_by(MomentComment.moment_id)
    )
    for moment_id, count in comment_rows.all():
        comment_counts[moment_id] = count

    def person_brief(person: Person | None) -> dict | None:
        if not person:
            return None
        return {
            "id": person.id,
            "display_name": person.display_name,
            "photo_url": person.photo_url,
        }

    cards: list[dict] = []
    for moment in moments:
        media_list: list[dict] = []
        for media_id in moment.media_ids:
            media = media_by_id.get(media_id)
            if not media or not await can_view_media(db, current_user, media):
                continue
            media_list.append(
                {
                    "id": media.id,
                    "url": f"/api/media/{media.id}/file",
                    "width": media.width,
                    "height": media.height,
                    "media_type": media.media_type,
                    "mime_type": media.mime_type,
                    "caption": media.caption,
                }
            )

        cards.append(
            {
                "id": moment.id,
                "kind": moment.kind,
                "poster": person_brief(persons_by_id.get(moment.posted_by)),
                "about": person_brief(persons_by_id.get(moment.person_id)),
                "tagged_people": [
                    person_brief(persons_by_id[tagged_person_id])
                    for tagged_person_id in moment.tagged_person_ids
                    if tagged_person_id in persons_by_id
                ],
                "title": moment.title,
                "body": moment.body,
                "media": media_list,
                "milestone_type": moment.milestone_type,
                "occurred_at": moment.occurred_at.isoformat() if moment.occurred_at else None,
                "source": moment.source,
                "lifecycle_state": moment.lifecycle_state,
                "moderation_reason": moment.moderation_reason,
                "reactions": reactions_by_moment.get(moment.id, {}),
                "my_reaction": my_reactions.get(moment.id),
                "comment_count": comment_counts.get(moment.id, 0),
                "created_at": moment.created_at.isoformat() if moment.created_at else None,
            }
        )

    return cards


async def build_moment_card(
    db: AsyncSession, moment: Moment, current_user: Person
) -> dict:
    cards = await build_moment_cards(db, [moment], current_user)
    return cards[0]


def build_moments_path(
    base_path: str,
    *,
    before: str | None = None,
    person_id: str | None = None,
    kind: str | None = None,
    limit: int | None = None,
) -> str:
    params: dict[str, str | int] = {}
    if before:
        params["before"] = before
    if person_id:
        params["person"] = person_id
    if kind:
        params["kind"] = kind
    if limit:
        params["limit"] = limit
    if not params:
        return base_path
    return f"{base_path}?{urlencode(params)}"
