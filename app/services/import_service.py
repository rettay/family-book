"""GEDCOM import orchestration service."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.gedcom_parser import (
    GedcomIndividual,
    GedcomParseResult,
    _parse_date_to_raw_and_iso,
)
from app.models.imports import GedcomImportBatch
from app.models.person import Person, PersonSource
from app.models.relationships import (
    ParentChild,
    ParentChildKind,
    Partnership,
    PartnershipKind,
    RelationshipSource,
)
from app.services.audit_service import log_audit
from app.services.revision_service import record_revision, serialize_person_snapshot

logger = logging.getLogger(__name__)


UNSUPPORTED_GEDCOM_TAG_MESSAGES = {
    "SOUR": "Source citations were detected but are not imported yet.",
    "OBJE": "Embedded media references were detected but are not imported yet.",
    "REPO": "Repository records were detected but are not imported yet.",
    "ALIA": "Alias records were detected but are not imported yet.",
    "_UID": "Custom identifier tags were detected but are not imported yet.",
}


@dataclass
class DuplicateCandidate:
    existing_person_id: str
    existing_name: str
    gedcom_xref: str
    gedcom_name: str
    match_reason: str


@dataclass
class ImportResult:
    persons_created: int = 0
    relationships_created: int = 0
    duplicates_skipped: int = 0
    duplicate_candidates: list[DuplicateCandidate] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    xref_to_person_id: dict[str, str] = field(default_factory=dict)
    created_person_ids: list[str] = field(default_factory=list)


async def find_duplicates(
    db: AsyncSession,
    individuals: list[GedcomIndividual],
) -> dict[str, DuplicateCandidate]:
    """Check for potential duplicates by name + birth date match."""
    result = await db.execute(
        select(Person).where(
            Person.lifecycle_state == "active",
        )
    )
    existing_persons = result.scalars().all()

    # Build lookup by normalized name
    existing_by_name: dict[str, list[Person]] = {}
    for p in existing_persons:
        key = f"{(p.first_name or '').strip().lower()} {(p.last_name or '').strip().lower()}"
        existing_by_name.setdefault(key, []).append(p)

    duplicates: dict[str, DuplicateCandidate] = {}
    for indi in individuals:
        key = f"{indi.first_name.strip().lower()} {indi.last_name.strip().lower()}"
        if key in existing_by_name:
            for existing in existing_by_name[key]:
                # Name matches — check birth date if available
                reason = "name match"
                if indi.birth and indi.birth.date and existing.birth_date_raw:
                    if indi.birth.date.strip().lower() in existing.birth_date_raw.strip().lower():
                        reason = "name + birth date match"
                    else:
                        continue  # Different birth dates, probably not a duplicate
                duplicates[indi.xref] = DuplicateCandidate(
                    existing_person_id=existing.id,
                    existing_name=existing.display_name,
                    gedcom_xref=indi.xref,
                    gedcom_name=f"{indi.first_name} {indi.last_name}",
                    match_reason=reason,
                )
                break  # Only flag the first match

    return duplicates


def detect_unsupported_gedcom_items(content: bytes) -> list[str]:
    text = content.decode("utf-8", errors="ignore")
    found_messages: list[str] = []
    for tag, message in UNSUPPORTED_GEDCOM_TAG_MESSAGES.items():
        if re.search(rf"(^|\n)\d+\s+{re.escape(tag)}\b", text):
            found_messages.append(message)
    return found_messages


def build_gedcom_import_summary(
    *,
    parsed: GedcomParseResult,
    result: ImportResult,
    unsupported_items: list[str] | None = None,
) -> dict:
    linked_xrefs = set()
    for family in parsed.families:
        if family.husband_xref:
            linked_xrefs.add(family.husband_xref)
        if family.wife_xref:
            linked_xrefs.add(family.wife_xref)
        linked_xrefs.update(family.children_xrefs)

    missing_key_dates = 0
    unknown_names = 0
    unlinked_people = 0
    for individual in parsed.individuals:
        if not ((individual.birth and individual.birth.date) or (individual.death and individual.death.date)):
            missing_key_dates += 1
        if not individual.first_name or individual.first_name.strip().lower() == "unknown":
            unknown_names += 1
        if individual.xref not in linked_xrefs:
            unlinked_people += 1

    return {
        "individuals_count": len(parsed.individuals),
        "families_count": len(parsed.families),
        "persons_created": result.persons_created,
        "relationships_created": result.relationships_created,
        "duplicates_skipped": result.duplicates_skipped,
        "duplicate_candidates": [
            {
                "existing_person_id": candidate.existing_person_id,
                "existing_name": candidate.existing_name,
                "gedcom_xref": candidate.gedcom_xref,
                "gedcom_name": candidate.gedcom_name,
                "match_reason": candidate.match_reason,
            }
            for candidate in result.duplicate_candidates
        ],
        "errors": result.errors,
        "unsupported_items": unsupported_items or [],
        "checklist": {
            "missing_key_dates": missing_key_dates,
            "unknown_names": unknown_names,
            "unlinked_people": unlinked_people,
            "duplicate_candidates": len(result.duplicate_candidates),
        },
        "created_person_ids": result.created_person_ids,
    }


async def import_gedcom(
    db: AsyncSession,
    parsed: GedcomParseResult,
    actor_id: str,
    skip_duplicates: bool = True,
    skip_duplicate_xrefs: set[str] | None = None,
    batch_id: str | None = None,
) -> ImportResult:
    """Import parsed GEDCOM data into the database.

    Args:
        db: Database session.
        parsed: Parsed GEDCOM result from gedcom_parser.
        actor_id: ID of the user performing the import.
        skip_duplicates: If True, skip individuals that match existing persons.

    Returns:
        ImportResult with counts and mappings.
    """
    result = ImportResult()

    # Find duplicates first
    duplicates = await find_duplicates(db, parsed.individuals)
    result.duplicate_candidates = list(duplicates.values())
    skip_duplicate_xrefs = skip_duplicate_xrefs or set()

    # Create persons from INDI records
    for indi in parsed.individuals:
        if indi.xref in duplicates:
            if skip_duplicates or indi.xref in skip_duplicate_xrefs:
                result.duplicates_skipped += 1
                # Map to existing person so relationships still work
                result.xref_to_person_id[indi.xref] = duplicates[indi.xref].existing_person_id
                continue

        birth_raw, birth_iso, birth_precision = ("", None, None)
        death_raw, death_iso, death_precision = ("", None, None)
        birth_place = ""
        burial_place = ""
        is_living = True

        if indi.birth:
            birth_raw, birth_iso, birth_precision = _parse_date_to_raw_and_iso(indi.birth.date)
            birth_place = indi.birth.place

        if indi.death:
            death_raw, death_iso, death_precision = _parse_date_to_raw_and_iso(indi.death.date)
            is_living = False

        if indi.burial:
            burial_place = indi.burial.place
            is_living = False

        person = Person(
            first_name=indi.first_name or "Unknown",
            last_name=indi.last_name or "",
            birth_last_name=indi.maiden_name or None,
            gender=indi.gender or None,
            birth_date_raw=birth_raw or None,
            birth_date=birth_iso,
            birth_date_precision=birth_precision,
            death_date_raw=death_raw or None,
            death_date=death_iso,
            death_date_precision=death_precision,
            is_living=is_living,
            birth_place=birth_place or None,
            burial_place=burial_place or None,
            bio=None,
            research_notes=indi.note or None,
            source=PersonSource.gedcom_import.value,
            created_by=actor_id,
        )
        db.add(person)
        await db.flush()

        result.xref_to_person_id[indi.xref] = person.id
        result.persons_created += 1
        result.created_person_ids.append(person.id)

        snapshot = serialize_person_snapshot(person)
        await record_revision(
            db,
            entity_type="person",
            entity_id=person.id,
            actor_id=actor_id,
            action="create",
            snapshot=snapshot,
        )

    # Build set of duplicate person IDs to avoid re-creating their relationships
    existing_person_ids = {d.existing_person_id for d in result.duplicate_candidates}

    # Create relationships from FAM records
    for fam in parsed.families:
        husb_id = result.xref_to_person_id.get(fam.husband_xref)
        wife_id = result.xref_to_person_id.get(fam.wife_xref)

        # Create partnership (skip if both partners already existed)
        if husb_id and wife_id:
            if husb_id in existing_person_ids and wife_id in existing_person_ids:
                pass  # Both already exist — relationship likely already exists
            else:
                # Ensure canonical order (person_a_id < person_b_id)
                a_id, b_id = (husb_id, wife_id) if husb_id < wife_id else (wife_id, husb_id)

                marriage_date = None
                marriage_precision = None
                if fam.marriage and fam.marriage.date:
                    _, marriage_date, marriage_precision = _parse_date_to_raw_and_iso(fam.marriage.date)

                partnership = Partnership(
                    person_a_id=a_id,
                    person_b_id=b_id,
                    kind=PartnershipKind.married.value,
                    start_date=marriage_date,
                    start_date_precision=marriage_precision,
                    source=RelationshipSource.gedcom_import.value,
                    created_by=actor_id,
                )
                db.add(partnership)
                result.relationships_created += 1

        # Create parent-child relationships
        for child_xref in fam.children_xrefs:
            child_id = result.xref_to_person_id.get(child_xref)
            if not child_id:
                continue

            for parent_id in [husb_id, wife_id]:
                if not parent_id:
                    continue
                # Skip if both parent and child already existed
                if parent_id in existing_person_ids and child_id in existing_person_ids:
                    continue
                pc = ParentChild(
                    parent_id=parent_id,
                    child_id=child_id,
                    kind=ParentChildKind.biological.value,
                    source=RelationshipSource.gedcom_import.value,
                    created_by=actor_id,
                )
                db.add(pc)
                result.relationships_created += 1

    await db.flush()

    audit_value = {
        "persons_created": result.persons_created,
        "relationships_created": result.relationships_created,
        "duplicates_skipped": result.duplicates_skipped,
    }
    if batch_id:
        audit_value["batch_id"] = batch_id

    await log_audit(
        db, actor_id, "create", "gedcom_import", batch_id or "batch",
        new_value=audit_value,
    )

    logger.info(
        "GEDCOM import: %d persons, %d relationships, %d duplicates skipped",
        result.persons_created,
        result.relationships_created,
        result.duplicates_skipped,
    )

    return result


async def rollback_gedcom_batch(
    db: AsyncSession,
    *,
    batch: GedcomImportBatch,
    actor_id: str,
) -> dict:
    stats = batch.stats
    created_person_ids = stats.get("created_person_ids") or []

    if created_person_ids:
        await db.execute(delete(Person).where(Person.id.in_(created_person_ids)))

    batch.status = "rolled_back"
    stats["rollback_at"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).isoformat()
    batch.stats = stats
    await db.flush()

    await log_audit(
        db,
        actor_id,
        "rollback",
        "gedcom_import",
        batch.id,
        new_value={"deleted_person_count": len(created_person_ids)},
    )
    return {"deleted_person_count": len(created_person_ids)}
