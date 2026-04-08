from __future__ import annotations

from dataclasses import dataclass
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media
from app.models.person import Person
from app.models.relationships import ParentChild, Partnership
from app.models.story import Story
from app.roles import get_person_role
from app.services.media_service import get_media_file_path, get_variant_path


@dataclass(frozen=True)
class ExportArtifact:
    path: str
    cleanup_dir: str


def create_temp_export_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="family-book-export-"))


def cleanup_export_artifact(path: str | None) -> None:
    if not path:
        return
    target = Path(path)
    cleanup_root = target.parent
    if target.suffix == ".zip" and target.parent.name == "archive":
        cleanup_root = target.parent.parent
    elif target.suffix == ".ged" and target.parent.name == "gedcom":
        cleanup_root = target.parent.parent
    if cleanup_root.name.startswith("family-book-export-") and cleanup_root.exists():
        for child in sorted(cleanup_root.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink(missing_ok=True)
            else:
                child.rmdir()
        cleanup_root.rmdir()


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _person_payload(person: Person) -> dict[str, object]:
    return {
        "id": person.id,
        "display_name": person.display_name,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "patronymic": person.patronymic,
        "birth_last_name": person.birth_last_name,
        "nickname": person.nickname,
        "alternate_nicknames": person.alternate_nicknames,
        "name_display_order": person.name_display_order,
        "gender": person.gender,
        "birth_date_raw": person.birth_date_raw,
        "birth_date": person.birth_date,
        "birth_date_precision": person.birth_date_precision,
        "death_date_raw": person.death_date_raw,
        "death_date": person.death_date,
        "death_date_precision": person.death_date_precision,
        "is_living": person.is_living,
        "birth_place": person.birth_place,
        "birth_country_code": person.birth_country_code,
        "birth_place_latitude": person.birth_place_latitude,
        "birth_place_longitude": person.birth_place_longitude,
        "residence_place": person.residence_place,
        "residence_country_code": person.residence_country_code,
        "residence_place_latitude": person.residence_place_latitude,
        "residence_place_longitude": person.residence_place_longitude,
        "burial_place": person.burial_place,
        "burial_country_code": person.burial_country_code,
        "burial_place_latitude": person.burial_place_latitude,
        "burial_place_longitude": person.burial_place_longitude,
        "burial_cemetery_name": person.burial_cemetery_name,
        "burial_plot_number": person.burial_plot_number,
        "remains_disposition": person.remains_disposition,
        "languages": person.languages,
        "bio": person.bio,
        "research_notes": person.research_notes,
        "medical_history": person.medical_history,
        "obituary": person.obituary,
        "obituary_source": person.obituary_source,
        "obituary_url": person.obituary_url,
        "education": person.education,
        "career": person.career,
        "organizations": person.organizations,
        "height": person.height,
        "weight": person.weight,
        "eye_color": person.eye_color,
        "hair_color": person.hair_color,
        "blood_type": person.blood_type,
        "maternal_haplogroup": person.maternal_haplogroup,
        "paternal_haplogroup": person.paternal_haplogroup,
        "dna_test_provider": person.dna_test_provider,
        "admixture": person.admixture,
        "medical_conditions": person.medical_conditions,
        "source_detail": person.source_detail,
        "confidence": person.confidence,
        "contact_whatsapp": person.contact_whatsapp,
        "contact_telegram": person.contact_telegram,
        "contact_signal": person.contact_signal,
        "contact_phone": person.contact_phone,
        "contact_email": person.contact_email,
        "contact_addresses": person.contact_addresses,
        "contact_phones": person.contact_phones,
        "contact_emails": person.contact_emails,
        "social_accounts": person.social_accounts,
        "name_history": person.name_history,
        "place_history": person.place_history,
        "photo_url": person.photo_url,
        "branch": person.branch,
        "role": get_person_role(person),
        "visibility": person.visibility,
        "contact_visibility": person.contact_visibility,
        "sensitive_visibility": person.sensitive_visibility,
        "account_state": person.account_state,
        "lifecycle_state": person.lifecycle_state,
        "slug": person.slug,
        "source": person.source,
        "created_by": person.created_by,
        "created_at": person.created_at.isoformat() if person.created_at else None,
        "updated_at": person.updated_at.isoformat() if person.updated_at else None,
    }


def _parent_child_payload(relationship: ParentChild) -> dict[str, object]:
    return {
        "id": relationship.id,
        "parent_id": relationship.parent_id,
        "child_id": relationship.child_id,
        "kind": relationship.kind,
        "confidence": relationship.confidence,
        "source": relationship.source,
        "source_detail": relationship.source_detail,
        "notes": relationship.notes,
        "start_date": relationship.start_date,
        "end_date": relationship.end_date,
        "created_by": relationship.created_by,
        "created_at": relationship.created_at.isoformat() if relationship.created_at else None,
    }


def _partnership_payload(partnership: Partnership) -> dict[str, object]:
    return {
        "id": partnership.id,
        "person_a_id": partnership.person_a_id,
        "person_b_id": partnership.person_b_id,
        "kind": partnership.kind,
        "status": partnership.status,
        "start_date": partnership.start_date,
        "start_date_precision": partnership.start_date_precision,
        "end_date": partnership.end_date,
        "end_date_precision": partnership.end_date_precision,
        "source": partnership.source,
        "notes": partnership.notes,
        "created_by": partnership.created_by,
        "created_at": partnership.created_at.isoformat() if partnership.created_at else None,
    }


def _story_payload(story: Story) -> dict[str, object]:
    return {
        "id": story.id,
        "person_id": story.person_id,
        "title": story.title,
        "body": story.body,
        "author_person_id": story.author_person_id,
        "audio_media_id": story.audio_media_id,
        "source": story.source,
        "created_at": story.created_at.isoformat() if story.created_at else None,
        "updated_at": story.updated_at.isoformat() if story.updated_at else None,
    }


def _media_payload(media: Media) -> dict[str, object]:
    return {
        "id": media.id,
        "person_id": media.person_id,
        "file_path": media.file_path,
        "original_filename": media.original_filename,
        "media_type": media.media_type,
        "mime_type": media.mime_type,
        "width": media.width,
        "height": media.height,
        "duration_seconds": media.duration_seconds,
        "file_size_bytes": media.file_size_bytes,
        "file_hash": media.file_hash,
        "embed_url": media.embed_url,
        "embed_provider": media.embed_provider,
        "caption": media.caption,
        "title": media.title,
        "description": media.description,
        "taken_date": media.taken_date,
        "taken_location": media.taken_location,
        "tagged_person_ids": media.tagged_person_ids,
        "source": media.source,
        "purpose": media.purpose,
        "visibility": media.visibility,
        "processing_status": media.processing_status,
        "uploaded_by": media.uploaded_by,
        "created_at": media.created_at.isoformat() if media.created_at else None,
    }


def _safe_name(value: str | None, fallback: str) -> str:
    raw = (value or fallback).strip()
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in raw)
    return cleaned or fallback


def _gedcom_date(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    value = raw_value[:10]
    parts = value.split("-")
    if len(parts) == 3 and all(parts):
        year, month, day = parts
        months = {
            "01": "JAN",
            "02": "FEB",
            "03": "MAR",
            "04": "APR",
            "05": "MAY",
            "06": "JUN",
            "07": "JUL",
            "08": "AUG",
            "09": "SEP",
            "10": "OCT",
            "11": "NOV",
            "12": "DEC",
        }
        return f"{int(day):02d} {months.get(month, 'JAN')} {year}"
    if len(parts) >= 1 and parts[0]:
        return parts[0]
    return raw_value


def _gedcom_name(person: Person) -> str:
    given = person.first_name or "Unknown"
    surname = person.last_name or "Unknown"
    return f"{given} /{surname}/"


def _gedcom_sex(person: Person) -> str | None:
    if person.gender == "male":
        return "M"
    if person.gender == "female":
        return "F"
    return None


def render_gedcom(
    *,
    persons: list[Person],
    parent_children: list[ParentChild],
    partnerships: list[Partnership],
    submitter_name: str = "Family Book",
) -> str:
    indi_map = {person.id: f"@I{index}@" for index, person in enumerate(persons, start=1)}

    family_defs: list[dict[str, object]] = []
    family_key_to_index: dict[tuple[str, ...], int] = {}
    child_to_family: dict[str, int] = {}

    def family_index_for(parents: tuple[str, ...]) -> int:
        key = tuple(sorted(parents))
        existing = family_key_to_index.get(key)
        if existing is not None:
            return existing
        family_defs.append({"parents": list(key), "children": []})
        family_key_to_index[key] = len(family_defs) - 1
        return len(family_defs) - 1

    child_parents: dict[str, list[str]] = {}
    for relationship in parent_children:
        child_parents.setdefault(relationship.child_id, []).append(relationship.parent_id)

    for child_id, parents in child_parents.items():
        index = family_index_for(tuple(sorted(set(parents))))
        family_defs[index]["children"].append(child_id)
        child_to_family[child_id] = index

    for partnership in partnerships:
        family_index_for((partnership.person_a_id, partnership.person_b_id))

    fam_map = {index: f"@F{index + 1}@" for index in range(len(family_defs))}
    spouse_families: dict[str, list[str]] = {}
    for index, family in enumerate(family_defs):
        fam_id = fam_map[index]
        for parent_id in family["parents"]:
            spouse_families.setdefault(parent_id, []).append(fam_id)

    lines = [
        "0 HEAD",
        "1 SOUR FAMILY-BOOK",
        "2 NAME Family Book",
        "1 CHAR UTF-8",
        "1 GEDC",
        "2 VERS 5.5.1",
        "1 SUBM @SUB1@",
        "0 @SUB1@ SUBM",
        f"1 NAME {submitter_name}",
    ]

    for person in persons:
        indi_id = indi_map[person.id]
        lines.append(f"0 {indi_id} INDI")
        lines.append(f"1 NAME {_gedcom_name(person)}")
        sex = _gedcom_sex(person)
        if sex:
            lines.append(f"1 SEX {sex}")
        lines.append(f"1 _UID {person.id}")
        lines.append(f"1 _FBROLE {get_person_role(person)}")
        birth_date = _gedcom_date(person.birth_date or person.birth_date_raw)
        if birth_date:
            lines.append("1 BIRT")
            lines.append(f"2 DATE {birth_date}")
            if person.birth_place:
                lines.append(f"2 PLAC {person.birth_place}")
        death_date = _gedcom_date(person.death_date or person.death_date_raw)
        if death_date:
            lines.append("1 DEAT")
            lines.append(f"2 DATE {death_date}")
            if person.burial_place:
                lines.append(f"2 PLAC {person.burial_place}")
        elif person.residence_place:
            lines.append("1 RESI")
            lines.append(f"2 PLAC {person.residence_place}")
        if person.bio:
            lines.append(f"1 NOTE {person.bio.replace(chr(10), ' ')}")
        if person.id in child_to_family:
            lines.append(f"1 FAMC {fam_map[child_to_family[person.id]]}")
        for family_id in spouse_families.get(person.id, []):
            lines.append(f"1 FAMS {family_id}")

    partnership_lookup = {
        tuple(sorted((partnership.person_a_id, partnership.person_b_id))): partnership
        for partnership in partnerships
    }

    for index, family in enumerate(family_defs):
        fam_id = fam_map[index]
        parents = family["parents"]
        lines.append(f"0 {fam_id} FAM")
        if len(parents) >= 1 and parents[0] in indi_map:
            lines.append(f"1 HUSB {indi_map[parents[0]]}")
        if len(parents) >= 2 and parents[1] in indi_map:
            lines.append(f"1 WIFE {indi_map[parents[1]]}")
        for child_id in family["children"]:
            if child_id in indi_map:
                lines.append(f"1 CHIL {indi_map[child_id]}")
        partnership = partnership_lookup.get(tuple(sorted(parents)))
        if partnership and partnership.start_date:
            lines.append("1 MARR")
            lines.append(f"2 DATE {_gedcom_date(partnership.start_date)}")
        if partnership and partnership.end_date:
            lines.append("1 DIV")
            lines.append(f"2 DATE {_gedcom_date(partnership.end_date)}")

    lines.append("0 TRLR")
    return "\n".join(lines) + "\n"


async def build_gedcom_export(db: AsyncSession) -> ExportArtifact:
    persons = list((await db.execute(select(Person).order_by(Person.last_name, Person.first_name))).scalars().all())
    parent_children = list((await db.execute(select(ParentChild))).scalars().all())
    partnerships = list((await db.execute(select(Partnership))).scalars().all())
    export_root = create_temp_export_dir()
    output_dir = export_root / "gedcom"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"family-book-{_timestamp_slug()}.ged"
    output_path.write_text(
        render_gedcom(persons=persons, parent_children=parent_children, partnerships=partnerships),
        encoding="utf-8",
    )
    return ExportArtifact(path=str(output_path), cleanup_dir=str(export_root))


async def build_archive_export(db: AsyncSession) -> ExportArtifact:
    persons = list((await db.execute(select(Person).order_by(Person.last_name, Person.first_name))).scalars().all())
    parent_children = list((await db.execute(select(ParentChild))).scalars().all())
    partnerships = list((await db.execute(select(Partnership))).scalars().all())
    stories = list((await db.execute(select(Story).order_by(Story.created_at.asc()))).scalars().all())
    media_items = list((await db.execute(select(Media).order_by(Media.created_at.asc()))).scalars().all())

    created_at = datetime.now(timezone.utc).isoformat()
    timestamp = _timestamp_slug()
    export_root = create_temp_export_dir()
    archive_dir = export_root / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"family-book-archive-{timestamp}.zip"
    gedcom_text = render_gedcom(
        persons=persons,
        parent_children=parent_children,
        partnerships=partnerships,
    )

    manifest = {
        "format_version": 1,
        "created_at": created_at,
        "export_scope": "admin_full_archive",
        "includes": [
            "manifest.json",
            "people.json",
            "relationships/parent_child.json",
            "relationships/partnerships.json",
            "stories.json",
            "media/media.json",
            "exports/family-book.ged",
        ],
        "portable_formats": {
            "people": "json",
            "relationships": "json",
            "stories": "json",
            "media_binary": "original files where present",
            "gedcom": "5.5.1 with Family Book custom tags",
        },
        "sensitive_field_behavior": {
            "archive_json": "includes contact, medical, and genetic fields because this export is admin-only",
            "gedcom": "does not represent most encrypted contact, medical, or genetic fields",
        },
        "omissions": [
            "auth sessions",
            "passkeys",
            "magic links",
            "invite tokens",
            "smtp credentials",
            "oauth credentials",
            "background job state",
        ],
        "custom_fields": [
            "_FBROLE in GEDCOM individual records",
            "contact_visibility in people.json",
            "sensitive_visibility in people.json",
            "full stories.json narrative export",
        ],
    }

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        zf.writestr(
            "people.json",
            json.dumps([_person_payload(person) for person in persons], indent=2, sort_keys=True),
        )
        zf.writestr(
            "relationships/parent_child.json",
            json.dumps(
                [_parent_child_payload(relationship) for relationship in parent_children],
                indent=2,
                sort_keys=True,
            ),
        )
        zf.writestr(
            "relationships/partnerships.json",
            json.dumps(
                [_partnership_payload(partnership) for partnership in partnerships],
                indent=2,
                sort_keys=True,
            ),
        )
        zf.writestr(
            "stories.json",
            json.dumps([_story_payload(story) for story in stories], indent=2, sort_keys=True),
        )
        zf.writestr(
            "media/media.json",
            json.dumps([_media_payload(media) for media in media_items], indent=2, sort_keys=True),
        )
        zf.writestr("exports/family-book.ged", gedcom_text)

        for media in media_items:
            if not media.file_path:
                continue
            resolved = get_media_file_path(media.file_path)
            if resolved and os.path.isfile(resolved):
                export_name = _safe_name(media.original_filename or media.file_path, media.id)
                zf.write(resolved, f"media/originals/{media.id}-{export_name}")
            thumb_path = get_variant_path(media.id, "thumb")
            if thumb_path and os.path.isfile(thumb_path):
                zf.write(thumb_path, f"media/variants/{media.id}/thumb.jpg")
            medium_path = get_variant_path(media.id, "medium")
            if medium_path and os.path.isfile(medium_path):
                zf.write(medium_path, f"media/variants/{media.id}/medium.jpg")
            poster_path = get_variant_path(media.id, "poster")
            if poster_path and os.path.isfile(poster_path):
                zf.write(poster_path, f"media/variants/{media.id}/poster.jpg")

    return ExportArtifact(path=str(archive_path), cleanup_dir=str(export_root))
