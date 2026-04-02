"""Tests for tree photo headshots feature (S24, Slice 1)."""

import io
import pytest
from httpx import AsyncClient

ROOT_ID = "root-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_tree_data_includes_photo_url(admin_client: AsyncClient):
    """Tree API response includes photo_url per person."""
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    data = resp.json()
    for person in data.get("persons", []):
        assert "photo_url" in person


@pytest.mark.asyncio
async def test_upload_media_and_set_profile_photo(admin_client: AsyncClient):
    """Uploading a photo for a person with no photo_url, then manually setting it."""
    # Create person with no photo
    resp = await admin_client.post("/api/persons", json={
        "first_name": "NoPhoto",
        "last_name": "Person",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]
    assert resp.json()["photo_url"] is None

    # Upload an image
    img_bytes = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    resp = await admin_client.post("/api/media", files={
        "file": ("test.png", img_bytes, "image/png"),
    }, data={"person_id": person_id})
    assert resp.status_code == 201
    media_id = resp.json()["id"]

    # Set photo_url via PUT (same as JS auto-set logic)
    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "photo_url": media_id,
    })
    assert resp.status_code == 200
    assert resp.json()["photo_url"] == media_id

    # Verify tree data now shows the photo
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    tree_person = next(
        (p for p in resp.json()["persons"] if p["id"] == person_id), None
    )
    assert tree_person is not None
    assert tree_person["photo_url"] == media_id


@pytest.mark.asyncio
async def test_existing_photo_not_overwritten(admin_client: AsyncClient):
    """If person already has photo_url, new upload should not change it."""
    # Create person
    resp = await admin_client.post("/api/persons", json={
        "first_name": "HasPhoto",
        "last_name": "Already",
    })
    assert resp.status_code == 201
    person_id = resp.json()["id"]

    # Upload first image and set as profile
    img1 = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 50)
    resp = await admin_client.post("/api/media", files={
        "file": ("first.png", img1, "image/png"),
    }, data={"person_id": person_id})
    assert resp.status_code == 201
    first_media_id = resp.json()["id"]

    resp = await admin_client.put(f"/api/persons/{person_id}", json={
        "photo_url": first_media_id,
    })
    assert resp.status_code == 200

    # Upload second image — person already has photo_url
    img2 = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 60)
    resp = await admin_client.post("/api/media", files={
        "file": ("second.png", img2, "image/png"),
    }, data={"person_id": person_id})
    assert resp.status_code == 201

    # photo_url should still be the first one
    resp = await admin_client.get(f"/api/persons/{person_id}")
    assert resp.status_code == 200
    assert resp.json()["photo_url"] == first_media_id


@pytest.mark.asyncio
async def test_tree_api_no_regression(admin_client: AsyncClient):
    """Tree API still returns persons and relationships without error."""
    resp = await admin_client.get("/api/tree")
    assert resp.status_code == 200
    data = resp.json()
    assert "persons" in data
    assert "parent_child" in data
    assert isinstance(data["persons"], list)
