"""Tests for life story fields — obituary, education, career, organizations."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_person_with_obituary(admin_client: AsyncClient):
    """POST /api/persons with obituary fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Obituary",
        "last_name": "Test",
        "obituary": "A beloved family member...",
        "obituary_source": "Local newspaper, 2020",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["obituary"] == "A beloved family member..."
    assert data["obituary_source"] == "Local newspaper, 2020"


@pytest.mark.asyncio
async def test_update_person_education(admin_client: AsyncClient):
    """PUT /api/persons with education array."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Education",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "education": [
            {
                "institution": "MIT",
                "degree": "PhD",
                "field_of_study": "Computer Science",
                "year_start": "2010",
                "year_end": "2015",
            }
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["education"]) == 1
    assert data["education"][0]["institution"] == "MIT"
    assert data["education"][0]["degree"] == "PhD"


@pytest.mark.asyncio
async def test_update_person_career(admin_client: AsyncClient):
    """PUT /api/persons with career array."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Career",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "career": [
            {
                "employer": "Google",
                "title": "Software Engineer",
                "year_start": "2015",
                "year_end": "2020",
                "location": "Mountain View, CA",
            }
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["career"]) == 1
    assert data["career"][0]["employer"] == "Google"
    assert data["career"][0]["title"] == "Software Engineer"


@pytest.mark.asyncio
async def test_update_person_organizations(admin_client: AsyncClient):
    """PUT /api/persons with organizations array."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "OrgTest",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "organizations": [
            {
                "name": "Rotary Club",
                "role": "President",
                "year_joined": "2005",
                "year_left": "2010",
            }
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["organizations"]) == 1
    assert data["organizations"][0]["name"] == "Rotary Club"


@pytest.mark.asyncio
async def test_person_detail_includes_new_fields(admin_client: AsyncClient):
    """GET /api/persons/{id} returns all life story fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "DetailTest",
        "last_name": "Person",
        "obituary": "In loving memory",
        "education": [{"institution": "Harvard"}],
        "career": [{"employer": "Apple"}],
        "organizations": [{"name": "Lions Club"}],
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["obituary"] == "In loving memory"
    assert len(data["education"]) == 1
    assert len(data["career"]) == 1
    assert len(data["organizations"]) == 1


@pytest.mark.asyncio
async def test_root_person_life_story_redacted(admin_client: AsyncClient):
    """Root person's life story fields should be redacted (None/[])."""
    # Get the root person
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    root_id = resp.json()["root_id"]

    # Get root person detail
    resp = await admin_client.get(f"/api/persons/{root_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_root"] is True
    assert data["obituary"] is None
    assert data["education"] == []
    assert data["career"] == []
    assert data["organizations"] == []


@pytest.mark.asyncio
async def test_revision_includes_life_story(admin_client: AsyncClient):
    """Verify that revisions include the new life story fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RevisionTest",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Update with life story data
    await admin_client.put(f"/api/persons/{person_id}", json={
        "obituary": "Test obituary",
        "education": [{"institution": "Yale"}],
        "career": [{"employer": "Meta"}],
        "organizations": [{"name": "ACM"}],
    })

    # Check revisions
    resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert resp.status_code == 200
    revisions = resp.json()
    assert len(revisions) >= 1
    # The latest revision should contain the new fields
    latest = revisions[0]
    snapshot = latest["snapshot"]
    assert "obituary" in snapshot
    assert "education" in snapshot
    assert "career" in snapshot
    assert "organizations" in snapshot


@pytest.mark.asyncio
async def test_obituary_max_length_enforced(admin_client: AsyncClient):
    """Obituary field should reject values exceeding max_length."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "LongObit",
        "last_name": "Test",
        "obituary": "x" * 10001,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_education_unknown_keys_stripped(admin_client: AsyncClient):
    """Education entries with unknown keys should accept only known fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "SchemaTest",
        "last_name": "Person",
        "education": [
            {"institution": "Stanford", "degree": "BS", "bogus_key": "should_be_dropped"}
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["education"]) == 1
    assert data["education"][0]["institution"] == "Stanford"
    assert "bogus_key" not in data["education"][0]
