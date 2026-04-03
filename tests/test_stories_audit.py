"""
Auditor adversarial probes for S42 — Person Stories.

These tests are NOT part of the normal suite. They probe failure paths,
access-control edges, and reward hacks the builder tests don't cover.
"""

import pytest
from httpx import AsyncClient


async def _create_person(client: AsyncClient, first: str = "Audit", last: str = "Subject") -> dict:
    resp = await client.post("/api/persons", json={"first_name": first, "last_name": last})
    assert resp.status_code == 201
    return resp.json()


# ── Probe A: unauthenticated access is rejected ───────────────────────

@pytest.mark.asyncio
async def test_probe_unauthenticated_cannot_list_stories(client: AsyncClient):
    """Unauthenticated client gets 401 / redirect on story list."""
    # Create a person first (using admin, then probe with bare client)
    # bare client has no session cookie
    resp = await client.get("/api/wiki/any-slug/stories")
    # Should be 401 (or redirect to login — either is acceptable)
    assert resp.status_code in (401, 302, 403)


@pytest.mark.asyncio
async def test_probe_unauthenticated_cannot_create_story(client: AsyncClient):
    """Unauthenticated POST to create story is rejected."""
    resp = await client.post(
        "/api/wiki/any-slug/stories",
        data={"title": "Injection", "body": "<p>Bad actor.</p>"},
    )
    assert resp.status_code in (401, 302, 403)


# ── Probe B: story isolation — cannot touch another person's story ────

@pytest.mark.asyncio
async def test_probe_delete_story_on_wrong_person_slug(
    admin_client: AsyncClient,
):
    """DELETE /api/wiki/{wrong-slug}/stories/{story_id} returns 404 even if story exists."""
    person_a = await _create_person(admin_client, "PersonA", "Alpha")
    person_b = await _create_person(admin_client, "PersonB", "Beta")

    # Create story on person_a
    await admin_client.post(
        f"/api/wiki/{person_a['slug']}/stories",
        data={"title": "A's Story", "body": "<p>Belongs to A.</p>"},
    )
    stories = (await admin_client.get(f"/api/wiki/{person_a['slug']}/stories")).json()
    story_id = stories[0]["id"]

    # Try to delete it via person_b's slug — should 404 (story not on person_b)
    resp = await admin_client.delete(f"/api/wiki/{person_b['slug']}/stories/{story_id}")
    assert resp.status_code == 404

    # Story still exists
    remaining = (await admin_client.get(f"/api/wiki/{person_a['slug']}/stories")).json()
    assert len(remaining) == 1


@pytest.mark.asyncio
async def test_probe_edit_story_on_wrong_person_slug(admin_client: AsyncClient):
    """PUT on story via wrong slug returns 404."""
    person_a = await _create_person(admin_client, "PersonC", "Gamma")
    person_b = await _create_person(admin_client, "PersonD", "Delta")

    await admin_client.post(
        f"/api/wiki/{person_a['slug']}/stories",
        data={"title": "Original", "body": "<p>A's story.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person_a['slug']}/stories")).json()[0]["id"]

    resp = await admin_client.put(
        f"/api/wiki/{person_b['slug']}/stories/{story_id}",
        data={"title": "Hijacked", "body": "<p>Wrong person.</p>"},
    )
    assert resp.status_code == 404

    # Original untouched
    stories = (await admin_client.get(f"/api/wiki/{person_a['slug']}/stories")).json()
    assert stories[0]["title"] == "Original"


# ── Probe C: XSS — onerror attribute variant ──────────────────────────

@pytest.mark.asyncio
async def test_probe_xss_onerror_stripped(admin_client: AsyncClient):
    """onerror= event handlers in body are stripped by sanitization."""
    person = await _create_person(admin_client, "XSS", "Probe")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "XSS onerror", "body": '<img src="x" onerror="alert(1)">Safe text'},
    )
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert "onerror" not in stories[0]["body"]


@pytest.mark.asyncio
async def test_probe_xss_javascript_href_stripped(admin_client: AsyncClient):
    """javascript: href in anchor is stripped."""
    person = await _create_person(admin_client, "XSS2", "Probe")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "XSS href", "body": '<a href="javascript:alert(1)">click</a>'},
    )
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert "javascript:" not in stories[0]["body"]


# ── Probe D: root person stories — confirm no special block ──────────

@pytest.mark.asyncio
async def test_probe_stories_allowed_on_root_person(admin_client: AsyncClient):
    """Root person can have stories created (no block at the story level)."""
    # Root person is 'root-0000-0000-0000-000000000001'
    # First get the root person's slug
    persons_resp = await admin_client.get("/api/persons")
    assert persons_resp.status_code == 200
    persons = persons_resp.json()
    root = next((p for p in persons if p.get("is_root")), None)
    if root is None or not root.get("slug"):
        pytest.skip("Root person has no slug — cannot test")

    resp = await admin_client.post(
        f"/api/wiki/{root['slug']}/stories",
        data={"title": "Family History", "body": "<p>The origin story.</p>"},
    )
    # Stories are about persons, not by them. Root person is a valid target.
    assert resp.status_code == 201


# ── Probe E: audit log is actually written ────────────────────────────

@pytest.mark.asyncio
async def test_probe_audit_log_written_on_create(
    admin_client: AsyncClient,
    seeded_db,
):
    """AuditLog entry is created when a story is created."""
    from sqlalchemy import select
    from app.models.audit import AuditLog

    person = await _create_person(admin_client, "Audit", "LogTest")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Logged Story", "body": "<p>Check the audit log.</p>"},
    )

    result = await seeded_db.execute(
        select(AuditLog).where(AuditLog.entity_type == "story", AuditLog.action == "create")
    )
    entries = result.scalars().all()
    assert len(entries) >= 1
    assert entries[-1].actor_id is not None


@pytest.mark.asyncio
async def test_probe_audit_log_written_on_delete(
    admin_client: AsyncClient,
    seeded_db,
):
    """AuditLog entry is created when a story is deleted."""
    from sqlalchemy import select
    from app.models.audit import AuditLog

    person = await _create_person(admin_client, "Audit", "DeleteTest")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "To Log Delete", "body": "<p>Watch me vanish.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]
    await admin_client.delete(f"/api/wiki/{person['slug']}/stories/{story_id}")

    result = await seeded_db.execute(
        select(AuditLog).where(AuditLog.entity_type == "story", AuditLog.action == "delete")
    )
    entries = result.scalars().all()
    assert len(entries) >= 1


# ── Probe F: N+1 guard — list returns author names without query-per-row

@pytest.mark.asyncio
async def test_probe_list_returns_author_name_for_multiple_stories(admin_client: AsyncClient):
    """List of multiple stories all have author_name populated (no silent None)."""
    person = await _create_person(admin_client, "Multi", "Author")
    for i in range(3):
        await admin_client.post(
            f"/api/wiki/{person['slug']}/stories",
            data={"title": f"Story {i}", "body": f"<p>Entry {i}</p>"},
        )
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert len(stories) == 3
    for s in stories:
        assert s["author_name"] is not None
        assert len(s["author_name"]) > 0


# ── Probe G: confirm-delete endpoint enforces auth ────────────────────

@pytest.mark.asyncio
async def test_probe_confirm_delete_blocked_for_non_author(
    admin_client: AsyncClient,
    member_client: AsyncClient,
):
    """Non-author non-admin gets 403 on the confirm-delete endpoint itself."""
    person = await _create_person(admin_client, "Confirm", "Delete")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Admin's Story", "body": "<p>Mine.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]

    resp = await member_client.get(
        f"/api/wiki/{person['slug']}/stories/{story_id}/confirm-delete"
    )
    assert resp.status_code == 403
