"""Tests for Moments API — CRUD, feed, permissions."""

import re
from pathlib import Path


ADMIN_ID = "tyler-000-0000-0000-000000000002"
TYLER_ID = "tyler-000-0000-0000-000000000002"
MEMBER_ID = "member-00-0000-0000-000000000005"


class TestMomentsCRUD:
    """POST, GET, PUT, DELETE /api/moments"""

    async def test_create_requires_auth(self, client):
        resp = await client.post("/api/moments", json={"kind": "text"})
        assert resp.status_code == 401

    async def test_create_text_moment(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Hello family!",
            "person_id": ADMIN_ID,
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["kind"] == "text"
        assert body["body"] == "Hello family!"
        assert body["poster"]["id"] == ADMIN_ID
        assert body["about"]["id"] == ADMIN_ID
        assert body["reactions"] == {}
        assert body["comment_count"] == 0

    async def test_create_moment_defaults_person_to_current_user(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Auto person_id",
        })
        assert resp.status_code == 201
        assert resp.json()["about"]["id"] == ADMIN_ID

    async def test_member_can_create_moment_for_other_person(self, member_client):
        resp = await member_client.post("/api/moments", json={
            "kind": "text",
            "body": "Impersonation attempt",
            "person_id": TYLER_ID,
        })
        assert resp.status_code == 201
        assert resp.json()["about"]["id"] == TYLER_ID

    async def test_create_moment_with_media_ids(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "photo",
            "body": "With photos",
            "media_ids": ["fake-media-id-1"],
        })
        assert resp.status_code == 201
        assert resp.json()["media"] == []  # fake ID, no media found

    async def test_create_story_moment_with_tagged_people(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Story about more than one person",
            "title": "A shared memory",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
            "occurred_at": "1998-06-15T12:00:00Z",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["kind"] == "story"
        assert body["title"] == "A shared memory"
        assert body["occurred_at"].startswith("1998-06-15")
        assert body["tagged_people"] == [{
            "id": MEMBER_ID,
            "display_name": "Jane Martin",
            "photo_url": None,
        }]

    async def test_create_story_moment_with_multiple_uploaded_media(self, admin_client, tmp_path, monkeypatch):
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="test",
            FERNET_KEY="dGVzdA==",
            DATA_DIR=str(tmp_path),
        )
        monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
        monkeypatch.setattr("app.routes.media.get_settings", lambda: settings)

        photo_paths = [
            Path(__file__).resolve().parents[1] / "app/static/demo-photos/family-dinner.jpg",
            Path(__file__).resolve().parents[1] / "app/static/demo-photos/summer-reunion.jpg",
        ]
        media_ids = []
        for photo_path in photo_paths:
            with photo_path.open("rb") as handle:
                upload_resp = await admin_client.post(
                    "/api/media",
                    data={"person_id": TYLER_ID},
                    files={"file": (photo_path.name, handle.read(), "image/jpeg")},
                )
            assert upload_resp.status_code == 201
            media_ids.append(upload_resp.json()["id"])

        resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "A richer memory with multiple photos.",
            "title": "Family reunion album",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
            "media_ids": media_ids,
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Family reunion album"
        assert len(body["media"]) == 2
        assert {item["id"] for item in body["media"]} == set(media_ids)
        assert body["tagged_people"][0]["id"] == MEMBER_ID

    async def test_shared_event_filter_applies_before_limit_for_person_feed(self, admin_client):
        shared_resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Older shared event",
            "title": "Shared Event Anchor",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
            "occurred_at": "2001-01-01T12:00:00Z",
        })
        assert shared_resp.status_code == 201

        for day in range(1, 22):
            resp = await admin_client.post("/api/moments", json={
                "kind": "text",
                "body": f"Recent personal note {day}",
                "person_id": TYLER_ID,
                "occurred_at": f"2024-02-{day:02d}T12:00:00Z",
            })
            assert resp.status_code == 201

        feed_resp = await admin_client.get(f"/api/moments?person={TYLER_ID}&limit=20&shared=true")
        assert feed_resp.status_code == 200
        payload = feed_resp.json()
        titles = [item["title"] for item in payload]
        assert "Shared Event Anchor" in titles
        assert all(item["tagged_people"] for item in payload)

    async def test_create_rejects_empty_moment(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "   ",
            "title": "",
        })
        assert resp.status_code == 400

    async def test_create_rejects_invalid_visibility(self, member_client):
        resp = await member_client.post("/api/moments", json={
            "kind": "text",
            "body": "Invisible ghost post",
            "visibility": "custom",
        })
        assert resp.status_code == 400

    async def test_update_moment_supports_richer_fields(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Original",
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.put(f"/api/moments/{moment_id}", json={
            "title": "Edited story title",
            "body": "Edited story body",
            "tagged_person_ids": [MEMBER_ID],
            "occurred_at": "2001-09-09T12:00:00Z",
        })
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["title"] == "Edited story title"
        assert payload["body"] == "Edited story body"
        assert payload["occurred_at"].startswith("2001-09-09")
        assert payload["tagged_people"][0]["id"] == MEMBER_ID

    async def test_update_rejects_invalid_visibility(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Original",
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.put(f"/api/moments/{moment_id}", json={
            "visibility": "custom",
        })
        assert resp.status_code == 400

    async def test_create_moment_bad_person(self, admin_client):
        resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "person_id": "nonexistent",
        })
        assert resp.status_code == 400

    async def test_get_moment(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Get me",
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.get(f"/api/moments/{moment_id}")
        assert resp.status_code == 200
        assert resp.json()["body"] == "Get me"

    async def test_get_nonexistent_moment(self, admin_client):
        resp = await admin_client.get("/api/moments/nonexistent")
        assert resp.status_code == 404

    async def test_update_moment(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Original",
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.put(f"/api/moments/{moment_id}", json={
            "body": "Edited",
        })
        assert resp.status_code == 200
        assert resp.json()["body"] == "Edited"

    async def test_delete_moment_by_poster(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Delete me",
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.delete(f"/api/moments/{moment_id}")
        assert resp.status_code == 204

        resp2 = await admin_client.get(f"/api/moments/{moment_id}")
        assert resp2.status_code == 404

    async def test_delete_nonexistent_moment(self, admin_client):
        resp = await admin_client.delete("/api/moments/nonexistent")
        assert resp.status_code == 404

    async def test_moment_history_visible_to_member(self, admin_client, member_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Original story",
            "person_id": TYLER_ID,
        })
        moment_id = create_resp.json()["id"]

        update_resp = await admin_client.put(f"/api/moments/{moment_id}", json={
            "body": "Edited story",
        })
        assert update_resp.status_code == 200

        history_resp = await member_client.get(f"/api/moments/{moment_id}/history")
        assert history_resp.status_code == 200
        actions = [entry["action"] for entry in history_resp.json()]
        assert "create" in actions
        assert "update" in actions

    async def test_admin_can_revert_moment_revision(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Original",
        })
        moment_id = create_resp.json()["id"]

        update_resp = await admin_client.put(f"/api/moments/{moment_id}", json={
            "body": "Edited",
        })
        assert update_resp.status_code == 200

        history_resp = await admin_client.get(f"/api/moments/{moment_id}/history")
        assert history_resp.status_code == 200
        create_revision = next(entry for entry in history_resp.json() if entry["action"] == "create")

        revert_resp = await admin_client.post(
            f"/api/moments/{moment_id}/history/{create_revision['id']}/revert"
        )
        assert revert_resp.status_code == 200
        assert revert_resp.json()["moment"]["body"] == "Original"

        moment_resp = await admin_client.get(f"/api/moments/{moment_id}")
        assert moment_resp.status_code == 200
        assert moment_resp.json()["body"] == "Original"

    async def test_delete_moment_is_recoverable_via_revision(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Delete and restore",
        })
        moment_id = create_resp.json()["id"]

        delete_resp = await admin_client.delete(f"/api/moments/{moment_id}")
        assert delete_resp.status_code == 204

        missing_resp = await admin_client.get(f"/api/moments/{moment_id}")
        assert missing_resp.status_code == 404

        history_resp = await admin_client.get(f"/api/moments/{moment_id}/history")
        assert history_resp.status_code == 200
        create_revision = next(entry for entry in history_resp.json() if entry["action"] == "create")

        revert_resp = await admin_client.post(
            f"/api/moments/{moment_id}/history/{create_revision['id']}/revert"
        )
        assert revert_resp.status_code == 200
        assert revert_resp.json()["lifecycle_state"] == "active"

        restored_resp = await admin_client.get(f"/api/moments/{moment_id}")
        assert restored_resp.status_code == 200
        assert restored_resp.json()["body"] == "Delete and restore"

    async def test_moderated_moment_is_hidden_from_member_and_restorable(self, admin_client, member_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Moderate me",
            "person_id": TYLER_ID,
        })
        moment_id = create_resp.json()["id"]

        moderate_resp = await admin_client.post(
            f"/api/moments/{moment_id}/moderate",
            json={"reason": "Incorrect content"},
        )
        assert moderate_resp.status_code == 200
        assert moderate_resp.json()["lifecycle_state"] == "moderated"

        member_feed = await member_client.get("/api/moments")
        assert member_feed.status_code == 200
        member_ids = {item["id"] for item in member_feed.json()}
        assert moment_id not in member_ids

        member_detail = await member_client.get(f"/api/moments/{moment_id}")
        assert member_detail.status_code == 403

        restore_resp = await admin_client.post(f"/api/moments/{moment_id}/restore")
        assert restore_resp.status_code == 200
        assert restore_resp.json()["lifecycle_state"] == "active"

        member_feed_after = await member_client.get("/api/moments")
        assert member_feed_after.status_code == 200
        restored_ids = {item["id"] for item in member_feed_after.json()}
        assert moment_id in restored_ids

    async def test_deleted_tagged_person_is_not_rendered_in_moment_card(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Story with tagged person",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
        })
        assert create_resp.status_code == 201
        moment_id = create_resp.json()["id"]
        assert create_resp.json()["tagged_people"][0]["id"] == MEMBER_ID

        delete_person_resp = await admin_client.delete(f"/api/persons/{MEMBER_ID}")
        assert delete_person_resp.status_code == 204

        detail_resp = await admin_client.get(f"/api/moments/{moment_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["tagged_people"] == []


class TestMomentsFeed:
    """GET /api/moments — feed with filtering and pagination."""

    async def test_feed_requires_auth(self, client):
        resp = await client.get("/api/moments")
        assert resp.status_code == 401

    async def test_feed_returns_moments(self, admin_client):
        await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Feed item 1",
        })
        await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Feed item 2",
        })

        resp = await admin_client.get("/api/moments")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) >= 2

    async def test_feed_pagination_limit(self, admin_client):
        for i in range(5):
            await admin_client.post("/api/moments", json={
                "kind": "text", "body": f"Item {i}",
            })

        resp = await admin_client.get("/api/moments?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_feed_filter_by_kind(self, admin_client):
        await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Text moment",
        })
        await admin_client.post("/api/moments", json={
            "kind": "milestone", "body": "Milestone", "milestone_type": "birthday",
        })

        resp = await admin_client.get("/api/moments?kind=milestone")
        assert resp.status_code == 200
        for item in resp.json():
            assert item["kind"] == "milestone"

    async def test_feed_filter_by_person(self, admin_client):
        await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Alex's moment",
            "person_id": ADMIN_ID,
        })

        resp = await admin_client.get(f"/api/moments?person={ADMIN_ID}")
        assert resp.status_code == 200
        for item in resp.json():
            assert item["about"]["id"] == ADMIN_ID

    async def test_member_branch_filter_returns_shared_results(self, admin_client, member_client):
        included = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Martin branch update",
            "person_id": TYLER_ID,
        })
        excluded = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Other branch update",
            "person_id": "yuliya-00-0000-0000-000000000003",
        })

        resp = await member_client.get("/api/moments?branch=martin")
        assert resp.status_code == 200
        ids = {item["id"] for item in resp.json()}
        assert included.json()["id"] in ids
        assert excluded.json()["id"] not in ids

    async def test_feed_filter_by_tagged_person(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Tagged family story",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
        })
        moment_id = create_resp.json()["id"]

        resp = await admin_client.get(f"/api/moments?person={MEMBER_ID}")
        assert resp.status_code == 200
        assert any(item["id"] == moment_id for item in resp.json())

    async def test_feed_filter_by_tagged_person_finds_older_matching_moment(self, admin_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "story",
            "body": "Older tagged story",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
        })
        moment_id = create_resp.json()["id"]

        for i in range(20):
            await admin_client.post("/api/moments", json={
                "kind": "text",
                "body": f"Recent unrelated moment {i}",
                "person_id": TYLER_ID,
            })

        resp = await admin_client.get(f"/api/moments?person={MEMBER_ID}&limit=20")
        assert resp.status_code == 200
        assert any(item["id"] == moment_id for item in resp.json())

    async def test_partial_person_timeline_matches_api_order(self, admin_client):
        first = await admin_client.post("/api/moments", json={
            "kind": "story",
            "title": "Shared trip",
            "body": "A trip that included Jane",
            "person_id": TYLER_ID,
            "tagged_person_ids": [MEMBER_ID],
            "occurred_at": "2099-05-01T12:00:00Z",
        })
        second = await admin_client.post("/api/moments", json={
            "kind": "story",
            "title": "Jane's birthday",
            "body": "Birthday note",
            "person_id": MEMBER_ID,
            "occurred_at": "2100-05-01T12:00:00Z",
        })

        api_resp = await admin_client.get(f"/api/moments?person={MEMBER_ID}&limit=20")
        assert api_resp.status_code == 200
        api_ids = [item["id"] for item in api_resp.json()]
        assert api_ids[:2] == [second.json()["id"], first.json()["id"]]

        partial_resp = await admin_client.get(f"/partials/moments?person={MEMBER_ID}&limit=20")
        assert partial_resp.status_code == 200
        partial_ids = re.findall(r'<div class="moment" id="moment-([^"]+)"', partial_resp.text)
        assert partial_ids[:2] == api_ids[:2]
        assert "Jane&#39;s birthday" in partial_resp.text
        assert "Shared trip" in partial_resp.text

    async def test_home_feed_matches_api_order_for_same_visible_moments(self, admin_client):
        latest = await admin_client.post("/api/moments", json={
            "kind": "story",
            "title": "Latest family story",
            "body": "Newest moment in the feed",
            "occurred_at": "2100-01-03T12:00:00Z",
        })
        earlier = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Earlier family note",
            "occurred_at": "2100-01-02T12:00:00Z",
        })

        api_resp = await admin_client.get("/api/moments?limit=5")
        assert api_resp.status_code == 200
        api_ids = [item["id"] for item in api_resp.json()]

        home_resp = await admin_client.get("/moments")
        assert home_resp.status_code == 200
        home_ids = re.findall(r'<div class="moment" id="moment-([^"]+)"', home_resp.text)
        assert home_ids[:2] == api_ids[:2]
        assert latest.json()["id"] in home_ids
        assert earlier.json()["id"] in home_ids


class TestMomentsPermissions:
    """Permission checks for moment operations."""

    async def test_member_cannot_delete_others_moment(self, admin_client, member_client):
        # Admin creates a moment
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Admin's moment",
        })
        moment_id = create_resp.json()["id"]

        # Member tries to delete it
        resp = await member_client.delete(f"/api/moments/{moment_id}")
        assert resp.status_code == 403

    async def test_member_cannot_edit_others_moment(self, admin_client, member_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Admin's moment",
        })
        moment_id = create_resp.json()["id"]

        resp = await member_client.put(f"/api/moments/{moment_id}", json={
            "body": "Hacked",
        })
        assert resp.status_code == 403

    async def test_hidden_moment_not_visible_to_member(self, admin_client, member_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text", "body": "Secret",
            "visibility": "hidden",
        })
        moment_id = create_resp.json()["id"]

        resp = await member_client.get(f"/api/moments/{moment_id}")
        assert resp.status_code == 403

    async def test_admin_only_moment_not_visible_to_member(self, admin_client, member_client):
        create_resp = await admin_client.post("/api/moments", json={
            "kind": "text",
            "body": "Admins only",
            "visibility": "admins",
        })
        moment_id = create_resp.json()["id"]

        detail_resp = await member_client.get(f"/api/moments/{moment_id}")
        feed_resp = await member_client.get("/api/moments")
        assert detail_resp.status_code == 403
        assert all(item["id"] != moment_id for item in feed_resp.json())
