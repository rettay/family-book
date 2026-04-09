from __future__ import annotations

import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_manage_person, get_person_access
from app.auth import require_auth
from app.config import get_settings
from app.database import get_db
from app.models.auth import Invite
from app.models.imports import GedcomImportBatch, ImportStatus
from app.models.media import MediaInboxItem, MediaInboxStatus, MediaSource
from app.models.onboarding import OnboardingStatus
from app.models.person import AccountState, Person, PersonLifecycleState, PersonSource
from app.models.relationships import ParentChild, Partnership, PartnershipKind, RelationshipSource
from app.routes.pages import _ctx, templates
from app.routes.imports import _validate_and_parse
from app.roles import get_person_role, is_admin_actor
from app.services.audit_service import log_audit
from app.services.auth_service import create_invite
from app.services.email_delivery import send_invite_email
from app.services.import_service import (
    build_gedcom_import_summary,
    detect_unsupported_gedcom_items,
    import_gedcom,
)
from app.services.io_limits import SizeLimitExceeded, stream_upload_to_temp
from app.services.media_service import (
    _media_type_for_mime,
    get_media_file_path,
    save_media_file,
    save_media_temp_file,
)
from app.services.onboarding_service import (
    get_or_create_onboarding_progress,
    onboarding_required_for_person,
    sync_onboarding_progress,
)

router = APIRouter(tags=["onboarding"])


def _onboarding_enabled_for_user(current_user: Person) -> bool:
    settings = get_settings()
    return settings.hosted_archive_enabled and is_admin_actor(current_user)


async def _load_onboarding_context(
    request: Request,
    *,
    current_user: Person,
    db: AsyncSession,
    notice: str | None = None,
):
    progress = await sync_onboarding_progress(db, person=current_user)
    batch_result = await db.execute(
        select(GedcomImportBatch)
        .where(GedcomImportBatch.imported_by == current_user.id)
        .order_by(GedcomImportBatch.created_at.desc())
        .limit(5)
    )
    batches = batch_result.scalars().all()

    invite_people_result = await db.execute(
        select(Person)
        .where(
            Person.id != current_user.id,
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    invite_people = invite_people_result.scalars().all()

    inbox_result = await db.execute(
        select(MediaInboxItem)
        .where(MediaInboxItem.uploaded_by == current_user.id)
        .order_by(MediaInboxItem.created_at.desc())
        .limit(10)
    )
    inbox_items = inbox_result.scalars().all()

    milestones = progress.milestones
    completion_count = sum(1 for key, value in milestones.items() if key != "owner_profile" and value)
    return templates.TemplateResponse(
        "onboarding.html",
        _ctx(
            request,
            current_user,
            active_page="onboarding",
            onboarding_progress=progress,
            onboarding_milestones=milestones,
            onboarding_completion_count=completion_count,
            onboarding_notice=notice,
            import_batches=batches,
            invite_people=invite_people,
            inbox_items=inbox_items,
        ),
    )


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(
    request: Request,
    notice: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        return RedirectResponse("/tree", status_code=302)
    return await _load_onboarding_context(
        request,
        current_user=current_user,
        db=db,
        notice=notice,
    )


@router.post("/onboarding/skip")
async def skip_onboarding(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        raise HTTPException(status_code=404, detail="Onboarding is not enabled")
    progress = await get_or_create_onboarding_progress(db, person_id=current_user.id)
    progress.status = OnboardingStatus.skipped
    progress.skipped_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await log_audit(
        db,
        current_user.id,
        "skip",
        "onboarding",
        progress.id,
        new_value={"status": OnboardingStatus.skipped},
    )
    return RedirectResponse("/tree", status_code=303)


@router.post("/onboarding/path")
async def select_onboarding_path(
    path: str = Form(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if path not in {"manual", "gedcom"}:
        raise HTTPException(status_code=422, detail="path must be manual or gedcom")
    progress = await get_or_create_onboarding_progress(db, person_id=current_user.id)
    progress.selected_path = path
    await log_audit(
        db,
        current_user.id,
        "select",
        "onboarding_path",
        progress.id,
        new_value={"path": path},
    )
    return RedirectResponse("/onboarding?notice=path-updated", status_code=303)


@router.post("/onboarding/relative")
async def add_onboarding_relative(
    first_name: str = Form(...),
    last_name: str = Form(...),
    relationship_type: str = Form("relative"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        raise HTTPException(status_code=404, detail="Onboarding is not enabled")
    person = Person(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        branch=current_user.branch,
        source=PersonSource.manual.value,
        account_state=AccountState.active.value,
        created_by=current_user.id,
    )
    db.add(person)
    await db.flush()

    relationship_type = relationship_type.strip().lower()
    if relationship_type == "child":
        db.add(
            ParentChild(
                parent_id=current_user.id,
                child_id=person.id,
                source=RelationshipSource.manual.value,
                created_by=current_user.id,
            )
        )
    elif relationship_type == "parent":
        db.add(
            ParentChild(
                parent_id=person.id,
                child_id=current_user.id,
                source=RelationshipSource.manual.value,
                created_by=current_user.id,
            )
        )
    elif relationship_type == "partner":
        a_id, b_id = sorted([current_user.id, person.id])
        db.add(
            Partnership(
                person_a_id=a_id,
                person_b_id=b_id,
                kind=PartnershipKind.married.value,
                source=RelationshipSource.manual.value,
                created_by=current_user.id,
            )
        )

    await log_audit(
        db,
        current_user.id,
        "create",
        "onboarding_relative",
        person.id,
        new_value={"relationship_type": relationship_type},
    )
    await sync_onboarding_progress(db, person=current_user)
    return RedirectResponse("/onboarding?notice=relative-added", status_code=303)


@router.post("/onboarding/media")
async def upload_onboarding_media(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    caption: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        raise HTTPException(status_code=404, detail="Onboarding is not enabled")
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Missing file type")

    max_size = 10 * 1024 * 1024
    try:
        streamed_upload = await stream_upload_to_temp(file, max_size)
    except SizeLimitExceeded:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        media, _ = await save_media_temp_file(
            db=db,
            temp_path=streamed_upload.path,
            file_size=streamed_upload.size,
            file_hash=streamed_upload.sha256,
            filename=file.filename or "upload",
            mime_type=file.content_type,
            person_id=current_user.id,
            uploaded_by=current_user.id,
            title=title,
            caption=caption,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    media.source = MediaSource.manual.value
    await db.flush()
    await sync_onboarding_progress(db, person=current_user)
    return RedirectResponse("/onboarding?notice=media-added", status_code=303)


@router.post("/onboarding/invite")
async def send_onboarding_invite(
    request: Request,
    person_id: str = Form(...),
    contact_email: str = Form(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        raise HTTPException(status_code=404, detail="Onboarding is not enabled")

    person = await db.get(Person, person_id)
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=404, detail="Person not found")

    person.contact_email = contact_email.strip()
    invite = await create_invite(db, person_id=person.id, created_by=current_user.id)
    settings = get_settings()
    invite_url = f"{settings.BASE_URL.rstrip('/')}/invite/{invite.raw_token}"
    delivery = await send_invite_email(
        recipient_email=person.contact_email or "",
        recipient_name=person.display_name,
        invite_url=invite_url,
        invited_by_name=current_user.display_name,
        expires_at=invite.expires_at,
        family_name=_ctx(request)["brand_display_name"],
    )
    invite.delivery_status = delivery.status
    invite.delivery_error = delivery.error
    invite.delivery_message_id = delivery.message_id
    await log_audit(
        db,
        current_user.id,
        "create",
        "invite_activation",
        invite.id,
        new_value={
            "person_id": person.id,
            "delivery_status": delivery.status,
        },
    )
    await sync_onboarding_progress(db, person=current_user)
    return JSONResponse(
        {
            "ok": True,
            "invite_url": invite_url,
            "delivery_status": delivery.status,
        }
    )


@router.post("/onboarding/import")
async def onboarding_import_gedcom(
    file: UploadFile = File(...),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not _onboarding_enabled_for_user(current_user):
        raise HTTPException(status_code=404, detail="Onboarding is not enabled")
    content = await file.read()
    parsed = _validate_and_parse(content, file.filename)

    batch = GedcomImportBatch(
        filename=file.filename or "unknown.ged",
        status=ImportStatus.importing.value,
        imported_by=current_user.id,
    )
    db.add(batch)
    await db.flush()

    result = await import_gedcom(
        db,
        parsed,
        actor_id=current_user.id,
        batch_id=batch.id,
    )
    summary = build_gedcom_import_summary(
        parsed=parsed,
        result=result,
        unsupported_items=detect_unsupported_gedcom_items(content),
    )

    batch.status = ImportStatus.completed.value
    batch.persons_created = result.persons_created
    batch.relationships_created = result.relationships_created
    batch.duplicates_skipped = result.duplicates_skipped
    batch.stats = summary
    batch.completed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db.flush()

    progress = await get_or_create_onboarding_progress(db, person_id=current_user.id)
    progress.selected_path = "gedcom"
    await sync_onboarding_progress(db, person=current_user)
    return RedirectResponse(f"/imports/gedcom/{batch.id}?from=onboarding", status_code=303)


@router.get("/imports/gedcom/{batch_id}", response_class=HTMLResponse)
async def gedcom_batch_page(
    batch_id: str,
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    batch = await db.get(GedcomImportBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")
    if batch.imported_by != current_user.id and not is_admin_actor(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view this import batch")

    return templates.TemplateResponse(
        "import_batch.html",
        _ctx(
            request,
            current_user,
            active_page="onboarding",
            batch=batch,
            batch_summary=batch.stats,
        ),
    )


async def _load_inbox_item_for_actor(
    db: AsyncSession,
    *,
    inbox_item_id: str,
    current_user: Person,
) -> MediaInboxItem:
    inbox_item = await db.get(MediaInboxItem, inbox_item_id)
    if not inbox_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    if inbox_item.uploaded_by != current_user.id and not is_admin_actor(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to manage this inbox item")
    return inbox_item


@router.get("/media/inbox", response_class=HTMLResponse)
async def media_inbox_page(
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MediaInboxItem)
        .where(MediaInboxItem.uploaded_by == current_user.id)
        .order_by(MediaInboxItem.created_at.desc())
    )
    inbox_items = result.scalars().all()
    people_result = await db.execute(
        select(Person)
        .where(
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    attach_people = []
    for person in people_result.scalars().all():
        if not can_manage_person(current_user, person):
            continue
        access = await get_person_access(db, current_user, person)
        if access.can_view or is_admin_actor(current_user):
            attach_people.append(person)
    return templates.TemplateResponse(
        "media_inbox.html",
        _ctx(
            request,
            current_user,
            active_page="gallery",
            inbox_items=inbox_items,
            attach_people=attach_people,
        ),
    )


@router.post("/media/inbox/{inbox_item_id}/attach")
async def attach_media_inbox_item(
    inbox_item_id: str,
    person_id: str = Form(...),
    title: str | None = Form(None),
    caption: str | None = Form(None),
    taken_date: str | None = Form(None),
    taken_location: str | None = Form(None),
    tagged_person_ids: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    inbox_item = await _load_inbox_item_for_actor(db, inbox_item_id=inbox_item_id, current_user=current_user)
    if inbox_item.status != MediaInboxStatus.pending.value:
        raise HTTPException(status_code=400, detail="Inbox item is no longer pending")

    person = await db.get(Person, person_id)
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized to attach media to this profile")

    file_path = get_media_file_path(inbox_item.file_path)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=410, detail="Inbox file is missing")

    with open(file_path, "rb") as handle:
        data = handle.read()

    parsed_tagged_ids = []
    if tagged_person_ids:
        parsed_tagged_ids = [item.strip() for item in tagged_person_ids.split(",") if item.strip()]
    for tagged_person_id in parsed_tagged_ids:
        tagged_person = await db.get(Person, tagged_person_id)
        if not tagged_person or tagged_person.lifecycle_state != PersonLifecycleState.active.value:
            raise HTTPException(status_code=400, detail=f"Tagged person not found: {tagged_person_id}")
        tagged_person_access = await get_person_access(db, current_user, tagged_person)
        if not tagged_person_access.can_view:
            raise HTTPException(status_code=403, detail="Not authorized to tag this person")

    media, _ = await save_media_file(
        db=db,
        file_data=data,
        filename=inbox_item.original_filename or "shared-upload",
        mime_type=inbox_item.mime_type or "application/octet-stream",
        person_id=person.id,
        uploaded_by=current_user.id,
        caption=caption or inbox_item.caption,
        title=title or inbox_item.title or inbox_item.source_title,
        taken_date=taken_date or inbox_item.taken_date,
        tagged_person_ids=parsed_tagged_ids or inbox_item.tagged_person_ids,
        dedupe_across_people=False,
    )
    media.source = MediaSource.share_sheet.value
    media.taken_location = taken_location or inbox_item.taken_location
    inbox_item.status = MediaInboxStatus.attached.value
    inbox_item.attached_media_id = media.id
    inbox_item.attached_person_id = person.id
    inbox_item.title = title or inbox_item.title
    inbox_item.caption = caption or inbox_item.caption
    inbox_item.taken_date = taken_date or inbox_item.taken_date
    inbox_item.taken_location = taken_location or inbox_item.taken_location
    if parsed_tagged_ids:
        inbox_item.tagged_person_ids = parsed_tagged_ids

    os.unlink(file_path)
    await log_audit(
        db,
        current_user.id,
        "attach",
        "media_inbox",
        inbox_item.id,
        new_value={"media_id": media.id, "person_id": person.id},
    )
    return RedirectResponse("/media/inbox", status_code=303)


@router.post("/media/inbox/{inbox_item_id}/reject")
async def reject_media_inbox_item(
    inbox_item_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    inbox_item = await _load_inbox_item_for_actor(db, inbox_item_id=inbox_item_id, current_user=current_user)
    file_path = get_media_file_path(inbox_item.file_path)
    if file_path and os.path.exists(file_path):
        os.unlink(file_path)
    inbox_item.status = MediaInboxStatus.rejected.value
    await log_audit(
        db,
        current_user.id,
        "reject",
        "media_inbox",
        inbox_item.id,
    )
    return RedirectResponse("/media/inbox", status_code=303)


@router.get("/invite/first-steps", response_class=HTMLResponse)
async def invite_first_steps_page(
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    role = get_person_role(current_user)
    return templates.TemplateResponse(
        "invite_first_steps.html",
        _ctx(
            request,
            current_user,
            active_page="tree",
            invite_role=role,
            invite_focus_person=current_user,
        ),
    )
