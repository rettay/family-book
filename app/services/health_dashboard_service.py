"""Health dashboard service — aggregates genetic, medical, and physical data across family."""

from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.access_control import get_accessible_person_ids
from app.models.person import Person, PersonLifecycleState, Visibility


async def get_health_dashboard(db: AsyncSession, current_user: Person) -> dict:
    accessible_ids = await get_accessible_person_ids(db, current_user)
    query = select(Person).where(
        Person.id.in_(accessible_ids),
        Person.is_root.is_(False),
        Person.lifecycle_state == PersonLifecycleState.active.value,
        Person.visibility != Visibility.hidden.value,
    )
    result = await db.execute(query)
    persons = list(result.scalars().all())

    total = len(persons)
    with_genetic = 0
    with_conditions = 0
    with_physical = 0

    condition_persons: dict[str, list[dict]] = {}
    maternal_counter: Counter = Counter()
    paternal_counter: Counter = Counter()
    blood_counter: Counter = Counter()

    for person in persons:
        has_genetic = bool(
            person.maternal_haplogroup
            or person.paternal_haplogroup
            or person.dna_test_provider
            or person.admixture
        )
        has_conditions = bool(person.medical_conditions)
        has_physical = bool(
            person.height
            or person.weight
            or person.eye_color
            or person.hair_color
            or person.blood_type
        )

        if has_genetic:
            with_genetic += 1
        if has_conditions:
            with_conditions += 1
        if has_physical:
            with_physical += 1

        if person.maternal_haplogroup:
            maternal_counter[person.maternal_haplogroup] += 1
        if person.paternal_haplogroup:
            paternal_counter[person.paternal_haplogroup] += 1
        if person.blood_type:
            blood_counter[person.blood_type] += 1

        for mc in person.medical_conditions:
            condition_name = (mc.get("condition") or "").strip()
            if not condition_name:
                continue
            key = condition_name.lower()
            condition_persons.setdefault(key, [])
            condition_persons[key].append({
                "person_id": person.id,
                "display_name": person.display_name,
                "condition_display": condition_name,
            })

    # Shared conditions: appearing in 2+ persons
    shared_conditions = []
    for key, entries in sorted(condition_persons.items()):
        if len(entries) >= 2:
            shared_conditions.append({
                "condition": entries[0]["condition_display"],
                "count": len(entries),
                "persons": [{"id": e["person_id"], "display_name": e["display_name"]} for e in entries],
            })

    return {
        "total_persons": total,
        "with_genetic_profile": with_genetic,
        "with_medical_conditions": with_conditions,
        "with_physical_attributes": with_physical,
        "shared_conditions": shared_conditions,
        "haplogroup_distribution": {
            "maternal": dict(maternal_counter.most_common()),
            "paternal": dict(paternal_counter.most_common()),
        },
        "blood_type_distribution": dict(blood_counter.most_common()),
    }
