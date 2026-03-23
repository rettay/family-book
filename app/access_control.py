from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.media import Media
from app.models.moments import Moment
from app.models.person import AccountState, Person, Visibility
from app.models.relationships import ParentChild, Partnership
from app.schemas import PersonDetail, PersonSummary


@dataclass(frozen=True)
class PersonAccess:
    can_view: bool
    can_view_profile: bool
    can_view_contacts: bool
    can_manage: bool
    distance: int | None = None


def can_collaborate(current_user: Person | None) -> bool:
    return current_user is not None and current_user.account_state == AccountState.active.value


async def get_person_access(
    db: AsyncSession,
    current_user: Person,
    person: Person,
) -> PersonAccess:
    if not can_collaborate(current_user):
        return PersonAccess(False, False, False, False)

    if current_user.is_admin:
        return PersonAccess(
            can_view=True,
            can_view_profile=True,
            can_view_contacts=True,
            can_manage=True,
            distance=0 if person.id == current_user.id else None,
        )

    if person.id == current_user.id:
        return PersonAccess(
            can_view=True,
            can_view_profile=True,
            can_view_contacts=True,
            can_manage=True,
            distance=0,
        )

    if person.visibility == Visibility.hidden.value:
        return PersonAccess(False, False, False, False)
    return PersonAccess(
        can_view=True,
        can_view_profile=True,
        can_view_contacts=True,
        can_manage=False,
        distance=None,
    )


async def get_accessible_person_ids(
    db: AsyncSession,
    current_user: Person,
    *,
    include_hidden: bool = False,
) -> set[str]:
    if not can_collaborate(current_user):
        return set()

    if current_user.is_admin:
        query = select(Person.id)
        if not include_hidden:
            query = query.where(Person.visibility != Visibility.hidden.value)
        result = await db.execute(query)
        return set(result.scalars().all())

    query = select(Person.id, Person.visibility)
    result = await db.execute(query)
    visible_ids: set[str] = set()
    for person_id, visibility in result.all():
        if include_hidden or visibility != Visibility.hidden.value:
            visible_ids.add(person_id)
    return visible_ids


def can_manage_person(current_user: Person, person: Person) -> bool:
    if not can_collaborate(current_user):
        return False
    if current_user.is_admin or current_user.id == person.id:
        return True
    return person.visibility != Visibility.hidden.value


async def can_view_media(
    db: AsyncSession,
    current_user: Person,
    media: Media,
) -> bool:
    result = await db.execute(select(Person).where(Person.id == media.person_id))
    person = result.scalar_one_or_none()
    if not person:
        return False
    return (await get_person_access(db, current_user, person)).can_view


async def can_view_moment(
    db: AsyncSession,
    current_user: Person,
    moment: Moment,
) -> bool:
    if not current_user.is_admin:
        if moment.visibility in {"hidden", "admins"}:
            return False

    result = await db.execute(select(Person).where(Person.id == moment.person_id))
    person = result.scalar_one_or_none()
    if not person:
        return False

    return (await get_person_access(db, current_user, person)).can_view


def can_manage_moment(current_user: Person, moment: Moment) -> bool:
    return current_user.is_admin or moment.posted_by == current_user.id


def can_create_moment_for_person(current_user: Person, person: Person) -> bool:
    return can_manage_person(current_user, person)


def redact_person_detail(person: Person, access: PersonAccess) -> PersonDetail:
    if person.is_root:
        first_name = None
        last_name = None
        nickname = None
    else:
        first_name = person.first_name
        last_name = person.last_name
        nickname = person.nickname

    show_profile = access.can_view_profile
    show_contacts = access.can_view_contacts

    return PersonDetail(
        id=person.id,
        display_name=person.display_name,
        nickname=nickname,
        photo_url=person.photo_url,
        residence_country_code=person.residence_country_code if show_profile else None,
        branch=person.branch if show_profile else None,
        is_living=person.is_living,
        visibility=person.visibility,
        first_name=first_name,
        last_name=last_name,
        patronymic=person.patronymic if show_profile and not person.is_root else None,
        birth_last_name=person.birth_last_name if show_profile and not person.is_root else None,
        gender=person.gender if show_profile and not person.is_root else None,
        birth_date_raw=person.birth_date_raw if show_profile else None,
        birth_date=person.birth_date if show_profile else None,
        birth_date_precision=person.birth_date_precision if show_profile else None,
        death_date_raw=person.death_date_raw if show_profile else None,
        death_date=person.death_date if show_profile else None,
        death_date_precision=person.death_date_precision if show_profile else None,
        birth_place=person.birth_place if show_profile else None,
        birth_country_code=person.birth_country_code if show_profile else None,
        residence_place=person.residence_place if show_profile else None,
        burial_place=person.burial_place if show_profile else None,
        burial_cemetery_name=person.burial_cemetery_name if show_profile else None,
        burial_plot_number=person.burial_plot_number if show_profile else None,
        languages=person.languages if show_profile else [],
        bio=person.bio if show_profile else None,
        medical_history=person.medical_history if show_profile else None,
        contact_whatsapp=person.contact_whatsapp if show_contacts else None,
        contact_telegram=person.contact_telegram if show_contacts else None,
        contact_signal=person.contact_signal if show_contacts else None,
        contact_email=person.contact_email if show_contacts else None,
        is_admin=person.is_admin if access.can_manage else False,
        is_root=person.is_root,
        source=person.source if access.can_manage else "manual",
        created_at=person.created_at if access.can_manage else None,
    )


def redact_person_summary(person: Person, access: PersonAccess) -> PersonSummary:
    return PersonSummary(
        id=person.id,
        display_name=person.display_name,
        nickname=person.nickname if not person.is_root else None,
        photo_url=person.photo_url,
        residence_country_code=person.residence_country_code if access.can_view_profile else None,
        branch=person.branch if access.can_view_profile else None,
        is_living=person.is_living,
        visibility=person.visibility,
    )


async def _graph_distances(
    db: AsyncSession,
    origin_id: str,
    max_distance: int,
) -> dict[str, int]:
    cache = db.info.setdefault("_access_control_cache", {})
    distance_cache: dict[tuple[str, int], dict[str, int]] = cache.setdefault("distances", {})
    cache_key = (origin_id, max_distance)
    if cache_key in distance_cache:
        return distance_cache[cache_key]

    adjacency = await _family_graph(db)
    distances = {origin_id: 0}
    queue: deque[str] = deque([origin_id])

    while queue:
        current = queue.popleft()
        current_distance = distances[current]
        if current_distance >= max_distance:
            continue
        for neighbor in adjacency.get(current, set()):
            if neighbor in distances:
                continue
            distances[neighbor] = current_distance + 1
            queue.append(neighbor)

    distance_cache[cache_key] = distances
    return distances


async def _family_graph(db: AsyncSession) -> dict[str, set[str]]:
    cache = db.info.setdefault("_access_control_cache", {})
    cached_graph = cache.get("family_graph")
    if cached_graph is not None:
        return cached_graph

    adjacency: dict[str, set[str]] = {}

    parent_child_rows = await db.execute(select(ParentChild.parent_id, ParentChild.child_id))
    for parent_id, child_id in parent_child_rows.all():
        adjacency.setdefault(parent_id, set()).add(child_id)
        adjacency.setdefault(child_id, set()).add(parent_id)

    partnerships = await db.execute(select(Partnership.person_a_id, Partnership.person_b_id))
    for person_a_id, person_b_id in partnerships.all():
        adjacency.setdefault(person_a_id, set()).add(person_b_id)
        adjacency.setdefault(person_b_id, set()).add(person_a_id)

    cache["family_graph"] = adjacency
    return adjacency
