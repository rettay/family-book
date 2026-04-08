"""Tests for family timeline with branch filtering."""

import pytest
from httpx import AsyncClient


# ── API tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_timeline_api_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/timeline")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_timeline_api_returns_events(admin_client: AsyncClient):
    """Create a person with a birth date and verify it appears in the timeline."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "TimelineTest",
        "last_name": "Person",
        "birth_date": "1985-06-15",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert isinstance(data["events"], list)
    # Should include at least the person we just created
    birth_events = [e for e in data["events"] if e["type"] == "birth" and "TimelineTest" in e["label"]]
    assert len(birth_events) >= 1
    # Check event field structure
    ev = birth_events[0]
    assert "date" in ev
    assert "year" in ev
    assert "type" in ev
    assert "label" in ev
    assert "person_id" in ev
    assert "person_name" in ev
    assert "detail" in ev


@pytest.mark.asyncio
async def test_timeline_api_filter_by_type(admin_client: AsyncClient):
    """Filter timeline to only birth events."""
    resp = await admin_client.get("/api/timeline?event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    for ev in data["events"]:
        assert ev["type"] == "birth"


@pytest.mark.asyncio
async def test_timeline_api_filter_by_year_range(admin_client: AsyncClient):
    """Create persons in known years and verify year filtering works."""
    await admin_client.post("/api/persons", json={
        "first_name": "OldPerson",
        "last_name": "Timeline",
        "birth_date": "1920-01-01",
        "birth_date_precision": "exact",
    })
    await admin_client.post("/api/persons", json={
        "first_name": "NewPerson",
        "last_name": "Timeline",
        "birth_date": "2010-06-01",
        "birth_date_precision": "exact",
    })

    # Filter to only 1900-1950
    resp = await admin_client.get("/api/timeline?year_from=1900&year_to=1950&event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    for ev in data["events"]:
        assert 1900 <= ev["year"] <= 1950

    # NewPerson should not appear
    new_events = [e for e in data["events"] if "NewPerson" in e["label"]]
    assert len(new_events) == 0


# ── Page tests ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_timeline_page_loads(admin_client: AsyncClient):
    resp = await admin_client.get("/timeline")
    assert resp.status_code == 200
    assert "timeline" in resp.text.lower()


@pytest.mark.asyncio
async def test_timeline_partial_returns_html(admin_client: AsyncClient):
    resp = await admin_client.get("/partials/timeline-events")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_timeline_partial_accepts_empty_htmx_year_fields(admin_client: AsyncClient):
    """Empty HTMX number inputs should not make the partial return a validation error."""
    resp = await admin_client.get(
        "/partials/timeline-events?event_type=&year_from=&year_to=&branch=",
        headers={"HX-Request": "true"},
    )
    assert resp.status_code == 200
    assert "could not load content" not in resp.text.lower()
    assert "must be a valid year" not in resp.text


@pytest.mark.asyncio
async def test_timeline_partial_reported_range_all_events(admin_client: AsyncClient):
    """Regression for founder-reported 1880-2002 + All Events filter flow."""
    birth_resp = await admin_client.post("/api/persons", json={
        "first_name": "RangeBirth",
        "last_name": "Timeline",
        "birth_date": "1880-01-01",
        "birth_date_precision": "exact",
    })
    assert birth_resp.status_code == 201
    death_resp = await admin_client.post("/api/persons", json={
        "first_name": "RangeDeath",
        "last_name": "Timeline",
        "birth_date": "1920-01-01",
        "birth_date_precision": "exact",
        "death_date": "2002-12-31",
        "death_date_precision": "exact",
        "is_living": False,
    })
    assert death_resp.status_code == 201

    resp = await admin_client.get(
        "/partials/timeline-events?event_type=&year_from=1880&year_to=2002",
        headers={"HX-Request": "true"},
    )
    assert resp.status_code == 200
    assert "RangeBirth" in resp.text
    assert "RangeDeath" in resp.text
    assert "must be a valid year" not in resp.text


@pytest.mark.asyncio
async def test_timeline_api_accepts_all_and_plural_event_aliases(admin_client: AsyncClient):
    resp = await admin_client.get("/api/timeline?event_type=all&year_from=&year_to=")
    assert resp.status_code == 200

    resp = await admin_client.get("/api/timeline?event_type=births")
    assert resp.status_code == 200
    for ev in resp.json()["events"]:
        assert ev["type"] == "birth"


# ── Graph traversal tests ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_ancestors(admin_client: AsyncClient, session_factory):
    """Create parent-child chain and verify ancestors."""
    from app.services.relationship_calculator import get_ancestors

    # Create grandparent -> parent -> child
    resp = await admin_client.post("/api/persons", json={
        "first_name": "GrandpaAncestor", "last_name": "Test",
    })
    grandparent_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "ParentAncestor", "last_name": "Test",
    })
    parent_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "ChildAncestor", "last_name": "Test",
    })
    child_id = resp.json()["id"]

    # Link grandparent -> parent
    await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": grandparent_id, "child_id": parent_id,
    })
    # Link parent -> child
    await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id, "child_id": child_id,
    })

    async with session_factory() as db:
        ancestors = await get_ancestors(db, child_id)
        assert parent_id in ancestors
        assert grandparent_id in ancestors
        assert child_id not in ancestors


@pytest.mark.asyncio
async def test_get_descendants(admin_client: AsyncClient, session_factory):
    """Verify descendants traversal."""
    from app.services.relationship_calculator import get_descendants

    resp = await admin_client.post("/api/persons", json={
        "first_name": "TopDesc", "last_name": "Test",
    })
    top_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "MidDesc", "last_name": "Test",
    })
    mid_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "BottomDesc", "last_name": "Test",
    })
    bottom_id = resp.json()["id"]

    await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": top_id, "child_id": mid_id,
    })
    await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": mid_id, "child_id": bottom_id,
    })

    async with session_factory() as db:
        descendants = await get_descendants(db, top_id)
        assert mid_id in descendants
        assert bottom_id in descendants
        assert top_id not in descendants


@pytest.mark.asyncio
async def test_lineage_filter_restricts_events(admin_client: AsyncClient):
    """Verify that lineage_person_id filter restricts timeline events."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "LineageParent", "last_name": "Filter",
        "birth_date": "1960-01-01", "birth_date_precision": "exact",
    })
    parent_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "LineageChild", "last_name": "Filter",
        "birth_date": "1990-01-01", "birth_date_precision": "exact",
    })
    child_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "UnrelatedPerson", "last_name": "Filter",
        "birth_date": "1990-02-02", "birth_date_precision": "exact",
    })
    unrelated_id = resp.json()["id"]

    await admin_client.post("/api/relationships/parent-child", json={
        "parent_id": parent_id, "child_id": child_id,
    })

    # Filter by lineage of child — should include child and parent, but not unrelated
    resp = await admin_client.get(f"/api/timeline?lineage_person_id={child_id}&event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    person_ids = {e["person_id"] for e in data["events"]}
    assert child_id in person_ids
    assert parent_id in person_ids
    assert unrelated_id not in person_ids


# ── Member-client tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_member_can_access_timeline(member_client: AsyncClient):
    """Non-admin member can access the timeline API."""
    resp = await member_client.get("/api/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_hidden_person_excluded_from_member_timeline(
    admin_client: AsyncClient, member_client: AsyncClient
):
    """Hidden person's events should not appear in member's timeline."""
    # Admin creates a hidden person with a birth date
    resp = await admin_client.post("/api/persons", json={
        "first_name": "HiddenTimeline",
        "last_name": "Person",
        "birth_date": "1975-03-20",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201
    hidden_id = resp.json()["id"]

    # Admin sets visibility to hidden
    resp = await admin_client.put(f"/api/persons/{hidden_id}", json={
        "visibility": "hidden",
    })
    assert resp.status_code == 200

    # Member's timeline should not include the hidden person
    resp = await member_client.get("/api/timeline?event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    hidden_events = [e for e in data["events"] if e["person_id"] == hidden_id]
    assert len(hidden_events) == 0


@pytest.mark.asyncio
async def test_timeline_total_reflects_pre_pagination_count(admin_client: AsyncClient):
    """The total field should reflect total matching events, not just the page size."""
    # Create 3 persons with birth dates
    for i in range(3):
        await admin_client.post("/api/persons", json={
            "first_name": f"TotalTest{i}",
            "last_name": "Counter",
            "birth_date": f"200{i}-01-01",
            "birth_date_precision": "exact",
        })

    # Request with limit=1 — total should be >= 3 (seed data adds more)
    resp = await admin_client.get("/api/timeline?event_type=birth&limit=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["events"]) == 1
    assert data["total"] >= 3


# ── Branch filter tests (S21-F04) ────────────────────────────────────


@pytest.mark.asyncio
async def test_branch_filter_returns_matching_persons(admin_client: AsyncClient):
    """Timeline with branch filter returns only persons in that branch."""
    await admin_client.post("/api/persons", json={
        "first_name": "BranchAlpha",
        "last_name": "Filter",
        "birth_date": "1980-01-01",
        "birth_date_precision": "exact",
        "branch": "maternal",
    })
    await admin_client.post("/api/persons", json={
        "first_name": "BranchBeta",
        "last_name": "Filter",
        "birth_date": "1982-01-01",
        "birth_date_precision": "exact",
        "branch": "paternal",
    })

    resp = await admin_client.get("/api/timeline?branch=maternal&event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    names = [e["person_name"] for e in data["events"]]
    assert any("BranchAlpha" in n for n in names)
    assert all("BranchBeta" not in n for n in names)


@pytest.mark.asyncio
async def test_branch_filter_case_insensitive(admin_client: AsyncClient):
    """Branch filter matches case-insensitively."""
    await admin_client.post("/api/persons", json={
        "first_name": "CaseBranch",
        "last_name": "Filter",
        "birth_date": "1975-06-01",
        "birth_date_precision": "exact",
        "branch": "Paternal",
    })

    resp = await admin_client.get("/api/timeline?branch=paternal&event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    names = [e["person_name"] for e in data["events"]]
    assert any("CaseBranch" in n for n in names)


@pytest.mark.asyncio
async def test_branch_filter_no_match_returns_empty(admin_client: AsyncClient):
    """Branch filter with nonexistent branch returns no events for that branch."""
    resp = await admin_client.get("/api/timeline?branch=nonexistent_branch_xyz&event_type=birth")
    assert resp.status_code == 200
    data = resp.json()
    # May include seed data with no branch, but none should match "nonexistent_branch_xyz"
    # The filter only includes persons where branch matches, so this should be empty or only unbranched
    assert data["total"] == 0


# ── Death event tests (S21-F05) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_death_event_appears_in_timeline(admin_client: AsyncClient):
    """Person with death_date generates a death event."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "DeathTest",
        "last_name": "Person",
        "birth_date": "1920-01-01",
        "birth_date_precision": "exact",
        "death_date": "2000-12-31",
        "death_date_precision": "exact",
        "is_living": False,
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/timeline?event_type=death")
    assert resp.status_code == 200
    data = resp.json()
    death_events = [e for e in data["events"] if "DeathTest" in e["person_name"]]
    assert len(death_events) == 1
    assert death_events[0]["type"] == "death"
    assert death_events[0]["year"] == 2000


# ── Marriage/partnership event tests (S21-F05) ───────────────────────


@pytest.mark.asyncio
async def test_marriage_event_appears_in_timeline(admin_client: AsyncClient):
    """Partnership with start_date generates a marriage event."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "SpouseA",
        "last_name": "Wedding",
        "birth_date": "1970-01-01",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201
    person_a_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "SpouseB",
        "last_name": "Wedding",
        "birth_date": "1972-01-01",
        "birth_date_precision": "exact",
    })
    assert resp.status_code == 201
    person_b_id = resp.json()["id"]

    resp = await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": person_a_id,
        "person_b_id": person_b_id,
        "kind": "marriage",
        "start_date": "1995-06-15",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/timeline?event_type=marriage")
    assert resp.status_code == 200
    data = resp.json()
    wedding_events = [e for e in data["events"] if "SpouseA" in e["label"] or "SpouseB" in e["label"]]
    assert len(wedding_events) >= 1
    assert wedding_events[0]["year"] == 1995


@pytest.mark.asyncio
async def test_hidden_partner_marriage_excluded(
    admin_client: AsyncClient, member_client: AsyncClient
):
    """Marriage event is excluded when one partner is hidden (no existence leak)."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "VisiblePartner",
        "last_name": "MarriageTest",
        "birth_date": "1965-01-01",
        "birth_date_precision": "exact",
    })
    visible_id = resp.json()["id"]

    resp = await admin_client.post("/api/persons", json={
        "first_name": "HiddenPartner",
        "last_name": "MarriageTest",
        "birth_date": "1966-01-01",
        "birth_date_precision": "exact",
    })
    hidden_id = resp.json()["id"]

    await admin_client.post("/api/relationships/partnership", json={
        "person_a_id": visible_id,
        "person_b_id": hidden_id,
        "kind": "marriage",
        "start_date": "1990-09-01",
    })

    # Hide one partner
    await admin_client.put(f"/api/persons/{hidden_id}", json={"visibility": "hidden"})

    # Member should not see the marriage event at all
    resp = await member_client.get("/api/timeline?event_type=marriage")
    assert resp.status_code == 200
    data = resp.json()
    leaked = [e for e in data["events"] if "VisiblePartner" in e.get("label", "")]
    assert len(leaked) == 0


# ── Lineage access check test (S21-F01) ──────────────────────────────


@pytest.mark.asyncio
async def test_lineage_with_hidden_person_returns_no_events(
    admin_client: AsyncClient, member_client: AsyncClient
):
    """Using a hidden person's ID as lineage_person_id returns no lineage events."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "HiddenLineage",
        "last_name": "Test",
        "birth_date": "1950-01-01",
        "birth_date_precision": "exact",
    })
    hidden_id = resp.json()["id"]

    await admin_client.put(f"/api/persons/{hidden_id}", json={"visibility": "hidden"})

    # Member tries to use hidden person as lineage filter
    resp = await member_client.get(f"/api/timeline?lineage_person_id={hidden_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
