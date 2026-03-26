"""Tests for media purpose classification (S23, Slice 2)."""

import io
import pytest
from httpx import AsyncClient

ADMIN_ID = "tyler-000-0000-0000-000000000002"


def _tiny_png():
    """Return a minimal valid PNG file."""
    import struct
    import zlib
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc & 0xffffffff)
    raw = zlib.compress(b'\x00\x00\x00\x00')
    idat_crc = zlib.crc32(b'IDAT' + raw)
    idat = struct.pack('>I', len(raw)) + b'IDAT' + raw + struct.pack('>I', idat_crc & 0xffffffff)
    iend_crc = zlib.crc32(b'IEND')
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc & 0xffffffff)
    return sig + ihdr + idat + iend


@pytest.mark.asyncio
async def test_upload_media_default_purpose(admin_client: AsyncClient):
    """Upload without purpose defaults to 'memory'."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID},
        files={"file": ("test.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    assert resp.status_code == 201
    assert resp.json()["purpose"] == "memory"


@pytest.mark.asyncio
async def test_upload_media_with_purpose(admin_client: AsyncClient):
    """Upload with purpose='document' returns correct value."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID, "purpose": "document"},
        files={"file": ("doc.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    assert resp.status_code == 201
    assert resp.json()["purpose"] == "document"


@pytest.mark.asyncio
async def test_upload_media_evidence_purpose(admin_client: AsyncClient):
    """Upload with purpose='evidence' works."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID, "purpose": "evidence"},
        files={"file": ("ev.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    assert resp.status_code == 201
    assert resp.json()["purpose"] == "evidence"


@pytest.mark.asyncio
async def test_upload_media_invalid_purpose(admin_client: AsyncClient):
    """Invalid purpose returns 422."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID, "purpose": "classified"},
        files={"file": ("bad.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_media_metadata_includes_purpose(admin_client: AsyncClient):
    """GET /api/media/{id} returns purpose."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID, "purpose": "evidence"},
        files={"file": ("meta.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    media_id = resp.json()["id"]

    resp = await admin_client.get(f"/api/media/{media_id}")
    assert resp.status_code == 200
    assert resp.json()["purpose"] == "evidence"


@pytest.mark.asyncio
async def test_update_media_purpose(admin_client: AsyncClient):
    """PATCH /api/media/{id} updates purpose."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID},
        files={"file": ("upd.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    media_id = resp.json()["id"]

    resp = await admin_client.patch(
        f"/api/media/{media_id}",
        data={"purpose": "document"},
    )
    assert resp.status_code == 200
    assert resp.json()["purpose"] == "document"


@pytest.mark.asyncio
async def test_update_media_invalid_purpose(admin_client: AsyncClient):
    """PATCH with invalid purpose returns 422."""
    resp = await admin_client.post(
        "/api/media",
        data={"person_id": ADMIN_ID},
        files={"file": ("inv.png", io.BytesIO(_tiny_png()), "image/png")},
    )
    media_id = resp.json()["id"]

    resp = await admin_client.patch(
        f"/api/media/{media_id}",
        data={"purpose": "secret"},
    )
    assert resp.status_code == 422
