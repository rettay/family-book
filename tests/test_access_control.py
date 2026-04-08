import pytest

import app.access_control as access_control
from app.access_control import (
    PersonAccess,
    can_collaborate,
    can_manage_person,
    get_accessible_person_ids,
    get_person_access,
    redact_person_detail,
    redact_person_summary,
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
    assert access.can_view_sensitive_profile is False
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
    assert access.can_view_sensitive_profile is True
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
        can_view_sensitive_profile=False,
        can_manage=False,
    )

    detail = redact_person_detail(person, access)

    assert detail.branch is None
    assert detail.residence_country_code is None
    assert detail.medical_history is None
    assert detail.contact_email is None


@pytest.mark.asyncio
async def test_get_accessible_person_ids_hides_hidden_people_from_members(seeded_db):
    hidden = Person(
        first_name="Hidden",
        last_name="Relative",
        visibility=Visibility.hidden.value,
        account_state=AccountState.active.value,
    )
    seeded_db.add(hidden)
    await seeded_db.flush()
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    seeded_db.add(access_control.ParentChild(parent_id=member.id, child_id=hidden.id, kind="biological"))
    await seeded_db.commit()

    visible_ids = await get_accessible_person_ids(seeded_db, member)
    all_ids = await get_accessible_person_ids(seeded_db, member, include_hidden=True)

    assert hidden.id not in visible_ids
    assert hidden.id in all_ids


def test_redact_person_summary_preserves_metrics_when_profile_visible():
    person = Person(
        id="person-summary-1",
        first_name="Metric",
        last_name="Person",
        branch="martin",
        residence_country_code="US",
        account_state=AccountState.active.value,
        visibility=Visibility.visible.value,
        is_living=True,
    )
    person.media_count = 9
    access = PersonAccess(True, True, False, False, False)

    summary = redact_person_summary(person, access)

    assert access_control.can_collaborate(person) is True
    assert summary.branch == "martin"
    assert summary.residence_country_code == "US"
    assert summary.media_count == 9


@pytest.mark.asyncio
async def test_member_cannot_view_unlinked_visible_person(seeded_db):
    outsider = Person(
        first_name="Outsider",
        last_name="Relative",
        visibility=Visibility.visible.value,
        account_state=AccountState.active.value,
    )
    seeded_db.add(outsider)
    await seeded_db.commit()

    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    access = await get_person_access(seeded_db, member, outsider)

    assert access.can_view is False
    assert access.distance is None


@pytest.mark.asyncio
async def test_member_contact_access_is_limited_to_close_family(seeded_db):
    tyler = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert tyler is not None
    assert member is not None
    tyler.contact_email = "tyler-private@example.com"
    await seeded_db.commit()

    access = await get_person_access(seeded_db, member, tyler)
    detail = redact_person_detail(tyler, access)

    assert access.can_view is True
    assert access.distance == 2
    assert access.can_view_contacts is False
    assert detail.contact_email is None


@pytest.mark.asyncio
async def test_steward_can_manage_visible_non_staff_profiles(seeded_db):
    steward = Person(
        first_name="Steward",
        last_name="User",
        role="steward",
        account_state=AccountState.active.value,
    )
    target = Person(
        first_name="Managed",
        last_name="Person",
        visibility=Visibility.visible.value,
        account_state=AccountState.active.value,
    )
    seeded_db.add_all([steward, target])
    await seeded_db.commit()

    access = await get_person_access(seeded_db, steward, target)

    assert access.can_view is True
    assert access.can_manage is True
    assert can_manage_person(steward, target) is True


@pytest.mark.asyncio
async def test_viewer_cannot_manage_even_their_own_profile(seeded_db):
    viewer = Person(
        first_name="Viewer",
        last_name="User",
        role="viewer",
        account_state=AccountState.active.value,
    )
    seeded_db.add(viewer)
    await seeded_db.commit()

    access = await get_person_access(seeded_db, viewer, viewer)

    assert access.can_view is True
    assert access.can_manage is False
    assert can_manage_person(viewer, viewer) is False


@pytest.mark.asyncio
async def test_living_minor_contacts_are_staff_only(seeded_db):
    minor = Person(
        first_name="Minor",
        last_name="Relative",
        birth_date="2012-05-01",
        is_living=True,
        visibility=Visibility.visible.value,
        account_state=AccountState.active.value,
        contact_email="minor@example.com",
    )
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    admin = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    assert member is not None
    assert admin is not None
    seeded_db.add(minor)
    await seeded_db.flush()
    seeded_db.add(access_control.ParentChild(parent_id=member.id, child_id=minor.id, kind="biological"))
    await seeded_db.commit()

    member_access = await get_person_access(seeded_db, member, minor)
    admin_access = await get_person_access(seeded_db, admin, minor)

    assert member_access.can_view is True
    assert member_access.can_view_contacts is False
    assert admin_access.can_view_contacts is True
