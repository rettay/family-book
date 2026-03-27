import pytest
from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media, MediaType
from app.models.person import Person
from app.models.relationships import ParentChild, Partnership


@pytest.mark.asyncio
async def test_person_creation_minimal(db: AsyncSession):
    person = Person(first_name="Test", last_name="Person")
    db.add(person)
    await db.flush()

    result = await db.execute(select(Person).where(Person.id == person.id))
    fetched = result.scalar_one()
    assert fetched.first_name == "Test"
    assert fetched.last_name == "Person"
    assert fetched.is_root is False
    assert fetched.is_admin is False
    assert fetched.is_living is True


@pytest.mark.asyncio
async def test_person_display_name_western(db: AsyncSession):
    person = Person(first_name="Alex", last_name="Rivera")
    assert person.display_name == "Alex Rivera"


@pytest.mark.asyncio
async def test_person_display_name_root(db: AsyncSession):
    person = Person(first_name="Real", last_name="Name", is_root=True)
    assert person.display_name == "Our Family"


@pytest.mark.asyncio
async def test_person_display_name_eastern(db: AsyncSession):
    person = Person(first_name="Yuki", last_name="Tanaka", name_display_order="eastern")
    assert person.display_name == "Tanaka Yuki"


@pytest.mark.asyncio
async def test_person_languages_property(db: AsyncSession):
    person = Person(first_name="Test", last_name="Lang")
    person.languages = ["en", "ru", "es"]
    db.add(person)
    await db.flush()

    result = await db.execute(select(Person).where(Person.id == person.id))
    fetched = result.scalar_one()
    assert fetched.languages == ["en", "ru", "es"]


@pytest.mark.asyncio
async def test_person_rich_fields_round_trip(db: AsyncSession):
    person = Person(
        first_name="Rich",
        last_name="Profile",
        medical_history="Family history of hypertension",
        burial_place="Springfield",
        burial_country_code="US",
        burial_cemetery_name="Maple Grove",
        burial_plot_number="A-42",
    )
    db.add(person)
    await db.flush()

    result = await db.execute(select(Person).where(Person.id == person.id))
    fetched = result.scalar_one()
    assert fetched.medical_history == "Family history of hypertension"
    assert fetched.burial_place == "Springfield"
    assert fetched.burial_country_code == "US"
    assert fetched.burial_cemetery_name == "Maple Grove"
    assert fetched.burial_plot_number == "A-42"


@pytest.mark.asyncio
async def test_sensitive_person_fields_persist_encrypted(db: AsyncSession):
    person = Person(
        first_name="Protected",
        last_name="Person",
        medical_history="High blood pressure notes",
        contact_email="protected@example.com",
        contact_signal="+15551234567",
    )
    db.add(person)
    await db.flush()

    row = (
        await db.execute(
            text(
                """
                SELECT medical_history, contact_email, contact_signal, contact_email_hash
                FROM persons
                WHERE id = :person_id
                """
            ),
            {"person_id": person.id},
        )
    ).one()

    assert row.medical_history != "High blood pressure notes"
    assert row.contact_email != "protected@example.com"
    assert row.contact_signal != "+15551234567"
    assert row.contact_email_hash is not None

    fetched = (
        await db.execute(select(Person).where(Person.id == person.id))
    ).scalar_one()
    assert fetched.medical_history == "High blood pressure notes"
    assert fetched.contact_email == "protected@example.com"
    assert fetched.contact_signal == "+15551234567"


@pytest.mark.asyncio
async def test_media_tagged_person_ids_property_round_trip(db: AsyncSession):
    owner = Person(first_name="Media", last_name="Owner")
    tagged = Person(first_name="Tagged", last_name="Person")
    db.add_all([owner, tagged])
    await db.flush()

    media = Media(person_id=owner.id, media_type=MediaType.image.value)
    media.tagged_person_ids = [owner.id, tagged.id]
    db.add(media)
    await db.flush()

    result = await db.execute(select(Media).where(Media.id == media.id))
    fetched = result.scalar_one()
    assert fetched.tagged_person_ids == [owner.id, tagged.id]


@pytest.mark.asyncio
async def test_parent_child_self_ref_rejected(db: AsyncSession):
    person = Person(first_name="Self", last_name="Ref")
    db.add(person)
    await db.flush()

    pc = ParentChild(parent_id=person.id, child_id=person.id, kind="biological")
    db.add(pc)
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()


@pytest.mark.asyncio
async def test_parent_child_unique_constraint(db: AsyncSession):
    p1 = Person(first_name="Parent", last_name="One")
    p2 = Person(first_name="Child", last_name="One")
    db.add_all([p1, p2])
    await db.flush()

    pc1 = ParentChild(parent_id=p1.id, child_id=p2.id, kind="biological")
    db.add(pc1)
    await db.flush()

    pc2 = ParentChild(parent_id=p1.id, child_id=p2.id, kind="biological")
    db.add(pc2)
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()


@pytest.mark.asyncio
async def test_partnership_canonical_order_constraint(db: AsyncSession):
    p1 = Person(id="aaaa-0000-0000-0000-000000000001", first_name="A", last_name="A")
    p2 = Person(id="zzzz-0000-0000-0000-000000000002", first_name="Z", last_name="Z")
    db.add_all([p1, p2])
    await db.flush()

    # Correct order (a < z)
    partnership = Partnership(person_a_id=p1.id, person_b_id=p2.id, kind="married")
    db.add(partnership)
    await db.flush()
    assert partnership.id is not None


@pytest.mark.asyncio
async def test_partnership_self_ref_rejected(db: AsyncSession):
    p1 = Person(first_name="Solo", last_name="Person")
    db.add(p1)
    await db.flush()

    partnership = Partnership(person_a_id=p1.id, person_b_id=p1.id, kind="married")
    db.add(partnership)
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()


@pytest.mark.asyncio
async def test_cascade_delete_person_removes_relationships(db: AsyncSession):
    p1 = Person(first_name="Parent", last_name="Del")
    p2 = Person(first_name="Child", last_name="Del")
    db.add_all([p1, p2])
    await db.flush()

    pc = ParentChild(parent_id=p1.id, child_id=p2.id, kind="biological")
    db.add(pc)
    await db.flush()
    pc_id = pc.id

    await db.delete(p1)
    await db.flush()

    result = await db.execute(select(ParentChild).where(ParentChild.id == pc_id))
    assert result.scalar_one_or_none() is None
