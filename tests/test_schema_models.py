from datetime import datetime, timezone

import app.models.moments as moment_models
import app.schemas as schemas
from app.models.moments import Moment, MomentKind, MomentLifecycleState
from app.models.person import Person
from app.schemas import PersonCreate, PersonUpdate, person_to_detail, person_to_summary


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


def test_moment_model_list_properties_round_trip():
    assert moment_models.MomentKind.story.value == "story"

    moment = Moment(person_id="person-id", kind=MomentKind.story.value, posted_by="poster-id")
    moment.media_ids = ["media-1", "media-2"]
    moment.tagged_person_ids = ["person-a", "person-b"]

    assert moment.media_ids == ["media-1", "media-2"]
    assert moment.tagged_person_ids == ["person-a", "person-b"]


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


def test_moment_model_defaults_and_repr_are_stable():
    moment = Moment(
        id="12345678-1234-1234-1234-123456789012",
        person_id="person-id",
        kind=MomentKind.story.value,
        posted_by="poster-id",
    )

    assert moment.media_ids == []
    assert moment.tagged_person_ids == []
    assert repr(moment) == "<Moment id=12345678 kind=story>"

    moment.lifecycle_state = MomentLifecycleState.active.value
    assert moment.lifecycle_state == MomentLifecycleState.active.value


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
    assert detail.contact_email == "detail@example.com"
