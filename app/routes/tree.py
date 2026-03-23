from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import get_accessible_person_ids, get_person_access, redact_person_summary
from app.auth import require_auth
from app.database import get_db
from app.models.person import Person, Visibility
from app.models.preferences import DEFAULT_TREE_PREFERENCES, TreePreference
from app.models.relationships import ParentChild, Partnership
from app.services.geo import country_centroid
from app.schemas import (
    ParentChildResponse,
    PartnershipResponse,
    TreeResponse,
)

router = APIRouter(prefix="/api", tags=["tree"])


class TreePreferencesPayload(BaseModel):
    show_names: bool = DEFAULT_TREE_PREFERENCES["show_names"]
    show_birth_dates: bool = DEFAULT_TREE_PREFERENCES["show_birth_dates"]
    show_country_flags: bool = DEFAULT_TREE_PREFERENCES["show_country_flags"]
    show_photos: bool = DEFAULT_TREE_PREFERENCES["show_photos"]


class MapMarkerPerson(BaseModel):
    id: str
    display_name: str
    photo_url: str | None


class MapMarker(BaseModel):
    person: MapMarkerPerson
    kind: str
    label: str
    place: str | None
    country_code: str
    latitude: float
    longitude: float


class MapResponse(BaseModel):
    markers: list[MapMarker]


async def _get_or_create_tree_preferences(db: AsyncSession, person_id: str) -> TreePreference:
    result = await db.execute(select(TreePreference).where(TreePreference.person_id == person_id))
    preference = result.scalar_one_or_none()
    if preference is None:
        preference = TreePreference(person_id=person_id)
        preference.display_options = DEFAULT_TREE_PREFERENCES
        db.add(preference)
        await db.flush()
    return preference


async def _filtered_tree_people(
    db: AsyncSession,
    current_user: Person,
    *,
    branch: str | None = None,
    residence_country: str | None = None,
    birth_country: str | None = None,
    living: str | None = None,
) -> list[Person]:
    accessible_person_ids = await get_accessible_person_ids(db, current_user)
    query = select(Person).where(
        Person.visibility != Visibility.hidden.value,
        Person.id.in_(accessible_person_ids),
    )
    if branch:
        query = query.where(Person.branch == branch)
    if residence_country:
        query = query.where(Person.residence_country_code == residence_country.upper())
    if birth_country:
        query = query.where(Person.birth_country_code == birth_country.upper())
    if living == "living":
        query = query.where(Person.is_living.is_(True))
    elif living == "deceased":
        query = query.where(Person.is_living.is_(False))

    result = await db.execute(query.order_by(Person.last_name, Person.first_name))
    return result.scalars().all()


@router.get("/tree", response_model=TreeResponse)
async def get_tree(
    branch: str | None = Query(None),
    residence_country: str | None = Query(None),
    birth_country: str | None = Query(None),
    living: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    persons = await _filtered_tree_people(
        db,
        current_user,
        branch=branch,
        residence_country=residence_country,
        birth_country=birth_country,
        living=living,
    )
    visible_person_ids = {person.id for person in persons}

    # Get root person
    result = await db.execute(select(Person).where(Person.is_root.is_(True)))
    root = result.scalar_one_or_none()
    root_id = root.id if root and root.id in visible_person_ids else ""
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


@router.get("/tree/preferences", response_model=TreePreferencesPayload)
async def get_tree_preferences(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    preference = await _get_or_create_tree_preferences(db, current_user.id)
    return TreePreferencesPayload(**preference.display_options)


@router.put("/tree/preferences", response_model=TreePreferencesPayload)
async def update_tree_preferences(
    body: TreePreferencesPayload,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    preference = await _get_or_create_tree_preferences(db, current_user.id)
    preference.display_options = body.model_dump()
    await db.flush()
    return TreePreferencesPayload(**preference.display_options)


@router.get("/map", response_model=MapResponse)
async def get_map_data(
    branch: str | None = Query(None),
    residence_country: str | None = Query(None),
    birth_country: str | None = Query(None),
    living: str | None = Query(None),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    persons = await _filtered_tree_people(
        db,
        current_user,
        branch=branch,
        residence_country=residence_country,
        birth_country=birth_country,
        living=living,
    )
    markers: list[MapMarker] = []

    for person in persons:
        if person.residence_country_code:
            residence_coordinates = country_centroid(person.residence_country_code)
            if residence_coordinates:
                markers.append(
                    MapMarker(
                        person=MapMarkerPerson(
                            id=person.id,
                            display_name=person.display_name,
                            photo_url=person.photo_url,
                        ),
                        kind="residence",
                        label=f"{person.display_name} residence",
                        place=person.residence_place,
                        country_code=person.residence_country_code,
                        latitude=residence_coordinates[0],
                        longitude=residence_coordinates[1],
                    )
                )

        burial_country_code = person.birth_country_code or person.residence_country_code
        if person.burial_place and burial_country_code:
            burial_coordinates = country_centroid(burial_country_code)
            if burial_coordinates:
                markers.append(
                    MapMarker(
                        person=MapMarkerPerson(
                            id=person.id,
                            display_name=person.display_name,
                            photo_url=person.photo_url,
                        ),
                        kind="burial",
                        label=f"{person.display_name} burial",
                        place=person.burial_place,
                        country_code=burial_country_code,
                        latitude=burial_coordinates[0],
                        longitude=burial_coordinates[1],
                    )
                )

    return MapResponse(markers=markers)
