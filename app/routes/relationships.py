import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import can_manage_person
from app.auth import require_admin, require_auth
from app.database import get_db
from app.models.person import Person, PersonLifecycleState
from app.models.relationships import ParentChild, Partnership
from app.schemas import (
    ParentChildCreate,
    ParentChildResponse,
    PartnershipCreate,
    PartnershipResponse,
    PartnershipUpdate,
)
from app.services.audit_service import log_audit

router = APIRouter(prefix="/api/relationships", tags=["relationships"])
logger = logging.getLogger(__name__)


async def _would_create_ancestry_cycle(
    db: AsyncSession,
    parent_id: str,
    child_id: str,
) -> bool:
    result = await db.execute(select(ParentChild.parent_id, ParentChild.child_id))
    descendants_by_parent: dict[str, set[str]] = {}
    for existing_parent_id, existing_child_id in result.all():
        descendants_by_parent.setdefault(existing_parent_id, set()).add(existing_child_id)

    stack = [child_id]
    visited: set[str] = set()
    while stack:
        current_id = stack.pop()
        if current_id == parent_id:
            return True
        if current_id in visited:
            continue
        visited.add(current_id)
        stack.extend(descendants_by_parent.get(current_id, ()))

    return False


async def _partnership_exists(
    db: AsyncSession,
    person_a_id: str,
    person_b_id: str,
    kind: str,
    start_date: str | None,
) -> bool:
    query = select(Partnership.id).where(
        Partnership.person_a_id == person_a_id,
        Partnership.person_b_id == person_b_id,
        Partnership.kind == kind,
    )
    if start_date is None:
        query = query.where(Partnership.start_date.is_(None))
    else:
        query = query.where(Partnership.start_date == start_date)

    result = await db.execute(query.limit(1))
    return result.scalar_one_or_none() is not None


async def _require_manageable_person(
    db: AsyncSession,
    current_user: Person,
    person_id: str,
) -> Person:
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person or person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized to relate this person")
    return person


# --- ParentChild ---

@router.post("/parent-child", response_model=ParentChildResponse, status_code=status.HTTP_201_CREATED)
async def create_parent_child(
    body: ParentChildCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if body.parent_id == body.child_id:
        raise HTTPException(status_code=400, detail="Parent and child cannot be the same person")

    for pid in (body.parent_id, body.child_id):
        await _require_manageable_person(db, current_user, pid)

    if await _would_create_ancestry_cycle(db, body.parent_id, body.child_id):
        raise HTTPException(
            status_code=409,
            detail="This parent-child relationship would create an ancestry cycle",
        )

    pc = ParentChild(
        parent_id=body.parent_id,
        child_id=body.child_id,
        kind=body.kind,
        confidence=body.confidence,
        source=body.source,
        source_detail=body.source_detail,
        notes=body.notes,
        start_date=body.start_date,
        end_date=body.end_date,
        created_by=current_user.id,
    )
    db.add(pc)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This parent-child relationship already exists")

    await log_audit(db, current_user.id, "create", "parent_child", pc.id,
                    new_value={"parent_id": pc.parent_id, "child_id": pc.child_id, "kind": pc.kind})
    logger.info("Parent-child relationship %s created by %s", pc.id, current_user.id)

    return ParentChildResponse.model_validate(pc)


@router.delete("/parent-child/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent_child(
    rel_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ParentChild).where(ParentChild.id == rel_id))
    pc = result.scalar_one_or_none()
    if not pc:
        raise HTTPException(status_code=404, detail="Relationship not found")

    await _require_manageable_person(db, current_user, pc.parent_id)
    await _require_manageable_person(db, current_user, pc.child_id)

    await log_audit(db, current_user.id, "delete", "parent_child", pc.id,
                    old_value={"parent_id": pc.parent_id, "child_id": pc.child_id})
    logger.info("Parent-child relationship %s deleted by %s", pc.id, current_user.id)

    await db.delete(pc)
    await db.flush()


# --- Partnership ---

@router.post("/partnership", response_model=PartnershipResponse, status_code=status.HTTP_201_CREATED)
async def create_partnership(
    body: PartnershipCreate,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    if body.person_a_id == body.person_b_id:
        raise HTTPException(status_code=400, detail="Cannot create partnership with self")

    # Enforce canonical ordering
    a_id, b_id = sorted([body.person_a_id, body.person_b_id])

    for pid in (a_id, b_id):
        await _require_manageable_person(db, current_user, pid)

    if await _partnership_exists(db, a_id, b_id, body.kind, body.start_date):
        raise HTTPException(status_code=409, detail="This partnership already exists")

    partnership = Partnership(
        person_a_id=a_id,
        person_b_id=b_id,
        kind=body.kind,
        status=body.status,
        start_date=body.start_date,
        start_date_precision=body.start_date_precision,
        end_date=body.end_date,
        end_date_precision=body.end_date_precision,
        source=body.source,
        notes=body.notes,
        created_by=current_user.id,
    )
    db.add(partnership)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This partnership already exists")

    await log_audit(db, current_user.id, "create", "partnership", partnership.id,
                    new_value={"person_a_id": a_id, "person_b_id": b_id, "kind": body.kind})
    logger.info("Partnership %s created by %s", partnership.id, current_user.id)

    return PartnershipResponse.model_validate(partnership)


@router.put("/partnership/{rel_id}", response_model=PartnershipResponse)
async def update_partnership(
    rel_id: str,
    body: PartnershipUpdate,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Partnership).where(Partnership.id == rel_id))
    partnership = result.scalar_one_or_none()
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")

    old_data = {"status": partnership.status}
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(partnership, field, value)

    await db.flush()
    await log_audit(db, current_user.id, "update", "partnership", partnership.id,
                    old_value=old_data,
                    new_value=update_data)
    logger.info("Partnership %s updated by admin %s", partnership.id, current_user.id)

    return PartnershipResponse.model_validate(partnership)


@router.delete("/partnership/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partnership(
    rel_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Partnership).where(Partnership.id == rel_id))
    partnership = result.scalar_one_or_none()
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")

    await _require_manageable_person(db, current_user, partnership.person_a_id)
    await _require_manageable_person(db, current_user, partnership.person_b_id)

    await log_audit(db, current_user.id, "delete", "partnership", partnership.id,
                    old_value={"person_a_id": partnership.person_a_id,
                               "person_b_id": partnership.person_b_id})
    logger.info("Partnership %s deleted by %s", partnership.id, current_user.id)

    await db.delete(partnership)
    await db.flush()
