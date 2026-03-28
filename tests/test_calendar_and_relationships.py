"""Tests for family calendar, relationship calculator, and visual relationship types."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.person import Person
from app.routes.calendar import _decorate_calendar_events
from app.services.calendar_service import clear_external_calendar_cache


# ── Calendar API ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calendar_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/calendar")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_calendar_default_month(admin_client: AsyncClient):
    resp = await admin_client.get("/api/calendar")
    assert resp.status_code == 200
    data = resp.json()
    assert "year" in data
    assert "month" in data
    assert "month_name" in data
    assert isinstance(data["events"], list)


@pytest.mark.asyncio
async def test_calendar_specific_month(admin_client: AsyncClient):
    resp = await admin_client.get("/api/calendar?month=2026-03")
    assert resp.status_code == 200
    data = resp.json()
    assert data["year"] == 2026
    assert data["month"] == 3
    assert data["month_name"] == "March"


@pytest.mark.asyncio
async def test_calendar_invalid_month_fallback(admin_client: AsyncClient):
    resp = await admin_client.get("/api/calendar?month=invalid")
    assert resp.status_code == 200
    # Falls back to current month
    data = resp.json()
    assert data["year"] > 0
    assert 1 <= data["month"] <= 12


@pytest.mark.asyncio
async def test_calendar_events_have_expected_fields(admin_client: AsyncClient):
    """Add a person with a birth date and verify it appears as calendar event."""
    # Create a person with a March birth date
    resp = await admin_client.post("/api/persons", json={
        "first_name": "CalendarTest",
        "last_name": "Person",
        "birth_date": "1990-03-15",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201

    # Check March calendar
    resp = await admin_client.get("/api/calendar?month=2026-03")
    assert resp.status_code == 200
    data = resp.json()
    birthday_events = [e for e in data["events"] if e["type"] == "birthday" and "CalendarTest" in e["label"]]
    assert len(birthday_events) >= 1
    ev = birthday_events[0]
    assert ev["day"] == 15
    assert "person_id" in ev
    assert ev["person_name"] == "CalendarTest Person"
    assert ev["age_turning"] == 36


@pytest.mark.asyncio
async def test_calendar_partnership_anniversary(admin_client: AsyncClient):
    """Partnership start_date should appear as anniversary event."""
    # Tyler and Yuliya already have a partnership but without start_date in seed
    # Create two people with a partnership that has a start_date
    resp1 = await admin_client.post("/api/persons", json={
        "first_name": "AnnivA",
        "last_name": "Test",
    })
    assert resp1.status_code == 201
    id_a = resp1.json()["id"]

    resp2 = await admin_client.post("/api/persons", json={
        "first_name": "AnnivB",
        "last_name": "Test",
    })
    assert resp2.status_code == 201
    id_b = resp2.json()["id"]

    resp = await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": id_a,
        "person_b_id": id_b,
        "kind": "married",
        "status": "active",
        "start_date": "2000-06-20",
        "start_date_precision": "exact",
    })
    assert resp.status_code == 201

    # Check June calendar
    resp = await admin_client.get("/api/calendar?month=2026-06")
    assert resp.status_code == 200
    data = resp.json()
    anniv_events = [e for e in data["events"] if e["type"] == "anniversary"]
    assert len(anniv_events) >= 1
    matching = [e for e in anniv_events if "AnnivA" in e["label"] or "AnnivB" in e["label"]]
    assert matching
    assert matching[0]["anniversary_years"] == 26


@pytest.mark.asyncio
async def test_calendar_root_person_uses_display_name(admin_client: AsyncClient):
    """Root person events should use display_name, not raw name."""
    # Root person has no birth date in seed, but verify through API response
    resp = await admin_client.get("/api/calendar?month=2026-01")
    assert resp.status_code == 200
    data = resp.json()
    # No root person first_name/last_name should appear
    for ev in data["events"]:
        # The root person display_name is "Our Family"
        # Their raw name fields should NOT appear
        assert "Our" not in ev["label"] or "Our Family" in ev["label"]


@pytest.mark.asyncio
async def test_calendar_page_renders(admin_client: AsyncClient):
    resp = await admin_client.get("/calendar")
    assert resp.status_code == 200
    # Title comes from i18n key calendar.title (en: "Family Calendar")
    assert "Family Calendar" in resp.text
    assert resp.text.index('id="calendar-grid-container"') < resp.text.index('id="calendar-manager"')
    assert "Close" in resp.text
    assert "common.close" not in resp.text


@pytest.mark.asyncio
async def test_calendar_partial_returns_html(admin_client: AsyncClient):
    resp = await admin_client.get("/partials/calendar-grid?month=2026-03")
    assert resp.status_code == 200
    assert "March" in resp.text


@pytest.mark.asyncio
async def test_calendar_birthdays_use_raw_date_fallback(admin_client: AsyncClient):
    """Legacy raw-only dates should still produce birthdays on the calendar."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Slash",
        "last_name": "Date",
        "birth_date_raw": "07/29/1947",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/calendar?month=2026-07")
    assert resp.status_code == 200
    data = resp.json()
    birthday_events = [e for e in data["events"] if e["type"] == "birthday" and "Slash Date" in e["label"]]
    assert len(birthday_events) == 1
    assert birthday_events[0]["day"] == 29


@pytest.mark.asyncio
async def test_calendar_external_ical_feed_events_appear(admin_client: AsyncClient, monkeypatch):
    clear_external_calendar_cache()

    async def fake_fetch_calendar_ics(url: str) -> bytes:
        assert url == "https://example.com/holidays.ics"
        return b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Family Book Test//EN
BEGIN:VEVENT
UID:test-christmas@example.com
DTSTART;VALUE=DATE:20201225
RRULE:FREQ=YEARLY
SUMMARY:Christmas Day
END:VEVENT
END:VCALENDAR
"""

    monkeypatch.setattr("app.services.calendar_service._fetch_calendar_ics", fake_fetch_calendar_ics)

    resp = await admin_client.post("/api/calendar/sources", json={
        "name": "Global Holidays",
        "url": "https://example.com/holidays.ics",
        "source_type": "holiday",
        "enabled": True,
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/calendar?month=2026-12")
    assert resp.status_code == 200
    data = resp.json()
    external_events = [e for e in data["events"] if e["type"] == "external" and e["label"] == "Christmas Day"]
    assert len(external_events) == 1
    assert external_events[0]["day"] == 25
    assert external_events[0]["source_name"] == "Global Holidays"


@pytest.mark.asyncio
async def test_calendar_page_renders_external_sources_panel_for_admin(admin_client: AsyncClient):
    resp = await admin_client.get("/calendar")
    assert resp.status_code == 200
    assert "Imported calendars" in resp.text
    assert "Add feed" in resp.text
    assert "Manage Calendars" in resp.text
    assert "Subscribe to this calendar" in resp.text


@pytest.mark.asyncio
async def test_calendar_page_uses_richer_event_labels(admin_client: AsyncClient):
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Aging",
        "last_name": "Person",
        "birth_date": "1990-03-15",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/partials/calendar-grid?month=2026-03")
    assert resp.status_code == 200
    assert "Aging Person turns 36" in resp.text


def test_calendar_event_decoration_uses_locale_safe_anniversary_copy():
    events = _decorate_calendar_events(
        [
            {
                "date": "2026-03-20",
                "day": 20,
                "type": "anniversary",
                "label": "Pareja Uno & Pareja Dos anniversary",
                "person_id": None,
                "name_a": "Pareja Uno",
                "name_b": "Pareja Dos",
                "anniversary_years": 12,
                "source_name": None,
                "source_type": None,
            }
        ],
        "es",
    )
    assert events[0]["display_label"] == "Pareja Uno y Pareja Dos celebran 12 años juntos"
    assert events[0]["display_short_label"] == "12 años"


@pytest.mark.asyncio
async def test_calendar_feed_requires_valid_token(client: AsyncClient):
    resp = await client.get("/calendar/feed.ics?token=bad-token")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_calendar_feed_rejects_invalid_type(admin_client: AsyncClient, seeded_db):
    result = await seeded_db.execute(
        select(Person).where(Person.id == "tyler-000-0000-0000-000000000002")
    )
    tyler = result.scalar_one()

    resp = await admin_client.get(f"/calendar/feed.ics?token={tyler.calendar_feed_token}&types=birthdy")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_calendar_feed_exports_birthdays(admin_client: AsyncClient, seeded_db):
    result = await seeded_db.execute(
        select(Person).where(Person.id == "tyler-000-0000-0000-000000000002")
    )
    tyler = result.scalar_one()
    tyler.birth_date = "1990-03-15"
    tyler.birth_date_precision = "exact"
    await seeded_db.commit()

    resp = await admin_client.get(f"/calendar/feed.ics?token={tyler.calendar_feed_token}&types=birthday")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/calendar")
    text = resp.text
    assert "BEGIN:VCALENDAR" in text
    assert "SUMMARY:Tyler Martin's birthday" in text
    assert "RRULE:FREQ=YEARLY" in text
    assert "CATEGORIES:birthday" in text


@pytest.mark.asyncio
async def test_calendar_feed_anniversary_filter_excludes_birthdays(admin_client: AsyncClient, seeded_db):
    resp1 = await admin_client.post("/api/persons", json={
        "first_name": "FeedA",
        "last_name": "Pair",
    })
    resp2 = await admin_client.post("/api/persons", json={
        "first_name": "FeedB",
        "last_name": "Pair",
    })
    id_a = resp1.json()["id"]
    id_b = resp2.json()["id"]

    resp = await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": id_a,
        "person_b_id": id_b,
        "kind": "married",
        "status": "active",
        "start_date": "2000-06-20",
        "start_date_precision": "exact",
    })
    assert resp.status_code == 201

    result = await seeded_db.execute(
        select(Person).where(Person.id == "tyler-000-0000-0000-000000000002")
    )
    tyler = result.scalar_one()
    tyler.birth_date = "1990-03-15"
    tyler.birth_date_precision = "exact"
    await seeded_db.commit()

    resp = await admin_client.get(f"/calendar/feed.ics?token={tyler.calendar_feed_token}&types=anniversary")
    assert resp.status_code == 200
    text = resp.text
    assert "SUMMARY:" in text
    assert "FeedA Pair" in text
    assert "FeedB Pair" in text
    assert "anniversary" in text
    assert "Tyler Martin's birthday" not in text


@pytest.mark.asyncio
async def test_calendar_feed_token_rotation_changes_subscription_url(admin_client: AsyncClient, seeded_db):
    result = await seeded_db.execute(
        select(Person).where(Person.id == "tyler-000-0000-0000-000000000002")
    )
    tyler = result.scalar_one()
    old_token = tyler.calendar_feed_token

    resp = await admin_client.post("/calendar/feed-token/rotate", data={"month": "2026-03"})
    assert resp.status_code == 200 or resp.status_code == 303

    await seeded_db.refresh(tyler)
    assert tyler.calendar_feed_token != old_token


# ── Relationship Calculator API ──────────────────────────────────────

@pytest.mark.asyncio
async def test_relationship_path_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/relationships/path?from=a&to=b")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_relationship_path_not_found_person(admin_client: AsyncClient):
    resp = await admin_client.get(
        "/api/relationships/path?from=tyler-000-0000-0000-000000000002&to=nonexistent-id"
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_relationship_same_person(admin_client: AsyncClient):
    tyler_id = "tyler-000-0000-0000-000000000002"
    resp = await admin_client.get(f"/api/relationships/path?from={tyler_id}&to={tyler_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert data["relationship_label"] == "same person"


@pytest.mark.asyncio
async def test_relationship_parent_child(admin_client: AsyncClient):
    """Tyler is parent of root (Luna) — should be labeled 'parent'."""
    tyler_id = "tyler-000-0000-0000-000000000002"
    root_id = "root-0000-0000-0000-000000000001"
    resp = await admin_client.get(f"/api/relationships/path?from={root_id}&to={tyler_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert "parent" in data["relationship_label"]
    assert len(data["path"]) == 2
    assert len(data["path_details"]) == 1


@pytest.mark.asyncio
async def test_relationship_grandparent(admin_client: AsyncClient):
    """Grandpa Robert is Tyler's parent → grandparent of root."""
    root_id = "root-0000-0000-0000-000000000001"
    grandpa_id = "grndpa-00-0000-0000-000000000004"
    resp = await admin_client.get(f"/api/relationships/path?from={root_id}&to={grandpa_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert "grandparent" in data["relationship_label"]
    assert len(data["path"]) == 3


@pytest.mark.asyncio
async def test_relationship_sibling(admin_client: AsyncClient):
    """Tyler and Jane share parent Robert → siblings."""
    tyler_id = "tyler-000-0000-0000-000000000002"
    jane_id = "member-00-0000-0000-000000000005"
    resp = await admin_client.get(f"/api/relationships/path?from={tyler_id}&to={jane_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert "sibling" in data["relationship_label"]


@pytest.mark.asyncio
async def test_relationship_spouse(admin_client: AsyncClient):
    """Tyler and Yuliya have a partnership → spouse."""
    tyler_id = "tyler-000-0000-0000-000000000002"
    yuliya_id = "yuliya-00-0000-0000-000000000003"
    resp = await admin_client.get(f"/api/relationships/path?from={tyler_id}&to={yuliya_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert data["relationship_label"] in ("spouse", "partner")


@pytest.mark.asyncio
async def test_relationship_disconnected(admin_client: AsyncClient):
    """Create an isolated person — no relationship path should exist."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Isolated",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    isolated_id = resp.json()["id"]

    tyler_id = "tyler-000-0000-0000-000000000002"
    resp = await admin_client.get(f"/api/relationships/path?from={tyler_id}&to={isolated_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is False
    assert "no path" in data["relationship_label"].lower()


@pytest.mark.asyncio
async def test_relationship_path_details_structure(admin_client: AsyncClient):
    """Path details should have the expected fields."""
    tyler_id = "tyler-000-0000-0000-000000000002"
    root_id = "root-0000-0000-0000-000000000001"
    resp = await admin_client.get(f"/api/relationships/path?from={root_id}&to={tyler_id}")
    assert resp.status_code == 200
    data = resp.json()
    for edge in data["path_details"]:
        assert "from_id" in edge
        assert "from_name" in edge
        assert "to_id" in edge
        assert "to_name" in edge
        assert "edge_type" in edge
        assert "edge_kind" in edge


# ── Tree API includes relationship kinds ─────────────────────────────

@pytest.mark.asyncio
async def test_tree_api_includes_parent_child_kind(admin_client: AsyncClient):
    """Tree API should include 'kind' field in parent_child records for visual distinction."""
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["parent_child"]) > 0
    for pc in data["parent_child"]:
        assert "kind" in pc


@pytest.mark.asyncio
async def test_tree_api_includes_partnership_kind(admin_client: AsyncClient):
    """Tree API should include 'kind' field in partnership records for visual distinction."""
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["partnerships"]) > 0
    for p in data["partnerships"]:
        assert "kind" in p
        assert "status" in p


# ── Audit defect fix tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_calendar_month_only_precision_appears_on_day_1(admin_client: AsyncClient):
    """Person with month-only birth_date_precision should appear on day 1."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MonthOnly",
        "last_name": "Precision",
        "birth_date": "1985-04",
        "birth_date_precision": "month",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/calendar?month=2026-04")
    assert resp.status_code == 200
    data = resp.json()
    birthday_events = [e for e in data["events"] if e["type"] == "birthday" and "MonthOnly" in e["label"]]
    assert len(birthday_events) >= 1
    assert birthday_events[0]["day"] == 1
    assert birthday_events[0]["year_only"] is True


@pytest.mark.asyncio
async def test_calendar_year_only_precision_excluded(admin_client: AsyncClient):
    """Person with year-only birth_date_precision should NOT appear on calendar."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "YearOnly",
        "last_name": "Precision",
        "birth_date": "1960",
        "birth_date_precision": "year",
    })
    assert resp.status_code == 201

    # Check all months — should not appear anywhere
    for m in (1, 6, 12):
        resp = await admin_client.get(f"/api/calendar?month=2026-{m:02d}")
        assert resp.status_code == 200
        data = resp.json()
        yearonly_events = [e for e in data["events"] if "YearOnly" in e.get("label", "")]
        assert len(yearonly_events) == 0


@pytest.mark.asyncio
async def test_calendar_page_has_jump_selector(admin_client: AsyncClient):
    """Calendar page should include a month jump selector."""
    resp = await admin_client.get("/calendar")
    assert resp.status_code == 200
    assert "cal__jump-select" in resp.text


@pytest.mark.asyncio
async def test_calendar_page_uses_i18n_filter_labels(admin_client: AsyncClient):
    """Calendar filter labels should come from i18n, not hardcoded English."""
    resp = await admin_client.get("/calendar")
    assert resp.status_code == 200
    # Default locale is 'en', so these should be the English i18n values
    assert "Birthdays" in resp.text
    assert "Remembrances" in resp.text
    assert "Anniversaries" in resp.text
    assert "Imported calendars" in resp.text
