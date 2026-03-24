from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.media import Media
from app.models.moments import Moment, MomentLifecycleState
from app.models.person import AccountState, Person, PersonLifecycleState, Visibility
from app.models.relationships import ParentChild, Partnership
from app.schemas import PersonDetail, PersonSummary

logger = logging.getLogger(__name__)


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
        logger.debug("Access denied for non-collaborating user")
        return PersonAccess(False, False, False, False)
    if person.lifecycle_state != PersonLifecycleState.active.value:
        logger.debug("Access denied for inactive person %s", person.id)
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
        logger.debug("Hidden person %s denied to user %s", person.id, current_user.id)
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
        query = select(Person.id).where(
            Person.lifecycle_state == PersonLifecycleState.active.value
        )
        if not include_hidden:
            query = query.where(Person.visibility != Visibility.hidden.value)
        result = await db.execute(query)
        return set(result.scalars().all())

    query = select(Person.id, Person.visibility, Person.lifecycle_state)
    result = await db.execute(query)
    visible_ids: set[str] = set()
    for person_id, visibility, lifecycle_state in result.all():
        if lifecycle_state != PersonLifecycleState.active.value:
            continue
        if include_hidden or visibility != Visibility.hidden.value:
            visible_ids.add(person_id)
    return visible_ids


def can_manage_person(current_user: Person, person: Person) -> bool:
    if not can_collaborate(current_user):
        return False
    if person.lifecycle_state != PersonLifecycleState.active.value:
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
    if moment.lifecycle_state == MomentLifecycleState.deleted.value:
        logger.debug("Deleted moment %s hidden from user %s", moment.id, current_user.id)
        return False
    if moment.lifecycle_state == MomentLifecycleState.moderated.value and not current_user.is_admin:
        logger.debug("Moderated moment %s denied to non-admin %s", moment.id, current_user.id)
        return False
    if not current_user.is_admin:
        if moment.visibility in {"hidden", "admins"}:
            logger.debug("Moment %s visibility %s denied to %s", moment.id, moment.visibility, current_user.id)
            return False

    result = await db.execute(select(Person).where(Person.id == moment.person_id))
    person = result.scalar_one_or_none()
    if not person:
        return False

    return (await get_person_access(db, current_user, person)).can_view


def can_manage_moment(current_user: Person, moment: Moment) -> bool:
    if moment.lifecycle_state != MomentLifecycleState.active.value:
        return current_user.is_admin and moment.lifecycle_state == MomentLifecycleState.moderated.value
    return current_user.is_admin or moment.posted_by == current_user.id


def can_create_moment_for_person(current_user: Person, person: Person) -> bool:
    return can_manage_person(current_user, person)


def redact_person_detail(person: Person, access: PersonAccess) -> PersonDetail:
    payload = _detail_identity_payload(person, access)
    payload.update(_detail_profile_payload(person, access))
    payload.update(_detail_contact_payload(person, access))
    return PersonDetail(**payload)


def redact_person_summary(person: Person, access: PersonAccess) -> PersonSummary:
    return PersonSummary(
        id=person.id,
        display_name=person.display_name,
        nickname=person.nickname if not person.is_root else None,
        photo_url=person.photo_url,
        birth_date_raw=person.birth_date_raw if access.can_view_profile else None,
        residence_country_code=person.residence_country_code if access.can_view_profile else None,
        branch=person.branch if access.can_view_profile else None,
        is_living=person.is_living,
        visibility=person.visibility,
        moment_count=getattr(person, "moment_count", 0) or 0,
        story_count=getattr(person, "story_count", 0) or 0,
        media_count=getattr(person, "media_count", 0) or 0,
    )


def _root_redacted_name(value: str | None, person: Person) -> str | None:
    return None if person.is_root else value


def _detail_identity_payload(person: Person, access: PersonAccess) -> dict[str, object]:
    return {
        "id": person.id,
        "display_name": person.display_name,
        "nickname": _detail_nickname(person),
        "photo_url": person.photo_url,
        "residence_country_code": _profile_value(person.residence_country_code, access),
        "branch": _profile_value(person.branch, access),
        "is_living": person.is_living,
        "visibility": person.visibility,
        "first_name": _root_redacted_name(person.first_name, person),
        "last_name": _root_redacted_name(person.last_name, person),
        "is_admin": person.is_admin if access.can_manage else False,
        "is_root": person.is_root,
        "source": person.source if access.can_manage else "manual",
        "created_at": person.created_at if access.can_manage else None,
    }


def _detail_profile_payload(person: Person, access: PersonAccess) -> dict[str, object]:
    return {
        "patronymic": _profile_name_value(person.patronymic, person, access),
        "birth_last_name": _profile_name_value(person.birth_last_name, person, access),
        "gender": _profile_name_value(person.gender, person, access),
        "birth_date_raw": _profile_value(person.birth_date_raw, access),
        "birth_date": _profile_value(person.birth_date, access),
        "birth_date_precision": _profile_value(person.birth_date_precision, access),
        "death_date_raw": _profile_value(person.death_date_raw, access),
        "death_date": _profile_value(person.death_date, access),
        "death_date_precision": _profile_value(person.death_date_precision, access),
        "birth_place": _profile_value(person.birth_place, access),
        "birth_country_code": _profile_value(person.birth_country_code, access),
        "residence_place": _profile_value(person.residence_place, access),
        "burial_place": _profile_value(person.burial_place, access),
        "burial_country_code": _profile_value(person.burial_country_code, access),
        "burial_cemetery_name": _profile_value(person.burial_cemetery_name, access),
        "burial_plot_number": _profile_value(person.burial_plot_number, access),
        "languages": _profile_list(person.languages, access),
        "bio": _profile_value(person.bio, access),
        "medical_history": _profile_value(person.medical_history, access),
    }


def _detail_contact_payload(person: Person, access: PersonAccess) -> dict[str, object]:
    return {
        "contact_whatsapp": _contact_value(person.contact_whatsapp, access),
        "contact_telegram": _contact_value(person.contact_telegram, access),
        "contact_signal": _contact_value(person.contact_signal, access),
        "contact_email": _contact_value(person.contact_email, access),
    }


def _detail_nickname(person: Person) -> str | None:
    return None if person.is_root else person.nickname


def _profile_value(value, access: PersonAccess):
    return value if access.can_view_profile else None


def _profile_list(value: list[str], access: PersonAccess) -> list[str]:
    return value if access.can_view_profile else []


def _profile_name_value(value: str | None, person: Person, access: PersonAccess) -> str | None:
    if person.is_root:
        return None
    return _profile_value(value, access)


def _contact_value(value: str | None, access: PersonAccess) -> str | None:
    return value if access.can_view_contacts else None


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
