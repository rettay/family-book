"""Tests for S45 gallery management: metadata editor, person tagging, sidebar edit controls."""
import io
import pytest
from httpx import AsyncClient
from PIL import Image


ADMIN_ID = "tyler-000-0000-0000-000000000002"
MEMBER_ID = "member-00-0000-0000-000000000005"
PERSON_ID = "grndpa-00-0000-0000-000000000004"


def _make_jpeg(width=60, height=60) -> bytes:
    img = Image.new("RGB", (width, height), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def _upload_image(client: AsyncClient, person_id: str, tmp_path, monkeypatch) -> str:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.config import Settings
    monkeypatch.setattr(
        "app.services.media_service.get_settings",
        lambda: Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path)),
    )
    data = _make_jpeg()
    resp = await client.post(
        "/api/media",
        data={"person_id": person_id},
        files={"file": ("photo.jpg", data, "image/jpeg")},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── FB-101: taken_location field ─────────────────────────────────────────────

class TestTakenLocation:
    async def test_patch_accepts_taken_location(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await admin_client.patch(
            f"/api/media/{media_id}",
            data={"taken_location": "Brooklyn, NY"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["taken_location"] == "Brooklyn, NY"

    async def test_patch_persists_taken_location(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        await admin_client.patch(f"/api/media/{media_id}", data={"taken_location": "Palermo, Sicily"})
        get_resp = await admin_client.get(f"/api/media/{media_id}")
        assert get_resp.status_code == 200

    async def test_patch_taken_location_requires_auth(self, client):
        resp = await client.patch("/api/media/nonexistent", data={"taken_location": "Paris"})
        assert resp.status_code == 401

    async def test_serialize_includes_taken_location(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        await admin_client.patch(f"/api/media/{media_id}", data={"taken_location": "Rome"})
        # Gallery endpoint serializes items with taken_location
        gallery_resp = await admin_client.get("/api/media/gallery")
        assert gallery_resp.status_code == 200
        items = gallery_resp.json()["items"]
        match = next((i for i in items if i["id"] == media_id), None)
        assert match is not None
        assert match["taken_location"] == "Rome"

    async def test_patch_person_id_changes_subject(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await admin_client.patch(
            f"/api/media/{media_id}",
            data={"person_id": ADMIN_ID},
        )
        assert resp.status_code == 200
        assert resp.json()["person_id"] == ADMIN_ID

    async def test_patch_invalid_person_id_returns_400(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await admin_client.patch(
            f"/api/media/{media_id}",
            data={"person_id": "does-not-exist"},
        )
        assert resp.status_code == 400

    async def test_non_owner_cannot_patch(self, admin_client, member_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await member_client.patch(
            f"/api/media/{media_id}",
            data={"title": "Hijacked"},
        )
        assert resp.status_code == 403


# ── FB-102: Person tagging API ────────────────────────────────────────────────

class TestPersonTagging:
    async def test_add_tag(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await admin_client.post(
            f"/api/media/{media_id}/tags",
            data={"person_id": MEMBER_ID},
        )
        assert resp.status_code == 200
        tagged = resp.json()
        assert any(t["id"] == MEMBER_ID for t in tagged)

    async def test_add_tag_idempotent(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        r1 = await admin_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        r2 = await admin_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Still only one entry for this person
        tagged = r2.json()
        ids = [t["id"] for t in tagged]
        assert ids.count(MEMBER_ID) == 1

    async def test_get_tags(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        await admin_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        resp = await admin_client.get(f"/api/media/{media_id}/tags")
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()]
        assert MEMBER_ID in ids

    async def test_remove_tag(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        await admin_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        del_resp = await admin_client.delete(f"/api/media/{media_id}/tags/{MEMBER_ID}")
        assert del_resp.status_code == 200
        remaining = del_resp.json()
        assert not any(t["id"] == MEMBER_ID for t in remaining)

    async def test_remove_nonexistent_tag_returns_404(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await admin_client.delete(f"/api/media/{media_id}/tags/{MEMBER_ID}")
        assert resp.status_code == 404

    async def test_tag_requires_auth(self, client):
        resp = await client.post("/api/media/nonexistent/tags", data={"person_id": MEMBER_ID})
        assert resp.status_code == 401

    async def test_non_owner_cannot_tag(self, admin_client, member_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        resp = await member_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        assert resp.status_code == 403

    async def test_serialize_includes_tagged_people(self, admin_client, tmp_path, monkeypatch):
        media_id = await _upload_image(admin_client, PERSON_ID, tmp_path, monkeypatch)
        await admin_client.post(f"/api/media/{media_id}/tags", data={"person_id": MEMBER_ID})
        gallery_resp = await admin_client.get("/api/media/gallery")
        assert gallery_resp.status_code == 200
        items = gallery_resp.json()["items"]
        match = next((i for i in items if i["id"] == media_id), None)
        assert match is not None
        assert any(tp["id"] == MEMBER_ID for tp in match["tagged_people"])


# ── i18n keys ─────────────────────────────────────────────────────────────────

S45_MEDIA_KEYS = [
    "edit_details",
    "taken_date_label",
    "taken_location_label",
    "person_label",
    "save_details",
    "details_saved",
    "tag_people",
    "tagged_in",
    "add_tag",
    "remove_tag",
]
LOCALES = ["en", "es", "it", "ru", "zh"]


@pytest.mark.parametrize("locale", LOCALES)
def test_s45_media_keys_present(locale):
    import json, pathlib
    path = pathlib.Path("locales") / f"{locale}.json"
    data = json.loads(path.read_text())
    media = data.get("media", {})
    for key in S45_MEDIA_KEYS:
        assert key in media, f"Missing media.{key} in {locale}.json"
