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
from app.services.field_protection import decrypt_string
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
    person = Person(
        first_name=body.first_name,
        last_name=body.last_name,
        patronymic=body.patronymic,
        birth_last_name=body.birth_last_name,
        nickname=body.nickname,
        name_display_order=body.name_display_order,
        gender=body.gender,
        birth_date_raw=body.birth_date_raw,
        birth_date=body.birth_date,
        birth_date_precision=body.birth_date_precision,
        death_date_raw=body.death_date_raw,
        death_date=body.death_date,
        death_date_precision=body.death_date_precision,
        is_living=body.is_living,
        birth_place=body.birth_place,
        birth_country_code=body.birth_country_code,
        residence_place=body.residence_place,
        residence_country_code=body.residence_country_code,
        burial_place=body.burial_place,
        burial_country_code=body.burial_country_code,
        burial_cemetery_name=body.burial_cemetery_name,
        burial_plot_number=body.burial_plot_number,
        bio=sanitize_html(body.bio) if body.bio else body.bio,
        research_notes=sanitize_html(body.research_notes) if body.research_notes else body.research_notes,
        medical_history=body.medical_history,
        contact_whatsapp=body.contact_whatsapp,
        contact_telegram=body.contact_telegram,
        contact_signal=body.contact_signal,
        contact_email=body.contact_email,
        obituary=sanitize_html(body.obituary) if body.obituary else body.obituary,
        obituary_source=body.obituary_source,
        height=body.height,
        weight=body.weight,
        eye_color=body.eye_color,
        hair_color=body.hair_color,
        blood_type=body.blood_type,
        maternal_haplogroup=body.maternal_haplogroup,
        paternal_haplogroup=body.paternal_haplogroup,
        dna_test_provider=body.dna_test_provider,
        source_detail=body.source_detail,
        confidence=body.confidence,
        branch=body.branch,
        source=body.source,
        created_by=current_user.id,
    )
    person.languages = body.languages
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
    update_data = body.model_dump(exclude_unset=True)

    # Handle JSON array fields separately, stripping None values per entry
    def _strip_none_entries(entries: list | None) -> list[dict]:
        if not entries:
            return []
        return [{k: v for k, v in e.items() if v is not None} if isinstance(e, dict) else e for e in entries]

    if "languages" in update_data:
        person.languages = update_data.pop("languages") or []
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

    for field, value in update_data.items():
        if field in RICH_TEXT_FIELDS and value:
            value = sanitize_html(value)
        setattr(person, field, value)

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
