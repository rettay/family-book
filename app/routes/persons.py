import json
import logging

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import (
    can_manage_person,
    get_accessible_person_ids,
    get_person_access,
    redact_person_detail,
    redact_person_summary,
)
from app.auth import require_admin, require_auth
from app.database import get_db
from app.models.media import Media
from app.models.person import Person, PersonLifecycleState, Visibility
from app.schemas import (
    PersonCreate,
    PersonDetail,
    PersonSummary,
    PersonUpdate,
    person_to_detail,
)
from app.services.audit_service import log_audit
from app.services.date_parsing import parse_date_raw_to_iso
from app.services.field_protection import decrypt_string
from app.services.location_service import resolve_location
from app.services.sanitization import RICH_TEXT_FIELDS, sanitize_html
from app.services.revision_service import (
    PERSON_SNAPSHOT_PROTECTED_JSON_FIELDS,
    apply_person_snapshot,
    get_revision,
    list_revisions,
    record_revision,
    serialize_person_snapshot,
)

router = APIRouter(prefix="/api/persons", tags=["persons"])
logger = logging.getLogger(__name__)


LOCATION_PREFIXES = ("birth", "residence", "burial")


def _enforce_single_primary(entries: list[dict]) -> list[dict]:
    """Ensure at most one entry has is_primary=True. Last one wins; if none, first gets it."""
    if not entries:
        return entries
    primary_indices = [i for i, e in enumerate(entries) if e.get("is_primary")]
    if len(primary_indices) > 1:
        for i in primary_indices[:-1]:
            entries[i]["is_primary"] = False
    elif not primary_indices and entries:
        entries[0]["is_primary"] = True
    return entries


async def _normalize_location_fields(
    payload: dict,
    *,
    person: Person | None = None,
) -> dict:
    normalized = dict(payload)
    for prefix in LOCATION_PREFIXES:
        place_key = f"{prefix}_place"
        country_key = f"{prefix}_country_code"
        latitude_key = f"{prefix}_place_latitude"
        longitude_key = f"{prefix}_place_longitude"

        if person is None:
            current_place = normalized.get(place_key)
            current_country = normalized.get(country_key)
            current_latitude = normalized.get(latitude_key)
            current_longitude = normalized.get(longitude_key)
        else:
            fields_present = any(
                key in normalized
                for key in (place_key, country_key, latitude_key, longitude_key)
            )
            if not fields_present:
                continue
            current_place = normalized.get(place_key, getattr(person, place_key))
            current_country = normalized.get(country_key, getattr(person, country_key))
            current_latitude = normalized.get(latitude_key, getattr(person, latitude_key))
            current_longitude = normalized.get(longitude_key, getattr(person, longitude_key))

        resolved = await resolve_location(
            place=current_place,
            country_code=current_country,
            latitude=current_latitude,
            longitude=current_longitude,
        )
        normalized[place_key] = resolved.place
        normalized[country_key] = resolved.country_code
        normalized[latitude_key] = resolved.latitude
        normalized[longitude_key] = resolved.longitude
    if "contact_addresses" in normalized:
        normalized["contact_addresses"] = await _normalize_contact_addresses(
            normalized.get("contact_addresses") or []
        )
    normalized = _normalize_memorial_fields(normalized, person=person)
    return normalized


def _normalize_memorial_fields(payload: dict, *, person: Person | None = None) -> dict:
    normalized = dict(payload)
    is_living = normalized.get("is_living", person.is_living if person is not None else True)
    remains_disposition = normalized.get(
        "remains_disposition",
        person.remains_disposition if person is not None else None,
    )

    if is_living:
        normalized["remains_disposition"] = None
        normalized["burial_place"] = None
        normalized["burial_country_code"] = None
        normalized["burial_place_latitude"] = None
        normalized["burial_place_longitude"] = None
        normalized["burial_cemetery_name"] = None
        normalized["burial_plot_number"] = None
        return normalized

    if remains_disposition == "cremated":
        normalized["burial_cemetery_name"] = None
        normalized["burial_plot_number"] = None

    return normalized


async def _normalize_contact_addresses(entries: list[dict]) -> list[dict]:
    normalized_entries: list[dict] = []
    for entry in entries:
        # Use line1 or legacy place field for location resolution
        place = entry.get("place") or entry.get("line1")
        country_code = entry.get("country_code")
        latitude = entry.get("latitude")
        longitude = entry.get("longitude")
        resolved = await resolve_location(
            place=place,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
        )
        # Preserve all structured fields, update resolved location fields
        normalized_entry = dict(entry)
        normalized_entry["place"] = resolved.place
        normalized_entry["country_code"] = resolved.country_code
        normalized_entry["latitude"] = resolved.latitude
        normalized_entry["longitude"] = resolved.longitude
        # Auto-compute is_partial when coordinates are missing
        if not resolved.latitude and not resolved.longitude:
            normalized_entry["is_partial"] = True
        normalized_entries.append(
            {key: value for key, value in normalized_entry.items() if value not in (None, "")}
        )
    return normalized_entries


async def _person_history_entries(
    db: AsyncSession,
    *,
    person_id: str,
    limit: int = 20,
) -> list[dict]:
    revisions = await list_revisions(db, entity_type="person", entity_id=person_id, limit=limit)
    actor_ids = {revision.actor_id for revision in revisions if revision.actor_id}
    actors_by_id: dict[str, Person] = {}
    if actor_ids:
        result = await db.execute(select(Person).where(Person.id.in_(actor_ids)))
        actors_by_id = {actor.id: actor for actor in result.scalars().all()}

    entries: list[dict] = []
    for revision in revisions:
        actor = actors_by_id.get(revision.actor_id or "")
        snapshot = revision.snapshot
        # Decrypt protected JSON array fields before serving
        for field in PERSON_SNAPSHOT_PROTECTED_JSON_FIELDS:
            raw = snapshot.get(field)
            if isinstance(raw, str):
                decrypted = decrypt_string(raw)
                snapshot[field] = json.loads(decrypted) if decrypted else []
        entries.append(
            {
                "id": revision.id,
                "action": revision.action,
                "actor_id": revision.actor_id,
                "actor_name": actor.display_name if actor else "Unknown",
                "created_at": revision.created_at.isoformat() if revision.created_at else None,
                "snapshot": {
                    "display_name": f"{snapshot.get('first_name', '')} {snapshot.get('last_name', '')}".strip(),
                    "bio": snapshot.get("bio"),
                    "branch": snapshot.get("branch"),
                    "lifecycle_state": snapshot.get("lifecycle_state"),
                    "obituary": snapshot.get("obituary"),
                    "obituary_source": snapshot.get("obituary_source"),
                    "education": snapshot.get("education", []),
                    "career": snapshot.get("career", []),
                    "organizations": snapshot.get("organizations", []),
                    "height": snapshot.get("height"),
                    "weight": snapshot.get("weight"),
                    "eye_color": snapshot.get("eye_color"),
                    "hair_color": snapshot.get("hair_color"),
                    "blood_type": snapshot.get("blood_type"),
                    "admixture": snapshot.get("admixture", []),
                    "medical_conditions": snapshot.get("medical_conditions", []),
                    "source_detail": snapshot.get("source_detail"),
                    "confidence": snapshot.get("confidence"),
                    "place_history": snapshot.get("place_history", []),
                },
            }
        )
    return entries


@router.get("", response_model=list[PersonSummary])
async def list_persons(
    search: str | None = Query(None),
    branch: str | None = Query(None),
    country: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("Person list requested by %s", current_user.id)
    country_filter = country

    query = select(Person).where(
        Person.visibility != Visibility.hidden.value,
        Person.lifecycle_state == PersonLifecycleState.active.value,
    )

    if search:
        query = query.where(Person.is_root.is_(False))
        like = f"%{search}%"
        query = query.where(
            (Person.first_name.ilike(like))
            | (Person.last_name.ilike(like))
            | (Person.nickname.ilike(like))
        )
    if branch:
        query = query.where(Person.branch == branch)
    if country_filter:
        query = query.where(Person.residence_country_code == country_filter)

    query = query.order_by(Person.last_name, Person.first_name)
    result = await db.execute(query)
    persons = result.scalars().all()
    accessible_ids = await get_accessible_person_ids(db, current_user)
    summaries: list[PersonSummary] = []
    for person in persons:
        if person.id not in accessible_ids:
            continue
        access = await get_person_access(db, current_user, person)
        if access.can_view:
            summaries.append(redact_person_summary(person, access))
    return summaries


@router.get("/completeness")
async def get_completeness(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    accessible_ids = await get_accessible_person_ids(db, current_user)
    query = select(Person).where(
        Person.id.in_(accessible_ids),
        Person.is_root.is_(False),
        Person.lifecycle_state == PersonLifecycleState.active.value,
        Person.visibility != Visibility.hidden.value,
    )
    result = await db.execute(query)
    persons = result.scalars().all()

    person_ids = [p.id for p in persons]

    # Count persons who have at least one media
    persons_with_media = set()
    if person_ids:
        media_rows = await db.execute(
            select(Media.person_id).where(
                Media.person_id.in_(person_ids),
            ).group_by(Media.person_id)
        )
        persons_with_media = {row[0] for row in media_rows.all()}

    gaps = {
        "no_birth_date": 0,
        "no_photo": 0,
        "no_bio": 0,
        "no_birth_place": 0,
        "no_gender": 0,
        "no_media": 0,
    }
    for person in persons:
        if not person.birth_date_raw:
            gaps["no_birth_date"] += 1
        if not person.photo_url:
            gaps["no_photo"] += 1
        if not person.bio:
            gaps["no_bio"] += 1
        if not person.birth_place:
            gaps["no_birth_place"] += 1
        if not person.gender:
            gaps["no_gender"] += 1
        if person.id not in persons_with_media:
            gaps["no_media"] += 1

    return {"total_persons": len(persons), "gaps": gaps}


@router.get("/{person_id}", response_model=PersonDetail)
async def get_person(
    person_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=404, detail="Person not found")
    access = await get_person_access(db, current_user, person)
    if not access.can_view:
        raise HTTPException(status_code=403, detail="Not visible")
    detail = redact_person_detail(person, access)
    detail_dict = detail.model_dump()
    from app.services.date_intelligence_service import enrich_person_ages
    enrich_person_ages(detail_dict)
    return PersonDetail(**detail_dict)


@router.post("", response_model=PersonDetail, status_code=status.HTTP_201_CREATED)
async def create_person(
    body: PersonCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    payload = await _normalize_location_fields(body.model_dump())
    person = Person(
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        patronymic=payload.get("patronymic"),
        birth_last_name=payload.get("birth_last_name"),
        nickname=payload.get("nickname"),
        name_display_order=payload.get("name_display_order") or "western",
        gender=payload.get("gender"),
        birth_date_raw=payload.get("birth_date_raw"),
        birth_date=payload.get("birth_date"),
        birth_date_precision=payload.get("birth_date_precision"),
        death_date_raw=payload.get("death_date_raw"),
        death_date=payload.get("death_date"),
        death_date_precision=payload.get("death_date_precision"),
        is_living=payload.get("is_living", True),
        birth_place=payload.get("birth_place"),
        birth_country_code=payload.get("birth_country_code"),
        birth_place_latitude=payload.get("birth_place_latitude"),
        birth_place_longitude=payload.get("birth_place_longitude"),
        residence_place=payload.get("residence_place"),
        residence_country_code=payload.get("residence_country_code"),
        residence_place_latitude=payload.get("residence_place_latitude"),
        residence_place_longitude=payload.get("residence_place_longitude"),
        burial_place=payload.get("burial_place"),
        burial_country_code=payload.get("burial_country_code"),
        burial_place_latitude=payload.get("burial_place_latitude"),
        burial_place_longitude=payload.get("burial_place_longitude"),
        burial_cemetery_name=payload.get("burial_cemetery_name"),
        burial_plot_number=payload.get("burial_plot_number"),
        remains_disposition=payload.get("remains_disposition"),
        bio=sanitize_html(payload.get("bio")) if payload.get("bio") else payload.get("bio"),
        research_notes=sanitize_html(payload.get("research_notes"))
        if payload.get("research_notes")
        else payload.get("research_notes"),
        medical_history=payload.get("medical_history"),
        contact_whatsapp=payload.get("contact_whatsapp"),
        contact_telegram=payload.get("contact_telegram"),
        contact_signal=payload.get("contact_signal"),
        contact_phone=payload.get("contact_phone"),
        contact_email=payload.get("contact_email"),
        obituary=sanitize_html(payload.get("obituary"))
        if payload.get("obituary")
        else payload.get("obituary"),
        obituary_source=payload.get("obituary_source"),
        height=payload.get("height"),
        weight=payload.get("weight"),
        eye_color=payload.get("eye_color"),
        hair_color=payload.get("hair_color"),
        blood_type=payload.get("blood_type"),
        maternal_haplogroup=payload.get("maternal_haplogroup"),
        paternal_haplogroup=payload.get("paternal_haplogroup"),
        dna_test_provider=payload.get("dna_test_provider"),
        source_detail=payload.get("source_detail"),
        confidence=payload.get("confidence"),
        social_instagram=payload.get("social_instagram"),
        social_facebook=payload.get("social_facebook"),
        social_twitter=payload.get("social_twitter"),
        social_linkedin=payload.get("social_linkedin"),
        social_tiktok=payload.get("social_tiktok"),
        social_youtube=payload.get("social_youtube"),
        branch=payload.get("branch"),
        source=payload.get("source") or "manual",
        created_by=current_user.id,
    )
    # Auto-parse raw dates to ISO if ISO not explicitly provided
    if person.birth_date_raw and not person.birth_date:
        iso, prec = parse_date_raw_to_iso(person.birth_date_raw)
        if iso:
            person.birth_date = iso
            person.birth_date_precision = prec
    if person.death_date_raw and not person.death_date:
        iso, prec = parse_date_raw_to_iso(person.death_date_raw)
        if iso:
            person.death_date = iso
            person.death_date_precision = prec

    person.languages = body.languages
    person.alternate_nicknames = [nickname for nickname in body.alternate_nicknames if nickname]
    person.contact_addresses = _enforce_single_primary(payload.get("contact_addresses") or [])
    person.contact_phones = _enforce_single_primary(payload.get("contact_phones") or [])
    person.contact_emails = _enforce_single_primary(payload.get("contact_emails") or [])
    person.social_accounts = payload.get("social_accounts") or []
    person.name_history = payload.get("name_history") or []
    person.place_history = [e.model_dump(exclude_none=True) for e in body.place_history]
    person.obituary_url = payload.get("obituary_url")
    person.education = [e.model_dump(exclude_none=True) for e in body.education]
    person.career = [e.model_dump(exclude_none=True) for e in body.career]
    person.organizations = [e.model_dump(exclude_none=True) for e in body.organizations]
    person.admixture = [e.model_dump(exclude_none=True) for e in body.admixture]
    person.medical_conditions = [e.model_dump(exclude_none=True) for e in body.medical_conditions]
    db.add(person)
    await db.flush()
    from app.services.wiki_service import generate_slug
    person.slug = generate_slug(body.first_name, body.last_name, person.id)
    await db.flush()

    snapshot = serialize_person_snapshot(person)
    await record_revision(
        db,
        entity_type="person",
        entity_id=person.id,
        actor_id=current_user.id,
        action="create",
        snapshot=snapshot,
    )
    await log_audit(db, current_user.id, "create", "person", person.id, new_value={
        "first_name": person.first_name,
        "last_name": person.last_name,
    })
    logger.info("Person %s created by %s", person.id, current_user.id)

    return person_to_detail(person)


@router.put("/{person_id}", response_model=PersonDetail)
async def update_person(
    person_id: str,
    body: PersonUpdate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized")

    old_snapshot = serialize_person_snapshot(person)
    update_data = await _normalize_location_fields(
        body.model_dump(exclude_unset=True),
        person=person,
    )

    # Handle JSON array fields separately, stripping None values per entry
    def _strip_none_entries(entries: list | None) -> list[dict]:
        if not entries:
            return []
        return [{k: v for k, v in e.items() if v is not None} if isinstance(e, dict) else e for e in entries]

    if "languages" in update_data:
        person.languages = update_data.pop("languages") or []
    if "alternate_nicknames" in update_data:
        person.alternate_nicknames = [
            nickname for nickname in (update_data.pop("alternate_nicknames") or []) if nickname
        ]
    if "contact_addresses" in update_data:
        person.contact_addresses = _enforce_single_primary(_strip_none_entries(update_data.pop("contact_addresses")))
    if "education" in update_data:
        person.education = _strip_none_entries(update_data.pop("education"))
    if "career" in update_data:
        person.career = _strip_none_entries(update_data.pop("career"))
    if "organizations" in update_data:
        person.organizations = _strip_none_entries(update_data.pop("organizations"))
    if "admixture" in update_data:
        person.admixture = _strip_none_entries(update_data.pop("admixture"))
    if "medical_conditions" in update_data:
        person.medical_conditions = _strip_none_entries(update_data.pop("medical_conditions"))
    if "contact_phones" in update_data:
        person.contact_phones = _enforce_single_primary(_strip_none_entries(update_data.pop("contact_phones")))
    if "contact_emails" in update_data:
        person.contact_emails = _enforce_single_primary(_strip_none_entries(update_data.pop("contact_emails")))
    if "social_accounts" in update_data:
        person.social_accounts = _strip_none_entries(update_data.pop("social_accounts"))
    if "name_history" in update_data:
        person.name_history = _strip_none_entries(update_data.pop("name_history"))
    if "place_history" in update_data:
        person.place_history = _strip_none_entries(update_data.pop("place_history"))

    for field, value in update_data.items():
        if field in RICH_TEXT_FIELDS and value:
            value = sanitize_html(value)
        setattr(person, field, value)

    # Auto-parse raw dates to ISO if raw was set but ISO wasn't in this update
    if "birth_date_raw" in update_data and "birth_date" not in update_data:
        if person.birth_date_raw:
            iso, prec = parse_date_raw_to_iso(person.birth_date_raw)
            if iso:
                person.birth_date = iso
                person.birth_date_precision = prec
        else:
            person.birth_date = None
            person.birth_date_precision = None
    if "death_date_raw" in update_data and "death_date" not in update_data:
        if person.death_date_raw:
            iso, prec = parse_date_raw_to_iso(person.death_date_raw)
            if iso:
                person.death_date = iso
                person.death_date_precision = prec
        else:
            person.death_date = None
            person.death_date_precision = None

    # DOD-after-DOB validation
    if person.birth_date and person.death_date:
        try:
            if person.death_date < person.birth_date:
                raise HTTPException(
                    status_code=422,
                    detail="Death date must be on or after birth date",
                )
        except TypeError:
            pass  # non-comparable date strings — skip validation

    await db.flush()
    await record_revision(
        db,
        entity_type="person",
        entity_id=person.id,
        actor_id=current_user.id,
        action="update",
        snapshot=serialize_person_snapshot(person),
    )
    await log_audit(db, current_user.id, "update", "person", person.id,
                    old_value=old_snapshot,
                    new_value={"fields_changed": list(body.model_dump(exclude_unset=True).keys())})
    logger.info("Person %s updated by %s", person.id, current_user.id)
    await db.commit()
    await db.refresh(person)

    access = await get_person_access(db, current_user, person)
    return redact_person_detail(person, access)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.is_root:
        raise HTTPException(status_code=403, detail="Cannot delete root person")
    if person.lifecycle_state == PersonLifecycleState.deleted.value:
        return

    person.lifecycle_state = PersonLifecycleState.deleted.value
    person.deleted_at = datetime.now(timezone.utc).isoformat()
    person.deleted_by = current_user.id
    await record_revision(
        db,
        entity_type="person",
        entity_id=person.id,
        actor_id=current_user.id,
        action="delete",
        snapshot=serialize_person_snapshot(person),
    )
    await log_audit(db, current_user.id, "delete", "person", person.id,
                    old_value={"first_name": person.first_name, "last_name": person.last_name})
    logger.info("Person %s soft-deleted by %s", person.id, current_user.id)
    await db.flush()


@router.get("/{person_id}/history")
async def get_person_history(
    person_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state == PersonLifecycleState.deleted.value:
        if not current_user.is_admin:
            raise HTTPException(status_code=404, detail="Person not found")
    else:
        access = await get_person_access(db, current_user, person)
        if not access.can_view:
            raise HTTPException(status_code=403, detail="Not visible")

    return await _person_history_entries(db, person_id=person_id)


@router.post("/{person_id}/history/{revision_id}/revert")
async def revert_person_revision(
    person_id: str,
    revision_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    revision = await get_revision(
        db, revision_id=revision_id, entity_type="person", entity_id=person_id
    )
    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    apply_person_snapshot(person, revision.snapshot)
    await db.flush()
    await record_revision(
        db,
        entity_type="person",
        entity_id=person.id,
        actor_id=current_user.id,
        action="revert",
        snapshot=serialize_person_snapshot(person),
    )
    await log_audit(
        db,
        current_user.id,
        "update",
        "person",
        person.id,
        new_value={"reverted_to_revision_id": revision.id},
    )
    logger.info("Person %s reverted to revision %s by %s", person.id, revision.id, current_user.id)

    if person.lifecycle_state != PersonLifecycleState.active.value:
        return {"ok": True, "lifecycle_state": person.lifecycle_state}

    access = await get_person_access(db, current_user, person)
    return {
        "ok": True,
        "lifecycle_state": person.lifecycle_state,
        "person": redact_person_detail(person, access).model_dump(mode="json"),
    }
