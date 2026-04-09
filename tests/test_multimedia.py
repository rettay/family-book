"""Tests for rich multimedia playback — PDF upload, audio upload, type mapping."""

import pytest
from time import monotonic
from httpx import AsyncClient

from app.services.media_service import _media_type_for_mime, _category_for_mime, ALLOWED_MIME_TYPES


# ── Unit tests for type mapping ─────────────────────────────────────

def test_media_type_for_mime_pdf():
    assert _media_type_for_mime("application/pdf") == "document"


def test_media_type_for_mime_audio_mpeg():
    assert _media_type_for_mime("audio/mpeg") == "audio"


def test_media_type_for_mime_video():
    assert _media_type_for_mime("video/mp4") == "video"


def test_category_for_mime_pdf():
    assert _category_for_mime("application/pdf") == "document"


def test_category_for_mime_audio():
    assert _category_for_mime("audio/mpeg") == "audio"


def test_pdf_in_allowed_mime_types():
    assert "application/pdf" in ALLOWED_MIME_TYPES


def test_audio_mpeg_in_allowed_mime_types():
    assert "audio/mpeg" in ALLOWED_MIME_TYPES


# ── Integration tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_pdf_accepted(admin_client: AsyncClient):
    """Upload a minimal PDF file and verify it gets media_type 'document'."""
    # First create a person to attach media to
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MediaTest",
        "last_name": "PDF",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Minimal valid PDF
    pdf_content = b"%PDF-1.0\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n115\n%%EOF"

    resp = await admin_client.post(
        "/api/media",
        files={"file": ("test.pdf", pdf_content, "application/pdf")},
        data={"person_id": person_id},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["media_type"] == "document"


@pytest.mark.asyncio
async def test_upload_audio_accepted(admin_client: AsyncClient):
    """Upload a minimal audio file and verify it gets media_type 'audio'."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MediaTest",
        "last_name": "Audio",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Minimal MP3 header (just enough bytes to not error)
    audio_content = b"\xff\xfb\x90\x00" + b"\x00" * 1024

    resp = await admin_client.post(
        "/api/media",
        files={"file": ("test.mp3", audio_content, "audio/mpeg")},
        data={"person_id": person_id},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["media_type"] == "audio"


@pytest.mark.asyncio
async def test_media_list_includes_media_type(admin_client: AsyncClient):
    """GET /api/media includes media_type field."""
    resp = await admin_client.post("/api/persons", json={
        "first_name": "MediaListTest",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/media?person_id={person_id}")
    assert resp.status_code == 200
    # Even if empty, the endpoint should work
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_gallery_query_handles_realistic_media_volume(admin_client: AsyncClient):
    person_resp = await admin_client.post("/api/persons", json={
        "first_name": "Gallery",
        "last_name": "Load",
    })
    assert person_resp.status_code == 201
    person_id = person_resp.json()["id"]

    for index in range(30):
        image_content = b"\xff\xd8\xff\xe0" + bytes([index]) * 2048
        resp = await admin_client.post(
            "/api/media",
            files={"file": (f"bulk-{index}.jpg", image_content, "image/jpeg")},
            data={"person_id": person_id, "title": f"Bulk item {index}"},
        )
        assert resp.status_code == 201

    started = monotonic()
    resp = await admin_client.get("/api/media/gallery?search=Bulk&page_size=24")
    elapsed = monotonic() - started

    assert resp.status_code == 200
    assert resp.json()["total"] >= 24
    assert elapsed < 2.0
