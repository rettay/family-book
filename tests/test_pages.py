import pytest
from fastapi import Request
from httpx import AsyncClient

import app.routes.pages as pages_routes

TYLER_ID = "tyler-000-0000-0000-000000000002"


@pytest.mark.asyncio
async def test_new_person_page_renders_for_authenticated_member(member_client: AsyncClient):
    resp = await member_client.get("/people/new")

    assert resp.status_code == 200
    assert 'id="create-person-form"' in resp.text
    assert 'id="person-first-name"' in resp.text


@pytest.mark.asyncio
async def test_admin_dashboard_renders_release_confidence_sections(admin_client: AsyncClient):
    resp = await admin_client.get("/admin")

    assert resp.status_code == 200
    assert 'id="backup-status"' in resp.text
    assert 'id="theme-settings-form"' in resp.text
    assert 'id="admin-accounts-card"' in resp.text
    assert 'class="flex gap-8 admin-action-row admin-action-row--wrap"' in resp.text


@pytest.mark.asyncio
async def test_moments_page_renders_accessible_compose_and_live_regions(admin_client: AsyncClient):
    resp = await admin_client.get("/moments")

    assert resp.status_code == 200
    assert 'id="compose-modal"' in resp.text
    assert 'role="dialog"' in resp.text
    assert 'aria-live="polite"' in resp.text
    assert 'id="moments-feed"' in resp.text
    assert 'class="form-select feed-filter-select"' in resp.text
    assert "const url = kind ? '/moments?kind=' + kind : '/moments';" in resp.text


@pytest.mark.asyncio
async def test_authenticated_root_redirects_to_tree(member_client: AsyncClient):
    resp = await member_client.get("/")

    assert resp.status_code == 302
    assert resp.headers["location"] == "/tree"


@pytest.mark.asyncio
async def test_login_page_preserves_safe_return_to_after_auth(client: AsyncClient):
    resp = await client.get("/login?return_to=/moments")

    assert resp.status_code == 200
    assert "const params = new URLSearchParams(window.location.search);" in resp.text
    assert "const safeReturnTo = returnTo && returnTo.startsWith('/') && !returnTo.startsWith('//')" in resp.text
    assert "window.location.href = safeReturnTo || '/tree';" in resp.text


@pytest.mark.asyncio
async def test_people_page_renders_search_label_and_live_results(member_client: AsyncClient):
    resp = await member_client.get("/people")

    assert resp.status_code == 200
    assert 'for="people-search-input"' in resp.text
    assert 'id="people-results" aria-live="polite" aria-busy="false"' in resp.text
    assert 'class="page-header page-header--split mb-16"' in resp.text


@pytest.mark.asyncio
async def test_tree_page_renders_sidebar_dialog_and_labeled_controls(member_client: AsyncClient):
    resp = await member_client.get("/tree")

    assert resp.status_code == 200
    assert 'id="person-sidebar"' in resp.text
    assert 'role="dialog"' in resp.text
    assert 'aria-label="' in resp.text
    assert 'id="tree-status" role="status" aria-live="polite"' in resp.text
    assert 'data-saved-message="' in resp.text
    assert 'data-tree-story-created="' in resp.text


@pytest.mark.asyncio
async def test_map_page_renders_accessible_svg_and_reset_filter(member_client: AsyncClient):
    resp = await member_client.get("/map")

    assert resp.status_code == 200
    assert 'id="map-svg"' in resp.text
    assert 'role="img"' in resp.text
    assert 'id="reset-map-filters"' in resp.text
    assert 'data-map-provider="svg"' in resp.text


@pytest.mark.asyncio
async def test_map_page_exposes_google_maps_provider_when_configured(
    member_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "maps-key")
    monkeypatch.setenv("GOOGLE_MAPS_MAP_ID", "map-id-1")

    resp = await member_client.get("/map")

    assert resp.status_code == 200
    assert 'data-map-provider="google"' in resp.text
    assert 'data-google-maps-api-key="maps-key"' in resp.text
    assert 'data-google-maps-map-id="map-id-1"' in resp.text
    assert 'id="google-map"' in resp.text


@pytest.mark.asyncio
async def test_admin_page_reports_resend_delivery_mode(
    admin_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("RESEND_API_KEY", "resend-key")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "Family Book <invites@example.com>")

    resp = await admin_client.get("/admin")

    assert resp.status_code == 200
    assert 'Invite delivery' in resp.text
    assert 'Resend is configured for direct email delivery.' in resp.text


@pytest.mark.asyncio
async def test_person_edit_page_renders_labeled_fields_and_inline_error_container(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/edit")

    assert resp.status_code == 200
    assert 'id="person-edit-error"' in resp.text
    assert 'for="edit-first-name"' in resp.text
    assert 'id="edit-first-name"' in resp.text
    assert 'class="form-section-title"' in resp.text


@pytest.mark.asyncio
async def test_tree_person_card_renders_workspace_tabs_and_tree_native_sections(member_client: AsyncClient):
    resp = await member_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'data-tree-sidebar-tab="overview"' in resp.text
    assert 'data-tree-sidebar-tab="moments"' in resp.text
    assert 'id="tree-sidebar-moments"' in resp.text
    assert 'id="tree-sidebar-media"' in resp.text
    assert 'id="tree-sidebar-people-options"' in resp.text
    assert 'class="tree-sidebar-inline-actions"' in resp.text
    assert 'class="tree-sidebar-pill-row"' in resp.text
    assert 'data-tree-moment-filter="shared"' in resp.text


@pytest.mark.asyncio
async def test_tree_person_card_uses_search_picker_not_raw_relationship_selects(member_client: AsyncClient):
    resp = await member_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'data-tree-picker' in resp.text
    assert 'placeholder="Search family members"' in resp.text
    assert 'select class="form-select" name="related_person_id"' not in resp.text


@pytest.mark.asyncio
async def test_admin_tree_person_card_renders_rich_storytelling_controls(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'name="authoring_scope"' in resp.text
    assert 'data-tree-story-files' in resp.text
    assert 'data-tree-multi-picker' in resp.text
    assert 'name="tagged_person_ids"' in resp.text
    assert 'multiple' in resp.text


@pytest.mark.asyncio
async def test_admin_tree_person_card_renders_relationship_cards_with_maintenance_actions(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'class="tree-related-card"' in resp.text
    assert "openTreeSidebarPerson('" in resp.text
    assert "removeTreeRelationship('" in resp.text


@pytest.mark.asyncio
async def test_settings_page_renders_wrapped_language_picker_and_page_header(member_client: AsyncClient):
    resp = await member_client.get("/settings")

    assert resp.status_code == 200
    assert 'class="lang-picker lang-picker--wrap"' in resp.text
    assert 'class="page-header__subtitle"' in resp.text


def test_pages_router_exports_routes():
    assert pages_routes.router.routes


def test_pages_helper_functions_cover_locale_and_flags():
    scope = {"type": "http", "headers": [], "method": "GET", "path": "/"}
    request = Request(scope)
    request._cookies = {"locale": "es"}

    assert pages_routes._get_locale(request) == "es"
    assert pages_routes._country_flag("US") == "🇺🇸"
