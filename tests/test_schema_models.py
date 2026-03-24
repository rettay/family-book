from app.models.moments import Moment, MomentKind
from app.models.person import Person
from app.schemas import person_to_detail, person_to_summary


def test_person_schema_helpers_preserve_expected_fields():
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
    moment = Moment(person_id="person-id", kind=MomentKind.story.value, posted_by="poster-id")
    moment.media_ids = ["media-1", "media-2"]
    moment.tagged_person_ids = ["person-a", "person-b"]

    assert moment.media_ids == ["media-1", "media-2"]
    assert moment.tagged_person_ids == ["person-a", "person-b"]
