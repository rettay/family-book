"""Tests for source citations and confidence fields (S23, Slice 1)."""

import pytest
from httpx import AsyncClient

ROOT_ID = "root-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_create_person_with_source_citation(admin_client: AsyncClient):
    """POST /api/persons with source_detail and confidence."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Citation",
        "last_name": "Test",
        "source_detail": "1940 US Census via Ancestry.com",
        "confidence": "confirmed",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_detail"] == "1940 US Census via Ancestry.com"
    assert data["confidence"] == "confirmed"


@pytest.mark.asyncio
async def test_update_person_source_citation(admin_client: AsyncClient):
    """PUT updates source_detail and confidence."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "UpdateCite",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "source_detail": "Aunt Maria at Thanksgiving 2019",
        "confidence": "probable",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_detail"] == "Aunt Maria at Thanksgiving 2019"
    assert data["confidence"] == "probable"


@pytest.mark.asyncio
async def test_confidence_validation(admin_client: AsyncClient):
    """Invalid confidence value returns 422."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "BadConf",
        "last_name": "Test",
        "confidence": "maybe",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_confidence_all_valid_values(admin_client: AsyncClient):
    """All 4 confidence values are accepted."""
    for value in ("confirmed", "probable", "uncertain", "unknown"):
        resp = await admin_client.post("/api/persons", json={
            "first_name": f"Conf{value}",
            "last_name": "Test",
            "confidence": value,
        })
        assert resp.status_code == 201, f"Failed for confidence={value}"
        assert resp.json()["confidence"] == value


@pytest.mark.asyncio
async def test_root_person_source_citation_redacted(admin_client: AsyncClient):
    """Root person returns None for source_detail."""
    resp = await admin_client.get(f"/api/persons/{ROOT_ID}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_detail"] is None
    assert data["confidence"] is None


@pytest.mark.asyncio
async def test_person_detail_includes_source_citation(admin_client: AsyncClient):
    """GET /api/persons/{id} returns source_detail and confidence."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "DetailCite",
        "last_name": "Test",
        "source_detail": "Family Bible",
        "confidence": "uncertain",
    })
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_detail"] == "Family Bible"
    assert data["confidence"] == "uncertain"


@pytest.mark.asyncio
async def test_revision_includes_source_citation(admin_client: AsyncClient):
    """Revision snapshot contains source_detail and confidence."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RevCite",
        "last_name": "Test",
        "source_detail": "Census record",
        "confidence": "confirmed",
    })
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 1
    snapshot = history[0]["snapshot"]
    assert snapshot["source_detail"] == "Census record"
    assert snapshot["confidence"] == "confirmed"
