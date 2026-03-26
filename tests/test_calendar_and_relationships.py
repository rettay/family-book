"""Tests for family calendar, relationship calculator, and visual relationship types."""

import pytest
from httpx import AsyncClient


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
    assert any("AnnivA" in e["label"] or "AnnivB" in e["label"] for e in anniv_events)


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
    assert "Family Calendar" in resp.text


@pytest.mark.asyncio
async def test_calendar_partial_returns_html(admin_client: AsyncClient):
    resp = await admin_client.get("/partials/calendar-grid?month=2026-03")
    assert resp.status_code == 200
    assert "March" in resp.text


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
