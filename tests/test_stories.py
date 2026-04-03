"""Tests for FB-088/FB-089/FB-090: Person Stories feature."""

import pytest
from httpx import AsyncClient


TYLER_ID = "tyler-000-0000-0000-000000000002"
MEMBER_ID = "member-00-0000-0000-000000000005"


async def _create_person(client: AsyncClient, first: str = "Story", last: str = "Subject") -> dict:
    resp = await client.post("/api/persons", json={"first_name": first, "last_name": last})
    assert resp.status_code == 201
    return resp.json()


# ── List (empty) ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_story_list_empty(admin_client: AsyncClient):
    """GET stories for a person with no stories returns empty list."""
    person = await _create_person(admin_client)
    resp = await admin_client.get(f"/api/wiki/{person['slug']}/stories")
    assert resp.status_code == 200
    assert resp.json() == []


# ── Create ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_story_create_admin(admin_client: AsyncClient):
    """Admin can create a story."""
    person = await _create_person(admin_client)
    resp = await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "A Great Tale", "body": "<p>Once upon a time...</p>"},
    )
    assert resp.status_code == 201
    assert "A Great Tale" in resp.text


@pytest.mark.asyncio
async def test_story_create_member(member_client: AsyncClient, admin_client: AsyncClient):
    """Any authenticated member can create a story (not admin-gated)."""
    person = await _create_person(admin_client)
    resp = await member_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Member Story", "body": "<p>From a member.</p>"},
    )
    assert resp.status_code == 201
    assert "Member Story" in resp.text


@pytest.mark.asyncio
async def test_story_create_requires_title(admin_client: AsyncClient):
    """Creating a story without a title returns 422."""
    person = await _create_person(admin_client)
    resp = await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "", "body": "<p>No title.</p>"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_story_create_sanitizes_body(admin_client: AsyncClient):
    """Script tags in body are stripped on create."""
    person = await _create_person(admin_client)
    resp = await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "XSS Test", "body": '<p>Safe</p><script>alert("xss")</script>'},
    )
    assert resp.status_code == 201
    # Fetch via list API to confirm sanitization
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert len(stories) == 1
    assert "<script>" not in stories[0]["body"]
    assert "Safe" in stories[0]["body"]


# ── List (non-empty) ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_story_list_returns_author_name(admin_client: AsyncClient):
    """List endpoint includes author_name resolved from Person."""
    person = await _create_person(admin_client)
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "By Tyler", "body": "<p>Hello.</p>"},
    )
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert len(stories) == 1
    assert stories[0]["author_name"] == "Tyler Martin"
    assert stories[0]["title"] == "By Tyler"


@pytest.mark.asyncio
async def test_story_list_newest_first(admin_client: AsyncClient):
    """Stories are ordered newest first."""
    person = await _create_person(admin_client)
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "First Story", "body": "<p>A</p>"},
    )
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Second Story", "body": "<p>B</p>"},
    )
    stories = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert stories[0]["title"] == "Second Story"
    assert stories[1]["title"] == "First Story"


# ── Edit (wiki-style) ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_story_edit_by_non_author_member(
    admin_client: AsyncClient, member_client: AsyncClient
):
    """Any member can edit any story (wiki-style — not author-gated)."""
    person = await _create_person(admin_client)
    # Admin creates story
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Admin's Story", "body": "<p>Original.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]

    # Member edits it
    resp = await member_client.put(
        f"/api/wiki/{person['slug']}/stories/{story_id}",
        data={"title": "Admin's Story (edited)", "body": "<p>Updated by member.</p>"},
    )
    assert resp.status_code == 200
    assert "edited" in resp.text


# ── Delete permissions ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_story_delete_by_admin(admin_client: AsyncClient):
    """Admin can delete any story."""
    person = await _create_person(admin_client)
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "To Delete", "body": "<p>Gone.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]
    resp = await admin_client.delete(f"/api/wiki/{person['slug']}/stories/{story_id}")
    assert resp.status_code == 204
    remaining = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert remaining == []


@pytest.mark.asyncio
async def test_story_delete_by_author(member_client: AsyncClient, admin_client: AsyncClient):
    """Original author can delete their own story."""
    person = await _create_person(admin_client)
    # Member creates story
    await member_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Member's Story", "body": "<p>Mine.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]
    resp = await member_client.delete(f"/api/wiki/{person['slug']}/stories/{story_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_story_delete_blocked_for_non_author_non_admin(
    admin_client: AsyncClient, member_client: AsyncClient
):
    """Non-author non-admin gets 403 on delete."""
    person = await _create_person(admin_client)
    # Admin creates story — member did not author it
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "Admin's Story", "body": "<p>Not yours.</p>"},
    )
    story_id = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()[0]["id"]
    resp = await member_client.delete(f"/api/wiki/{person['slug']}/stories/{story_id}")
    assert resp.status_code == 403
    # Story still exists
    remaining = (await admin_client.get(f"/api/wiki/{person['slug']}/stories")).json()
    assert len(remaining) == 1


# ── Wiki page rendering ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_wiki_page_renders_stories_section(admin_client: AsyncClient):
    """Wiki person page includes the #stories anchor."""
    person = await _create_person(admin_client)
    resp = await admin_client.get(f"/wiki/{person['slug']}")
    assert resp.status_code == 200
    assert 'id="stories"' in resp.text


@pytest.mark.asyncio
async def test_wiki_page_shows_story_content(admin_client: AsyncClient):
    """Stories are rendered on the wiki person page."""
    person = await _create_person(admin_client)
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "The Fishing Trip", "body": "<p>Caught a big one.</p>"},
    )
    resp = await admin_client.get(f"/wiki/{person['slug']}")
    assert resp.status_code == 200
    assert "The Fishing Trip" in resp.text
    assert "Caught a big one" in resp.text


@pytest.mark.asyncio
async def test_wiki_page_empty_state_when_no_stories(admin_client: AsyncClient):
    """Empty state is shown when a person has no stories."""
    person = await _create_person(admin_client)
    resp = await admin_client.get(f"/wiki/{person['slug']}")
    assert resp.status_code == 200
    assert 'data-wiki-stories-empty="true"' in resp.text


# ── Sidebar story count ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sidebar_story_count_attribute(admin_client: AsyncClient):
    """Person card partial includes data-tree-sidebar-story-count attribute."""
    resp = await admin_client.get("/people/tyler-000-0000-0000-000000000002/card")
    assert resp.status_code == 200
    assert "data-tree-sidebar-story-count" in resp.text


@pytest.mark.asyncio
async def test_sidebar_story_count_zero_hides_link(admin_client: AsyncClient):
    """When story count is 0, the stories link is not shown in sidebar."""
    person = await _create_person(admin_client, "Zero", "Stories")
    # Create person then get their card — no stories yet
    resp = await admin_client.get(f"/people/{person['id']}/card")
    assert resp.status_code == 200
    # The story metric link should not appear
    assert "tree-sidebar-metric--link" not in resp.text or f"/wiki/{person['slug']}#stories" not in resp.text


@pytest.mark.asyncio
async def test_sidebar_story_count_shown_when_stories_exist(admin_client: AsyncClient):
    """Sidebar shows story count link when stories exist for the person."""
    person = await _create_person(admin_client, "Has", "Stories")
    await admin_client.post(
        f"/api/wiki/{person['slug']}/stories",
        data={"title": "A Story", "body": "<p>Content.</p>"},
    )
    resp = await admin_client.get(f"/people/{person['id']}/card")
    assert resp.status_code == 200
    assert f"/wiki/{person['slug']}#stories" in resp.text
