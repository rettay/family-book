import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.settings import AppThemeSettings
from app.services.theme_service import ThemeSettingsPayload


@pytest.mark.asyncio
async def test_admin_can_update_theme_and_rendered_surfaces_reflect_it(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    payload = {
        "brand_display_name": "Martin Family Archive",
        "brand_tagline": "Stories, people, and places kept together",
        "background_color": "#f2efe8",
        "surface_color": "#fffaf2",
        "primary_color": "#1f4a7c",
        "accent_color": "#b86c2f",
        "text_color": "#1f1f1f",
        "muted_text_color": "#6a6258",
        "border_color": "#d4c3b0",
        "theme_color": "#1f4a7c",
    }

    resp = await admin_client.put("/api/admin/theme", json=payload)
    assert resp.status_code == 200
    assert resp.json()["brand_display_name"] == "Martin Family Archive"

    settings_record = (
        await seeded_db.execute(select(AppThemeSettings))
    ).scalar_one()
    assert settings_record.settings["primary_color"] == "#1f4a7c"

    manifest_resp = await admin_client.get("/static/manifest.json")
    assert manifest_resp.status_code == 200
    manifest = manifest_resp.json()
    assert manifest["name"] == "Martin Family Archive"
    assert manifest["theme_color"] == "#1f4a7c"

    admin_client.cookies.clear()

    login_resp = await admin_client.get("/login")
    assert login_resp.status_code == 200
    assert 'content="#1f4a7c"' in login_resp.text
    assert "Martin Family Archive" in login_resp.text
    assert "Stories, people, and places kept together" in login_resp.text

    landing_resp = await admin_client.get("/")
    assert landing_resp.status_code == 200
    assert "Martin Family Archive" in landing_resp.text
    assert "Stories, people, and places kept together" in landing_resp.text


@pytest.mark.asyncio
async def test_non_admin_cannot_update_theme(member_client: AsyncClient):
    resp = await member_client.put(
        "/api/admin/theme",
        json={
            "brand_display_name": "Blocked",
            "brand_tagline": "Blocked",
            "background_color": "#faf8f5",
            "surface_color": "#fefcf9",
            "primary_color": "#2d5016",
            "accent_color": "#c49a3c",
            "text_color": "#2c2c2c",
            "muted_text_color": "#6b6054",
            "border_color": "#e0d6c8",
            "theme_color": "#faf8f5",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_reset_theme_to_defaults(admin_client: AsyncClient):
    await admin_client.put(
        "/api/admin/theme",
        json={
            "brand_display_name": "Reset Me",
            "brand_tagline": "Temporary",
            "background_color": "#f2efe8",
            "surface_color": "#fffaf2",
            "primary_color": "#1f4a7c",
            "accent_color": "#b86c2f",
            "text_color": "#1f1f1f",
            "muted_text_color": "#6a6258",
            "border_color": "#d4c3b0",
            "theme_color": "#1f4a7c",
        },
    )

    reset_resp = await admin_client.post("/api/admin/theme/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["brand_display_name"] == "Family Book"
    assert reset_resp.json()["primary_color"] == "#2d5016"


def test_theme_payload_rejects_unreadable_palette():
    with pytest.raises(ValidationError, match="contrast|readable|visible|distinguishable"):
        ThemeSettingsPayload(
            brand_display_name="Unreadable",
            brand_tagline="bad palette",
            background_color="#ffffff",
            surface_color="#ffffff",
            primary_color="#ffffff",
            accent_color="#ffffff",
            text_color="#ffffff",
            muted_text_color="#ffffff",
            border_color="#ffffff",
            theme_color="#ffffff",
        )


@pytest.mark.asyncio
async def test_admin_page_hides_staging_link_without_config(
    admin_client: AsyncClient,
    monkeypatch,
):
    monkeypatch.setenv("STAGING_REVIEW_URL", "")
    resp = await admin_client.get("/admin")
    assert resp.status_code == 200
    assert "Open Staging" not in resp.text
