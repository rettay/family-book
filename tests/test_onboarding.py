from io import BytesIO

import pytest
from httpx import AsyncClient
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hosted_archive import HostedArchive
from app.models.imports import GedcomImportBatch
from app.models.media import Media
from app.models.onboarding import OnboardingProgress
from app.models.person import Person
from app.services.onboarding_service import sync_onboarding_progress


async def _enable_hosted_archive(seeded_db: AsyncSession, monkeypatch) -> None:
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


def _make_test_png() -> bytes:
    image = Image.new("RGB", (32, 32), color="green")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


@pytest.mark.asyncio
async def test_hosted_admin_is_redirected_into_onboarding(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    await _enable_hosted_archive(seeded_db, monkeypatch)

    resp = await admin_client.get("/tree", follow_redirects=False)

    assert resp.status_code == 302
    assert resp.headers["location"] == "/onboarding"


@pytest.mark.asyncio
async def test_onboarding_page_renders_activation_surfaces(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    await _enable_hosted_archive(seeded_db, monkeypatch)

    resp = await admin_client.get("/onboarding")

    assert resp.status_code == 200
    assert 'id="onboarding-page"' in resp.text
    assert 'id="onboarding-relative-card"' in resp.text
    assert 'id="onboarding-gedcom-card"' in resp.text
    assert 'id="onboarding-media-card"' in resp.text
    assert 'id="onboarding-invite-card"' in resp.text


@pytest.mark.asyncio
async def test_onboarding_relative_and_media_update_progress(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
    tmp_path,
):
    await _enable_hosted_archive(seeded_db, monkeypatch)
    from app.config import Settings
    settings = Settings(SECRET_KEY="test", FERNET_KEY="dGVzdA==", DATA_DIR=str(tmp_path))
    monkeypatch.setattr("app.services.media_service.get_settings", lambda: settings)

    relative_resp = await admin_client.post(
        "/onboarding/relative",
        data={"first_name": "Ava", "last_name": "Martin", "relationship_type": "child"},
        follow_redirects=False,
    )
    assert relative_resp.status_code == 303

    media_resp = await admin_client.post(
        "/onboarding/media",
        files={"file": ("memory.png", BytesIO(_make_test_png()), "image/png")},
        data={"title": "First Memory", "caption": "A memory"},
        follow_redirects=False,
    )
    assert media_resp.status_code == 303

    progress = (
        await seeded_db.execute(
            select(OnboardingProgress).where(
                OnboardingProgress.person_id == "tyler-000-0000-0000-000000000002"
            )
        )
    ).scalar_one()
    media_count = (
        await seeded_db.execute(select(Media).where(Media.uploaded_by == "tyler-000-0000-0000-000000000002"))
    ).scalars().all()
    created_people = (
        await seeded_db.execute(select(Person).where(Person.created_by == "tyler-000-0000-0000-000000000002"))
    ).scalars().all()

    assert progress.milestones["relative_added"] is True
    assert progress.milestones["first_media"] is True
    assert len(media_count) == 1
    assert any(person.first_name == "Ava" for person in created_people)


@pytest.mark.asyncio
async def test_rolled_back_gedcom_batch_does_not_count_toward_onboarding(
    seeded_db: AsyncSession,
):
    seeded_db.add(
        GedcomImportBatch(
            filename="rolled-back.ged",
            status="rolled_back",
            imported_by="tyler-000-0000-0000-000000000002",
        )
    )
    await seeded_db.commit()

    admin = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    progress = await sync_onboarding_progress(seeded_db, person=admin)

    assert progress.milestones["gedcom_imported"] is False
