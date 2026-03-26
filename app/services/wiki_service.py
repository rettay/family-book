"""Wiki service — slug generation and biographical section assembly."""

import re
import unicodedata


def generate_slug(first_name: str | None, last_name: str | None, person_id: str) -> str:
    """Generate URL-safe slug: first-last-shortid."""
    def _slugify(text: str) -> str:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\w\s-]", "", text.lower())
        return re.sub(r"[-\s]+", "-", text).strip("-")

    short_id = person_id[:8]
    parts = []
    if first_name:
        parts.append(_slugify(first_name))
    if last_name:
        parts.append(_slugify(last_name))
    parts.append(short_id)
    return "-".join(p for p in parts if p)


def _section(section_id: str, title: str, content_lines: list[str], edit_fields: list[str] | None = None) -> dict | None:
    """Build a section dict. Returns None if no content."""
    text = "\n".join(line for line in content_lines if line)
    if not text.strip():
        return None
    return {
        "id": section_id,
        "title": title,
        "content": text,
        "edit_fields": edit_fields or [],
    }


def _empty_section(section_id: str, title: str, edit_fields: list[str] | None = None) -> dict:
    """Return an empty placeholder section for editable areas."""
    return {
        "id": section_id,
        "title": title,
        "content": "",
        "edit_fields": edit_fields or [],
    }


def build_summary_section(person) -> dict | None:
    """Auto-generated lead paragraph from name, dates, places."""
    parts = []
    name = person.display_name
    if person.is_living:
        if person.birth_date_raw:
            parts.append(f"{name} (born {person.birth_date_raw})")
        else:
            parts.append(name)
    else:
        dates = ""
        if person.birth_date_raw and person.death_date_raw:
            dates = f" ({person.birth_date_raw} – {person.death_date_raw})"
        elif person.birth_date_raw:
            dates = f" (born {person.birth_date_raw})"
        elif person.death_date_raw:
            dates = f" (died {person.death_date_raw})"
        parts.append(f"{name}{dates}")

    if person.bio:
        parts.append(person.bio)

    return _section("summary", "Summary", parts, edit_fields=["bio"])


def build_early_life_section(person, parents: list) -> dict | None:
    """Birth info and parents."""
    lines = []
    if person.birth_place:
        born_in = f"Born in {person.birth_place}"
        if person.birth_country_code:
            born_in += f" ({person.birth_country_code.upper()})"
        lines.append(born_in + ".")
    if parents:
        parent_names = [p.display_name for p in parents]
        if len(parent_names) == 1:
            lines.append(f"Child of {parent_names[0]}.")
        elif len(parent_names) == 2:
            lines.append(f"Child of {parent_names[0]} and {parent_names[1]}.")
        else:
            lines.append(f"Child of {', '.join(parent_names)}.")

    if not lines:
        return _empty_section("early-life", "Early Life",
                              edit_fields=["birth_place", "birth_country_code", "birth_date_raw"])
    return _section("early-life", "Early Life", lines,
                    edit_fields=["birth_place", "birth_country_code", "birth_date_raw"])


def build_education_section(person) -> dict | None:
    """From education[] array."""
    if not person.education:
        return None
    lines = []
    for entry in person.education:
        parts = []
        if isinstance(entry, dict):
            if entry.get("degree"):
                parts.append(entry["degree"])
            if entry.get("institution"):
                parts.append(f"at {entry['institution']}")
            if entry.get("year"):
                parts.append(f"({entry['year']})")
        if parts:
            lines.append(" ".join(parts))
    return _section("education", "Education", lines, edit_fields=["education"])


def build_career_section(person) -> dict | None:
    """From career[] array."""
    if not person.career:
        return None
    lines = []
    for entry in person.career:
        parts = []
        if isinstance(entry, dict):
            if entry.get("title"):
                parts.append(entry["title"])
            if entry.get("company"):
                parts.append(f"at {entry['company']}")
            if entry.get("years"):
                parts.append(f"({entry['years']})")
        if parts:
            lines.append(" ".join(parts))
    return _section("career", "Career", lines, edit_fields=["career"])


def build_personal_life_section(person, partnerships: list, children: list) -> dict | None:
    """Partnerships and children."""
    lines = []
    for p in partnerships:
        partner = p.get("partner")
        if partner:
            verb = "Married" if p.get("type") == "married" else "Partner of"
            line = f"{verb} {partner.display_name}"
            if p.get("start_date"):
                line += f" ({p['start_date']})"
            lines.append(line + ".")
    if children:
        child_names = [c.display_name for c in children]
        if len(child_names) == 1:
            lines.append(f"Has one child: {child_names[0]}.")
        else:
            lines.append(f"Has {len(child_names)} children: {', '.join(child_names)}.")

    if not lines:
        return _empty_section("personal-life", "Personal Life", edit_fields=[])
    return _section("personal-life", "Personal Life", lines, edit_fields=[])


def build_organizations_section(person) -> dict | None:
    """From organizations[] array."""
    if not person.organizations:
        return None
    lines = []
    for entry in person.organizations:
        parts = []
        if isinstance(entry, dict):
            if entry.get("name"):
                parts.append(entry["name"])
            if entry.get("role"):
                parts.append(f"({entry['role']})")
        if parts:
            lines.append(" ".join(parts))
    return _section("organizations", "Organizations", lines, edit_fields=["organizations"])


def build_later_life_section(person) -> dict | None:
    """Residence and health overview."""
    lines = []
    if person.residence_place:
        line = f"Resides in {person.residence_place}"
        if getattr(person, "residence_country_code", None):
            line += f" ({person.residence_country_code.upper()})"
        lines.append(line + ".")

    conditions = getattr(person, "medical_conditions", None) or []
    if conditions:
        condition_names = [c.get("condition", "") for c in conditions if isinstance(c, dict) and c.get("condition")]
        if condition_names:
            lines.append(f"Known health conditions: {', '.join(condition_names)}.")

    if not lines:
        return None
    return _section("later-life", "Later Life", lines,
                    edit_fields=["residence_place", "residence_country_code"])


def build_death_section(person) -> dict | None:
    """Death date, burial, obituary."""
    lines = []
    if person.death_date_raw:
        lines.append(f"Died {person.death_date_raw}.")
    if person.burial_place:
        burial = f"Buried at {person.burial_place}"
        if getattr(person, "burial_cemetery_name", None):
            burial += f" ({person.burial_cemetery_name})"
        lines.append(burial + ".")
    if person.obituary:
        lines.append(person.obituary)

    if not lines:
        return None
    return _section("death-legacy", "Death & Legacy", lines,
                    edit_fields=["death_date_raw", "burial_place", "obituary"])


def build_research_section(person) -> dict | None:
    """Research notes."""
    if not person.research_notes:
        return None
    return _section("research-notes", "Research Notes", [person.research_notes],
                    edit_fields=["research_notes"])


async def get_parents(db, person_id: str):
    """Get parent persons for a person."""
    from sqlalchemy import select
    from app.models.relationships import ParentChild
    from app.models.person import Person, PersonLifecycleState

    result = await db.execute(
        select(ParentChild).where(ParentChild.child_id == person_id)
    )
    parent_rels = result.scalars().all()
    parents = []
    for rel in parent_rels:
        result = await db.execute(
            select(Person).where(
                Person.id == rel.parent_id,
                Person.lifecycle_state == PersonLifecycleState.active.value,
            )
        )
        parent = result.scalar_one_or_none()
        if parent:
            parents.append(parent)
    return parents


async def get_children(db, person_id: str):
    """Get children persons for a person."""
    from sqlalchemy import select
    from app.models.relationships import ParentChild
    from app.models.person import Person, PersonLifecycleState

    result = await db.execute(
        select(ParentChild).where(ParentChild.parent_id == person_id)
    )
    child_rels = result.scalars().all()
    children = []
    for rel in child_rels:
        result = await db.execute(
            select(Person).where(
                Person.id == rel.child_id,
                Person.lifecycle_state == PersonLifecycleState.active.value,
            )
        )
        child = result.scalar_one_or_none()
        if child:
            children.append(child)
    return children


async def get_partnerships(db, person_id: str):
    """Get partnership info for a person."""
    from sqlalchemy import select, or_
    from app.models.relationships import Partnership
    from app.models.person import Person, PersonLifecycleState

    result = await db.execute(
        select(Partnership).where(
            or_(Partnership.person_a_id == person_id, Partnership.person_b_id == person_id)
        )
    )
    partnerships = result.scalars().all()
    results = []
    for p in partnerships:
        partner_id = p.person_b_id if p.person_a_id == person_id else p.person_a_id
        result = await db.execute(
            select(Person).where(
                Person.id == partner_id,
                Person.lifecycle_state == PersonLifecycleState.active.value,
            )
        )
        partner = result.scalar_one_or_none()
        if partner:
            results.append({
                "partner": partner,
                "type": getattr(p, "kind", "partnership"),
                "start_date": getattr(p, "start_date", None),
            })
    return results


async def assemble_wiki_sections(db, person, current_user) -> list[dict]:
    """Assemble biographical sections from structured data."""
    sections = []

    summary = build_summary_section(person)
    if summary:
        sections.append(summary)

    parents = await get_parents(db, person.id)
    early = build_early_life_section(person, parents)
    if early:
        sections.append(early)

    if person.education:
        edu = build_education_section(person)
        if edu:
            sections.append(edu)

    if person.career:
        career = build_career_section(person)
        if career:
            sections.append(career)

    partnerships = await get_partnerships(db, person.id)
    children = await get_children(db, person.id)
    personal = build_personal_life_section(person, partnerships, children)
    if personal:
        sections.append(personal)

    if person.organizations:
        orgs = build_organizations_section(person)
        if orgs:
            sections.append(orgs)

    later = build_later_life_section(person)
    if later:
        sections.append(later)

    if not person.is_living:
        death = build_death_section(person)
        if death:
            sections.append(death)

    research = build_research_section(person)
    if research:
        sections.append(research)

    return sections
