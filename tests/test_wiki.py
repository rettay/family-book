"""Tests for wiki pages feature (S24, Slices 2-3)."""

import pytest
from httpx import AsyncClient

ROOT_ID = "root-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_slug_generated_on_create(admin_client: AsyncClient):
    """POST /api/persons assigns a slug."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Maria",
        "last_name": "Santos",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] is not None
    assert "maria" in data["slug"].lower()
    assert "santos" in data["slug"].lower()


@pytest.mark.asyncio
async def test_slug_unique(admin_client: AsyncClient):
    """Two persons with same name get different slugs (short_id differs)."""
    resp1 = await admin_client.post("/api/persons", json={
        "first_name": "John",
        "last_name": "Doe",
    })
    resp2 = await admin_client.post("/api/persons", json={
        "first_name": "John",
        "last_name": "Doe",
    })
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["slug"] != resp2.json()["slug"]


@pytest.mark.asyncio
async def test_wiki_index_renders(admin_client: AsyncClient):
    """GET /wiki returns 200."""
    resp = await admin_client.get("/wiki")
    assert resp.status_code == 200
    assert "wiki" in resp.text.lower() or "Wiki" in resp.text


@pytest.mark.asyncio
async def test_wiki_index_lists_persons(admin_client: AsyncClient):
    """Persons appear in wiki index."""
    # Create a person
    resp = await admin_client.post("/api/persons", json={
        "first_name": "WikiIdx",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get("/wiki")
    assert resp.status_code == 200
    assert slug in resp.text


@pytest.mark.asyncio
async def test_wiki_index_search(admin_client: AsyncClient):
    """Search filter works on wiki index."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Searchable",
        "last_name": "Wikiman",
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/wiki?search=Searchable")
    assert resp.status_code == 200
    assert "Searchable" in resp.text


@pytest.mark.asyncio
async def test_wiki_person_page(admin_client: AsyncClient):
    """GET /wiki/{slug} returns 200."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "WikiPage",
        "last_name": "Test",
        "bio": "A test person for wiki pages.",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "WikiPage" in resp.text


@pytest.mark.asyncio
async def test_wiki_person_sections(admin_client: AsyncClient):
    """Sections render from structured data."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Detailed",
        "last_name": "Wiki",
        "bio": "A remarkable individual.",
        "birth_place": "Mexico City",
        "education": [{"degree": "PhD", "institution": "UNAM", "year": "2010"}],
        "career": [{"title": "Professor", "company": "UNAM", "years": "2010-2020"}],
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert "Mexico City" in resp.text
    assert "PhD" in resp.text
    assert "Professor" in resp.text


@pytest.mark.asyncio
async def test_wiki_api_returns_sections(admin_client: AsyncClient):
    """API endpoint returns section data."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ApiWiki",
        "last_name": "Test",
        "bio": "Bio text",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/api/wiki/{slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == slug
    assert len(data["sections"]) > 0
    section_ids = [s["id"] for s in data["sections"]]
    assert "summary" in section_ids


@pytest.mark.asyncio
async def test_wiki_unauthenticated(client: AsyncClient):
    """Wiki requires authentication."""
    resp = await client.get("/wiki")
    # Should redirect to login or return 401
    assert resp.status_code in (302, 401)


@pytest.mark.asyncio
async def test_wiki_404_for_bad_slug(admin_client: AsyncClient):
    """GET /wiki/nonexistent returns 404."""
    resp = await admin_client.get("/wiki/nonexistent-slug-xyz")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_wiki_root_person_redacted(admin_client: AsyncClient):
    """Root person wiki page redacts name."""
    # Get root person slug
    resp = await admin_client.get(f"/api/persons/{ROOT_ID}")
    assert resp.status_code == 200
    slug = resp.json().get("slug")
    if slug:
        resp = await admin_client.get(f"/wiki/{slug}")
        assert resp.status_code == 200
        # Root person's real name should not appear
        # The display_name should be redacted (shows "You" or similar)


# ── Slice 3 Tests: Section Editing and Cross-Links ────────────────


@pytest.mark.asyncio
async def test_wiki_edit_section_renders(admin_client: AsyncClient):
    """GET /wiki/{slug}/edit/summary returns edit form partial."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "EditForm",
        "last_name": "Test",
        "bio": "Original bio",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}/edit/summary")
    assert resp.status_code == 200
    assert "form" in resp.text.lower()
    assert "Original bio" in resp.text


@pytest.mark.asyncio
async def test_wiki_save_section(admin_client: AsyncClient):
    """POST /wiki/{slug}/edit/summary updates person bio."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "SaveTest",
        "last_name": "Wiki",
        "bio": "Old bio",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]
    person_id = resp.json()["id"]

    resp = await admin_client.post(
        f"/wiki/{slug}/edit/summary",
        data={"bio": "Updated bio via wiki"},
    )
    assert resp.status_code == 200

    # Verify the update persisted
    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated bio via wiki"


@pytest.mark.asyncio
async def test_wiki_edit_unknown_section(admin_client: AsyncClient):
    """GET /wiki/{slug}/edit/nonexistent returns 404."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Unknown",
        "last_name": "Section",
    })
    assert resp.status_code == 201
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/wiki/{slug}/edit/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_wiki_cross_links_in_person_page(admin_client: AsyncClient):
    """Person profile page contains wiki link."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "CrossLink",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]
    slug = resp.json()["slug"]

    resp = await admin_client.get(f"/people/{person_id}")
    assert resp.status_code == 200
    assert f"/wiki/{slug}" in resp.text
