from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Invite
from app.models.imports import GedcomImportBatch
from app.models.media import Media
from app.models.onboarding import OnboardingProgress, OnboardingStatus
from app.models.person import Person, PersonLifecycleState
from app.roles import is_admin_actor
from app.services.audit_service import log_audit


ONBOARDING_ALLOWED_PATH_PREFIXES = (
    "/onboarding",
    "/admin",
    "/settings",
    "/trust",
    "/auth/",
    "/api/",
    "/health",
    "/static/",
)


async def get_or_create_onboarding_progress(
    db: AsyncSession,
    *,
    person_id: str,
) -> OnboardingProgress:
    result = await db.execute(
        select(OnboardingProgress).where(OnboardingProgress.person_id == person_id)
    )
    progress = result.scalar_one_or_none()
    if progress:
        return progress

    progress = OnboardingProgress(person_id=person_id)
    progress.milestones = {}
    db.add(progress)
    await db.flush()
    return progress


async def sync_onboarding_progress(
    db: AsyncSession,
    *,
    person: Person,
) -> OnboardingProgress:
    progress = await get_or_create_onboarding_progress(db, person_id=person.id)
    previous = dict(progress.milestones)

    created_people_count = (
        await db.execute(
            select(func.count(Person.id)).where(
                Person.created_by == person.id,
                Person.lifecycle_state == PersonLifecycleState.active.value,
                Person.is_root.is_(False),
            )
        )
    ).scalar() or 0

    uploaded_media_count = (
        await db.execute(
            select(func.count(Media.id)).where(Media.uploaded_by == person.id)
        )
    ).scalar() or 0

    invite_count = (
        await db.execute(
            select(func.count(Invite.id)).where(Invite.created_by == person.id)
        )
    ).scalar() or 0

    batch_result = await db.execute(
        select(GedcomImportBatch)
        .where(GedcomImportBatch.imported_by == person.id)
        .order_by(GedcomImportBatch.created_at.desc())
        .limit(1)
    )
    latest_batch = batch_result.scalar_one_or_none()

    milestones = {
        "owner_profile": True,
        "relative_added": created_people_count > 0,
        "gedcom_imported": latest_batch is not None and latest_batch.status == "completed",
        "first_media": uploaded_media_count > 0,
        "first_invite": invite_count > 0,
    }
    progress.milestones = milestones

    if progress.selected_path not in {"manual", "gedcom"}:
        if milestones["gedcom_imported"]:
            progress.selected_path = "gedcom"
        elif milestones["relative_added"]:
            progress.selected_path = "manual"

    required_done = (
        milestones["owner_profile"]
        and (milestones["relative_added"] or milestones["gedcom_imported"])
        and milestones["first_media"]
        and milestones["first_invite"]
    )

    if progress.status != OnboardingStatus.skipped:
        progress.status = OnboardingStatus.completed if required_done else OnboardingStatus.active
        if progress.status == OnboardingStatus.completed and progress.completed_at is None:
            progress.completed_at = datetime.now(timezone.utc)
        if progress.status != OnboardingStatus.completed:
            progress.completed_at = None

    progress.updated_at = datetime.now(timezone.utc)
    await db.flush()

    for milestone, is_complete in milestones.items():
        if is_complete and not previous.get(milestone):
            await log_audit(
                db,
                actor_id=person.id,
                action="complete",
                entity_type="onboarding_milestone",
                entity_id=progress.id,
                new_value={"milestone": milestone},
            )

    return progress


def onboarding_required_for_person(progress: OnboardingProgress | None, person: Person | None) -> bool:
    if person is None or not is_admin_actor(person):
        return False
    if progress is None:
        return True
    return progress.status not in {OnboardingStatus.completed, OnboardingStatus.skipped}


def onboarding_redirect_path_allowed(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ONBOARDING_ALLOWED_PATH_PREFIXES)
