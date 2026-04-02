"""Tests for GEDCOM import endpoint and external record search routes."""

import io
import pytest
from httpx import AsyncClient


# ── GEDCOM Import Endpoint ───────────────────────────────────────────

VALID_GEDCOM = b"""0 HEAD
1 SOUR TestApp
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Giovanni /Rossi/
1 SEX M
1 BIRT
2 DATE 15 MAR 1890
2 PLAC Naples, Italy
1 DEAT
2 DATE 10 JAN 1965
0 @I2@ INDI
1 NAME Maria /Bianchi/
1 SEX F
1 BIRT
2 DATE 1 JUN 1895
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 5 MAY 1920
1 CHIL @I3@
0 @I3@ INDI
1 NAME Luigi /Rossi/
1 SEX M
1 BIRT
2 DATE 10 FEB 1921
0 TRLR
"""


@pytest.mark.asyncio
async def test_gedcom_upload_unauthenticated(client: AsyncClient):
    resp = await client.post(
        "/api/import/gedcom",
        files={"file": ("test.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_gedcom_upload_invalid_extension(admin_client: AsyncClient):
    resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("test.txt", io.BytesIO(b"not gedcom"), "text/plain")},
    )
    assert resp.status_code == 400
    assert "must be" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_gedcom_upload_invalid_content(admin_client: AsyncClient):
    resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("test.ged", io.BytesIO(b"This is not GEDCOM"), "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "HEAD" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_gedcom_upload_empty_file(admin_client: AsyncClient):
    empty_gedcom = b"""0 HEAD
1 SOUR Test
0 TRLR
"""
    resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("empty.ged", io.BytesIO(empty_gedcom), "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "no individual" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_gedcom_upload_success(admin_client: AsyncClient):
    resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["persons_created"] == 3
    assert data["relationships_created"] >= 3  # 1 partnership + 2 parent-child
    assert isinstance(data["duplicate_candidates"], list)
    assert isinstance(data["errors"], list)
    assert "batch_id" in data  # Import batch tracking


@pytest.mark.asyncio
async def test_gedcom_preview_returns_individuals(admin_client: AsyncClient):
    resp = await admin_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["individuals_count"] == 3
    assert data["families_count"] == 1
    assert len(data["individuals"]) == 3
    # Verify individual preview entries have expected fields
    for indi in data["individuals"]:
        assert "xref" in indi
        assert "name" in indi
        assert "is_duplicate" in indi


@pytest.mark.asyncio
async def test_gedcom_preview_detects_duplicates(admin_client: AsyncClient):
    # First import
    resp1 = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp1.status_code == 200

    # Preview same file — should flag duplicates
    resp2 = await admin_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family2.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["duplicates_count"] >= 3
    dupes = [i for i in data["individuals"] if i["is_duplicate"]]
    assert len(dupes) >= 3
    # Each duplicate should show match info
    for d in dupes:
        assert "duplicate_match" in d
        assert "existing_name" in d["duplicate_match"]
        assert "match_reason" in d["duplicate_match"]


@pytest.mark.asyncio
async def test_gedcom_preview_does_not_create_records(admin_client: AsyncClient):
    # Get current person count
    persons_before = await admin_client.get("/api/persons")
    count_before = len(persons_before.json())

    # Preview only
    await admin_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )

    # Person count should not change
    persons_after = await admin_client.get("/api/persons")
    count_after = len(persons_after.json())
    assert count_after == count_before


@pytest.mark.asyncio
async def test_gedcom_persons_appear_after_import(admin_client: AsyncClient):
    # Import first
    import_resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert import_resp.status_code == 200
    data = import_resp.json()
    assert data["ok"] is True
    assert data["persons_created"] == 3

    # Check persons list — PersonSummary uses display_name, not first_name
    resp = await admin_client.get("/api/persons")
    assert resp.status_code == 200
    persons = resp.json()
    names = [p["display_name"] for p in persons]
    assert any("Giovanni" in n for n in names)
    assert any("Maria" in n for n in names)
    assert any("Luigi" in n for n in names)


@pytest.mark.asyncio
async def test_gedcom_duplicate_detection(admin_client: AsyncClient):
    # Import once
    resp1 = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp1.status_code == 200
    assert resp1.json()["persons_created"] == 3

    # Import same file again — should detect duplicates
    resp2 = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family2.ged", io.BytesIO(VALID_GEDCOM), "application/octet-stream")},
    )
    assert resp2.status_code == 200
    data = resp2.json()
    # Second import should skip all 3 as duplicates
    assert data["duplicates_skipped"] >= 3
    assert len(data["duplicate_candidates"]) >= 3


# ── External Record Search Endpoints ─────────────────────────────────

@pytest.mark.asyncio
async def test_external_records_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/external-records/search?q=test")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_external_records_no_query(admin_client: AsyncClient):
    resp = await admin_client.get("/api/external-records/search")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_external_records_search_by_person_id(admin_client: AsyncClient):
    resp = await admin_client.get(
        "/api/external-records/search?person_id=tyler-000-0000-0000-000000000002"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)
    # Should have entries for each source
    assert len(data["sources"]) >= 1


@pytest.mark.asyncio
async def test_external_records_search_by_query(admin_client: AsyncClient):
    resp = await admin_client.get("/api/external-records/search?q=Martin")
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data


@pytest.mark.asyncio
async def test_external_records_search_single_source(admin_client: AsyncClient):
    resp = await admin_client.get(
        "/api/external-records/search?q=Martin&source=familysearch"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source"] == "familysearch"


@pytest.mark.asyncio
async def test_external_records_person_not_found(admin_client: AsyncClient):
    resp = await admin_client.get(
        "/api/external-records/search?person_id=nonexistent-0000-0000"
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_external_records_blocks_root_person(admin_client: AsyncClient):
    """Root person's real name must never be sent to external APIs."""
    resp = await admin_client.get(
        "/api/external-records/search?person_id=root-0000-0000-0000-000000000001"
    )
    assert resp.status_code == 403
    assert "not available" in resp.json()["detail"].lower()


# ── CEMLA Endpoint ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cemla_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/external-records/cemla?surname=Rossi")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cemla_missing_surname(admin_client: AsyncClient):
    resp = await admin_client.get("/api/external-records/cemla")
    assert resp.status_code == 422  # validation error — surname required


@pytest.mark.asyncio
async def test_cemla_returns_fallback_url(admin_client: AsyncClient):
    resp = await admin_client.get("/api/external-records/cemla?surname=Rossi")
    assert resp.status_code == 200
    data = resp.json()
    assert "fallback_url" in data
    assert "cemla" in data["fallback_url"].lower()
    assert "Rossi" in data["fallback_url"]


@pytest.mark.asyncio
async def test_cemla_with_all_params(admin_client: AsyncClient):
    resp = await admin_client.get(
        "/api/external-records/cemla?surname=Rossi&given_name=Giovanni&year_from=1890&year_to=1920"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "fallback_url" in data
    assert isinstance(data["results"], list)


# ── Source isolation ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_source_failure_doesnt_break_others(admin_client: AsyncClient):
    """Each source's failure should be isolated; other sources still return."""
    resp = await admin_client.get("/api/external-records/search?q=TestPerson")
    assert resp.status_code == 200
    data = resp.json()
    sources = data["sources"]
    # Even if external APIs fail (expected in test env), we get structured responses
    for src in sources:
        assert "source" in src
        assert "results" in src
        assert isinstance(src["results"], list)
