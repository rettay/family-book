"""Tests for the family health dashboard."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_api_unauthenticated(client: AsyncClient):
    """GET /api/health-dashboard without auth returns 401."""
    resp = await client.get("/api/health-dashboard")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_health_dashboard_empty(admin_client: AsyncClient):
    """Dashboard with seed data returns zero genetic/medical counts (seed has no health data)."""
    resp = await admin_client.get("/api/health-dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_persons"] >= 1  # seed persons exist
    assert data["with_genetic_profile"] == 0
    assert data["with_medical_conditions"] == 0
    assert data["with_physical_attributes"] == 0
    assert data["shared_conditions"] == []
    assert data["blood_type_distribution"] == {}


@pytest.mark.asyncio
async def test_health_dashboard_with_data(admin_client: AsyncClient):
    """Create persons with genetic+medical data, verify counts increase."""
    # Get baseline
    baseline_resp = await admin_client.get("/api/health-dashboard")
    baseline = baseline_resp.json()
    baseline_total = baseline["total_persons"]

    await admin_client.post("/api/persons", json={
        "first_name": "Alice",
        "last_name": "Health",
        "maternal_haplogroup": "H1a",
        "blood_type": "A+",
        "height": "165cm",
        "medical_conditions": [{"condition": "Diabetes", "status": "active"}],
    })
    await admin_client.post("/api/persons", json={
        "first_name": "Bob",
        "last_name": "Health",
        "paternal_haplogroup": "R1b",
        "blood_type": "O+",
    })

    resp = await admin_client.get("/api/health-dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_persons"] == baseline_total + 2
    assert data["with_genetic_profile"] >= 2
    assert data["with_medical_conditions"] >= 1
    assert data["with_physical_attributes"] >= 2
    assert "A+" in data["blood_type_distribution"]
    assert "O+" in data["blood_type_distribution"]


@pytest.mark.asyncio
async def test_shared_conditions_detected(admin_client: AsyncClient):
    """Two persons with same condition appear in shared_conditions."""
    await admin_client.post("/api/persons", json={
        "first_name": "SharedA",
        "last_name": "Cond",
        "medical_conditions": [{"condition": "Hypertension", "status": "active"}],
    })
    await admin_client.post("/api/persons", json={
        "first_name": "SharedB",
        "last_name": "Cond",
        "medical_conditions": [{"condition": "hypertension", "status": "managed"}],
    })

    resp = await admin_client.get("/api/health-dashboard")
    assert resp.status_code == 200
    data = resp.json()
    shared = data["shared_conditions"]
    assert len(shared) >= 1
    hypertension = next(s for s in shared if s["condition"].lower() == "hypertension")
    assert hypertension["count"] == 2
    assert len(hypertension["persons"]) == 2


@pytest.mark.asyncio
async def test_haplogroup_distribution(admin_client: AsyncClient):
    """Verify haplogroup counts."""
    await admin_client.post("/api/persons", json={
        "first_name": "HaploA",
        "last_name": "Dist",
        "maternal_haplogroup": "K1a",
    })
    await admin_client.post("/api/persons", json={
        "first_name": "HaploB",
        "last_name": "Dist",
        "maternal_haplogroup": "K1a",
    })

    resp = await admin_client.get("/api/health-dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["haplogroup_distribution"]["maternal"]["K1a"] == 2


@pytest.mark.asyncio
async def test_health_page_renders(admin_client: AsyncClient):
    """GET /health-dashboard returns 200."""
    resp = await admin_client.get("/health-dashboard")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_member_can_access_health(member_client: AsyncClient):
    """Non-admin member gets 200 on health dashboard."""
    resp = await member_client.get("/api/health-dashboard")
    assert resp.status_code == 200
