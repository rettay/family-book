"""Tests for date intelligence service (S23, Slice 3)."""

import pytest
from datetime import date
from httpx import AsyncClient

from app.services.date_intelligence_service import (
    compute_age,
    compute_age_at_death,
    compute_current_age,
    enrich_person_ages,
)


class TestComputeAge:
    def test_exact_dates(self):
        assert compute_age("1990-06-15", "2026-03-26") == 35

    def test_birthday_not_yet(self):
        """If birthday hasn't happened this ref year, age is one less."""
        assert compute_age("1990-12-25", "2026-03-26") == 35

    def test_birthday_same_day(self):
        assert compute_age("1990-03-26", "2026-03-26") == 36

    def test_year_month_precision(self):
        """Year-month precision is accepted."""
        assert compute_age("1990-06", "2026-03-26", birth_precision="month") is not None

    def test_year_only_returns_none(self):
        """Year-only precision returns None."""
        assert compute_age("1990", "2026-03-26", birth_precision="year") is None

    def test_missing_birth_returns_none(self):
        assert compute_age(None, "2026-03-26") is None

    def test_missing_reference_returns_none(self):
        assert compute_age("1990-06-15", None) is None


class TestComputeCurrentAge:
    def test_living_person(self):
        age = compute_current_age("2000-01-01")
        assert age is not None
        assert age >= 26  # Will be 26 in 2026

    def test_year_only_precision_returns_none(self):
        assert compute_current_age("2000", birth_precision="year") is None

    def test_missing_date_returns_none(self):
        assert compute_current_age(None) is None


class TestComputeAgeAtDeath:
    def test_age_at_death(self):
        assert compute_age_at_death("1920-05-10", "2000-12-25") == 80

    def test_death_before_birthday(self):
        assert compute_age_at_death("1920-12-25", "2000-06-15") == 79

    def test_year_only_birth_returns_none(self):
        assert compute_age_at_death("1920", "2000-12-25", birth_precision="year") is None


class TestEnrichPersonAges:
    def test_living_person_gets_current_age(self):
        d = {
            "birth_date": "2000-01-01",
            "birth_date_precision": "exact",
            "death_date": None,
            "death_date_precision": None,
            "is_living": True,
        }
        enrich_person_ages(d)
        assert d.get("current_age") is not None
        assert d.get("current_age") >= 26

    def test_deceased_person_gets_age_at_death(self):
        d = {
            "birth_date": "1920-05-10",
            "birth_date_precision": "exact",
            "death_date": "2000-12-25",
            "death_date_precision": "exact",
            "is_living": False,
        }
        enrich_person_ages(d)
        assert d.get("age_at_death") == 80

    def test_no_birth_date_no_age(self):
        d = {
            "birth_date": None,
            "birth_date_precision": None,
            "death_date": None,
            "death_date_precision": None,
            "is_living": True,
        }
        enrich_person_ages(d)
        assert d.get("current_age") is None


@pytest.mark.asyncio
async def test_person_detail_includes_current_age(admin_client: AsyncClient):
    """GET /api/persons/{id} returns current_age for living person with birth_date."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Young",
        "last_name": "Living",
        "birth_date": "2000-01-01",
        "birth_date_precision": "exact",
        "is_living": True,
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_age"] is not None
    assert data["current_age"] >= 26


@pytest.mark.asyncio
async def test_person_detail_includes_age_at_death(admin_client: AsyncClient):
    """GET /api/persons/{id} returns age_at_death for deceased person."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Elder",
        "last_name": "Deceased",
        "birth_date": "1920-05-10",
        "birth_date_precision": "exact",
        "death_date": "2000-12-25",
        "death_date_precision": "exact",
        "is_living": False,
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["age_at_death"] == 80


@pytest.mark.asyncio
async def test_person_detail_year_only_no_age(admin_client: AsyncClient):
    """Year-only precision does not compute age."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Circa",
        "last_name": "Year",
        "birth_date": "1950",
        "birth_date_precision": "year",
        "is_living": True,
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_age"] is None


@pytest.mark.asyncio
async def test_timeline_birth_event_includes_age(admin_client: AsyncClient):
    """Timeline birth event label includes age context."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Timeline",
        "last_name": "Birth",
        "birth_date": "2000-01-15",
        "birth_date_precision": "exact",
        "is_living": True,
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/timeline", params={"event_type": "birth"})
    assert resp.status_code == 200
    events = resp.json()["events"]
    birth_events = [e for e in events if "Timeline Birth" in e["label"]]
    assert len(birth_events) >= 1
    assert "age" in birth_events[0]["label"]


@pytest.mark.asyncio
async def test_timeline_death_event_includes_age(admin_client: AsyncClient):
    """Timeline death event label includes age at death."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "Timeline",
        "last_name": "Death",
        "birth_date": "1920-05-10",
        "birth_date_precision": "exact",
        "death_date": "2000-06-20",
        "death_date_precision": "exact",
        "is_living": False,
    })
    assert resp.status_code == 201

    resp = await admin_client.get("/api/timeline", params={"event_type": "death"})
    assert resp.status_code == 200
    events = resp.json()["events"]
    death_events = [e for e in events if "Timeline Death" in e["label"]]
    assert len(death_events) >= 1
    assert "age 80" in death_events[0]["label"]
