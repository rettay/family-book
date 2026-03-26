"""Tests for structured medical conditions."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_person_with_medical_conditions(admin_client: AsyncClient):
    """POST /api/persons with medical_conditions array."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MedCond",
        "last_name": "Test",
        "medical_conditions": [
            {
                "condition": "Type 2 Diabetes",
                "onset_age": "45",
                "status": "managed",
                "severity": "moderate",
                "treatment": "Metformin",
                "hereditary_line": "paternal",
                "notes": "Runs in family",
            }
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["medical_conditions"]) == 1
    mc = data["medical_conditions"][0]
    assert mc["condition"] == "Type 2 Diabetes"
    assert mc["onset_age"] == "45"
    assert mc["status"] == "managed"
    assert mc["treatment"] == "Metformin"
    assert mc["hereditary_line"] == "paternal"


@pytest.mark.asyncio
async def test_update_person_medical_conditions(admin_client: AsyncClient):
    """PUT /api/persons with medical_conditions array."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "UpdateMed",
        "last_name": "Test",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "medical_conditions": [
            {"condition": "Hypertension", "status": "active", "severity": "mild"},
            {"condition": "Asthma", "status": "resolved"},
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["medical_conditions"]) == 2
    assert data["medical_conditions"][0]["condition"] == "Hypertension"
    assert data["medical_conditions"][1]["condition"] == "Asthma"


@pytest.mark.asyncio
async def test_medical_conditions_status_values(admin_client: AsyncClient):
    """Each status value works."""
    for status in ["active", "resolved", "managed", "unknown"]:
        resp = await admin_client.post("/api/persons", json={
            "first_name": f"Status{status}",
            "last_name": "Test",
            "medical_conditions": [{"condition": "TestCond", "status": status}],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["medical_conditions"][0]["status"] == status


@pytest.mark.asyncio
async def test_root_person_medical_conditions_redacted(admin_client: AsyncClient, seeded_db):
    """Root person returns [] for medical_conditions."""
    resp = await admin_client.get("/api/persons/root-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["medical_conditions"] == []


@pytest.mark.asyncio
async def test_revision_includes_medical_conditions(admin_client: AsyncClient):
    """Snapshot from revision contains medical_conditions."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "RevMedCond",
        "last_name": "Test",
        "medical_conditions": [{"condition": "Migraine", "status": "active"}],
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}/history")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= 1
    snapshot = entries[0]["snapshot"]
    assert snapshot["medical_conditions"] is not None
    assert len(snapshot["medical_conditions"]) == 1


@pytest.mark.asyncio
async def test_medical_conditions_unknown_keys_stripped(admin_client: AsyncClient):
    """Bogus keys in medical_conditions entries are not in response."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MedStrip",
        "last_name": "Test",
        "medical_conditions": [
            {"condition": "Arthritis", "bogus_key": "should vanish"},
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["medical_conditions"]) == 1
    assert "bogus_key" not in data["medical_conditions"][0]
    assert data["medical_conditions"][0]["condition"] == "Arthritis"
