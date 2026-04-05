"""Tests for S43 features: photo edit-image endpoint, story audio_media_id, TTS keys."""
import io
import pytest
from httpx import AsyncClient
from PIL import Image


ADMIN_ID = "tyler-000-0000-0000-000000000002"


def _make_jpeg(width=80, height=80) -> bytes:
    img = Image.new("RGB", (width, height), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def _create_person(client: AsyncClient, first: str = "Test", last: str = "Person") -> dict:
    resp = await client.post("/api/persons", json={"first_name": first, "last_name": last})
    assert resp.status_code == 201
    return resp.json()


async def _upload_image(client: AsyncClient, person_id: str, tmp_path, monkeypatch) -> str:
    """Upload a test image, return media_id."""
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


# ── edit-image endpoint ───────────────────────────────────────────────────────


class TestEditImageEndpoint:
    """POST /api/media/{id}/edit-image"""

    async def test_edit_image_requires_auth(self, client):
        resp = await client.post("/api/media/nonexistent/edit-image")
        assert resp.status_code == 401

    async def test_edit_image_404_on_unknown_media(self, admin_client):
        data = _make_jpeg()
        resp = await admin_client.post(
            "/api/media/does-not-exist/edit-image",
            files={"file": ("edit.jpg", data, "image/jpeg")},
        )
        assert resp.status_code == 404

    async def test_edit_image_owner_can_edit(self, admin_client, tmp_path, monkeypatch):
        """Owner can replace media file via edit-image."""
        person = await _create_person(admin_client)
        media_id = await _upload_image(admin_client, person["id"], tmp_path, monkeypatch)

        new_data = _make_jpeg(width=60, height=60)
        resp = await admin_client.post(
            f"/api/media/{media_id}/edit-image",
            files={"file": ("edited.jpg", new_data, "image/jpeg")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == media_id

    async def test_edit_image_member_cannot_edit_others(
        self, admin_client, member_client, tmp_path, monkeypatch
    ):
        """Member cannot edit an image they did not upload."""
        person = await _create_person(admin_client)
        media_id = await _upload_image(admin_client, person["id"], tmp_path, monkeypatch)

        new_data = _make_jpeg(width=40, height=40)
        resp = await member_client.post(
            f"/api/media/{media_id}/edit-image",
            files={"file": ("edited.jpg", new_data, "image/jpeg")},
        )
        # Should be forbidden (403) — not the owner
        assert resp.status_code == 403

    async def test_edit_image_rejects_non_image(self, admin_client, tmp_path, monkeypatch):
        """Replacing with a non-image file should be rejected."""
        person = await _create_person(admin_client)
        media_id = await _upload_image(admin_client, person["id"], tmp_path, monkeypatch)

        resp = await admin_client.post(
            f"/api/media/{media_id}/edit-image",
            files={"file": ("audio.mp3", b"\x00\x01\x02", "audio/mpeg")},
        )
        # 400 or 422 — endpoint must reject non-image files
        assert resp.status_code in (400, 422)


# ── Story audio_media_id ──────────────────────────────────────────────────────


class TestStoryAudioMediaId:
    """Stories can have an optional audio_media_id attached."""

    async def test_create_story_without_audio(self, admin_client: AsyncClient):
        person = await _create_person(admin_client)
        resp = await admin_client.post(
            f"/api/wiki/{person['slug']}/stories",
            data={"title": "No Audio", "body": "<p>Plain text story.</p>"},
        )
        assert resp.status_code == 201
        # List endpoint returns audio_media_id = None
        stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
        assert len(stories) == 1
        assert stories[0]["audio_media_id"] is None

    async def test_create_story_with_audio_media_id(self, admin_client: AsyncClient, tmp_path, monkeypatch):
        """Create story with audio_media_id — field is persisted and returned."""
        person = await _create_person(admin_client)

        # Upload a minimal audio file
        monkeypatch.setenv("DATA_DIR", str(tmp_path))
        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path)),
        )
        audio_bytes = b"ID3" + b"\x00" * 128  # minimal MP3-like header
        audio_resp = await admin_client.post(
            "/api/media",
            data={"person_id": person["id"]},
            files={"file": ("voice.mp3", audio_bytes, "audio/mpeg")},
        )
        assert audio_resp.status_code == 201
        audio_id = audio_resp.json()["id"]

        # Create story with audio attached
        resp = await admin_client.post(
            f"/api/wiki/{person['slug']}/stories",
            data={
                "title": "Story with Voice",
                "body": "<p>Listen along.</p>",
                "audio_media_id": audio_id,
            },
        )
        assert resp.status_code == 201

        # Confirm via list API
        stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
        assert len(stories) == 1
        assert stories[0]["audio_media_id"] == audio_id

    async def test_update_story_clears_audio(self, admin_client: AsyncClient, tmp_path, monkeypatch):
        """Update with empty audio_media_id clears the attachment."""
        person = await _create_person(admin_client)

        # Upload audio
        monkeypatch.setenv("DATA_DIR", str(tmp_path))
        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path)),
        )
        audio_bytes = b"ID3" + b"\x00" * 128
        audio_resp = await admin_client.post(
            "/api/media",
            data={"person_id": person["id"]},
            files={"file": ("voice.mp3", audio_bytes, "audio/mpeg")},
        )
        audio_id = audio_resp.json()["id"]

        # Create with audio
        create_resp = await admin_client.post(
            f"/api/wiki/{person['slug']}/stories",
            data={"title": "Voiced Story", "body": "<p>Heard it.</p>", "audio_media_id": audio_id},
        )
        assert create_resp.status_code == 201
        stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
        story_id = stories[0]["id"]
        assert stories[0]["audio_media_id"] == audio_id

        # Update, clearing audio
        await admin_client.put(
            f"/api/wiki/{person['slug']}/stories/{story_id}",
            data={"title": "Voiced Story", "body": "<p>Silent now.</p>", "audio_media_id": ""},
        )
        stories2 = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
        assert stories2[0]["audio_media_id"] is None


# ── i18n keys for S43 ────────────────────────────────────────────────────────


class TestS43I18nKeys:
    """New locale keys introduced in S43 are present in all locales."""

    S43_MEDIA_KEYS = [
        "edit_photo",
        "edit_photo_title",
        "edit_photo_confirm",
        "edit_photo_cancel",
        "edit_photo_rotate_left",
        "edit_photo_rotate_right",
        "edit_photo_saved",
        "edit_before_upload",
    ]

    S43_STORY_AUDIO_KEYS = [
        "attach_audio",
        "audio_player_label",
        "listen",
        "stop_listening",
    ]

    S43_TREE_KEYS = [
        "edit_name_title",
        "ctx_edit_relationships",
        "sidebar_popout",
        "sidebar_dock",
        "remove_relationship_action",
        "remove_relationship_confirm",
    ]

    def _load_locale(self, locale: str) -> dict:
        import json
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "locales", f"{locale}.json"
        )
        with open(path) as f:
            return json.load(f)

    @pytest.mark.parametrize("locale", ["en", "es", "ru", "it", "zh"])
    def test_media_edit_keys_present(self, locale: str):
        data = self._load_locale(locale)
        media = data.get("media", {})
        for key in self.S43_MEDIA_KEYS:
            assert key in media, f"Missing media.{key} in {locale}.json"

    @pytest.mark.parametrize("locale", ["en", "es", "ru", "it", "zh"])
    def test_story_audio_keys_present(self, locale: str):
        data = self._load_locale(locale)
        stories = data.get("stories", {})
        for key in self.S43_STORY_AUDIO_KEYS:
            assert key in stories, f"Missing stories.{key} in {locale}.json"

    @pytest.mark.parametrize("locale", ["en", "es", "ru", "it", "zh"])
    def test_tree_interaction_keys_present(self, locale: str):
        data = self._load_locale(locale)
        tree = data.get("tree", {})
        for key in self.S43_TREE_KEYS:
            assert key in tree, f"Missing tree.{key} in {locale}.json"
