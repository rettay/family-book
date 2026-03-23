from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import get_accessible_person_ids, get_person_access, redact_person_summary
from app.auth import require_auth
from app.database import get_db
from app.models.person import Person, Visibility
from app.models.relationships import ParentChild, Partnership
from app.schemas import (
    ParentChildResponse,
    PartnershipResponse,
    TreeResponse,
)

router = APIRouter(prefix="/api", tags=["tree"])


@router.get("/tree", response_model=TreeResponse)
async def get_tree(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    accessible_person_ids = await get_accessible_person_ids(db, current_user)

    # Get root person
    result = await db.execute(select(Person).where(Person.is_root.is_(True)))
    root = result.scalar_one_or_none()
    root_id = root.id if root and root.id in accessible_person_ids else ""

    # Get all visible persons
    result = await db.execute(
        select(Person).where(Person.visibility != Visibility.hidden.value)
    )
    persons = [person for person in result.scalars().all() if person.id in accessible_person_ids]
    visible_person_ids = {person.id for person in persons}
    summaries = [
        redact_person_summary(person, await get_person_access(db, current_user, person))
        for person in persons
    ]

    # Get all parent-child relationships
    result = await db.execute(select(ParentChild))
    parent_children = [
        relationship
        for relationship in result.scalars().all()
        if relationship.parent_id in visible_person_ids
        and relationship.child_id in visible_person_ids
    ]

    # Get all partnerships
    result = await db.execute(select(Partnership))
    partnerships = [
        relationship
        for relationship in result.scalars().all()
        if relationship.person_a_id in visible_person_ids
        and relationship.person_b_id in visible_person_ids
    ]

    return TreeResponse(
        root_id=root_id,
        persons=summaries,
        parent_child=[ParentChildResponse.model_validate(pc) for pc in parent_children],
        partnerships=[PartnershipResponse.model_validate(p) for p in partnerships],
    )
