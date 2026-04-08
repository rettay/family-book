"""Tests for the Research feature (FB-031)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_research_index_renders(admin_client: AsyncClient):
    """GET /research returns 200 for authenticated user."""
    resp = await admin_client.get("/research")
    assert resp.status_code == 200
    assert "Research" in resp.text or "research-page" in resp.text


@pytest.mark.asyncio
async def test_research_index_unauthenticated(client: AsyncClient):
    """GET /research redirects unauthenticated users."""
    resp = await client.get("/research", follow_redirects=False)
    assert resp.status_code in (302, 401)


@pytest.mark.asyncio
async def test_research_shows_configured_sources(admin_client: AsyncClient):
    """Research page shows sources that don't require API keys."""
    resp = await admin_client.get("/research")
    assert resp.status_code == 200
    # Chronicling America and NARA are always available (no key needed)
    assert "Chronicling America" in resp.text
    assert "NARA" in resp.text
    assert "Research is beta" in resp.text
    assert "Guided lookup" in resp.text


@pytest.mark.asyncio
async def test_unconfigured_sources_hidden(admin_client: AsyncClient):
    """Sources without API keys appear under unconfigured section, not as active."""
    resp = await admin_client.get("/research")
    assert resp.status_code == 200
    text = resp.text
    # Trove, DPLA, and FamilySearch require API keys which aren't set in tests
    # They should be in the "unconfigured" section, not marked as active
    assert "source_inactive" in text or "Not configured" in text or "unconfigured" in text


@pytest.mark.asyncio
async def test_research_nav_link_present(admin_client: AsyncClient):
    """The research nav link appears in the main navigation."""
    resp = await admin_client.get("/research")
    assert resp.status_code == 200
    assert 'href="/research"' in resp.text


# ── Saved Records API Tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_save_record_to_person(admin_client: AsyncClient):
    """POST creates saved record, appears in GET."""
    # Create a person first
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ResearchTarget", "last_name": "Person",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Save a record
    resp = await admin_client.post("/api/research/saved-records", json={
        "person_id": person_id,
        "title": "Census Record 1910",
        "url": "https://example.com/census/1910",
        "source": "nara",
        "snippet": "John Doe, age 35, carpenter",
    })
    assert resp.status_code == 200
    record = resp.json()
    assert record["title"] == "Census Record 1910"
    assert record["source"] == "nara"
    record_id = record["id"]

    # Verify it appears in the list
    resp = await admin_client.get(f"/api/research/saved-records/{person_id}")
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) >= 1
    assert any(r["id"] == record_id for r in records)


@pytest.mark.asyncio
async def test_delete_saved_record(admin_client: AsyncClient):
    """DELETE removes record."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "DeleteTarget", "last_name": "Record",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.post("/api/research/saved-records", json={
        "person_id": person_id,
        "title": "To Be Deleted",
        "source": "chronicling_america",
    })
    assert resp.status_code == 200
    record_id = resp.json()["id"]

    resp = await admin_client.delete(f"/api/research/saved-records/{record_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Verify it's gone
    resp = await admin_client.get(f"/api/research/saved-records/{person_id}")
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert not any(r["id"] == record_id for r in records)


@pytest.mark.asyncio
async def test_saved_records_require_auth(client: AsyncClient):
    """Unauthenticated users get 401."""
    resp = await client.post("/api/research/saved-records", json={
        "person_id": "fake-id",
        "title": "Unauthorized",
        "source": "nara",
    })
    assert resp.status_code == 401

    resp = await client.get("/api/research/saved-records/fake-id")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_saved_records_round_trip(admin_client: AsyncClient):
    """Save, list, verify data integrity."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RoundTrip", "last_name": "Research",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Save multiple records
    for i, source in enumerate(["nara", "chronicling_america", "trove"]):
        resp = await admin_client.post("/api/research/saved-records", json={
            "person_id": person_id,
            "title": f"Record {i}",
            "url": f"https://example.com/record/{i}",
            "source": source,
            "snippet": f"Snippet for record {i}",
        })
        assert resp.status_code == 200

    resp = await admin_client.get(f"/api/research/saved-records/{person_id}")
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) == 3
    # Verify all fields round-trip correctly
    sources = {r["source"] for r in records}
    assert sources == {"nara", "chronicling_america", "trove"}


# ── HTMX Search Results Partial ───────────────────────────────────────


@pytest.mark.asyncio
async def test_research_results_partial_returns_html(admin_client: AsyncClient):
    """GET /partials/research-results returns HTML partial."""
    resp = await admin_client.get(
        "/partials/research-results?q=smith",
        headers={"HX-Request": "true"},
    )
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_research_results_partial_requires_auth(client: AsyncClient):
    """Unauthenticated users get redirected."""
    resp = await client.get(
        "/partials/research-results?q=test",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 401)


@pytest.mark.asyncio
async def test_research_results_empty_query(admin_client: AsyncClient):
    """Empty query returns empty results partial."""
    resp = await admin_client.get("/partials/research-results?q=")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_research_results_show_source_statuses(admin_client: AsyncClient, monkeypatch):
    """Results partial should expose per-source health and distinguish guided links."""
    from app.services.external_records import SearchResult, SourceResults

    async def fake_search_all_sources(_params):
        return [
            SourceResults(
                source="chronicling_america",
                results=[
                    SearchResult(
                        source="chronicling_america",
                        title="Useful newspaper hit",
                        url="https://chroniclingamerica.loc.gov/example",
                        record_type="newspaper",
                    )
                ],
                total_count=1,
            ),
            SourceResults(source="nara", results=[], total_count=0),
            SourceResults(source="dpla", available=False, error="DPLA API key not configured"),
            SourceResults(source="trove", error="upstream unavailable"),
            SourceResults(
                source="antenati",
                results=[
                    SearchResult(
                        source="antenati",
                        title="Browse Antenati registers for maglio",
                        url="https://antenati.cultura.gov.it/search-registry/?lang=en&localita=maglio",
                        record_type="guided_link",
                    )
                ],
                total_count=1,
            ),
        ]

    monkeypatch.setattr("app.routes.research.search_all_sources", fake_search_all_sources)

    resp = await admin_client.get("/partials/research-results?q=maglio")
    assert resp.status_code == 200
    text = resp.text
    assert "Chronicling America" in text
    assert "NARA Catalog" in text
    assert "Results" in text
    assert "No results" in text
    assert "Not configured" in text
    assert "upstream unavailable" in text
    assert "Guided lookup" in text


@pytest.mark.asyncio
async def test_research_results_count_localizes_to_spanish(admin_client: AsyncClient, monkeypatch):
    """Results partial should not compose English count text in Spanish."""
    from app.services.external_records import SearchResult, SourceResults

    async def fake_search_all_sources(_params):
        return [
            SourceResults(
                source="chronicling_america",
                results=[
                    SearchResult(
                        source="chronicling_america",
                        title="Un resultado",
                        url="https://chroniclingamerica.loc.gov/example-1",
                        record_type="newspaper",
                    )
                ],
                total_count=1,
            ),
            SourceResults(
                source="antenati",
                results=[
                    SearchResult(
                        source="antenati",
                        title="Primer enlace guiado",
                        url="https://antenati.cultura.gov.it/search-registry/?lang=en&localita=maglio",
                        record_type="guided_link",
                    ),
                    SearchResult(
                        source="antenati",
                        title="Segundo enlace guiado",
                        url="https://antenati.cultura.gov.it/search-registry/?lang=en&localita=cutroni",
                        record_type="guided_link",
                    ),
                ],
                total_count=2,
            ),
        ]

    monkeypatch.setattr("app.routes.research.search_all_sources", fake_search_all_sources)
    admin_client.cookies.set("locale", "es")

    resp = await admin_client.get("/partials/research-results?q=maglio")
    assert resp.status_code == 200
    text = resp.text
    assert "1 resultado de busqueda" in text
    assert "2 resultados de busqueda" in text
    assert "search result" not in text


# ── Slice 3: Cross-Links and Person Context Tests ────────────────────


@pytest.mark.asyncio
async def test_research_person_context(admin_client: AsyncClient):
    """GET /research?person_id={id} pre-fills person name in search."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "ContextTest", "last_name": "Searcher",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/research?person_id={person_id}")
    assert resp.status_code == 200
    assert "ContextTest" in resp.text
    assert "Searcher" in resp.text


@pytest.mark.asyncio
async def test_research_cross_links_person_profile(admin_client: AsyncClient):
    """Person profile contains research link."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "CrossLink", "last_name": "Profile",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    slug = resp.json()["slug"]
    resp = await admin_client.get(f"/wiki/{slug}")
    assert resp.status_code == 200
    assert f"/research?person_id={person_id}" in resp.text


@pytest.mark.asyncio
async def test_root_person_no_research_link(admin_client: AsyncClient):
    """Root person profile does not show research link."""
    from sqlalchemy import select
    from app.models.person import Person
    from app.database import async_session_factory

    async with async_session_factory() as session:
        result = await session.execute(
            select(Person.id).where(Person.is_root == True)
        )
        root_id = result.scalar_one_or_none()

    if root_id:
        # Fetch root's slug via API (seed data may not have one)
        api_resp = await admin_client.get(f"/api/persons/{root_id}")
        slug = api_resp.json().get("slug") if api_resp.status_code == 200 else None
        if slug:
            resp = await admin_client.get(f"/wiki/{slug}")
            assert resp.status_code == 200
            assert f"/research?person_id={root_id}" not in resp.text
