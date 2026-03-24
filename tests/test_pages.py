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


@pytest.mark.asyncio
async def test_home_page_renders_accessible_compose_and_live_regions(admin_client: AsyncClient):
    resp = await admin_client.get("/")

    assert resp.status_code == 200
    assert 'id="compose-modal"' in resp.text
    assert 'role="dialog"' in resp.text
    assert 'aria-live="polite"' in resp.text
    assert 'id="moments-feed"' in resp.text


@pytest.mark.asyncio
async def test_people_page_renders_search_label_and_live_results(member_client: AsyncClient):
    resp = await member_client.get("/people")

    assert resp.status_code == 200
    assert 'for="people-search-input"' in resp.text
    assert 'id="people-results" aria-live="polite" aria-busy="false"' in resp.text


@pytest.mark.asyncio
async def test_tree_page_renders_sidebar_dialog_and_labeled_controls(member_client: AsyncClient):
    resp = await member_client.get("/tree")

    assert resp.status_code == 200
    assert 'id="person-sidebar"' in resp.text
    assert 'role="dialog"' in resp.text
    assert 'aria-label="' in resp.text
    assert 'id="tree-status" role="status" aria-live="polite"' in resp.text


@pytest.mark.asyncio
async def test_map_page_renders_accessible_svg_and_reset_filter(member_client: AsyncClient):
    resp = await member_client.get("/map")

    assert resp.status_code == 200
    assert 'id="map-svg"' in resp.text
    assert 'role="img"' in resp.text
    assert 'id="reset-map-filters"' in resp.text


@pytest.mark.asyncio
async def test_person_edit_page_renders_labeled_fields_and_inline_error_container(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/edit")

    assert resp.status_code == 200
    assert 'id="person-edit-error"' in resp.text
    assert 'for="edit-first-name"' in resp.text
    assert 'id="edit-first-name"' in resp.text


def test_pages_router_exports_routes():
    assert pages_routes.router.routes


def test_pages_helper_functions_cover_locale_and_flags():
    scope = {"type": "http", "headers": [], "method": "GET", "path": "/"}
    request = Request(scope)
    request._cookies = {"locale": "es"}

    assert pages_routes._get_locale(request) == "es"
    assert pages_routes._country_flag("US") == "🇺🇸"
