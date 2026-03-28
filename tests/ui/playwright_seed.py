import asyncio

from sqlalchemy import delete

from app.database import async_session_factory, engine
from app.models.base import Base
from app.models.person import AccountState, Person, PersonSource
from app.models.relationships import ParentChild, Partnership
from app.services.auth_service import create_session


ROOT_ID = "root-0000-0000-0000-000000000001"
TYLER_ID = "tyler-000-0000-0000-000000000002"
YULIYA_ID = "yuliya-00-0000-0000-000000000003"
GRANDPA_ID = "grndpa-00-0000-0000-000000000004"
MEMBER_ID = "member-00-0000-0000-000000000005"
ALEX_ID = "alex-000-0000-0000-000000000006"
JORDAN_ID = "jrdn-000-0000-0000-000000000007"


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await session.execute(delete(Partnership))
        await session.execute(delete(ParentChild))

        for person_id in [ROOT_ID, TYLER_ID, YULIYA_ID, GRANDPA_ID, MEMBER_ID, ALEX_ID, JORDAN_ID]:
            person = await session.get(Person, person_id)
            if person:
                await session.delete(person)
        await session.flush()

        root = Person(
            id=ROOT_ID,
            first_name="Our",
            last_name="Family",
            is_root=True,
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        tyler = Person(
            id=TYLER_ID,
            first_name="Tyler",
            last_name="Martin",
            birth_date_raw="14 Mar 1985",
            birth_date="1985-03-14",
            birth_date_precision="exact",
            residence_country_code="ES",
            residence_place="Barcelona",
            branch="martin",
            is_admin=True,
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
            contact_email="tyler@example.com",
            social_instagram="https://instagram.com/tylermartin",
            social_linkedin="https://linkedin.com/in/tylermartin",
            slug="tyler-martin",
        )
        yuliya = Person(
            id=YULIYA_ID,
            first_name="Yuliya",
            last_name="Semesock",
            residence_country_code="ES",
            residence_place="Barcelona",
            branch="yuliya",
            is_admin=True,
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        grandpa = Person(
            id=GRANDPA_ID,
            first_name="Robert",
            last_name="Martin",
            residence_country_code="CA",
            residence_place="Toronto",
            branch="martin",
            is_living=False,
            burial_place="Toronto",
            burial_country_code="CA",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        member = Person(
            id=MEMBER_ID,
            first_name="Jane",
            last_name="Martin",
            residence_country_code="CA",
            residence_place="Toronto",
            branch="martin",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        alex = Person(
            id=ALEX_ID,
            first_name="Alex",
            last_name="Stone",
            residence_country_code="US",
            residence_place="Chicago",
            branch="stone",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        jordan = Person(
            id=JORDAN_ID,
            first_name="Jordan",
            last_name="Stone",
            residence_country_code="US",
            residence_place="Chicago",
            branch="stone",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )

        session.add_all([root, tyler, yuliya, grandpa, member, alex, jordan])
        await session.flush()

        session.add_all(
            [
                ParentChild(parent_id=TYLER_ID, child_id=ROOT_ID, kind="biological"),
                ParentChild(parent_id=YULIYA_ID, child_id=ROOT_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=TYLER_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=MEMBER_ID, kind="biological"),
                ParentChild(parent_id=MEMBER_ID, child_id=JORDAN_ID, kind="biological"),
                ParentChild(parent_id=ALEX_ID, child_id=JORDAN_ID, kind="biological"),
                Partnership(
                    person_a_id=min(TYLER_ID, YULIYA_ID),
                    person_b_id=max(TYLER_ID, YULIYA_ID),
                    kind="married",
                    status="active",
                ),
            ]
        )

        admin_session = await create_session(
            session,
            person_id=TYLER_ID,
            auth_method="google_oauth",
        )
        member_session = await create_session(
            session,
            person_id=MEMBER_ID,
            auth_method="google_oauth",
        )

        await session.commit()

    print(f"ADMIN_SESSION={admin_session}")
    print(f"MEMBER_SESSION={member_session}")
    print(f"TYLER_ID={TYLER_ID}")
    print(f"MEMBER_ID={MEMBER_ID}")


if __name__ == "__main__":
    asyncio.run(seed())
