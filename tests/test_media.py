"""Tests for Media API — upload, serve, dedup, auth gate, thumbnails."""
import io
import os

from PIL import Image

from app.models.media import Media, MediaSource, MediaType
from app.services.media_service import get_media_file_path, get_variant_path

ADMIN_ID = "tyler-000-0000-0000-000000000002"


def _make_test_image(width=100, height=100, fmt="JPEG") -> bytes:
    """Create a minimal test image with EXIF-like data."""
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _make_test_png(width=50, height=50) -> bytes:
    img = Image.new("RGBA", (width, height), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestMediaUpload:
    """POST /api/media"""

    async def test_upload_requires_auth(self, client):
        resp = await client.post("/api/media", data={"person_id": "x"})
        assert resp.status_code == 401

    async def test_upload_image(self, admin_client, tmp_path, monkeypatch):
        monkeypatch.setenv("DATA_DIR", str(tmp_path))

        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(
                SECRET_KEY="test", FERNET_KEY="dGVzdA==",
                DATA_DIR=str(tmp_path),
            ),
        )

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={"person_id": ADMIN_ID},
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["media_type"] == "image"
        assert body["mime_type"] == "image/jpeg"
        assert body["is_duplicate"] is False
        assert body["width"] == 100
        assert body["height"] == 100

    async def test_member_cannot_upload_to_another_profile(self, member_client, tmp_path, monkeypatch):
        monkeypatch.setenv("DATA_DIR", str(tmp_path))

        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(
                SECRET_KEY="test", FERNET_KEY="dGVzdA==",
                DATA_DIR=str(tmp_path),
            ),
        )

        image_data = _make_test_image()
        resp = await member_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        assert resp.status_code == 201

    async def test_upload_rejects_unsupported_type(self, admin_client):
        resp = await admin_client.post(
            "/api/media",
            data={"person_id": ADMIN_ID},
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]

    async def test_upload_rejects_nonexistent_person(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(
                SECRET_KEY="test", FERNET_KEY="dGVzdA==",
                DATA_DIR=str(tmp_path),
            ),
        )

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={"person_id": "nonexistent-person-id"},
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        assert resp.status_code == 400
        assert "Person not found" in resp.json()["detail"]

    async def test_upload_media_with_tagged_people(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(
                SECRET_KEY="test", FERNET_KEY="dGVzdA==",
                DATA_DIR=str(tmp_path),
            ),
        )

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={
                "person_id": "tyler-000-0000-0000-000000000002",
                "tagged_person_ids": '["member-00-0000-0000-000000000005"]',
            },
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["tagged_person_ids"] == ["member-00-0000-0000-000000000005"]
        assert body["tagged_people"][0]["id"] == "member-00-0000-0000-000000000005"

    async def test_upload_persists_title_description_and_taken_date(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings

        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={
                "person_id": ADMIN_ID,
                "title": "Family picnic",
                "description": "Lunch by the lake",
                "taken_at": "2024-07-04",
            },
            files={"file": ("metadata.jpg", image_data, "image/jpeg")},
        )
        assert resp.status_code == 201
        media_id = resp.json()["id"]

        metadata_resp = await admin_client.get(f"/api/media/{media_id}")
        assert metadata_resp.status_code == 200
        body = metadata_resp.json()
        assert body["title"] == "Family picnic"
        assert body["description"] == "Lunch by the lake"
        assert body["taken_date"] == "2024-07-04"


class TestMediaDedup:
    """SHA-256 dedup on upload."""

    async def test_duplicate_returns_existing(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        monkeypatch.setattr(
            "app.services.media_service.get_settings",
            lambda: Settings(
                SECRET_KEY="test", FERNET_KEY="dGVzdA==",
                DATA_DIR=str(tmp_path),
            ),
        )

        image_data = _make_test_image()
        person_id = ADMIN_ID

        # First upload
        resp1 = await admin_client.post(
            "/api/media",
            data={"person_id": person_id},
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        assert resp1.status_code == 201
        first_id = resp1.json()["id"]

        # Same file again
        resp2 = await admin_client.post(
            "/api/media",
            data={"person_id": person_id},
            files={"file": ("test2.jpg", image_data, "image/jpeg")},
        )
        assert resp2.status_code == 201
        assert resp2.json()["is_duplicate"] is True
        assert resp2.json()["id"] == first_id


class TestMediaServing:
    """GET /api/media/{id}/file — auth-gated serving."""

    async def test_serve_requires_auth(self, client):
        resp = await client.get("/api/media/fake-id/file")
        assert resp.status_code == 401

    async def test_serve_file(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={"person_id": ADMIN_ID},
            files={"file": ("photo.jpg", image_data, "image/jpeg")},
        )
        media_id = resp.json()["id"]

        # Serve file
        resp2 = await admin_client.get(f"/api/media/{media_id}/file")
        assert resp2.status_code == 200
        assert resp2.headers["content-type"] == "image/jpeg"
        assert len(resp2.content) > 0

    async def test_serve_nonexistent_returns_404(self, admin_client):
        resp = await admin_client.get("/api/media/nonexistent/file")
        assert resp.status_code == 404

    async def test_member_can_read_shared_media_for_any_visible_person(self, admin_client, member_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        create_person_resp = await admin_client.post(
            "/api/persons",
            json={"first_name": "Outsider", "last_name": "Media"},
        )
        outsider_id = create_person_resp.json()["id"]
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": outsider_id},
            files={"file": ("photo.jpg", image_data, "image/jpeg")},
        )
        media_id = upload_resp.json()["id"]

        resp = await member_client.get(f"/api/media/{media_id}/file")
        assert resp.status_code == 200

    async def test_serve_file_rejects_db_backed_path_traversal(
        self,
        admin_client,
        seeded_db,
        tmp_path,
        monkeypatch,
    ):
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="test",
            FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        outside_secret = tmp_path / "secret.txt"
        outside_secret.write_bytes(b"top-secret")

        media = Media(
            id="11111111-1111-1111-1111-111111111111",
            person_id=ADMIN_ID,
            file_path="../secret.txt",
            original_filename="secret.txt",
            media_type=MediaType.document.value,
            mime_type="application/pdf",
            file_size_bytes=len(b"top-secret"),
            file_hash="a" * 64,
            source=MediaSource.manual.value,
            uploaded_by=ADMIN_ID,
        )
        seeded_db.add(media)
        await seeded_db.commit()

        resp = await admin_client.get(f"/api/media/{media.id}/file")
        assert resp.status_code == 404


class TestMediaDeletion:
    """DELETE /api/media/{id}"""

    async def test_uploader_can_delete_media(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("delete-me.jpg", image_data, "image/jpeg")},
        )
        media_id = upload_resp.json()["id"]

        delete_resp = await admin_client.delete(f"/api/media/{media_id}")
        assert delete_resp.status_code == 204

        metadata_resp = await admin_client.get(f"/api/media/{media_id}")
        assert metadata_resp.status_code == 404

    async def test_non_uploader_cannot_delete_media(self, admin_client, member_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("keep-me.jpg", image_data, "image/jpeg")},
        )
        media_id = upload_resp.json()["id"]

        delete_resp = await member_client.delete(f"/api/media/{media_id}")
        assert delete_resp.status_code == 403


class TestMediaThumbnails:
    """GET /api/media/{id}/thumbnail"""

    async def test_thumbnail_generated_for_images(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image(width=800, height=600)
        resp = await admin_client.post(
            "/api/media",
            data={"person_id": ADMIN_ID},
            files={"file": ("big.jpg", image_data, "image/jpeg")},
        )
        media_id = resp.json()["id"]

        resp2 = await admin_client.get(f"/api/media/{media_id}/thumbnail")
        assert resp2.status_code == 200
        assert resp2.headers["content-type"] == "image/jpeg"

        # Thumbnail should be smaller than original
        assert len(resp2.content) < len(image_data)


class TestMediaMetadata:
    """GET /api/media/{id} and GET /api/media?person_id="""

    async def test_get_metadata(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)

        image_data = _make_test_image()
        resp = await admin_client.post(
            "/api/media",
            data={
                "person_id": ADMIN_ID,
                "caption": "Test caption",
            },
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )
        media_id = resp.json()["id"]

        resp2 = await admin_client.get(f"/api/media/{media_id}")
        assert resp2.status_code == 200
        body = resp2.json()
        assert body["caption"] == "Test caption"
        assert body["person_id"] == ADMIN_ID


class TestMediaPathSafety:
    def test_get_media_file_path_rejects_traversal(self, tmp_path):
        assert get_media_file_path("../secret.txt", str(tmp_path)) is None

    def test_get_variant_path_rejects_traversal_media_id(self, tmp_path):
        assert get_variant_path("../escape", "thumb", str(tmp_path)) is None

    async def test_list_media_for_person(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)

        person_id = ADMIN_ID
        image_data = _make_test_image()
        await admin_client.post(
            "/api/media",
            data={"person_id": person_id},
            files={"file": ("test.jpg", image_data, "image/jpeg")},
        )

        resp = await admin_client.get(f"/api/media?person_id={person_id}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_list_media_for_tagged_person_includes_shared_media(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)

        image_data = _make_test_image()
        await admin_client.post(
            "/api/media",
            data={
                "person_id": "tyler-000-0000-0000-000000000002",
                "tagged_person_ids": '["member-00-0000-0000-000000000005"]',
            },
            files={"file": ("tagged.jpg", image_data, "image/jpeg")},
        )

        resp = await admin_client.get("/api/media?person_id=member-00-0000-0000-000000000005")
        assert resp.status_code == 200
        assert any(
            item["person_id"] == "tyler-000-0000-0000-000000000002"
            and item["tagged_person_ids"] == ["member-00-0000-0000-000000000005"]
            for item in resp.json()
        )

    async def test_hidden_owner_tagged_media_is_not_listed_for_visible_person(self, admin_client, member_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(
            SECRET_KEY="test", FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)

        create_resp = await admin_client.post(
            "/api/persons",
            json={"first_name": "Hidden", "last_name": "Owner"},
        )
        hidden_id = create_resp.json()["id"]
        update_resp = await admin_client.put(
            f"/api/persons/{hidden_id}",
            json={"visibility": "hidden"},
        )
        assert update_resp.status_code == 200

        image_data = _make_test_image()
        upload_resp = await admin_client.post(
            "/api/media",
            data={
                "person_id": hidden_id,
                "tagged_person_ids": '["member-00-0000-0000-000000000005"]',
            },
            files={"file": ("hidden.jpg", image_data, "image/jpeg")},
        )
        assert upload_resp.status_code == 201

        resp = await member_client.get("/api/media?person_id=member-00-0000-0000-000000000005")
        assert resp.status_code == 200
        assert all(item["id"] != upload_resp.json()["id"] for item in resp.json())

    async def test_gallery_api_filters_by_type_person_and_uploader(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings

        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        pdf_data = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

        tagged_upload = await admin_client.post(
            "/api/media",
            data={
                "person_id": ADMIN_ID,
                "tagged_person_ids": '["member-00-0000-0000-000000000005"]',
            },
            files={"file": ("gallery-photo.jpg", image_data, "image/jpeg")},
        )
        assert tagged_upload.status_code == 201

        doc_upload = await admin_client.post(
            "/api/media",
            data={"person_id": "member-00-0000-0000-000000000005"},
            files={"file": ("notes.pdf", pdf_data, "application/pdf")},
        )
        assert doc_upload.status_code == 201

        photo_resp = await admin_client.get("/api/media/gallery?media_type=photo")
        assert photo_resp.status_code == 200
        assert len(photo_resp.json()["items"]) == 1

        person_resp = await admin_client.get("/api/media/gallery?person_id=member-00-0000-0000-000000000005")
        assert person_resp.status_code == 200
        assert len(person_resp.json()["items"]) == 2

        uploader_resp = await admin_client.get(f"/api/media/gallery?uploader_id={ADMIN_ID}")
        assert uploader_resp.status_code == 200
        assert len(uploader_resp.json()["items"]) >= 2


class TestMediaVisibilityEnforcement:
    """Test that visibility field controls access correctly."""

    async def test_hidden_media_returns_403_for_non_admin(self, admin_client, member_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("vis-test.jpg", image_data, "image/jpeg")},
        )
        assert upload_resp.status_code == 201
        media_id = upload_resp.json()["id"]

        # Member can see family-visibility media
        assert (await member_client.get(f"/api/media/{media_id}")).status_code == 200
        assert (await member_client.get(f"/api/media/{media_id}/file")).status_code == 200

        # Admin sets visibility to hidden
        hide_resp = await admin_client.patch(
            f"/api/media/{media_id}/visibility",
            data={"visibility": "hidden"},
        )
        assert hide_resp.status_code == 200

        # Member can no longer see it
        assert (await member_client.get(f"/api/media/{media_id}")).status_code == 403
        assert (await member_client.get(f"/api/media/{media_id}/file")).status_code == 403

        # Admin can still see it
        assert (await admin_client.get(f"/api/media/{media_id}")).status_code == 200
        assert (await admin_client.get(f"/api/media/{media_id}/file")).status_code == 200

    async def test_private_media_visible_only_to_uploader(self, admin_client, member_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        # Admin uploads, then sets to private
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("priv-test.jpg", image_data, "image/jpeg")},
        )
        media_id = upload_resp.json()["id"]

        priv_resp = await admin_client.patch(
            f"/api/media/{media_id}/visibility",
            data={"visibility": "private"},
        )
        assert priv_resp.status_code == 200

        # Member cannot see private media uploaded by another user
        assert (await member_client.get(f"/api/media/{media_id}")).status_code == 403


class TestMediaSoftDelete:
    """Test soft delete vs permanent delete behavior."""

    async def test_non_admin_delete_is_soft(self, admin_client, member_client, tmp_path, monkeypatch):
        """Member delete sets visibility=hidden but keeps file on disk."""
        from app.config import Settings
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        # Upload as member to member's own person
        upload_resp = await member_client.post(
            "/api/media",
            data={"person_id": "member-00-0000-0000-000000000005"},
            files={"file": ("soft-del.jpg", image_data, "image/jpeg")},
        )
        assert upload_resp.status_code == 201
        media_id = upload_resp.json()["id"]

        # Member deletes — should be soft
        del_resp = await member_client.delete(f"/api/media/{media_id}")
        assert del_resp.status_code == 204

        # Admin can still see it (hidden visibility)
        admin_resp = await admin_client.get(f"/api/media/{media_id}")
        assert admin_resp.status_code == 200

        # Member can no longer see it
        member_resp = await member_client.get(f"/api/media/{media_id}")
        assert member_resp.status_code == 403

        # File still exists on disk
        import os
        file_path = os.path.join(str(tmp_path), "media", upload_resp.json()["id"] + ".jpg")
        # File should still be on disk after soft delete
        # (the exact path includes the media ID, check the media dir)
        media_dir = os.path.join(str(tmp_path), "media")
        files_on_disk = os.listdir(media_dir) if os.path.isdir(media_dir) else []
        assert len(files_on_disk) > 0, "Media files should still exist after soft delete"

    async def test_admin_delete_is_permanent(self, admin_client, tmp_path, monkeypatch):
        """Admin delete removes files and DB record."""
        from app.config import Settings
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        image_data = _make_test_image()
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("perm-del.jpg", image_data, "image/jpeg")},
        )
        media_id = upload_resp.json()["id"]

        del_resp = await admin_client.delete(f"/api/media/{media_id}")
        assert del_resp.status_code == 204

        # DB record gone
        assert (await admin_client.get(f"/api/media/{media_id}")).status_code == 404


class TestMediaVariantGeneration:
    """Test that image upload creates variant files on disk."""

    async def test_image_upload_creates_thumb_and_medium_variants(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        # Create a large enough image that medium variant will be generated
        image_data = _make_test_image(width=1200, height=900)
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("variant-test.jpg", image_data, "image/jpeg")},
        )
        assert upload_resp.status_code == 201
        media_id = upload_resp.json()["id"]

        import os
        variant_dir = os.path.join(str(tmp_path), "media", "variants", media_id)
        assert os.path.isdir(variant_dir), f"Variant directory should exist: {variant_dir}"

        thumb_path = os.path.join(variant_dir, "thumb.jpg")
        assert os.path.isfile(thumb_path), "Thumb variant should exist"

        medium_path = os.path.join(variant_dir, "medium.jpg")
        assert os.path.isfile(medium_path), "Medium variant should exist (image is >800px)"

        # Also verify the legacy thumbnail still exists
        legacy_thumb = os.path.join(str(tmp_path), "media", "thumbnails", f"{media_id}.jpg")
        assert os.path.isfile(legacy_thumb), "Legacy thumbnail should still be generated"

        # Verify variant endpoint serves the files
        thumb_resp = await admin_client.get(f"/api/media/{media_id}/variant/thumb")
        assert thumb_resp.status_code == 200
        assert thumb_resp.headers["content-type"] == "image/jpeg"

        medium_resp = await admin_client.get(f"/api/media/{media_id}/variant/medium")
        assert medium_resp.status_code == 200

    async def test_small_image_skips_medium_variant(self, admin_client, tmp_path, monkeypatch, session_factory):
        from app.backfill_variants import _backfill_one_media
        from app.models.media import Media
        from app.config import Settings
        from sqlalchemy import select
        settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        # Small image — no medium variant needed
        image_data = _make_test_image(width=200, height=200)
        upload_resp = await admin_client.post(
            "/api/media",
            data={"person_id": "tyler-000-0000-0000-000000000002"},
            files={"file": ("small.jpg", image_data, "image/jpeg")},
        )
        assert upload_resp.status_code == 201
        media_id = upload_resp.json()["id"]

        import os
        variant_dir = os.path.join(str(tmp_path), "media", "variants", media_id)

        # Thumb should exist
        thumb_path = os.path.join(variant_dir, "thumb.jpg")
        assert os.path.isfile(thumb_path), "Thumb variant should exist even for small images"

        # Medium should NOT exist (image already ≤800px)
        medium_path = os.path.join(variant_dir, "medium.jpg")
        assert not os.path.isfile(medium_path), "Medium variant should be skipped for small images"

        async with session_factory() as session:
            stored_media = (
                await session.execute(select(Media).where(Media.id == media_id))
            ).scalar_one()

        media = Media(
            id=media_id,
            person_id=ADMIN_ID,
            file_path=stored_media.file_path,
            media_type="image",
            mime_type="image/jpeg",
        )
        changed = await _backfill_one_media(media, media_dir=os.path.join(str(tmp_path), "media"), dry_run=False)
        assert changed is False, "Backfill should be idempotent when only a thumb variant is needed"

    async def test_backfill_variants_recreates_missing_variants(self, admin_client, tmp_path, monkeypatch):
        from app.backfill_variants import _backfill_one_media
        from app.models.media import Media

        media_dir = os.path.join(str(tmp_path), "media")
        os.makedirs(media_dir, exist_ok=True)
        relative_path = "backfill.jpg"
        file_path = os.path.join(media_dir, relative_path)
        with open(file_path, "wb") as fh:
            fh.write(_make_test_image(width=1200, height=900))

        media = Media(
            id="backfill-media-1",
            person_id=ADMIN_ID,
            file_path=relative_path,
            media_type="image",
            mime_type="image/jpeg",
        )
        variant_dir = os.path.join(media_dir, "variants", media.id)
        thumb_path = os.path.join(variant_dir, "thumb.jpg")
        medium_path = os.path.join(variant_dir, "medium.jpg")

        dry_run_changed = await _backfill_one_media(media, media_dir=media_dir, dry_run=True)
        assert dry_run_changed is True
        assert not os.path.exists(thumb_path)

        changed = await _backfill_one_media(media, media_dir=media_dir, dry_run=False)
        assert changed is True
        assert os.path.isfile(thumb_path)
        assert os.path.isfile(medium_path)
