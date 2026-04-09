import pytest
from pathlib import Path
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.routes.pages as pages_routes
from app.models.hosted_archive import HostedArchive
from app.models.media import MediaInboxItem

TYLER_ID = "tyler-000-0000-0000-000000000002"
ROOT_DIR = Path(__file__).resolve().parents[1]


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
    assert 'id="admin-download-gedcom-button"' in resp.text
    assert 'id="admin-download-archive-button"' in resp.text
    assert 'id="admin-open-trust-center-button"' in resp.text
    assert resp.text.index('id="admin-accounts-card"') < resp.text.index("Accounts &amp; Invites")
    assert resp.text.index('id="admin-accounts-card"') > resp.text.index("Theme &amp; Branding")
    assert 'class="flex gap-8 admin-action-row admin-action-row--wrap"' in resp.text


@pytest.mark.asyncio
async def test_admin_dashboard_renders_hosted_archive_section_when_enabled(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    monkeypatch.setenv("HOSTED_ARCHIVE_ENABLED", "true")
    seeded_db.add(
        HostedArchive(
            archive_key="archive-1",
            archive_name="Hosted Archive",
            owner_email="owner@example.com",
            base_url="https://family.example.com",
            hosting_mode="managed_single_tenant",
            plan_code="founding",
            lifecycle_state="active",
            billing_provider="stripe",
            billing_status="active",
        )
    )
    await seeded_db.commit()

    resp = await admin_client.get("/admin")

    assert resp.status_code == 200
    assert 'id="admin-hosted-archive-card"' in resp.text
    assert "Hosted Archive" in resp.text
    assert "Start Hosted Checkout" in resp.text


@pytest.mark.asyncio
async def test_authenticated_root_redirects_to_tree(member_client: AsyncClient):
    resp = await member_client.get("/")

    assert resp.status_code == 302
    assert resp.headers["location"] == "/tree"


@pytest.mark.asyncio
async def test_hosted_root_redirects_admin_to_onboarding(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    monkeypatch.setenv("HOSTED_ARCHIVE_ENABLED", "true")
    seeded_db.add(
        HostedArchive(
            archive_key="archive-1",
            archive_name="Hosted Archive",
            owner_email="owner@example.com",
            base_url="https://family.example.com",
            hosting_mode="managed_single_tenant",
            plan_code="founding",
            lifecycle_state="active",
            billing_provider="stripe",
            billing_status="active",
        )
    )
    await seeded_db.commit()

    resp = await admin_client.get("/", follow_redirects=False)

    assert resp.status_code == 302
    assert resp.headers["location"] == "/onboarding"


@pytest.mark.asyncio
async def test_trust_page_renders_privacy_and_export_commitments(client: AsyncClient):
    resp = await client.get("/trust")

    assert resp.status_code == 200
    assert "Trust Center" in resp.text
    assert "family-graph distance" in resp.text
    assert "download a GEDCOM export" in resp.text


@pytest.mark.asyncio
async def test_login_page_preserves_safe_return_to_after_auth(client: AsyncClient):
    resp = await client.get("/login?return_to=/tree")

    assert resp.status_code == 200
    assert "const params = new URLSearchParams(window.location.search);" in resp.text
    assert "const safeReturnTo = returnTo && returnTo.startsWith('/') && !returnTo.startsWith('//')" in resp.text
    assert "window.location.href = safeReturnTo || '/tree';" in resp.text


@pytest.mark.asyncio
async def test_settings_page_renders_hosted_subscription_when_enabled(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    monkeypatch.setenv("HOSTED_ARCHIVE_ENABLED", "true")
    seeded_db.add(
        HostedArchive(
            archive_key="archive-1",
            archive_name="Hosted Archive",
            owner_email="owner@example.com",
            base_url="https://family.example.com",
            hosting_mode="managed_single_tenant",
            plan_code="founding",
            lifecycle_state="active",
            billing_provider="stripe",
            billing_status="active",
        )
    )
    await seeded_db.commit()

    resp = await admin_client.get("/settings")

    assert resp.status_code == 200
    assert 'id="hosted-subscription-section"' in resp.text
    assert "Hosted Subscription" in resp.text
    assert "Open Billing Portal" in resp.text


@pytest.mark.asyncio
async def test_tree_page_renders_sidebar_dialog_and_labeled_controls(member_client: AsyncClient):
    resp = await member_client.get("/tree")

    assert resp.status_code == 200
    assert 'id="person-sidebar"' in resp.text
    assert 'id="sidebar-collapse-btn"' in resp.text
    assert 'role="dialog"' in resp.text
    assert 'aria-label="' in resp.text
    assert 'id="tree-status" role="status" aria-live="polite"' in resp.text
    assert 'data-saved-message="' in resp.text
    assert 'data-tree-graph-prompt-link="' in resp.text
    assert 'data-tree-graph-confirm-replace="' in resp.text


def test_tree_sidebar_floating_collapse_docks_instead_of_closing():
    tree_js = (ROOT_DIR / "app/static/js/tree.js").read_text()
    collapse_block = tree_js[
        tree_js.index("window.collapseSidebar = function()"):
        tree_js.index("window.expandSidebar = function()")
    ]
    popout_block = tree_js[
        tree_js.index("window.popOutSidebar = function()"):
        tree_js.index("window.dockSidebar = function()")
    ]
    dock_block = tree_js[
        tree_js.index("window.dockSidebar = function()"):
        tree_js.index("function _initSidebarDrag")
    ]

    assert "classList.contains('person-sidebar--floating')" in collapse_block
    assert "window.dockSidebar();" in collapse_block
    assert "return;" in collapse_block
    assert "collapseBtn.hidden = true" in popout_block
    assert "collapseBtn.hidden = false" in dock_block


@pytest.mark.asyncio
async def test_map_page_renders_accessible_svg_and_reset_filter(
    member_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "PENDING_SETUP")
    monkeypatch.setenv("GOOGLE_MAPS_BROWSER_API_KEY", "PENDING_SETUP")
    monkeypatch.setenv("GOOGLE_MAPS_SERVER_API_KEY", "PENDING_SETUP")
    resp = await member_client.get("/map")

    assert resp.status_code == 200
    assert 'id="map-svg"' in resp.text
    assert 'role="img"' in resp.text
    assert 'id="reset-map-filters"' in resp.text
    assert 'id="map-filter-relationship-scope"' in resp.text
    assert 'data-map-provider="svg"' in resp.text


@pytest.mark.asyncio
async def test_map_page_exposes_google_maps_provider_when_configured(
    member_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("GOOGLE_MAPS_BROWSER_API_KEY", "maps-browser-key")
    monkeypatch.setenv("GOOGLE_MAPS_MAP_ID", "map-id-1")

    resp = await member_client.get("/map")

    assert resp.status_code == 200
    assert 'data-map-provider="google"' in resp.text
    assert 'data-google-maps-api-key="maps-browser-key"' in resp.text
    assert 'data-google-maps-map-id="map-id-1"' in resp.text
    assert 'id="google-map"' in resp.text


@pytest.mark.asyncio
async def test_gallery_page_renders_filters_and_nav_link(member_client: AsyncClient):
    resp = await member_client.get("/gallery")

    assert resp.status_code == 200
    assert 'action="/gallery"' in resp.text
    assert 'name="search"' in resp.text
    assert 'name="source"' in resp.text
    assert 'name="album_id"' in resp.text
    assert 'name="media_type"' in resp.text
    assert 'name="person_id"' in resp.text
    assert 'name="uploader_id"' in resp.text
    assert 'class="nav__link nav__link--active"' in resp.text


@pytest.mark.asyncio
async def test_prompts_page_renders_digest_and_incoming_sections(member_client: AsyncClient):
    resp = await member_client.get("/prompts")

    assert resp.status_code == 200
    assert 'id="prompts-page"' in resp.text
    assert 'id="incoming-prompts-section"' in resp.text
    assert 'id="digest-preview-section"' in resp.text


@pytest.mark.asyncio
async def test_books_page_renders_export_builder_for_admin(admin_client: AsyncClient):
    resp = await admin_client.get("/books")

    assert resp.status_code == 200
    assert 'id="book-export-page"' in resp.text
    assert 'id="book-project-create-section"' in resp.text


@pytest.mark.asyncio
async def test_settings_page_renders_engagement_controls(member_client: AsyncClient):
    resp = await member_client.get("/settings")

    assert resp.status_code == 200
    assert 'id="engagement-section"' in resp.text
    assert 'action="/settings/digest-preferences"' in resp.text
    assert 'href="/prompts"' in resp.text
    assert 'href="/books"' in resp.text


@pytest.mark.asyncio
async def test_media_inbox_page_renders_empty_state(member_client: AsyncClient):
    resp = await member_client.get("/media/inbox")

    assert resp.status_code == 200
    assert 'id="media-inbox-page"' in resp.text
    assert "No shared media is waiting for review." in resp.text


@pytest.mark.asyncio
async def test_media_inbox_page_only_lists_attachable_people(
    member_client: AsyncClient,
    seeded_db: AsyncSession,
):
    seeded_db.add(
        MediaInboxItem(
            file_path="inbox/test.jpg",
            original_filename="test.jpg",
            mime_type="image/jpeg",
            media_type="image",
            status="pending",
            uploaded_by="member-00-0000-0000-000000000005",
        )
    )
    await seeded_db.commit()

    resp = await member_client.get("/media/inbox")

    assert resp.status_code == 200
    assert 'value="member-00-0000-0000-000000000005"' in resp.text
    assert 'value="tyler-000-0000-0000-000000000002"' not in resp.text
    assert 'value="grndpa-00-0000-0000-000000000004"' not in resp.text


@pytest.mark.asyncio
async def test_admin_page_reports_smtp_delivery_mode(
    admin_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "invites@example.com")
    monkeypatch.setenv("SMTP_PASS", "smtp-secret")
    monkeypatch.setenv("SMTP_FROM", "Family Book <invites@example.com>")

    resp = await admin_client.get("/admin")

    assert resp.status_code == 200
    assert 'Invite delivery' in resp.text
    assert 'SMTP email delivery is configured.' in resp.text


@pytest.mark.asyncio
async def test_login_page_prioritizes_email_magic_link(client: AsyncClient):
    resp = await client.get("/login?return_to=/tree")

    assert resp.status_code == 200
    assert 'id="magic-link-form"' in resp.text
    assert 'Email me a sign-in link' in resp.text
    assert "fetch('/auth/magic-link/request'" in resp.text


@pytest.mark.asyncio
async def test_person_edit_page_renders_labeled_fields_and_inline_error_container(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/edit")

    assert resp.status_code == 200
    assert 'id="person-edit-error"' in resp.text
    assert 'data-place-field' in resp.text
    assert 'name="residence_place_latitude"' in resp.text
    assert 'id="contact-address-list"' in resp.text
    assert 'id="phone-list"' in resp.text
    assert 'id="memorial-section"' in resp.text
    assert 'id="nickname-tag-input"' in resp.text


@pytest.mark.asyncio
async def test_new_person_page_renders_place_lookup_fields(member_client: AsyncClient):
    resp = await member_client.get("/people/new")

    assert resp.status_code == 200
    assert 'data-place-field' in resp.text
    assert 'name="birth_place_latitude"' in resp.text
    assert 'id="person-first-name"' in resp.text
    assert 'id="person-residence-place"' in resp.text


@pytest.mark.asyncio
async def test_tree_person_card_renders_workspace_tabs_and_tree_native_sections(member_client: AsyncClient):
    resp = await member_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'data-tree-sidebar-tab="overview"' in resp.text
    assert 'id="tree-sidebar-media"' in resp.text
    assert 'id="tree-sidebar-people-options"' in resp.text
    assert 'class="tree-sidebar-inline-actions"' in resp.text
    assert 'class="tree-sidebar-pill-row"' in resp.text


@pytest.mark.asyncio
async def test_tree_person_card_uses_search_picker_not_raw_relationship_selects(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'data-tree-picker' in resp.text
    assert 'placeholder="Search family members"' in resp.text
    assert 'select class="form-select" name="related_person_id"' not in resp.text


@pytest.mark.asyncio
async def test_admin_tree_person_card_renders_relationship_cards_with_maintenance_actions(admin_client: AsyncClient):
    resp = await admin_client.get(f"/people/{TYLER_ID}/card")

    assert resp.status_code == 200
    assert 'class="tree-related-card"' in resp.text
    assert "openTreeSidebarPerson('" in resp.text
    assert "removeTreeRelationship(" in resp.text
    assert "startTreeGraphMode('" in resp.text
    assert "replaceTreeRelationship(" in resp.text
    assert "editTreeRelationship(" in resp.text
    assert 'data-tree-relationship-edit-form="parent"' in resp.text
    assert 'id="tree-graph-mode-banner"' in resp.text


@pytest.mark.asyncio
async def test_wiki_person_page_renders_media_gallery_section_when_media_exists(
    admin_client: AsyncClient,
    tmp_path,
    monkeypatch,
):
    from app.config import Settings
    from tests.test_media import _make_test_image

    settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
    monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)
    create_resp = await admin_client.post(
        "/api/persons",
        json={"first_name": "Gallery", "last_name": "Person"},
    )
    assert create_resp.status_code == 201
    person_id = create_resp.json()["id"]
    person_slug = create_resp.json()["slug"]

    image_data = _make_test_image()
    upload_resp = await admin_client.post(
        "/api/media",
        data={"person_id": person_id},
        files={"file": ("wiki-photo.jpg", image_data, "image/jpeg")},
    )
    assert upload_resp.status_code == 201

    resp = await admin_client.get(f"/wiki/{person_slug}")

    assert resp.status_code == 200
    assert 'id="person-media-gallery"' in resp.text
    assert 'id="person-media"' in resp.text
    assert 'Photos' in resp.text


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
