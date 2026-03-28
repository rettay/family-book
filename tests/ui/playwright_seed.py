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
ORPHAN_PARENT_ID = "orphnpar-0000-0000-000000000008"
ORPHAN_CHILD_ID = "orphnchd-0000-0000-000000000009"
ORPHAN_SINGLE_ID = "orphnsng-0000-0000-000000000010"
MADELINE_ID = "madeline-000-0000-000000000011"
ROSS_ID = "ross-0000-0000-000000000012"
JOHN_JR_ID = "johnjr-000-0000-000000000013"
MONICA_ID = "monica-000-0000-000000000014"
FATHER_JIANG_ID = "fatherj-000-0000-000000000015"
MOTHER_JIANG_ID = "motherj-000-0000-000000000016"
BO_JIANG_ID = "bojiang-000-0000-000000000017"
ANDREW_ID = "andrew-000-0000-000000000018"
ANNA_ID = "anna-0000-0000-000000000019"
CASEY_ID = "casey-000-0000-000000000020"
TAYLOR_ID = "taylor-00-0000-000000000021"
MORGAN_ID = "morgan-00-0000-000000000022"
PARKER_ID = "parker-00-0000-000000000023"
QUINN_ID = "quinn-000-0000-000000000024"
ROSA_ID = "rosa-0000-0000-000000000025"
BEN_ID = "ben-00000-0000-000000000026"
MIA_ID = "mia-00000-0000-000000000027"
LEE_ID = "lee-00000-0000-000000000028"
JUNE_ID = "june-0000-0000-000000000029"


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await session.execute(delete(Partnership))
        await session.execute(delete(ParentChild))

        for person_id in [
            ROOT_ID, TYLER_ID, YULIYA_ID, GRANDPA_ID, MEMBER_ID, ALEX_ID, JORDAN_ID,
            ORPHAN_PARENT_ID, ORPHAN_CHILD_ID, ORPHAN_SINGLE_ID,
            MADELINE_ID, ROSS_ID, JOHN_JR_ID, MONICA_ID, FATHER_JIANG_ID,
            MOTHER_JIANG_ID, BO_JIANG_ID, ANDREW_ID, ANNA_ID,
            CASEY_ID, TAYLOR_ID, MORGAN_ID, PARKER_ID, QUINN_ID,
            ROSA_ID, BEN_ID, MIA_ID, LEE_ID, JUNE_ID
        ]:
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
            nickname="Ty",
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
            birth_date_raw="22 Mar 1988",
            birth_date="1988-03-22",
            birth_date_precision="exact",
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
        orphan_parent = Person(
            id=ORPHAN_PARENT_ID,
            first_name="Olive",
            last_name="Detached",
            residence_country_code="US",
            residence_place="Portland",
            branch="detached",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        orphan_child = Person(
            id=ORPHAN_CHILD_ID,
            first_name="Owen",
            last_name="Detached",
            residence_country_code="US",
            residence_place="Portland",
            branch="detached",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        orphan_single = Person(
            id=ORPHAN_SINGLE_ID,
            first_name="Nora",
            last_name="Untethered",
            residence_country_code="US",
            residence_place="Salem",
            branch="untethered",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        madeline = Person(
            id=MADELINE_ID,
            first_name="Madeline",
            last_name="Branch",
            residence_country_code="US",
            residence_place="Boston",
            branch="branch",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        ross = Person(
            id=ROSS_ID,
            first_name="Ross",
            last_name="Branch",
            residence_country_code="US",
            residence_place="Boston",
            branch="branch",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        john_jr = Person(
            id=JOHN_JR_ID,
            first_name="John",
            last_name="Branch",
            residence_country_code="US",
            residence_place="Boston",
            branch="branch",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        monica = Person(
            id=MONICA_ID,
            first_name="Yenting",
            last_name="Branch",
            nickname="Monica",
            birth_last_name="Jiang",
            birth_date_raw="26 Mar 1991",
            birth_date="1991-03-26",
            birth_date_precision="exact",
            residence_country_code="US",
            residence_place="Seattle",
            branch="jiang",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        father_jiang = Person(
            id=FATHER_JIANG_ID,
            first_name="Father",
            last_name="Jiang",
            residence_country_code="US",
            residence_place="Seattle",
            branch="jiang",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        mother_jiang = Person(
            id=MOTHER_JIANG_ID,
            first_name="Mother",
            last_name="Jiang",
            residence_country_code="US",
            residence_place="Seattle",
            branch="jiang",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        bo_jiang = Person(
            id=BO_JIANG_ID,
            first_name="Bo",
            last_name="Jiang",
            residence_country_code="US",
            residence_place="Seattle",
            branch="jiang",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        andrew = Person(
            id=ANDREW_ID,
            first_name="Andrew",
            last_name="Branch",
            residence_country_code="US",
            residence_place="Seattle",
            branch="branch",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        anna = Person(
            id=ANNA_ID,
            first_name="Anna",
            last_name="Branch",
            residence_country_code="US",
            residence_place="Seattle",
            branch="branch",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        casey = Person(
            id=CASEY_ID,
            first_name="Casey",
            last_name="Rivers",
            residence_country_code="US",
            residence_place="Austin",
            branch="rivers",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        taylor = Person(
            id=TAYLOR_ID,
            first_name="Taylor",
            last_name="Rivers",
            residence_country_code="US",
            residence_place="Austin",
            branch="rivers",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        morgan = Person(
            id=MORGAN_ID,
            first_name="Morgan",
            last_name="Wells",
            residence_country_code="US",
            residence_place="Dallas",
            branch="wells",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        parker = Person(
            id=PARKER_ID,
            first_name="Parker",
            last_name="Rivers",
            residence_country_code="US",
            residence_place="Austin",
            branch="rivers",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        quinn = Person(
            id=QUINN_ID,
            first_name="Quinn",
            last_name="Wells",
            residence_country_code="US",
            residence_place="Dallas",
            branch="wells",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        rosa = Person(
            id=ROSA_ID,
            first_name="Rosa",
            last_name="Home",
            residence_country_code="US",
            residence_place="Denver",
            branch="home",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        ben = Person(
            id=BEN_ID,
            first_name="Ben",
            last_name="Home",
            residence_country_code="US",
            residence_place="Denver",
            branch="home",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        mia = Person(
            id=MIA_ID,
            first_name="Mia",
            last_name="Home",
            residence_country_code="US",
            residence_place="Denver",
            branch="home",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        lee = Person(
            id=LEE_ID,
            first_name="Lee",
            last_name="Solo",
            residence_country_code="US",
            residence_place="Phoenix",
            branch="solo",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        june = Person(
            id=JUNE_ID,
            first_name="June",
            last_name="Solo",
            residence_country_code="US",
            residence_place="Phoenix",
            branch="solo",
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )

        session.add_all([
            root, tyler, yuliya, grandpa, member, alex, jordan,
            orphan_parent, orphan_child, orphan_single, madeline, ross,
            john_jr, monica, father_jiang, mother_jiang, bo_jiang,
            andrew, anna, casey, taylor, morgan, parker, quinn,
            rosa, ben, mia, lee, june
        ])
        await session.flush()

        session.add_all(
            [
                ParentChild(parent_id=TYLER_ID, child_id=ROOT_ID, kind="biological"),
                ParentChild(parent_id=YULIYA_ID, child_id=ROOT_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=TYLER_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=MEMBER_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=MADELINE_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=JOHN_JR_ID, kind="biological"),
                ParentChild(parent_id=GRANDPA_ID, child_id=CASEY_ID, kind="biological"),
                ParentChild(parent_id=MEMBER_ID, child_id=JORDAN_ID, kind="biological"),
                ParentChild(parent_id=ALEX_ID, child_id=JORDAN_ID, kind="biological"),
                ParentChild(parent_id=FATHER_JIANG_ID, child_id=MONICA_ID, kind="biological"),
                ParentChild(parent_id=MOTHER_JIANG_ID, child_id=MONICA_ID, kind="biological"),
                ParentChild(parent_id=FATHER_JIANG_ID, child_id=BO_JIANG_ID, kind="biological"),
                ParentChild(parent_id=MOTHER_JIANG_ID, child_id=BO_JIANG_ID, kind="biological"),
                ParentChild(parent_id=JOHN_JR_ID, child_id=ANDREW_ID, kind="biological"),
                ParentChild(parent_id=MONICA_ID, child_id=ANDREW_ID, kind="biological"),
                ParentChild(parent_id=JOHN_JR_ID, child_id=ANNA_ID, kind="biological"),
                ParentChild(parent_id=MONICA_ID, child_id=ANNA_ID, kind="biological"),
                ParentChild(parent_id=CASEY_ID, child_id=PARKER_ID, kind="biological"),
                ParentChild(parent_id=TAYLOR_ID, child_id=PARKER_ID, kind="biological"),
                ParentChild(parent_id=CASEY_ID, child_id=QUINN_ID, kind="biological"),
                ParentChild(parent_id=MORGAN_ID, child_id=QUINN_ID, kind="biological"),
                ParentChild(parent_id=ROSA_ID, child_id=MIA_ID, kind="adoptive"),
                ParentChild(parent_id=BEN_ID, child_id=MIA_ID, kind="adoptive"),
                ParentChild(parent_id=LEE_ID, child_id=JUNE_ID, kind="guardian"),
                ParentChild(parent_id=ORPHAN_PARENT_ID, child_id=ORPHAN_CHILD_ID, kind="biological"),
                Partnership(
                    person_a_id=min(TYLER_ID, YULIYA_ID),
                    person_b_id=max(TYLER_ID, YULIYA_ID),
                    kind="married",
                    status="active",
                    start_date="2014-03-20",
                    start_date_precision="exact",
                ),
                Partnership(
                    person_a_id=min(MADELINE_ID, ROSS_ID),
                    person_b_id=max(MADELINE_ID, ROSS_ID),
                    kind="married",
                    status="active",
                ),
                Partnership(
                    person_a_id=min(JOHN_JR_ID, MONICA_ID),
                    person_b_id=max(JOHN_JR_ID, MONICA_ID),
                    kind="married",
                    status="active",
                ),
                Partnership(
                    person_a_id=min(FATHER_JIANG_ID, MOTHER_JIANG_ID),
                    person_b_id=max(FATHER_JIANG_ID, MOTHER_JIANG_ID),
                    kind="married",
                    status="active",
                ),
                Partnership(
                    person_a_id=min(CASEY_ID, TAYLOR_ID),
                    person_b_id=max(CASEY_ID, TAYLOR_ID),
                    kind="married",
                    status="dissolved",
                ),
                Partnership(
                    person_a_id=min(CASEY_ID, MORGAN_ID),
                    person_b_id=max(CASEY_ID, MORGAN_ID),
                    kind="domestic_partner",
                    status="active",
                ),
                Partnership(
                    person_a_id=min(ROSA_ID, BEN_ID),
                    person_b_id=max(ROSA_ID, BEN_ID),
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
