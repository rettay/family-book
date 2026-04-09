from io import BytesIO

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.imports import GedcomImportBatch
from app.models.person import Person, PersonRole


GEDCOM_WITH_UNSUPPORTED = b"""0 HEAD
1 SOUR TestApp
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Alex /Branch/
1 SEX M
1 BIRT
2 DATE 10 FEB 1980
1 SOUR Some source
0 @I2@ INDI
1 NAME Unknown //
0 TRLR
"""


@pytest.mark.asyncio
async def test_gedcom_preview_reports_unsupported_items(
    admin_client: AsyncClient,
):
    resp = await admin_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family.ged", BytesIO(GEDCOM_WITH_UNSUPPORTED), "application/octet-stream")},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["unsupported_items"]
    assert "Source citations" in body["unsupported_items"][0]


@pytest.mark.asyncio
async def test_gedcom_upload_creates_reviewable_batch_and_can_roll_back(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    upload_resp = await admin_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", BytesIO(GEDCOM_WITH_UNSUPPORTED), "application/octet-stream")},
    )

    assert upload_resp.status_code == 200
    batch_id = upload_resp.json()["batch_id"]

    batch_resp = await admin_client.get(f"/api/import/gedcom/{batch_id}")
    assert batch_resp.status_code == 200
    batch_body = batch_resp.json()
    assert batch_body["summary"]["unsupported_items"]
    assert batch_body["summary"]["created_person_ids"]

    created_person_ids = batch_body["summary"]["created_person_ids"]

    rollback_resp = await admin_client.post(f"/api/import/gedcom/{batch_id}/rollback")
    assert rollback_resp.status_code == 200
    assert rollback_resp.json()["status"] == "rolled_back"

    batch = await seeded_db.get(GedcomImportBatch, batch_id)
    assert batch is not None
    assert batch.status == "rolled_back"

    remaining = (
        await seeded_db.execute(select(Person).where(Person.id.in_(created_person_ids)))
    ).scalars().all()
    assert remaining == []


@pytest.mark.asyncio
async def test_member_cannot_preview_or_import_gedcom(member_client: AsyncClient):
    preview_resp = await member_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family.ged", BytesIO(GEDCOM_WITH_UNSUPPORTED), "application/octet-stream")},
    )
    import_resp = await member_client.post(
        "/api/import/gedcom",
        files={"file": ("family.ged", BytesIO(GEDCOM_WITH_UNSUPPORTED), "application/octet-stream")},
    )

    assert preview_resp.status_code == 403
    assert import_resp.status_code == 403


@pytest.mark.asyncio
async def test_steward_can_preview_gedcom(
    member_client: AsyncClient,
    seeded_db: AsyncSession,
):
    steward = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    steward.role = PersonRole.steward.value
    await seeded_db.commit()

    resp = await member_client.post(
        "/api/import/gedcom/preview",
        files={"file": ("family.ged", BytesIO(GEDCOM_WITH_UNSUPPORTED), "application/octet-stream")},
    )

    assert resp.status_code == 200
