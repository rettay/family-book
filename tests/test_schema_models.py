from datetime import datetime, timezone

import pytest
import app.schemas as schemas
from app.models.person import Person
from pydantic import ValidationError
from app.schemas import (
    ParentChildCreate,
    ParentChildResponse,
    PartnershipResponse,
    PartnershipUpdate,
    PersonCreate,
    PersonUpdate,
    person_to_detail,
    person_to_summary,
)


def test_person_schema_helpers_preserve_expected_fields():
    assert schemas.PersonSummary.model_config["from_attributes"] is True

    person = Person(
        id="schema-person-1",
        first_name="Schema",
        last_name="Person",
        is_living=True,
        is_root=False,
        is_admin=False,
        visibility="visible",
        source="manual",
        branch="martin",
        residence_country_code="US",
        contact_email="schema@example.com",
    )

    summary = person_to_summary(person)
    detail = person_to_detail(person)

    assert summary.display_name == "Schema Person"
    assert detail.contact_email == "schema@example.com"
    assert detail.branch == "martin"
    assert detail.role == "member"


def test_root_person_detail_redacts_name_fields():
    root = Person(
        id="root-person-1",
        first_name="Real",
        last_name="Name",
        is_root=True,
        is_admin=False,
        is_living=True,
        visibility="visible",
        source="manual",
    )

    detail = person_to_detail(root)

    assert detail.display_name == "Our Family"
    assert detail.first_name is None
    assert detail.last_name is None


def test_schema_models_do_not_share_default_language_list():
    first = PersonCreate(first_name="A", last_name="B")
    second = PersonCreate(first_name="C", last_name="D")

    first.languages.append("en")

    assert second.languages == []


def test_person_update_can_clear_fields_without_setting_unrelated_defaults():
    update = PersonUpdate(contact_email=None, languages=None, visibility="hidden")

    assert update.contact_email is None
    assert update.languages is None
    assert update.visibility == "hidden"


def test_person_summary_helper_preserves_datetime_fields_for_detail():
    created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
    person = Person(
        id="schema-person-2",
        first_name="Detail",
        last_name="Case",
        is_living=True,
        is_root=False,
        is_admin=True,
        visibility="visible",
        source="manual",
        created_at=created_at,
        contact_email="detail@example.com",
    )

    detail = person_to_detail(person)

    assert detail.created_at == created_at
    assert detail.is_admin is True
    assert detail.role == "admin"
    assert detail.contact_email == "detail@example.com"


def test_relationship_schemas_validate_integration_shapes():
    relationship = ParentChildCreate(
        parent_id="parent-1",
        child_id="child-1",
    )
    relationship_response = ParentChildResponse(
        id="pc-1",
        parent_id="parent-1",
        child_id="child-1",
        kind="biological",
        confidence="confirmed",
        source="manual",
    )
    partnership = PartnershipResponse(
        id="partner-1",
        person_a_id="person-a",
        person_b_id="person-b",
        kind="married",
        status="active",
        source="manual",
    )
    partnership_update = PartnershipUpdate(status="ended", notes="archived")

    with pytest.raises(ValidationError):
        schemas.PersonCreate(first_name="x" * 201, last_name="Person")
    assert relationship.kind == "biological"
    assert relationship_response.parent_id == "parent-1"
    assert partnership.status == "active"
    assert partnership_update.status == "ended"
