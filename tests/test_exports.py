import io
import json
import zipfile
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import Story
from tests.test_media import _make_test_image


@pytest.mark.asyncio
async def test_admin_can_download_gedcom_export(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    resp = await admin_client.get("/api/admin/exports/gedcom")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/octet-stream")
    body = resp.text
    assert "0 HEAD" in body
    assert "0 TRLR" in body
    assert "_FBROLE admin" in body


@pytest.mark.asyncio
async def test_admin_can_download_full_archive_export_with_media_and_stories(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    create_resp = await admin_client.post(
        "/api/persons",
        json={
            "first_name": "Export",
            "last_name": "Person",
            "contact_email": "export@example.com",
            "medical_history": "Export-sensitive note",
        },
    )
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]

    seeded_db.add(
        Story(
            person_id=person_id,
            title="Archive Story",
            body="A portable family story",
            author_person_id="tyler-000-0000-0000-000000000002",
        )
    )
    await seeded_db.commit()

    upload_resp = await admin_client.post(
        "/api/media",
        data={"person_id": person_id},
        files={"file": ("export-photo.jpg", _make_test_image(), "image/jpeg")},
    )
    assert upload_resp.status_code == 201

    resp = await admin_client.get("/api/admin/exports/archive")

    assert resp.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(resp.content))
    names = set(archive.namelist())
    assert "manifest.json" in names
    assert "people.json" in names
    assert "relationships/parent_child.json" in names
    assert "relationships/partnerships.json" in names
    assert "stories.json" in names
    assert "media/media.json" in names
    assert "exports/family-book.ged" in names
    assert any(name.startswith("media/originals/") for name in names)

    manifest = json.loads(archive.read("manifest.json"))
    assert manifest["export_scope"] == "admin_full_archive"
    assert manifest["sensitive_field_behavior"]["archive_json"].startswith("includes contact")

    people = json.loads(archive.read("people.json"))
    exported_person = next(person for person in people if person["id"] == person_id)
    assert exported_person["contact_email"] == "export@example.com"
    assert exported_person["medical_history"] == "Export-sensitive note"

    stories = json.loads(archive.read("stories.json"))
    assert any(story["title"] == "Archive Story" for story in stories)


@pytest.mark.asyncio
async def test_non_admin_cannot_download_exports(member_client: AsyncClient):
    gedcom_resp = await member_client.get("/api/admin/exports/gedcom")
    archive_resp = await member_client.get("/api/admin/exports/archive")

    assert gedcom_resp.status_code == 403
    assert archive_resp.status_code == 403


@pytest.mark.asyncio
async def test_export_downloads_are_cleaned_up_after_response(
    admin_client: AsyncClient,
    monkeypatch,
    tmp_path,
):
    gedcom_root = tmp_path / "family-book-export-gedcom"
    archive_root = tmp_path / "family-book-export-archive"
    roots = iter([gedcom_root, archive_root])

    monkeypatch.setattr(
        "app.services.export_service.create_temp_export_dir",
        lambda: Path(next(roots)),
    )

    async with admin_client.stream("GET", "/api/admin/exports/gedcom") as gedcom_resp:
        assert gedcom_resp.status_code == 200
        await gedcom_resp.aread()

    assert not gedcom_root.exists()

    async with admin_client.stream("GET", "/api/admin/exports/archive") as archive_resp:
        assert archive_resp.status_code == 200
        await archive_resp.aread()

    assert not archive_root.exists()
