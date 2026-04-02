"""Tests for physical attributes and genetic profile fields."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_person_with_physical_attributes(admin_client: AsyncClient):
    """POST /api/persons with all 5 physical attribute fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Physical",
        "last_name": "Test",
        "height": "5'10\"",
        "weight": "170 lbs",
        "eye_color": "brown",
        "hair_color": "black",
        "blood_type": "O+",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["height"] == "5'10\""
    assert data["weight"] == "170 lbs"
    assert data["eye_color"] == "brown"
    assert data["hair_color"] == "black"
    assert data["blood_type"] == "O+"


@pytest.mark.asyncio
async def test_update_person_physical_attributes(admin_client: AsyncClient):
    """POST minimal person, then PUT with physical attrs."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "UpdatePhys",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "height": "180cm",
        "weight": "80kg",
        "eye_color": "blue",
        "hair_color": "blonde",
        "blood_type": "A-",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["height"] == "180cm"
    assert data["weight"] == "80kg"
    assert data["eye_color"] == "blue"
    assert data["blood_type"] == "A-"


@pytest.mark.asyncio
async def test_create_person_with_genetic_profile(admin_client: AsyncClient):
    """POST /api/persons with haplogroups and provider."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Genetic",
        "last_name": "Test",
        "maternal_haplogroup": "H1a",
        "paternal_haplogroup": "R1b",
        "dna_test_provider": "23andMe",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["maternal_haplogroup"] == "H1a"
    assert data["paternal_haplogroup"] == "R1b"
    assert data["dna_test_provider"] == "23andMe"


@pytest.mark.asyncio
async def test_update_person_admixture(admin_client: AsyncClient):
    """PUT /api/persons with admixture array, assert round-trip."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Admixture",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "admixture": [
            {"ethnicity": "Eastern European", "percentage": "45", "source": "23andMe"},
            {"ethnicity": "Western European", "percentage": "30", "source": "23andMe"},
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["admixture"]) == 2
    assert data["admixture"][0]["ethnicity"] == "Eastern European"
    assert data["admixture"][1]["percentage"] == "30"


@pytest.mark.asyncio
async def test_root_person_genetic_redacted(admin_client: AsyncClient, seeded_db):
    """Root person returns None/[] for all new fields."""
    resp = await admin_client.get("/api/persons/root-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["height"] is None
    assert data["weight"] is None
    assert data["eye_color"] is None
    assert data["hair_color"] is None
    assert data["blood_type"] is None
    assert data["maternal_haplogroup"] is None
    assert data["paternal_haplogroup"] is None
    assert data["dna_test_provider"] is None
    assert data["admixture"] == []
    assert data["medical_conditions"] == []


@pytest.mark.asyncio
async def test_revision_includes_genetic_fields(admin_client: AsyncClient):
    """Snapshot from revision contains new fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RevGenetic",
        "last_name": "Test",
        "maternal_haplogroup": "J1c",
        "height": "6'0\"",
        "blood_type": "B+",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= 1
    snapshot = entries[0]["snapshot"]
    assert snapshot["height"] == "6'0\""
    assert snapshot["blood_type"] == "B+"
    # Encrypted genetic fields must NOT appear in history snapshots
    assert "maternal_haplogroup" not in snapshot
    assert "paternal_haplogroup" not in snapshot
    assert "dna_test_provider" not in snapshot


@pytest.mark.asyncio
async def test_admixture_unknown_keys_stripped(admin_client: AsyncClient):
    """Bogus key in admixture entry not in response."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "AdmStrip",
        "last_name": "Test",
        "admixture": [
            {"ethnicity": "Iberian", "percentage": "20", "bogus_key": "should vanish"},
        ]
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["admixture"]) == 1
    assert "bogus_key" not in data["admixture"][0]
    assert data["admixture"][0]["ethnicity"] == "Iberian"


@pytest.mark.asyncio
async def test_person_detail_includes_physical_genetic(admin_client: AsyncClient):
    """GET /api/persons/{id} returns all new fields."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "DetailCheck",
        "last_name": "Test",
        "height": "175cm",
        "eye_color": "green",
        "maternal_haplogroup": "T2b",
        "admixture": [{"ethnicity": "Scandinavian", "percentage": "15"}],
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["height"] == "175cm"
    assert data["eye_color"] == "green"
    assert data["maternal_haplogroup"] == "T2b"
    assert len(data["admixture"]) == 1
