import pytest
from httpx import AsyncClient


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
