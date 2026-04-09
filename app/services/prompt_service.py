from __future__ import annotations

import html
import os
import shutil
import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_view_media, get_accessible_person_ids
from app.config import get_settings
from app.models.media import Media, MediaInboxItem, MediaInboxStatus
from app.models.notifications import (
    NotificationPreference,
    PushChannel,
    PushFrequency,
)
from app.models.person import Person, PersonLifecycleState
from app.models.prompts import PromptCampaign, PromptCampaignRecipient
from app.models.story import Story
from app.services.calendar_service import get_calendar_events
from app.services.media_service import _media_type_for_mime


async def get_or_create_digest_preference(
    db: AsyncSession,
    *,
    person: Person,
) -> NotificationPreference:
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.person_id == person.id)
    )
    preference = result.scalar_one_or_none()
    if preference is None:
        preference = NotificationPreference(
            person_id=person.id,
            push_channel=PushChannel.email.value if person.contact_email else PushChannel.none.value,
            push_email=person.contact_email,
            push_frequency=PushFrequency.weekly_digest.value,
        )
        db.add(preference)
        await db.flush()
    elif not preference.push_email and person.contact_email:
        preference.push_email = person.contact_email
        await db.flush()
    return preference


def digest_enabled(preference: NotificationPreference | None) -> bool:
    if preference is None:
        return True
    return (
        preference.push_channel != PushChannel.none.value
        and preference.push_frequency == PushFrequency.weekly_digest.value
        and bool(preference.push_email)
    )


async def build_weekly_digest(
    db: AsyncSession,
    *,
    recipient: Person,
    today: date | None = None,
) -> dict[str, list[dict]]:
    if today is None:
        today = datetime.now(UTC).date()
    since = datetime.now(UTC) - timedelta(days=7)
    accessible_ids = await get_accessible_person_ids(db, recipient)

    story_result = await db.execute(
        select(Story)
        .where(
            Story.person_id.in_(accessible_ids),
            Story.created_at >= since,
        )
        .order_by(Story.created_at.desc())
    )
    stories = []
    for story in story_result.scalars().all():
        person = await db.get(Person, story.person_id)
        if person is None:
            continue
        stories.append(
            {
                "id": story.id,
                "title": story.title,
                "person_name": person.display_name,
                "created_at": story.created_at.isoformat() if story.created_at else None,
                "source": story.source,
            }
        )

    media_result = await db.execute(
        select(Media).where(Media.created_at >= since).order_by(Media.created_at.desc())
    )
    media_items = []
    for media in media_result.scalars().all():
        if not await can_view_media(db, recipient, media):
            continue
        person = await db.get(Person, media.person_id)
        media_items.append(
            {
                "id": media.id,
                "title": media.title or media.caption or media.original_filename or "Untitled media",
                "person_name": person.display_name if person else "Unknown person",
                "created_at": media.created_at.isoformat() if media.created_at else None,
            }
        )
        if len(media_items) >= 8:
            break

    upcoming = await _upcoming_calendar_events(db, recipient, today=today)

    prompt_result = await db.execute(
        select(PromptCampaignRecipient, PromptCampaign)
        .join(PromptCampaign, PromptCampaign.id == PromptCampaignRecipient.campaign_id)
        .where(
            PromptCampaignRecipient.recipient_person_id == recipient.id,
            PromptCampaignRecipient.status == "pending",
        )
        .order_by(PromptCampaign.sent_at.desc())
    )
    unanswered_prompts = [
        {
            "campaign_id": campaign.id,
            "title": campaign.title,
            "prompt_body": campaign.prompt_body,
            "due_date": campaign.due_date,
        }
        for _recipient_row, campaign in prompt_result.all()
    ]

    return {
        "stories": stories,
        "media": media_items,
        "upcoming": upcoming,
        "unanswered_prompts": unanswered_prompts,
    }


async def _upcoming_calendar_events(
    db: AsyncSession,
    recipient: Person,
    *,
    today: date,
) -> list[dict]:
    month_cursor = date(today.year, today.month, 1)
    months = [month_cursor]
    if month_cursor.month == 12:
        months.append(date(month_cursor.year + 1, 1, 1))
    else:
        months.append(date(month_cursor.year, month_cursor.month + 1, 1))

    events = []
    for month_start in months:
        events.extend(await get_calendar_events(db, recipient, month_start.year, month_start.month))

    results = []
    horizon = today + timedelta(days=14)
    for event in events:
        try:
            event_day = date.fromisoformat(event["date"][:10])
        except (TypeError, ValueError):
            continue
        if today <= event_day <= horizon:
            results.append(
                {
                    "date": event_day.isoformat(),
                    "label": event["label"],
                    "type": event["type"],
                }
            )
    results.sort(key=lambda item: item["date"])
    return results[:10]


async def create_prompt_media_inbox_item(
    db: AsyncSession,
    *,
    uploaded_by: Person,
    filename: str,
    mime_type: str,
    temp_path: str,
    file_size: int,
    file_hash: str,
    title: str | None,
    caption: str | None,
    source_text: str | None,
) -> MediaInboxItem:
    settings = get_settings()
    media_dir = os.path.join(settings.resolved_data_dir, "media")
    inbox_dir = os.path.join(media_dir, "inbox")
    os.makedirs(inbox_dir, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower() or ".bin"
    storage_name = f"{uuid.uuid4()}{ext}"
    relative_path = os.path.join("inbox", storage_name)
    destination = os.path.join(inbox_dir, storage_name)
    shutil.move(temp_path, destination)

    item = MediaInboxItem(
        file_path=relative_path,
        original_filename=filename,
        mime_type=mime_type,
        file_size_bytes=file_size,
        file_hash=file_hash,
        media_type=_media_type_for_mime(mime_type),
        status=MediaInboxStatus.pending.value,
        uploaded_by=uploaded_by.id,
        source_title=title,
        source_text=source_text,
        title=title,
        caption=caption,
    )
    db.add(item)
    await db.flush()
    return item


def render_weekly_digest_html(
    *,
    recipient_name: str,
    digest: dict[str, list[dict]],
    family_name: str,
) -> str:
    sections = [
        _render_digest_section("New stories", digest["stories"], lambda item: f'{item["title"]} - {item["person_name"]}'),
        _render_digest_section("New media", digest["media"], lambda item: f'{item["title"]} - {item["person_name"]}'),
        _render_digest_section("Coming up", digest["upcoming"], lambda item: f'{item["date"]} - {item["label"]}'),
        _render_digest_section("Waiting for you", digest["unanswered_prompts"], lambda item: item["title"]),
    ]
    safe_name = html.escape(recipient_name)
    safe_family_name = html.escape(family_name)
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"></head><body>"
        f"<h1>{safe_family_name} weekly digest</h1>"
        f"<p>Hello {safe_name}, here is what changed in your family archive this week.</p>"
        + "".join(sections)
        + "</body></html>"
    )


def render_weekly_digest_text(
    *,
    recipient_name: str,
    digest: dict[str, list[dict]],
    family_name: str,
) -> str:
    lines = [
        f"{family_name} weekly digest",
        "",
        f"Hello {recipient_name},",
        "",
        "Stories:",
    ]
    lines.extend(f"- {item['title']} ({item['person_name']})" for item in digest["stories"])
    lines.extend(["", "Media:"])
    lines.extend(f"- {item['title']} ({item['person_name']})" for item in digest["media"])
    lines.extend(["", "Coming up:"])
    lines.extend(f"- {item['date']} {item['label']}" for item in digest["upcoming"])
    lines.extend(["", "Waiting for you:"])
    lines.extend(f"- {item['title']}" for item in digest["unanswered_prompts"])
    return "\n".join(lines)


def _render_digest_section(
    title: str,
    items: list[dict],
    formatter,
) -> str:
    safe_title = html.escape(title)
    if not items:
        return f"<h2>{safe_title}</h2><p>Nothing new.</p>"
    bullet_items = "".join(f"<li>{html.escape(formatter(item))}</li>" for item in items)
    return f"<h2>{safe_title}</h2><ul>{bullet_items}</ul>"
