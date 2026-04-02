"""
Comprehensive demo seed — ~100 synthetic persons across 5 family branches, 4-5 generations.
Idempotent: deletes all existing data before seeding.
Run: uv run python -m app.seed_comprehensive
"""

import asyncio
import json

from sqlalchemy import delete

from app.database import async_session_factory
from app.models.auth import Invite, MagicLinkToken, UserSession
from app.models.audit import AuditLog
from app.models.media import Media
from app.models.person import Person
from app.models.relationships import ParentChild, Partnership
from app.models.revisions import EntityRevision
from app.models.saved_record import SavedRecord
from app.services.auth_service import create_session
from app.services.wiki_service import generate_slug


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _person(id: str, first: str, last: str, **kw) -> dict:
    """Build a person dict with sensible defaults."""
    d = {
        "id": id,
        "first_name": first,
        "last_name": last,
        "source": "manual",
        "is_living": kw.pop("is_living", True),
        "gender": kw.pop("gender", None),
        "name_display_order": kw.pop("name_display_order", "western"),
    }
    d.update(kw)
    return d


def _pc(parent_id: str, child_id: str, kind: str = "biological") -> dict:
    return {"parent_id": parent_id, "child_id": child_id, "kind": kind, "source": "manual"}


def _partnership(a_id: str, b_id: str, kind: str = "married",
                 status: str = "active", start: str | None = None, end: str | None = None) -> dict:
    # Enforce canonical order: person_a_id < person_b_id
    if a_id > b_id:
        a_id, b_id = b_id, a_id
    d: dict = {"person_a_id": a_id, "person_b_id": b_id, "kind": kind, "status": status, "source": "manual"}
    if start:
        d["start_date"] = start
    if end:
        d["end_date"] = end
    return d


# ---------------------------------------------------------------------------
# Branch 1: Anglo core (~30 persons, 4 generations)
# ---------------------------------------------------------------------------

ANGLO = [
    # Gen 1 — founders (1920s)
    _person("seed-001", "Robert", "Harrison", gender="male",
            birth_date_raw="1922-03-15", birth_date="1922-03-15", birth_date_precision="exact",
            is_living=False, death_date_raw="2001-11-20", death_date="2001-11-20",
            birth_place="Boston, Massachusetts", birth_country_code="US",
            branch="Harrison", is_root=True,
            bio="Robert Harrison served in the Navy during World War II and later built a successful construction company in New England. He was known for his meticulous record-keeping and love of jazz music."),
    _person("seed-002", "Eleanor", "Harrison", gender="female", birth_last_name="Mitchell",
            birth_date_raw="1925-07-08", birth_date="1925-07-08", birth_date_precision="exact",
            is_living=False, death_date_raw="2010-02-14", death_date="2010-02-14",
            birth_place="Hartford, Connecticut", birth_country_code="US", branch="Harrison"),

    # Gen 2 — 4 children
    _person("seed-003", "James", "Harrison", gender="male",
            birth_date_raw="1948-01-22", birth_date="1948-01-22", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison",
            bio="Eldest son. Practiced law in Boston for 40 years before retiring to Cape Cod.",
            is_admin=True, google_email="familybook.demo@gmail.com", google_sub="demo-google-sub-001"),
    _person("seed-004", "Margaret", "Harrison", gender="female",
            birth_date_raw="1950-06-11", birth_date="1950-06-11", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison", nickname="Maggie"),
    _person("seed-005", "William", "Harrison", gender="male",
            birth_date_raw="1953-09-30", birth_date="1953-09-30", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison", nickname="Bill"),
    _person("seed-006", "Patricia", "Harrison", gender="female",
            birth_date_raw="1957-12-03", birth_date="1957-12-03", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),

    # Gen 2 spouses
    _person("seed-007", "Susan", "Harrison", gender="female", birth_last_name="Chen",
            birth_date_raw="1949-04-18", birth_date="1949-04-18", birth_date_precision="exact",
            birth_place="San Francisco, CA", birth_country_code="US", branch="Harrison"),
    _person("seed-008", "Thomas", "O'Brien", gender="male",
            birth_date_raw="1948-08-25", birth_date="1948-08-25", birth_date_precision="exact",
            is_living=False, death_date_raw="2019-05-03", death_date="2019-05-03",
            birth_place="Dublin, Ireland", birth_country_code="IE", branch="Harrison"),
    _person("seed-009", "Linda", "Harrison", gender="female", birth_last_name="Johansson",
            birth_date_raw="1955-02-14", birth_date="1955-02-14", birth_date_precision="exact",
            birth_place="Minneapolis, MN", birth_country_code="US", branch="Harrison"),
    # William's ex-wife (divorced)
    _person("seed-010", "Karen", "Phillips", gender="female",
            birth_date_raw="1956-11-09", birth_date="1956-11-09", birth_date_precision="exact",
            birth_place="Chicago, IL", birth_country_code="US", branch="Harrison"),
    # Patricia's husband — connects to Latin branch
    _person("seed-011", "Carlos", "Ramirez", gender="male",
            birth_date_raw="1955-03-21", birth_date="1955-03-21", birth_date_precision="exact",
            birth_place="Mexico City, Mexico", birth_country_code="MX", branch="Harrison-Ramirez"),

    # Gen 3 — grandchildren
    _person("seed-012", "Emily", "Harrison", gender="female",
            birth_date_raw="1975-05-20", birth_date="1975-05-20", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison",
            bio="Emily teaches marine biology at Woods Hole Oceanographic Institution."),
    _person("seed-013", "Michael", "Harrison", gender="male",
            birth_date_raw="1978-10-12", birth_date="1978-10-12", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-014", "Sarah", "O'Brien", gender="female",
            birth_date_raw="1976-03-07", birth_date="1976-03-07", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-015", "Patrick", "O'Brien", gender="male",
            birth_date_raw="1979-07-19", birth_date="1979-07-19", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-016", "Daniel", "Harrison", gender="male",
            birth_date_raw="1980-01-30", birth_date="1980-01-30", birth_date_precision="exact",
            birth_place="Chicago, IL", birth_country_code="US", branch="Harrison"),
    # adopted by William after divorce
    _person("seed-017", "Jessica", "Harrison", gender="female",
            birth_date_raw="1985-08-15", birth_date="1985-08-15", birth_date_precision="exact",
            birth_place="Seoul, South Korea", birth_country_code="KR", branch="Harrison"),
    _person("seed-018", "David", "Ramirez", gender="male",
            birth_date_raw="1982-04-09", birth_date="1982-04-09", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison-Ramirez"),
    _person("seed-019", "Sofia", "Ramirez", gender="female",
            birth_date_raw="1985-11-22", birth_date="1985-11-22", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison-Ramirez"),

    # Gen 3 spouses
    _person("seed-020", "Ryan", "Cooper", gender="male",
            birth_date_raw="1974-12-01", birth_date="1974-12-01", birth_date_precision="exact",
            birth_place="Portland, OR", birth_country_code="US", branch="Harrison"),
    _person("seed-021", "Aiko", "Harrison", gender="female", birth_last_name="Tanaka",
            birth_date_raw="1980-06-15", birth_date="1980-06-15", birth_date_precision="exact",
            birth_place="Osaka, Japan", birth_country_code="JP", branch="Harrison",
            name_display_order="western"),

    # Gen 4 — great-grandchildren
    _person("seed-022", "Olivia", "Cooper", gender="female",
            birth_date_raw="2005-02-28", birth_date="2005-02-28", birth_date_precision="exact",
            birth_place="Portland, OR", birth_country_code="US", branch="Harrison"),
    _person("seed-023", "Ethan", "Cooper", gender="male",
            birth_date_raw="2008-09-14", birth_date="2008-09-14", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-024", "Kenji", "Harrison", gender="male",
            birth_date_raw="2010-03-03", birth_date="2010-03-03", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-025", "Hana", "Harrison", gender="female",
            birth_date_raw="2013-07-21", birth_date="2013-07-21", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-026", "Bartholomew Christopher Alexander", "Worthington III", gender="male",
            birth_date_raw="2000-01-01", birth_date="2000-01-01", birth_date_precision="exact",
            birth_place="Greenwich, CT", birth_country_code="US", branch="Harrison",
            nickname="Bart"),
    _person("seed-027", "Grace", "O'Brien", gender="female",
            birth_date_raw="2015-12-25", birth_date="2015-12-25", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-028", "Liam", "Ramirez", gender="male",
            birth_date_raw="2012-06-10", birth_date="2012-06-10", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison-Ramirez"),

    # Additional Gen 3 spouses / Gen 4
    _person("seed-029", "Nathan", "Wright", gender="male",
            birth_date_raw="1979-05-08", birth_date="1979-05-08", birth_date_precision="exact",
            birth_place="Denver, CO", birth_country_code="US", branch="Harrison"),
    _person("seed-110", "Chloe", "Harrison", gender="female",
            birth_date_raw="2007-04-17", birth_date="2007-04-17", birth_date_precision="exact",
            birth_place="Chicago, IL", birth_country_code="US", branch="Harrison"),
    _person("seed-111", "Noah", "Harrison", gender="male",
            birth_date_raw="2019-01-09", birth_date="2019-01-09", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
    _person("seed-112", "Ava", "Wright", gender="female",
            birth_date_raw="2011-08-23", birth_date="2011-08-23", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="Harrison"),
]

ANGLO_PARENT_CHILD = [
    # Gen 1 -> Gen 2
    _pc("seed-001", "seed-003"), _pc("seed-002", "seed-003"),
    _pc("seed-001", "seed-004"), _pc("seed-002", "seed-004"),
    _pc("seed-001", "seed-005"), _pc("seed-002", "seed-005"),
    _pc("seed-001", "seed-006"), _pc("seed-002", "seed-006"),
    # Gen 2 -> Gen 3
    _pc("seed-003", "seed-012"), _pc("seed-007", "seed-012"),
    _pc("seed-003", "seed-013"), _pc("seed-007", "seed-013"),
    _pc("seed-004", "seed-014"), _pc("seed-008", "seed-014"),
    _pc("seed-004", "seed-015"), _pc("seed-008", "seed-015"),
    _pc("seed-005", "seed-016", "step"),  # step-parent
    _pc("seed-009", "seed-016"),  # biological mother
    _pc("seed-005", "seed-017", "adoptive"),  # adopted
    _pc("seed-009", "seed-017", "adoptive"),
    _pc("seed-006", "seed-018"), _pc("seed-011", "seed-018"),
    _pc("seed-006", "seed-019"), _pc("seed-011", "seed-019"),
    # Gen 3 -> Gen 4
    _pc("seed-012", "seed-022"), _pc("seed-020", "seed-022"),
    _pc("seed-012", "seed-023"), _pc("seed-020", "seed-023"),
    _pc("seed-013", "seed-024"), _pc("seed-021", "seed-024"),
    _pc("seed-013", "seed-025"), _pc("seed-021", "seed-025"),
    _pc("seed-015", "seed-027"),
    _pc("seed-018", "seed-028"),
    # Bart is Sarah O'Brien's partner's kid — step
    _pc("seed-014", "seed-026", "step"),
    # Sofia Ramirez + Nathan Wright
    _pc("seed-019", "seed-112"), _pc("seed-029", "seed-112"),
    # Daniel + Nour's kids (added in scattered partnerships)
    _pc("seed-016", "seed-110"),
    _pc("seed-016", "seed-111"),
    _pc("seed-013", "seed-111"),  # Michael Harrison and Aiko
]

ANGLO_PARTNERSHIPS = [
    _partnership("seed-001", "seed-002", start="1945-06-10"),
    _partnership("seed-003", "seed-007", start="1973-09-01"),
    _partnership("seed-004", "seed-008", start="1974-05-18"),
    _partnership("seed-005", "seed-010", status="dissolved", start="1978-03-01", end="1983-12-01"),
    _partnership("seed-005", "seed-009", start="1984-06-15"),
    _partnership("seed-006", "seed-011", start="1980-10-10"),
    _partnership("seed-012", "seed-020", start="2002-08-20"),
    _partnership("seed-013", "seed-021", start="2008-04-12"),
    _partnership("seed-014", "seed-026", kind="domestic_partner", start="1999-01-01"),
    _partnership("seed-019", "seed-029", start="2009-05-15"),
]


# ---------------------------------------------------------------------------
# Branch 2: European / International (~20 persons)
# ---------------------------------------------------------------------------

EUROPEAN = [
    # Gen 1 — German-French founders
    _person("seed-030", "Friedrich", "Müller", gender="male",
            birth_date_raw="about 1925", birth_date="1925-01-01", birth_date_precision="approximate",
            is_living=False, death_date_raw="1998-04-12", death_date="1998-04-12",
            birth_place="Stuttgart, Germany", birth_country_code="DE", branch="Müller"),
    _person("seed-031", "Colette", "Müller", gender="female", birth_last_name="Lefèvre",
            birth_date_raw="1928-11-03", birth_date="1928-11-03", birth_date_precision="exact",
            is_living=False, death_date_raw="2015-09-27", death_date="2015-09-27",
            birth_place="Lyon, France", birth_country_code="FR", branch="Müller"),

    # Gen 2
    _person("seed-032", "Hans", "Müller", gender="male",
            birth_date_raw="1952-05-14", birth_date="1952-05-14", birth_date_precision="exact",
            birth_place="Stuttgart, Germany", birth_country_code="DE", branch="Müller"),
    _person("seed-033", "François", "Lefèvre", gender="male",
            birth_date_raw="1954-08-22", birth_date="1954-08-22", birth_date_precision="exact",
            birth_place="Lyon, France", birth_country_code="FR", branch="Lefèvre"),
    _person("seed-034", "Ingrid", "Schröder", gender="female",
            birth_date_raw="1953-02-28", birth_date="1953-02-28", birth_date_precision="exact",
            birth_place="Munich, Germany", birth_country_code="DE", branch="Müller"),
    _person("seed-035", "Анна Сергеевна", "Волкова", gender="female", patronymic="Сергеевна",
            first_name="Анна", last_name="Волкова",
            birth_date_raw="1955-12-10", birth_date="1955-12-10", birth_date_precision="exact",
            birth_place="Moscow, Russia", birth_country_code="RU", branch="Müller",
            name_display_order="patronymic"),
    _person("seed-036", "Brigitte", "Müller", gender="female",
            birth_date_raw="1956-07-19", birth_date="1956-07-19", birth_date_precision="exact",
            birth_place="Stuttgart, Germany", birth_country_code="DE", branch="Müller"),

    # Gen 3 — mixed European
    _person("seed-037", "Łukasz", "Wójcik", gender="male",
            birth_date_raw="1978-03-05", birth_date="1978-03-05", birth_date_precision="exact",
            birth_place="Warsaw, Poland", birth_country_code="PL", branch="Müller"),
    _person("seed-038", "Katarina", "Müller", gender="female",
            birth_date_raw="1980-09-12", birth_date="1980-09-12", birth_date_precision="exact",
            birth_place="Stuttgart, Germany", birth_country_code="DE", branch="Müller"),
    _person("seed-039", "Дмитрий Иванович", "Петров", gender="male", patronymic="Иванович",
            first_name="Дмитрий", last_name="Петров",
            birth_date_raw="1979-06-30", birth_date="1979-06-30", birth_date_precision="exact",
            birth_place="Saint Petersburg, Russia", birth_country_code="RU", branch="Müller",
            name_display_order="patronymic",
            bio="Дмитрий is a classical pianist who studied at the Saint Petersburg Conservatory. He performs internationally and teaches master classes."),
    _person("seed-040", "Jiří", "Dvořák", gender="male",
            birth_date_raw="1982-01-17", birth_date="1982-01-17", birth_date_precision="exact",
            birth_place="Prague, Czech Republic", birth_country_code="CZ", branch="Müller"),
    _person("seed-041", "Ágnes", "Tóth", gender="female",
            birth_date_raw="1984-04-25", birth_date="1984-04-25", birth_date_precision="exact",
            birth_place="Budapest, Hungary", birth_country_code="HU", branch="Müller"),
    _person("seed-042", "Николай", "Козлов", gender="male",
            birth_date_raw="1976-11-08", birth_date="1976-11-08", birth_date_precision="exact",
            birth_place="Novosibirsk, Russia", birth_country_code="RU", branch="Müller",
            name_display_order="patronymic"),
    _person("seed-043", "Günther", "Weber", gender="male",
            birth_date_raw="1977-08-03", birth_date="1977-08-03", birth_date_precision="exact",
            birth_place="Berlin, Germany", birth_country_code="DE", branch="Müller"),

    # Gen 4
    _person("seed-044", "Sophie", "Wójcik", gender="female",
            birth_date_raw="2006-05-11", birth_date="2006-05-11", birth_date_precision="exact",
            birth_place="Warsaw, Poland", birth_country_code="PL", branch="Müller"),
    _person("seed-045", "Максим", "Петров", gender="male",
            first_name="Максим", last_name="Петров",
            birth_date_raw="2008-12-20", birth_date="2008-12-20", birth_date_precision="exact",
            birth_place="Berlin, Germany", birth_country_code="DE", branch="Müller",
            name_display_order="patronymic"),
    _person("seed-046", "Tomáš", "Dvořák", gender="male",
            birth_date_raw="2011-07-14", birth_date="2011-07-14", birth_date_precision="exact",
            birth_place="Prague, Czech Republic", birth_country_code="CZ", branch="Müller"),
    # Guardian ward — orphan taken in by Brigitte
    _person("seed-047", "Elena", "Popescu", gender="female",
            birth_date_raw="2005-02-19", birth_date="2005-02-19", birth_date_precision="exact",
            birth_place="Bucharest, Romania", birth_country_code="RO", branch="Müller"),

    # Additional European persons
    _person("seed-048", "Светлана", "Козлова", gender="female",
            first_name="Светлана", last_name="Козлова",
            birth_date_raw="1979-03-22", birth_date="1979-03-22", birth_date_precision="exact",
            birth_place="Novosibirsk, Russia", birth_country_code="RU", branch="Müller",
            name_display_order="patronymic"),
    _person("seed-049", "Marta", "Weber", gender="female",
            birth_date_raw="2009-10-06", birth_date="2009-10-06", birth_date_precision="exact",
            birth_place="Berlin, Germany", birth_country_code="DE", branch="Müller"),
    _person("seed-113", "Aleksei", "Kozlov", gender="male",
            birth_date_raw="2005-07-30", birth_date="2005-07-30", birth_date_precision="exact",
            birth_place="Novosibirsk, Russia", birth_country_code="RU", branch="Müller"),
]

EUROPEAN_PARENT_CHILD = [
    _pc("seed-030", "seed-032"), _pc("seed-031", "seed-032"),
    _pc("seed-030", "seed-036"), _pc("seed-031", "seed-036"),
    _pc("seed-032", "seed-038"), _pc("seed-034", "seed-038"),
    _pc("seed-032", "seed-039"),  # Hans is Dmitry's father (cross-cultural)
    _pc("seed-035", "seed-039"),  # Anna is Dmitry's mother
    _pc("seed-033", "seed-040", "adoptive"),  # François adopted Jiří
    _pc("seed-040", "seed-046"),  # Jiří -> Tomáš
    _pc("seed-041", "seed-046"),
    _pc("seed-037", "seed-044"), _pc("seed-038", "seed-044"),
    _pc("seed-039", "seed-045"),
    _pc("seed-036", "seed-047", "guardian"),  # Brigitte is Elena's guardian
    _pc("seed-042", "seed-113"), _pc("seed-048", "seed-113"),  # Nikolai + Svetlana -> Aleksei
    _pc("seed-043", "seed-049"),  # Günther -> Marta
]

EUROPEAN_PARTNERSHIPS = [
    _partnership("seed-030", "seed-031", start="1950-06-01"),
    _partnership("seed-032", "seed-034", start="1976-09-15"),
    _partnership("seed-032", "seed-035", kind="domestic_partner", start="1978-01-01"),
    _partnership("seed-037", "seed-038", start="2004-07-20"),
    _partnership("seed-039", "seed-045", kind="co_parent"),  # won't work — 045 is child. Skip below.
    _partnership("seed-040", "seed-041", start="2009-11-01"),
    _partnership("seed-042", "seed-048", start="2003-08-15"),  # Nikolai + Svetlana
]


# ---------------------------------------------------------------------------
# Branch 3: East Asian (~15 persons)
# ---------------------------------------------------------------------------

EAST_ASIAN = [
    # Gen 1 — Chinese founders
    _person("seed-050", "大山", "刘", gender="male",
            first_name="大山", last_name="刘",
            birth_date_raw="circa 1930", birth_date="1930-01-01", birth_date_precision="approximate",
            is_living=False, death_date_raw="2005-03-18", death_date="2005-03-18",
            birth_place="Shanghai, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),
    _person("seed-051", "美玲", "陈", gender="female",
            first_name="美玲", last_name="陈",
            birth_date_raw="1932-09-01", birth_date="1932-09-01", birth_date_precision="month",
            is_living=False, death_date_raw="2018-01-05", death_date="2018-01-05",
            birth_place="Shanghai, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),

    # Gen 2
    _person("seed-052", "明", "李", gender="male",
            first_name="明", last_name="李",
            birth_date_raw="1958-04-12", birth_date="1958-04-12", birth_date_precision="exact",
            birth_place="Shanghai, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern",
            bio="李明 is a retired professor of mathematics at Fudan University. He emigrated to the US in 1990 and taught at UC Berkeley."),
    _person("seed-053", "小红", "王", gender="female",
            first_name="小红", last_name="王",
            birth_date_raw="1960-07-22", birth_date="1960-07-22", birth_date_precision="exact",
            birth_place="Beijing, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),
    _person("seed-054", "伟", "张", gender="male",
            first_name="伟", last_name="张",
            birth_date_raw="1962-11-05", birth_date="1962-11-05", birth_date_precision="exact",
            birth_place="Shanghai, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),
    _person("seed-055", "Li", "Bo", gender="male",
            birth_date_raw="1965-03-08", birth_date="1965-03-08", birth_date_precision="exact",
            birth_place="Guangzhou, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),  # Very short name

    # Gen 2 — Japanese connection
    _person("seed-056", "太郎", "田中", gender="male",
            first_name="太郎", last_name="田中",
            birth_date_raw="1957-02-14", birth_date="1957-02-14", birth_date_precision="exact",
            birth_place="Tokyo, Japan", birth_country_code="JP", branch="Tanaka",
            name_display_order="eastern"),
    _person("seed-057", "花子", "佐藤", gender="female",
            first_name="花子", last_name="佐藤",
            birth_date_raw="1960-10-30", birth_date="1960-10-30", birth_date_precision="exact",
            birth_place="Osaka, Japan", birth_country_code="JP", branch="Tanaka",
            name_display_order="eastern"),

    # Gen 3
    _person("seed-058", "Wei", "Li", gender="male",
            birth_date_raw="1985-06-18", birth_date="1985-06-18", birth_date_precision="exact",
            birth_place="San Francisco, CA", birth_country_code="US", branch="Liu"),
    _person("seed-059", "Mei", "Li", gender="female",
            birth_date_raw="1988-01-25", birth_date="1988-01-25", birth_date_precision="exact",
            birth_place="San Francisco, CA", birth_country_code="US", branch="Liu"),
    _person("seed-060", "健一", "山田", gender="male",
            first_name="健一", last_name="山田",
            birth_date_raw="1984-09-07", birth_date="1984-09-07", birth_date_precision="exact",
            birth_place="Tokyo, Japan", birth_country_code="JP", branch="Tanaka",
            name_display_order="eastern"),
    # Mei married Kenichi (cross-Chinese-Japanese)
    _person("seed-061", "Yuki", "Yamada", gender="female",
            birth_date_raw="2014-04-03", birth_date="2014-04-03", birth_date_precision="exact",
            birth_place="Tokyo, Japan", birth_country_code="JP", branch="Tanaka"),
    _person("seed-062", "Jason", "Li", gender="male",
            birth_date_raw="2016-11-19", birth_date="2016-11-19", birth_date_precision="exact",
            birth_place="San Francisco, CA", birth_country_code="US", branch="Liu"),

    # Gen 3 — unknown dates person
    _person("seed-063", "Hua", "Zhang", gender="female",
            birth_place="Nanjing, China", birth_country_code="CN", branch="Liu",
            name_display_order="eastern"),  # No birth date at all
]

EAST_ASIAN_PARENT_CHILD = [
    _pc("seed-050", "seed-052"), _pc("seed-051", "seed-052"),
    _pc("seed-050", "seed-054"), _pc("seed-051", "seed-054"),
    _pc("seed-052", "seed-058"), _pc("seed-053", "seed-058"),
    _pc("seed-052", "seed-059"), _pc("seed-053", "seed-059"),
    _pc("seed-056", "seed-060"), _pc("seed-057", "seed-060"),
    _pc("seed-059", "seed-061"), _pc("seed-060", "seed-061"),
    _pc("seed-058", "seed-062"), _pc("seed-063", "seed-062"),
]

EAST_ASIAN_PARTNERSHIPS = [
    _partnership("seed-050", "seed-051", start="1955-10-01"),
    _partnership("seed-052", "seed-053", start="1983-03-20"),
    _partnership("seed-056", "seed-057", start="1982-11-15"),
    _partnership("seed-059", "seed-060", start="2012-06-01"),
    _partnership("seed-055", "seed-054", kind="domestic_partner"),
]


# ---------------------------------------------------------------------------
# Branch 4: Latin / Mixed (~15 persons)
# ---------------------------------------------------------------------------

LATIN = [
    # Gen 1
    _person("seed-070", "José María", "García López", gender="male",
            birth_date_raw="1930-12-12", birth_date="1930-12-12", birth_date_precision="exact",
            is_living=False, death_date_raw="2008-07-04", death_date="2008-07-04",
            birth_place="Guadalajara, Mexico", birth_country_code="MX", branch="García"),
    _person("seed-071", "María del Carmen", "Herrera", gender="female",
            birth_date_raw="1933-05-20", birth_date="1933-05-20", birth_date_precision="exact",
            birth_place="Puebla, Mexico", birth_country_code="MX", branch="García"),

    # Gen 2
    _person("seed-072", "Alejandro", "García", gender="male",
            birth_date_raw="1958-02-08", birth_date="1958-02-08", birth_date_precision="exact",
            birth_place="Guadalajara, Mexico", birth_country_code="MX", branch="García",
            bio="Alejandro is a celebrated architect who designed several landmark buildings in Mexico City. He splits his time between Mexico and Boston."),
    _person("seed-073", "Isabel", "García", gender="female",
            birth_date_raw="1961-09-15", birth_date="1961-09-15", birth_date_precision="exact",
            birth_place="Guadalajara, Mexico", birth_country_code="MX", branch="García"),
    _person("seed-074", "Rosa", "Mendoza", gender="female",
            birth_date_raw="1960-04-30", birth_date="1960-04-30", birth_date_precision="exact",
            birth_place="Oaxaca, Mexico", birth_country_code="MX", branch="García"),
    # Carlos Ramirez (seed-011) is Patricia Harrison's husband — connects branches
    # Isabel married into European branch
    _person("seed-075", "Pierre", "Dubois", gender="male",
            birth_date_raw="1959-06-17", birth_date="1959-06-17", birth_date_precision="exact",
            birth_place="Paris, France", birth_country_code="FR", branch="García"),

    # Gen 3
    _person("seed-076", "Valentina", "García", gender="female",
            birth_date_raw="1986-03-14", birth_date="1986-03-14", birth_date_precision="exact",
            birth_place="Mexico City, Mexico", birth_country_code="MX", branch="García"),
    _person("seed-077", "Diego", "García", gender="male",
            birth_date_raw="1989-08-29", birth_date="1989-08-29", birth_date_precision="exact",
            birth_place="Mexico City, Mexico", birth_country_code="MX", branch="García"),
    _person("seed-078", "Camille", "Dubois", gender="female",
            birth_date_raw="1987-01-11", birth_date="1987-01-11", birth_date_precision="exact",
            birth_place="Paris, France", birth_country_code="FR", branch="García"),
    _person("seed-079", "Lucía", "Dubois", gender="female",
            birth_date_raw="1990-05-06", birth_date="1990-05-06", birth_date_precision="exact",
            birth_place="Paris, France", birth_country_code="FR", branch="García"),
    _person("seed-080", "Marco", "Rossi", gender="male",
            birth_date_raw="1984-10-21", birth_date="1984-10-21", birth_date_precision="exact",
            birth_place="Rome, Italy", birth_country_code="IT", branch="García"),

    # Gen 4
    _person("seed-081", "Mateo", "Rossi", gender="male",
            birth_date_raw="2015-07-30", birth_date="2015-07-30", birth_date_precision="exact",
            birth_place="Rome, Italy", birth_country_code="IT", branch="García"),
    _person("seed-082", "Luna", "García", gender="female",
            birth_date_raw="2018-02-14", birth_date="2018-02-14", birth_date_precision="exact",
            birth_place="Mexico City, Mexico", birth_country_code="MX", branch="García"),
    _person("seed-083", "Santiago", "García", gender="male",
            birth_date_raw="2020-11-01", birth_date="2020-11-01", birth_date_precision="exact",
            birth_place="Boston, MA", birth_country_code="US", branch="García"),
]

LATIN_PARENT_CHILD = [
    _pc("seed-070", "seed-072"), _pc("seed-071", "seed-072"),
    _pc("seed-070", "seed-073"), _pc("seed-071", "seed-073"),
    _pc("seed-070", "seed-011"), _pc("seed-071", "seed-011"),  # Carlos Ramirez is García child
    _pc("seed-072", "seed-076"), _pc("seed-074", "seed-076"),
    _pc("seed-072", "seed-077"), _pc("seed-074", "seed-077"),
    _pc("seed-073", "seed-078"), _pc("seed-075", "seed-078"),
    _pc("seed-073", "seed-079"), _pc("seed-075", "seed-079"),
    _pc("seed-076", "seed-081"), _pc("seed-080", "seed-081"),
    _pc("seed-077", "seed-082"),
    _pc("seed-077", "seed-083"),
]

LATIN_PARTNERSHIPS = [
    _partnership("seed-070", "seed-071", start="1955-04-15"),
    _partnership("seed-072", "seed-074", start="1983-12-01"),
    _partnership("seed-073", "seed-075", start="1985-06-20"),
    _partnership("seed-076", "seed-080", start="2012-09-10"),
]


# ---------------------------------------------------------------------------
# Branch 5: Scattered / Arabic + single parents (~12 persons)
# ---------------------------------------------------------------------------

SCATTERED = [
    # Arabic family
    _person("seed-090", "أحمد", "محمد", gender="male",
            first_name="أحمد", last_name="محمد",
            birth_date_raw="1960-01-15", birth_date="1960-01-15", birth_date_precision="exact",
            birth_place="Cairo, Egypt", birth_country_code="EG", branch="Mohammed"),
    _person("seed-091", "فاطمة", "الحسن", gender="female",
            first_name="فاطمة", last_name="الحسن",
            birth_date_raw="1963-08-22", birth_date="1963-08-22", birth_date_precision="exact",
            birth_place="Amman, Jordan", birth_country_code="JO", branch="Mohammed"),
    _person("seed-092", "يوسف", "محمد", gender="male",
            first_name="يوسف", last_name="محمد",
            birth_date_raw="1988-05-10", birth_date="1988-05-10", birth_date_precision="exact",
            birth_place="Cairo, Egypt", birth_country_code="EG", branch="Mohammed"),
    _person("seed-093", "نور", "محمد", gender="female",
            first_name="نور", last_name="محمد",
            birth_date_raw="1991-12-03", birth_date="1991-12-03", birth_date_precision="exact",
            birth_place="Cairo, Egypt", birth_country_code="EG", branch="Mohammed"),

    # Co-parenting arrangement
    _person("seed-094", "Rachel", "Kim", gender="female",
            birth_date_raw="1985-09-14", birth_date="1985-09-14", birth_date_precision="exact",
            birth_place="Los Angeles, CA", birth_country_code="US", branch="scattered"),
    _person("seed-095", "Omar", "Hassan", gender="male",
            birth_date_raw="1983-03-27", birth_date="1983-03-27", birth_date_precision="exact",
            birth_place="Beirut, Lebanon", birth_country_code="LB", branch="scattered"),
    _person("seed-096", "Zara", "Hassan", gender="female",
            birth_date_raw="2015-06-01", birth_date="2015-06-01", birth_date_precision="exact",
            birth_place="Los Angeles, CA", birth_country_code="US", branch="scattered"),

    # Single parent
    _person("seed-097", "Ingrid", "Larsson", gender="female",
            birth_date_raw="1978-10-05", birth_date="1978-10-05", birth_date_precision="exact",
            birth_place="Stockholm, Sweden", birth_country_code="SE", branch="scattered"),
    _person("seed-098", "Erik", "Larsson", gender="male",
            birth_date_raw="2010-08-19", birth_date="2010-08-19", birth_date_precision="exact",
            birth_place="Stockholm, Sweden", birth_country_code="SE", branch="scattered"),

    # Unknown date persons
    _person("seed-099", "Amara", "Okafor", gender="female",
            birth_place="Lagos, Nigeria", birth_country_code="NG", branch="scattered"),
    _person("seed-100", "Kofi", "Mensah", gender="male",
            birth_date_raw="1970-01-01", birth_date="1970-01-01", birth_date_precision="year",
            birth_place="Accra, Ghana", birth_country_code="GH", branch="scattered"),
    # Nour married into Anglo branch via Daniel Harrison
    _person("seed-101", "Tariq", "Al-Rashid", gender="male",
            birth_date_raw="1979-04-12", birth_date="1979-04-12", birth_date_precision="exact",
            birth_place="Dubai, UAE", birth_country_code="AE", branch="scattered"),

    # Additional scattered persons
    _person("seed-102", "Priya", "Sharma", gender="female",
            birth_date_raw="1982-07-15", birth_date="1982-07-15", birth_date_precision="exact",
            birth_place="Mumbai, India", birth_country_code="IN", branch="scattered"),
    _person("seed-103", "Arun", "Patel", gender="male",
            birth_date_raw="1980-02-28", birth_date="1980-02-28", birth_date_precision="exact",
            birth_place="Delhi, India", birth_country_code="IN", branch="scattered"),
    _person("seed-104", "Ananya", "Patel", gender="female",
            birth_date_raw="2012-11-05", birth_date="2012-11-05", birth_date_precision="exact",
            birth_place="London, England", birth_country_code="GB", branch="scattered"),
    _person("seed-105", "Ravi", "Patel", gender="male",
            birth_date_raw="2015-03-18", birth_date="2015-03-18", birth_date_precision="exact",
            birth_place="London, England", birth_country_code="GB", branch="scattered"),
    _person("seed-106", "Suki", "Nakamura", gender="female",
            birth_date_raw="1990-06-22", birth_date="1990-06-22", birth_date_precision="exact",
            birth_place="Kyoto, Japan", birth_country_code="JP", branch="scattered"),
    _person("seed-107", "Emeka", "Okafor", gender="male",
            birth_date_raw="1988-09-10", birth_date="1988-09-10", birth_date_precision="exact",
            birth_place="Lagos, Nigeria", birth_country_code="NG", branch="scattered"),
    _person("seed-108", "Chioma", "Okafor", gender="female",
            birth_date_raw="2017-01-30", birth_date="2017-01-30", birth_date_precision="exact",
            birth_place="Lagos, Nigeria", birth_country_code="NG", branch="scattered"),
    _person("seed-109", "Kwame", "Mensah", gender="male",
            birth_date_raw="2000-12-12", birth_date="2000-12-12", birth_date_precision="exact",
            birth_place="Accra, Ghana", birth_country_code="GH", branch="scattered"),
]

SCATTERED_PARENT_CHILD = [
    _pc("seed-090", "seed-092"), _pc("seed-091", "seed-092"),
    _pc("seed-090", "seed-093"), _pc("seed-091", "seed-093"),
    _pc("seed-094", "seed-096"), _pc("seed-095", "seed-096"),
    _pc("seed-097", "seed-098"),
    _pc("seed-102", "seed-104"), _pc("seed-103", "seed-104"),  # Priya + Arun -> Ananya
    _pc("seed-102", "seed-105"), _pc("seed-103", "seed-105"),  # Priya + Arun -> Ravi
    _pc("seed-099", "seed-108"), _pc("seed-107", "seed-108"),  # Amara + Emeka -> Chioma
    _pc("seed-100", "seed-109"),  # Kofi -> Kwame (single parent)
]

SCATTERED_PARTNERSHIPS = [
    _partnership("seed-090", "seed-091", start="1985-03-01"),
    _partnership("seed-094", "seed-095", kind="co_parent", start="2014-01-01"),
    _partnership("seed-016", "seed-093", start="2015-06-20"),  # Daniel Harrison + Nour Mohammed
    _partnership("seed-092", "seed-099", kind="domestic_partner"),  # Youssef + Amara
    _partnership("seed-102", "seed-103", start="2010-12-20"),  # Priya + Arun
    _partnership("seed-099", "seed-107", kind="co_parent"),  # Amara + Emeka
]


# ---------------------------------------------------------------------------
# Rich data for ~12 select persons
# ---------------------------------------------------------------------------

def _edu(inst, deg, yr):
    return {"institution": inst, "degree": deg, "year_end": yr}

def _job(co, title, ys, ye=None):
    d = {"company": co, "title": title, "year_start": ys}
    if ye: d["year_end"] = ye
    return d

def _place(p, cc, ys, ye=None):
    d = {"place": p, "country_code": cc, "year_start": ys}
    if ye: d["year_end"] = ye
    return d

RICH_DATA: dict[str, dict] = {
    "seed-003": {  # James Harrison
        "languages": ["en"],
        "education": [_edu("Harvard Law School", "J.D.", "1973"), _edu("Boston College", "B.A. Political Science", "1970")],
        "career": [_job("Harrison & Associates", "Senior Partner", "1980", "2015"), _job("Suffolk County DA", "Assistant DA", "1973", "1980")],
        "place_history": [_place("Boston, MA", "US", "1948", "2015"), _place("Cape Cod, MA", "US", "2015")],
        "residence_place": "Cape Cod, MA", "residence_country_code": "US",
    },
    "seed-012": {  # Emily Harrison
        "languages": ["en", "fr"],
        "education": [_edu("MIT", "Ph.D. Marine Biology", "2003"), _edu("Brown University", "B.S. Biology", "1997")],
        "career": [_job("Woods Hole Oceanographic", "Senior Researcher", "2005")],
        "place_history": [_place("Boston, MA", "US", "1975", "1993"), _place("Providence, RI", "US", "1993", "1997"), _place("Woods Hole, MA", "US", "2003")],
        "residence_place": "Woods Hole, MA", "residence_country_code": "US",
    },
    "seed-032": {  # Hans Müller
        "languages": ["de", "fr", "en"],
        "education": [_edu("Universität Stuttgart", "Diplom-Ingenieur", "1976")],
        "career": [_job("Bosch GmbH", "Engineering Director", "1985", "2018")],
        "residence_place": "Stuttgart, Germany", "residence_country_code": "DE",
    },
    "seed-039": {  # Дмитрий Петров
        "languages": ["ru", "de", "en"],
        "education": [_edu("Saint Petersburg Conservatory", "Master of Music", "2003")],
        "career": [_job("Berlin Philharmonic", "Guest Pianist", "2005")],
        "place_history": [_place("Saint Petersburg, Russia", "RU", "1979", "2004"), _place("Berlin, Germany", "DE", "2004")],
        "residence_place": "Berlin, Germany", "residence_country_code": "DE",
    },
    "seed-052": {  # 李明
        "languages": ["zh", "en"],
        "education": [_edu("Fudan University", "M.S. Mathematics", "1982"), _edu("UC Berkeley", "Ph.D. Mathematics", "1988")],
        "career": [_job("UC Berkeley", "Professor of Mathematics", "1990", "2020"), _job("Fudan University", "Lecturer", "1982", "1986")],
        "place_history": [_place("Shanghai, China", "CN", "1958", "1986"), _place("Berkeley, CA", "US", "1986")],
        "residence_place": "Berkeley, CA", "residence_country_code": "US",
    },
    "seed-056": {  # 田中太郎
        "languages": ["ja", "en"],
        "education": [_edu("University of Tokyo", "B.Eng.", "1980")],
        "career": [_job("Sony Corporation", "VP Engineering", "1995", "2017")],
        "residence_place": "Tokyo, Japan", "residence_country_code": "JP",
    },
    "seed-072": {  # Alejandro García
        "languages": ["es", "en", "fr"],
        "education": [_edu("UNAM", "Architecture", "1982"), _edu("Harvard GSD", "M.Arch", "1985")],
        "career": [_job("García Arquitectos", "Principal", "1988")],
        "place_history": [_place("Guadalajara, Mexico", "MX", "1958", "1976"), _place("Mexico City", "MX", "1976", "1983"), _place("Cambridge, MA", "US", "1983", "1985"), _place("Mexico City", "MX", "1985")],
        "residence_place": "Mexico City, Mexico", "residence_country_code": "MX",
    },
    "seed-090": {  # أحمد محمد
        "languages": ["ar", "en"],
        "education": [_edu("Cairo University", "B.Sc. Engineering", "1983")],
        "career": [_job("Egyptian Ministry of Infrastructure", "Chief Engineer", "1990")],
        "residence_place": "Cairo, Egypt", "residence_country_code": "EG",
    },
    "seed-037": {  # Łukasz Wójcik
        "languages": ["pl", "de", "en"],
        "education": [_edu("Warsaw University of Technology", "M.Sc. Computer Science", "2002")],
        "career": [_job("SAP", "Software Architect", "2005")],
        "residence_place": "Stuttgart, Germany", "residence_country_code": "DE",
    },
    "seed-076": {  # Valentina García
        "languages": ["es", "it", "en"],
        "education": [_edu("Politecnico di Milano", "M.Des.", "2010")],
        "career": [_job("Rossi & García Design", "Co-Founder", "2013")],
        "place_history": [_place("Mexico City", "MX", "1986", "2008"), _place("Milan, Italy", "IT", "2008", "2012"), _place("Rome, Italy", "IT", "2012")],
        "residence_place": "Rome, Italy", "residence_country_code": "IT",
    },
    "seed-097": {  # Ingrid Larsson
        "languages": ["sv", "en", "no"],
        "education": [_edu("KTH Royal Institute of Technology", "M.Sc. Environmental Engineering", "2003")],
        "career": [_job("IKEA", "Sustainability Director", "2010")],
        "residence_place": "Stockholm, Sweden", "residence_country_code": "SE",
    },
    "seed-041": {  # Ágnes Tóth
        "languages": ["hu", "cs", "de", "en"],
        "career": [_job("Czech Philharmonic", "First Violin", "2008")],
        "residence_place": "Prague, Czech Republic", "residence_country_code": "CZ",
    },
}


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------

# JSON list fields that use property setters
_JSON_LIST_FIELDS = {"languages", "education", "career", "place_history", "organizations",
                     "admixture", "medical_conditions", "contact_phones", "contact_emails",
                     "social_accounts", "name_history", "contact_addresses", "alternate_nicknames"}

# Scalar fields set directly on the person dict (non-JSON, non-list)
_RICH_SCALAR_FIELDS = {"residence_place", "residence_country_code"}


def _create_person(data: dict, rich: dict | None = None) -> Person:
    """Instantiate a Person from a data dict, applying rich data if provided."""
    # Separate JSON list fields from scalar fields
    json_fields = {}
    scalar_fields = {}
    for k, v in data.items():
        if k in _JSON_LIST_FIELDS:
            json_fields[k] = v
        else:
            scalar_fields[k] = v

    # Generate slug
    pid = scalar_fields["id"]
    slug = generate_slug(scalar_fields.get("first_name"), scalar_fields.get("last_name"), pid)
    scalar_fields["slug"] = slug

    person = Person(**scalar_fields)

    # Apply JSON list fields via property setters
    for k, v in json_fields.items():
        setattr(person, k, v)

    # Apply rich data
    if rich:
        for k, v in rich.items():
            if k in _JSON_LIST_FIELDS:
                setattr(person, k, v)
            elif k in _RICH_SCALAR_FIELDS:
                setattr(person, k, v)

    return person


async def seed() -> None:
    async with async_session_factory() as session:
        # ------------------------------------------------------------------
        # Clean slate — delete in FK-safe order
        # ------------------------------------------------------------------
        print("Clearing existing data...")
        await session.execute(delete(EntityRevision))
        await session.execute(delete(AuditLog))
        await session.execute(delete(SavedRecord))
        await session.execute(delete(Media))
        await session.execute(delete(Partnership))
        await session.execute(delete(ParentChild))
        await session.execute(delete(MagicLinkToken))
        await session.execute(delete(UserSession))
        await session.execute(delete(Invite))
        await session.execute(delete(Person))
        await session.flush()

        # ------------------------------------------------------------------
        # Create persons
        # ------------------------------------------------------------------
        all_persons_data = ANGLO + EUROPEAN + EAST_ASIAN + LATIN + SCATTERED
        person_count = 0
        for data in all_persons_data:
            rich = RICH_DATA.get(data["id"])
            person = _create_person(data, rich)
            session.add(person)
            person_count += 1

        await session.flush()

        # ------------------------------------------------------------------
        # Create relationships
        # ------------------------------------------------------------------
        all_pc = ANGLO_PARENT_CHILD + EUROPEAN_PARENT_CHILD + EAST_ASIAN_PARENT_CHILD + LATIN_PARENT_CHILD + SCATTERED_PARENT_CHILD
        # Deduplicate (same parent+child+kind)
        seen_pc: set[tuple[str, str, str]] = set()
        pc_count = 0
        for data in all_pc:
            key = (data["parent_id"], data["child_id"], data["kind"])
            if key in seen_pc:
                continue
            seen_pc.add(key)
            session.add(ParentChild(**data))
            pc_count += 1

        all_partnerships = ANGLO_PARTNERSHIPS + EUROPEAN_PARTNERSHIPS + EAST_ASIAN_PARTNERSHIPS + LATIN_PARTNERSHIPS + SCATTERED_PARTNERSHIPS
        p_count = 0
        for data in all_partnerships:
            session.add(Partnership(**data))
            p_count += 1

        await session.flush()

        # ------------------------------------------------------------------
        # Create admin session for Playwright
        # ------------------------------------------------------------------
        admin_id = "seed-003"
        token = await create_session(session, admin_id, "google_oauth")
        print(f"Admin session token: {token}")

        await session.commit()

        print(f"Seeded {person_count} persons, {pc_count} parent-child, {p_count} partnerships")
        print("Done.")


def main():
    asyncio.run(seed())


if __name__ == "__main__":
    main()
