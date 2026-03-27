from __future__ import annotations

import json
from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person
from app.models.revisions import EntityRevision
from app.services.field_protection import decrypt_mapping_fields, decrypt_string, encrypt_mapping_fields, encrypt_string
from app.services.sanitization import RICH_TEXT_FIELDS, sanitize_html

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
    "obituary",
    "obituary_source",
    "contact_whatsapp",
    "contact_telegram",
    "contact_signal",
    "contact_email",
    "height",
    "weight",
    "eye_color",
    "hair_color",
    "blood_type",
    "maternal_haplogroup",
    "paternal_haplogroup",
    "dna_test_provider",
    "source_detail",
    "confidence",
    "photo_url",
    "branch",
    "visibility",
    "lifecycle_state",
    "deleted_at",
    "deleted_by",
]

PERSON_SNAPSHOT_PROTECTED_FIELDS = [
    "medical_history",
    "contact_whatsapp",
    "contact_telegram",
    "contact_signal",
    "contact_email",
    "maternal_haplogroup",
    "paternal_haplogroup",
    "dna_test_provider",
]

PERSON_SNAPSHOT_PROTECTED_JSON_FIELDS = [
    "admixture",
    "medical_conditions",
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
    snapshot["education"] = person.education
    snapshot["career"] = person.career
    snapshot["organizations"] = person.organizations
    snapshot["admixture"] = person.admixture
    snapshot["medical_conditions"] = person.medical_conditions
    snapshot = encrypt_mapping_fields(snapshot, PERSON_SNAPSHOT_PROTECTED_FIELDS)
    for field in PERSON_SNAPSHOT_PROTECTED_JSON_FIELDS:
        if field in snapshot and snapshot[field] is not None:
            snapshot[field] = encrypt_string(json.dumps(snapshot[field]))
    return snapshot


def apply_person_snapshot(person: Person, snapshot: dict) -> None:
    snapshot = decrypt_mapping_fields(snapshot, PERSON_SNAPSHOT_PROTECTED_FIELDS)
    for field in PERSON_SNAPSHOT_PROTECTED_JSON_FIELDS:
        if field in snapshot and isinstance(snapshot[field], str):
            decrypted = decrypt_string(snapshot[field])
            snapshot[field] = json.loads(decrypted) if decrypted else []
    for field in PERSON_MUTABLE_FIELDS:
        if field in snapshot:
            value = snapshot[field]
            if field in RICH_TEXT_FIELDS and value:
                value = sanitize_html(value)
            setattr(person, field, value)
    if "languages" in snapshot:
        person.languages = snapshot["languages"] or []
    if "education" in snapshot:
        person.education = snapshot["education"] or []
    if "career" in snapshot:
        person.career = snapshot["career"] or []
    if "organizations" in snapshot:
        person.organizations = snapshot["organizations"] or []
    if "admixture" in snapshot:
        person.admixture = snapshot["admixture"] or []
    if "medical_conditions" in snapshot:
        person.medical_conditions = snapshot["medical_conditions"] or []


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
