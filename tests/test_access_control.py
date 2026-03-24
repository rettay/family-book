import pytest

from app.access_control import (
    PersonAccess,
    can_collaborate,
    can_manage_person,
    get_person_access,
    redact_person_detail,
)
from app.models.person import AccountState, Person, PersonLifecycleState, Visibility


@pytest.mark.asyncio
async def test_hidden_person_denied_to_member(seeded_db):
    hidden = Person(
        first_name="Hidden",
        last_name="Relative",
        visibility=Visibility.hidden.value,
        account_state=AccountState.active.value,
    )
    seeded_db.add(hidden)
    await seeded_db.flush()

    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    access = await get_person_access(seeded_db, member, hidden)

    assert access.can_view is False
    assert access.can_view_profile is False
    assert access.can_view_contacts is False
    assert access.can_manage is False


@pytest.mark.asyncio
async def test_admin_can_view_hidden_person(seeded_db):
    hidden = Person(
        first_name="Hidden",
        last_name="Relative",
        visibility=Visibility.hidden.value,
        account_state=AccountState.active.value,
    )
    seeded_db.add(hidden)
    await seeded_db.flush()

    admin = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    access = await get_person_access(seeded_db, admin, hidden)

    assert access.can_view is True
    assert access.can_view_contacts is True
    assert access.can_manage is True


def test_can_collaborate_requires_active_account():
    active = Person(first_name="A", last_name="User", account_state=AccountState.active.value)
    pending = Person(first_name="P", last_name="User", account_state=AccountState.pending.value)

    assert can_collaborate(active) is True
    assert can_collaborate(pending) is False
    assert can_collaborate(None) is False


def test_can_manage_person_blocks_deleted_profile():
    current_user = Person(first_name="Admin", last_name="User", is_admin=True)
    deleted = Person(
        first_name="Deleted",
        last_name="Person",
        lifecycle_state=PersonLifecycleState.deleted.value,
    )

    assert can_manage_person(current_user, deleted) is False


def test_redact_person_detail_hides_sensitive_fields_without_profile_access():
    person = Person(
        id="person-redacted-1",
        first_name="Redacted",
        last_name="Person",
        is_living=True,
        is_root=False,
        is_admin=False,
        visibility=Visibility.visible.value,
        source="manual",
        branch="martin",
        residence_country_code="US",
        medical_history="Sensitive note",
        contact_email="hidden@example.com",
    )
    access = PersonAccess(
        can_view=True,
        can_view_profile=False,
        can_view_contacts=False,
        can_manage=False,
    )

    detail = redact_person_detail(person, access)

    assert detail.branch is None
    assert detail.residence_country_code is None
    assert detail.medical_history is None
    assert detail.contact_email is None
