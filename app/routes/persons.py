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
from app.models.person import Person, PersonLifecycleState, Visibility
from app.schemas import (
    PersonCreate,
    PersonDetail,
    PersonSummary,
    PersonUpdate,
    person_to_detail,
)
from app.services.audit_service import log_audit
from app.services.revision_service import (
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
    return redact_person_detail(person, access)


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
        bio=body.bio,
        research_notes=body.research_notes,
        medical_history=body.medical_history,
        contact_whatsapp=body.contact_whatsapp,
        contact_telegram=body.contact_telegram,
        contact_signal=body.contact_signal,
        contact_email=body.contact_email,
        branch=body.branch,
        source=body.source,
        created_by=current_user.id,
    )
    person.languages = body.languages
    db.add(person)
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

    # Handle languages separately
    if "languages" in update_data:
        person.languages = update_data.pop("languages")

    for field, value in update_data.items():
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
