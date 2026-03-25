from __future__ import annotations

from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moments import Moment
from app.models.person import Person
from app.models.revisions import EntityRevision
from app.services.field_protection import decrypt_mapping_fields, encrypt_mapping_fields

logger = logging.getLogger(__name__)


PERSON_MUTABLE_FIELDS = [
    "first_name",
    "last_name",
    "patronymic",
    "birth_last_name",
    "nickname",
    "name_display_order",
    "gender",
    "birth_date_raw",
    "birth_date",
    "birth_date_precision",
    "death_date_raw",
    "death_date",
    "death_date_precision",
    "is_living",
    "birth_place",
    "birth_country_code",
    "residence_place",
    "residence_country_code",
    "burial_place",
    "burial_country_code",
    "burial_cemetery_name",
    "burial_plot_number",
    "bio",
    "research_notes",
    "medical_history",
    "contact_whatsapp",
    "contact_telegram",
    "contact_signal",
    "contact_email",
    "photo_url",
    "branch",
    "visibility",
    "lifecycle_state",
    "deleted_at",
    "deleted_by",
]

MOMENT_MUTABLE_FIELDS = [
    "person_id",
    "kind",
    "title",
    "body",
    "milestone_type",
    "source",
    "visibility",
    "posted_by",
    "lifecycle_state",
    "moderated_by",
    "moderation_reason",
    "deleted_by",
]

PERSON_SNAPSHOT_PROTECTED_FIELDS = [
    "medical_history",
    "contact_whatsapp",
    "contact_telegram",
    "contact_signal",
    "contact_email",
]


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def serialize_person_snapshot(person: Person) -> dict:
    snapshot = {field: getattr(person, field) for field in PERSON_MUTABLE_FIELDS}
    snapshot["languages"] = person.languages
    return encrypt_mapping_fields(snapshot, PERSON_SNAPSHOT_PROTECTED_FIELDS)


def apply_person_snapshot(person: Person, snapshot: dict) -> None:
    snapshot = decrypt_mapping_fields(snapshot, PERSON_SNAPSHOT_PROTECTED_FIELDS)
    for field in PERSON_MUTABLE_FIELDS:
        if field in snapshot:
            setattr(person, field, snapshot[field])
    if "languages" in snapshot:
        person.languages = snapshot["languages"] or []


def serialize_moment_snapshot(moment: Moment) -> dict:
    snapshot = {field: getattr(moment, field) for field in MOMENT_MUTABLE_FIELDS}
    snapshot["occurred_at"] = _serialize_datetime(moment.occurred_at)
    snapshot["moderated_at"] = _serialize_datetime(moment.moderated_at)
    snapshot["deleted_at"] = _serialize_datetime(moment.deleted_at)
    snapshot["media_ids"] = moment.media_ids
    snapshot["tagged_person_ids"] = moment.tagged_person_ids
    return snapshot


def apply_moment_snapshot(moment: Moment, snapshot: dict) -> None:
    for field in MOMENT_MUTABLE_FIELDS:
        if field in snapshot:
            setattr(moment, field, snapshot[field])
    moment.occurred_at = _parse_datetime(snapshot.get("occurred_at"))
    moment.moderated_at = _parse_datetime(snapshot.get("moderated_at"))
    moment.deleted_at = _parse_datetime(snapshot.get("deleted_at"))
    moment.media_ids = snapshot.get("media_ids", [])
    moment.tagged_person_ids = snapshot.get("tagged_person_ids", [])


async def record_revision(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: str,
    actor_id: str | None,
    action: str,
    snapshot: dict,
) -> EntityRevision:
    revision = EntityRevision(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        action=action,
    )
    revision.snapshot = snapshot
    db.add(revision)
    await db.flush()
    logger.debug("Recorded revision %s for %s %s", revision.id, entity_type, entity_id)
    return revision


async def list_revisions(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: str,
    limit: int = 20,
) -> list[EntityRevision]:
    result = await db.execute(
        select(EntityRevision)
        .where(
            EntityRevision.entity_type == entity_type,
            EntityRevision.entity_id == entity_id,
        )
        .order_by(EntityRevision.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_revision(
    db: AsyncSession,
    *,
    revision_id: str,
    entity_type: str,
    entity_id: str,
) -> EntityRevision | None:
    result = await db.execute(
        select(EntityRevision).where(
            EntityRevision.id == revision_id,
            EntityRevision.entity_type == entity_type,
            EntityRevision.entity_id == entity_id,
        )
    )
    return result.scalar_one_or_none()
