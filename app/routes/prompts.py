from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import get_accessible_person_ids, get_person_access
from app.auth import require_auth
from app.database import get_db
from app.models.person import Person, PersonLifecycleState
from app.models.prompts import (
    PromptCampaign,
    PromptCampaignRecipient,
    PromptRecipientStatus,
    PromptResponseKind,
)
from app.models.story import Story
from app.routes.pages import _ctx, templates
from app.roles import is_staff_actor
from app.services.audit_service import log_audit
from app.services.email_delivery import send_weekly_digest_email
from app.services.io_limits import SizeLimitExceeded, stream_upload_to_temp
from app.services.prompt_service import (
    build_weekly_digest,
    create_prompt_media_inbox_item,
    digest_enabled,
    get_or_create_digest_preference,
)

router = APIRouter(tags=["prompts"])


async def _recipient_can_view_target(
    db: AsyncSession,
    *,
    recipient: Person,
    target_person: Person | None,
) -> bool:
    if target_person is None:
        return True
    access = await get_person_access(db, recipient, target_person)
    return access.can_view


@router.get("/prompts", response_class=HTMLResponse)
async def prompts_page(
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    accessible_ids = await get_accessible_person_ids(db, current_user)
    people_result = await db.execute(
        select(Person)
        .where(
            Person.id.in_(accessible_ids),
            Person.is_root.is_(False),
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
        .order_by(Person.last_name, Person.first_name)
    )
    selectable_people = [
        person for person in people_result.scalars().all() if person.id != current_user.id
    ]

    campaign_result = await db.execute(
        select(PromptCampaign).order_by(PromptCampaign.sent_at.desc())
    )
    campaigns = campaign_result.scalars().all()

    incoming_result = await db.execute(
        select(PromptCampaignRecipient, PromptCampaign)
        .join(PromptCampaign, PromptCampaign.id == PromptCampaignRecipient.campaign_id)
        .where(PromptCampaignRecipient.recipient_person_id == current_user.id)
        .order_by(PromptCampaign.sent_at.desc())
    )
    incoming_prompts = []
    for recipient_row, campaign in incoming_result.all():
        target_person = await db.get(Person, campaign.target_person_id) if campaign.target_person_id else None
        target_person_name = None
        if await _recipient_can_view_target(db, recipient=current_user, target_person=target_person):
            target_person_name = target_person.display_name if target_person else None
        incoming_prompts.append(
            {
                "recipient_id": recipient_row.id,
                "campaign": campaign,
                "target_person_name": target_person_name,
            }
        )

    digest_preference = await get_or_create_digest_preference(db, person=current_user)
    digest_preview = await build_weekly_digest(db, recipient=current_user)
    return templates.TemplateResponse(
        "prompts.html",
        _ctx(
            request,
            current_user,
            active_page="prompts",
            selectable_people=selectable_people,
            campaigns=campaigns,
            incoming_prompts=incoming_prompts,
            can_send_prompts=is_staff_actor(current_user),
            digest_enabled_value=digest_enabled(digest_preference),
            digest_email=digest_preference.push_email or current_user.contact_email or "",
            digest_preview=digest_preview,
        ),
    )


@router.post("/prompts/campaigns")
async def create_prompt_campaign(
    title: str = Form(...),
    prompt_body: str = Form(...),
    recipient_ids: list[str] = Form(...),
    response_kind: str = Form(PromptResponseKind.story.value),
    target_person_id: str | None = Form(None),
    due_date: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not is_staff_actor(current_user):
        raise HTTPException(status_code=403, detail="Staff access required")
    if response_kind not in {PromptResponseKind.story.value, PromptResponseKind.media.value}:
        raise HTTPException(status_code=422, detail="Unsupported response kind")

    target_person = None
    if target_person_id:
        target_person = await db.get(Person, target_person_id)
        if target_person is None:
            raise HTTPException(status_code=404, detail="Target person not found")
        access = await get_person_access(db, current_user, target_person)
        if not access.can_view:
            raise HTTPException(status_code=403, detail="Target person is not visible")

    campaign = PromptCampaign(
        created_by=current_user.id,
        target_person_id=target_person.id if target_person else None,
        title=title.strip(),
        prompt_body=prompt_body.strip(),
        response_kind=response_kind,
        due_date=due_date.strip() if due_date else None,
    )
    db.add(campaign)
    await db.flush()

    deduped_recipient_ids = []
    for recipient_id in recipient_ids:
        recipient_id = recipient_id.strip()
        if recipient_id and recipient_id not in deduped_recipient_ids:
            deduped_recipient_ids.append(recipient_id)
    if not deduped_recipient_ids:
        raise HTTPException(status_code=422, detail="At least one recipient is required")

    for recipient_id in deduped_recipient_ids:
        person = await db.get(Person, recipient_id)
        if person is None or person.lifecycle_state != PersonLifecycleState.active.value:
            raise HTTPException(status_code=404, detail="Recipient not found")
        access = await get_person_access(db, current_user, person)
        if not access.can_view:
            raise HTTPException(status_code=403, detail="Recipient is not visible")
        if not await _recipient_can_view_target(db, recipient=person, target_person=target_person):
            raise HTTPException(
                status_code=403,
                detail="Recipient cannot view the selected subject person",
            )
        db.add(
            PromptCampaignRecipient(
                campaign_id=campaign.id,
                recipient_person_id=person.id,
            )
        )

    await db.flush()
    await log_audit(
        db,
        current_user.id,
        "create",
        "prompt_campaign",
        campaign.id,
        new_value={
            "recipient_count": len(deduped_recipient_ids),
            "response_kind": response_kind,
        },
    )
    return RedirectResponse("/prompts", status_code=303)


@router.post("/prompts/recipients/{recipient_id}/respond")
async def respond_to_prompt_campaign(
    recipient_id: str,
    title: str | None = Form(None),
    body: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    recipient_row = await db.get(PromptCampaignRecipient, recipient_id)
    if recipient_row is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if recipient_row.recipient_person_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to respond")
    if recipient_row.status != PromptRecipientStatus.pending.value:
        raise HTTPException(status_code=400, detail="Prompt already answered")

    campaign = await db.get(PromptCampaign, recipient_row.campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    target_person = await db.get(Person, campaign.target_person_id) if campaign.target_person_id else current_user
    if target_person is None:
        target_person = current_user
    if not await _recipient_can_view_target(db, recipient=current_user, target_person=target_person):
        raise HTTPException(status_code=403, detail="Prompt target is not visible")

    if campaign.response_kind == PromptResponseKind.story.value:
        story = Story(
            person_id=target_person.id,
            title=(title or campaign.title).strip(),
            body=(body or "").strip(),
            author_person_id=current_user.id,
            source=f"Prompt response: {campaign.title}",
        )
        db.add(story)
        await db.flush()
        recipient_row.response_story_id = story.id
        recipient_row.response_excerpt = (body or "").strip()[:500] or None
    else:
        if file is None or not file.content_type:
            raise HTTPException(status_code=400, detail="A file is required for media prompts")
        try:
            streamed_upload = await stream_upload_to_temp(file, 10 * 1024 * 1024)
        except SizeLimitExceeded:
            raise HTTPException(status_code=413, detail="File too large")
        inbox_item = await create_prompt_media_inbox_item(
            db,
            uploaded_by=current_user,
            filename=file.filename or "prompt-upload",
            mime_type=file.content_type,
            temp_path=streamed_upload.path,
            file_size=streamed_upload.size,
            file_hash=streamed_upload.sha256,
            title=(title or campaign.title).strip() or None,
            caption=(body or "").strip() or None,
            source_text=(body or "").strip() or None,
        )
        recipient_row.response_inbox_item_id = inbox_item.id
        recipient_row.response_excerpt = (body or "").strip()[:500] or None

    recipient_row.status = PromptRecipientStatus.responded.value
    recipient_row.responded_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await log_audit(
        db,
        current_user.id,
        "respond",
        "prompt_campaign",
        campaign.id,
        new_value={
            "recipient_id": recipient_row.id,
            "status": recipient_row.status,
        },
    )
    return RedirectResponse("/prompts", status_code=303)


@router.post("/prompts/digest/send")
async def send_weekly_digest(
    request: Request,
    recipient_id: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if not is_staff_actor(current_user):
        raise HTTPException(status_code=403, detail="Staff access required")

    query = select(Person).where(
        Person.is_root.is_(False),
        Person.lifecycle_state == PersonLifecycleState.active.value,
    )
    if recipient_id:
        query = query.where(Person.id == recipient_id)
    result = await db.execute(query.order_by(Person.last_name, Person.first_name))

    sent_count = 0
    skipped_count = 0
    family_name = _ctx(request)["brand_display_name"]
    for person in result.scalars().all():
        preference = await get_or_create_digest_preference(db, person=person)
        if not digest_enabled(preference):
            skipped_count += 1
            continue
        if not preference.push_email:
            skipped_count += 1
            continue
        digest = await build_weekly_digest(db, recipient=person)
        delivery = await send_weekly_digest_email(
            recipient_email=preference.push_email,
            recipient_name=person.display_name,
            digest=digest,
            family_name=family_name,
        )
        if delivery.status == "sent":
            sent_count += 1
        else:
            skipped_count += 1

    await log_audit(
        db,
        current_user.id,
        "send",
        "weekly_digest",
        recipient_id or "all",
        new_value={"sent_count": sent_count, "skipped_count": skipped_count},
    )
    return JSONResponse({"sent_count": sent_count, "skipped_count": skipped_count})


@router.post("/settings/digest-preferences")
async def update_digest_preferences(
    enabled: str | None = Form(None),
    push_email: str | None = Form(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    preference = await get_or_create_digest_preference(db, person=current_user)
    enabled_value = (enabled or "").strip().lower() in {"1", "true", "yes", "on"}
    preference.push_channel = "email" if enabled_value else "none"
    preference.push_frequency = "weekly_digest"
    preference.push_email = (push_email or current_user.contact_email or "").strip() or None
    await db.flush()
    return RedirectResponse("/settings", status_code=303)
