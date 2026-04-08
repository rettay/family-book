from __future__ import annotations

from app.models.person import Person, PersonRole


ADMIN_ROLES = {PersonRole.owner.value, PersonRole.admin.value}
STAFF_ROLES = ADMIN_ROLES | {PersonRole.steward.value}


def get_person_role(person: Person | None) -> str:
    if person is None:
        return PersonRole.viewer.value
    normalized = (getattr(person, "role", None) or "").strip().lower()
    if normalized in {role.value for role in PersonRole}:
        return normalized
    if getattr(person, "is_admin", False):
        return PersonRole.admin.value
    return PersonRole.member.value


def is_admin_actor(person: Person | None) -> bool:
    return get_person_role(person) in ADMIN_ROLES


def is_staff_actor(person: Person | None) -> bool:
    return get_person_role(person) in STAFF_ROLES


def is_viewer_actor(person: Person | None) -> bool:
    return get_person_role(person) == PersonRole.viewer.value
