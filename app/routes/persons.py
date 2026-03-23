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
from app.models.person import Person, Visibility
from app.schemas import (
    PersonCreate,
    PersonDetail,
    PersonSummary,
    PersonUpdate,
    person_to_detail,
)
from app.services.audit_service import log_audit

router = APIRouter(prefix="/api/persons", tags=["persons"])


@router.get("", response_model=list[PersonSummary])
async def list_persons(
    search: str | None = Query(None),
    branch: str | None = Query(None),
    country: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    country_filter = country

    query = select(Person).where(Person.visibility != Visibility.hidden.value)

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
    if not person:
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

    await log_audit(db, current_user.id, "create", "person", person.id, new_value={
        "first_name": person.first_name,
        "last_name": person.last_name,
    })

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
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_manage_person(current_user, person):
        raise HTTPException(status_code=403, detail="Not authorized")

    old_data = {"first_name": person.first_name, "last_name": person.last_name}
    update_data = body.model_dump(exclude_unset=True)

    # Handle languages separately
    if "languages" in update_data:
        person.languages = update_data.pop("languages")

    for field, value in update_data.items():
        setattr(person, field, value)

    await db.flush()
    await log_audit(db, current_user.id, "update", "person", person.id,
                    old_value=old_data,
                    new_value={"fields_changed": list(body.model_dump(exclude_unset=True).keys())})

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

    await log_audit(db, current_user.id, "delete", "person", person.id,
                    old_value={"first_name": person.first_name, "last_name": person.last_name})

    await db.delete(person)
    await db.flush()
