"""Wiki service — slug generation and biographical section assembly."""

import re
import unicodedata

from markupsafe import escape as _esc

from app.services.date_intelligence_service import compute_current_age, compute_age_at_death


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
    """Auto-generated lead paragraph from name, dates, places, age, languages."""
    parts = []
    name = _esc(person.display_name)

    # Build name line with dates and computed age
    if person.is_living:
        age = compute_current_age(
            getattr(person, "birth_date", None),
            getattr(person, "birth_date_precision", None),
        )
        if person.birth_date_raw:
            bdr = _esc(person.birth_date_raw)
            age_str = f", age {age}" if age is not None else ""
            parts.append(f"{name} (born {bdr}{age_str})")
        else:
            parts.append(str(name))
    else:
        age = compute_age_at_death(
            getattr(person, "birth_date", None),
            getattr(person, "death_date", None),
            getattr(person, "birth_date_precision", None),
            getattr(person, "death_date_precision", None),
        )
        dates = ""
        if person.birth_date_raw and person.death_date_raw:
            bdr = _esc(person.birth_date_raw)
            ddr = _esc(person.death_date_raw)
            age_str = f", aged {age}" if age is not None else ""
            dates = f" ({bdr} \u2013 {ddr}{age_str})"
        elif person.birth_date_raw:
            dates = f" (born {_esc(person.birth_date_raw)})"
        elif person.death_date_raw:
            dates = f" (died {_esc(person.death_date_raw)})"
        parts.append(f"{name}{dates}")

    # Languages
    languages = getattr(person, "languages", None) or []
    if languages:
        parts.append(f"Languages: {', '.join(_esc(lang) for lang in languages)}.")

    if person.bio:
        parts.append(person.bio)  # Already sanitized via nh3

    return _section("summary", "Summary", parts, edit_fields=["bio"])


def build_early_life_section(person, parents: list) -> dict | None:
    """Birth info, maiden name, and parents."""
    lines = []
    if person.birth_place:
        born_in = f"Born in {_esc(person.birth_place)}"
        if person.birth_country_code:
            born_in += f" ({_esc(person.birth_country_code.upper())})"
        lines.append(born_in + ".")

    # Maiden name (birth_last_name) when different from current last_name
    birth_last_name = getattr(person, "birth_last_name", None)
    if birth_last_name and birth_last_name != getattr(person, "last_name", None):
        lines.append(f"Born as {_esc(birth_last_name)}.")

    if parents:
        parent_names = [_esc(p.display_name) for p in parents]
        if len(parent_names) == 1:
            lines.append(f"Child of {parent_names[0]}.")
        elif len(parent_names) == 2:
            lines.append(f"Child of {parent_names[0]} and {parent_names[1]}.")
        else:
            lines.append(f"Child of {', '.join(parent_names)}.")

    if not lines:
        return _empty_section("early-life", "Early Life",
                              edit_fields=["birth_place", "birth_country_code", "birth_date_raw", "birth_last_name"])
    return _section("early-life", "Early Life", lines,
                    edit_fields=["birth_place", "birth_country_code", "birth_date_raw", "birth_last_name"])


def build_education_section(person) -> dict | None:
    """From education[] array."""
    if not person.education:
        return None
    lines = []
    for entry in person.education:
        parts = []
        if isinstance(entry, dict):
            if entry.get("degree"):
                parts.append(str(_esc(entry["degree"])))
            if entry.get("institution"):
                parts.append(f"at {_esc(entry['institution'])}")
            if entry.get("year"):
                parts.append(f"({_esc(entry['year'])})")
            elif entry.get("year_start"):
                year_range = str(_esc(entry["year_start"]))
                if entry.get("year_end"):
                    year_range += f"\u2013{_esc(entry['year_end'])}"
                parts.append(f"({year_range})")
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
                parts.append(str(_esc(entry["title"])))
            if entry.get("company"):
                parts.append(f"at {_esc(entry['company'])}")
            elif entry.get("employer"):
                parts.append(f"at {_esc(entry['employer'])}")
            if entry.get("years"):
                parts.append(f"({_esc(entry['years'])})")
            elif entry.get("year_start"):
                year_range = str(_esc(entry["year_start"]))
                if entry.get("year_end"):
                    year_range += f"\u2013{_esc(entry['year_end'])}"
                parts.append(f"({year_range})")
        if parts:
            lines.append(" ".join(parts))
    return _section("career", "Career", lines, edit_fields=["career"])


def build_personal_life_section(person, partnerships: list, children: list) -> dict | None:
    """Partnerships, children, and residence."""
    lines = []
    for p in partnerships:
        partner = p.get("partner")
        if partner:
            verb = "Married" if p.get("type") == "married" else "Partner of"
            line = f"{verb} {_esc(partner.display_name)}"
            if p.get("start_date"):
                line += f" ({_esc(str(p['start_date']))})"
            lines.append(line + ".")
    if children:
        child_names = [_esc(c.display_name) for c in children]
        if len(child_names) == 1:
            lines.append(f"Has one child: {child_names[0]}.")
        else:
            lines.append(f"Has {len(child_names)} children: {', '.join(child_names)}.")

    # Residence info
    if person.residence_place:
        res_line = f"Resides in {_esc(person.residence_place)}"
        if getattr(person, "residence_country_code", None):
            res_line += f" ({_esc(person.residence_country_code.upper())})"
        lines.append(res_line + ".")

    if not lines:
        return _empty_section("personal-life", "Personal Life",
                              edit_fields=["residence_place", "residence_country_code"])
    return _section("personal-life", "Personal Life", lines,
                    edit_fields=["residence_place", "residence_country_code"])


def build_place_history_section(person) -> dict | None:
    """From place_history[] array — chronological list of places lived."""
    if not person.place_history:
        return None
    lines = []
    # Sort by from_year (entries without from_year go last)
    entries = sorted(
        person.place_history,
        key=lambda e: (e.get("from_year") or "9999") if isinstance(e, dict) else "9999",
    )
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        place = entry.get("place")
        if not place:
            continue
        parts = [str(_esc(place))]
        from_year = entry.get("from_year")
        to_year = entry.get("to_year")
        if from_year and to_year:
            parts.append(f"({_esc(str(from_year))}\u2013{_esc(str(to_year))})")
        elif from_year:
            parts.append(f"({_esc(str(from_year))}\u2013)")
        elif to_year:
            parts.append(f"(\u2013{_esc(str(to_year))})")
        if entry.get("is_current"):
            parts.append("(current)")
        desc = entry.get("description")
        if desc:
            parts.append(f"\u2014 {_esc(desc)}")
        lines.append(" ".join(parts))
    return _section("place-history", "Places Lived", lines, edit_fields=["place_history"])


def build_organizations_section(person) -> dict | None:
    """From organizations[] array."""
    if not person.organizations:
        return None
    lines = []
    for entry in person.organizations:
        parts = []
        if isinstance(entry, dict):
            if entry.get("name"):
                parts.append(str(_esc(entry["name"])))
            if entry.get("role"):
                parts.append(f"({_esc(entry['role'])})")
        if parts:
            lines.append(" ".join(parts))
    return _section("organizations", "Organizations", lines, edit_fields=["organizations"])


def build_physical_description_section(person) -> dict | None:
    """Physical attributes: height, weight, eye/hair color, blood type."""
    lines = []
    if getattr(person, "height", None):
        lines.append(f"Height: {_esc(person.height)}.")
    if getattr(person, "weight", None):
        lines.append(f"Weight: {_esc(person.weight)}.")
    if getattr(person, "eye_color", None):
        lines.append(f"Eye color: {_esc(person.eye_color)}.")
    if getattr(person, "hair_color", None):
        lines.append(f"Hair color: {_esc(person.hair_color)}.")
    if getattr(person, "blood_type", None):
        lines.append(f"Blood type: {_esc(person.blood_type)}.")

    if not lines:
        return _empty_section("physical-description", "Physical Description",
                              edit_fields=["height", "weight", "eye_color", "hair_color", "blood_type"])
    return _section("physical-description", "Physical Description", lines,
                    edit_fields=["height", "weight", "eye_color", "hair_color", "blood_type"])


def build_later_life_section(person) -> dict | None:
    """Health overview (condition names only)."""
    lines = []

    conditions = getattr(person, "medical_conditions", None) or []
    if conditions:
        condition_names = [str(_esc(c.get("condition", ""))) for c in conditions if isinstance(c, dict) and c.get("condition")]
        if condition_names:
            lines.append(f"Known health conditions: {', '.join(condition_names)}.")

    if not lines:
        return None
    return _section("later-life", "Later Life", lines, edit_fields=[])


def build_death_section(person) -> dict | None:
    """Death date, full burial details, obituary."""
    lines = []
    if person.death_date_raw:
        lines.append(f"Died {_esc(person.death_date_raw)}.")
    if person.burial_place:
        burial = f"Buried at {_esc(person.burial_place)}"
        if getattr(person, "burial_cemetery_name", None):
            burial += f" ({_esc(person.burial_cemetery_name)})"
        if getattr(person, "burial_country_code", None):
            burial += f", {_esc(person.burial_country_code.upper())}"
        lines.append(burial + ".")
    if getattr(person, "burial_plot_number", None):
        lines.append(f"Plot: {_esc(person.burial_plot_number)}.")
    if person.obituary:
        lines.append(person.obituary)  # Already sanitized via nh3
    if getattr(person, "obituary_source", None):
        lines.append(f"Source: {_esc(person.obituary_source)}.")

    if not lines:
        return None
    return _section("death-legacy", "Death & Legacy", lines,
                    edit_fields=["death_date_raw", "burial_place", "burial_cemetery_name",
                                 "burial_country_code", "burial_plot_number", "obituary", "obituary_source"])


def build_sources_section(person) -> dict | None:
    """Source citations and confidence level."""
    lines = []
    if getattr(person, "source_detail", None):
        lines.append(str(_esc(person.source_detail)))
    confidence = getattr(person, "confidence", None)
    if confidence:
        lines.append(f"Confidence: {_esc(confidence)}.")

    if not lines:
        return _empty_section("sources", "Sources & Citations",
                              edit_fields=["source_detail", "confidence"])
    return _section("sources", "Sources & Citations", lines,
                    edit_fields=["source_detail", "confidence"])


def build_research_section(person) -> dict | None:
    """Research notes."""
    if not person.research_notes:
        return _empty_section("research-notes", "Research Notes",
                              edit_fields=["research_notes"])
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
    """Assemble biographical sections from structured data — 11 Wikipedia-style sections."""
    sections = []

    # 1. Summary (always present — has name at minimum)
    summary = build_summary_section(person)
    if summary:
        sections.append(summary)

    # 2. Early Life
    parents = await get_parents(db, person.id)
    early = build_early_life_section(person, parents)
    if early:
        sections.append(early)

    # 3. Education
    edu = build_education_section(person)
    if edu:
        sections.append(edu)

    # 4. Career
    career = build_career_section(person)
    if career:
        sections.append(career)

    # 5. Personal Life
    partnerships = await get_partnerships(db, person.id)
    children = await get_children(db, person.id)
    personal = build_personal_life_section(person, partnerships, children)
    if personal:
        sections.append(personal)

    # 5b. Places Lived
    places_lived = build_place_history_section(person)
    if places_lived:
        sections.append(places_lived)

    # 6. Organizations
    orgs = build_organizations_section(person)
    if orgs:
        sections.append(orgs)

    # 7. Physical Description (NEW)
    phys = build_physical_description_section(person)
    if phys:
        sections.append(phys)

    # 8. Later Life
    later = build_later_life_section(person)
    if later:
        sections.append(later)

    # 9. Death & Legacy
    if not person.is_living:
        death = build_death_section(person)
        if death:
            sections.append(death)

    # 10. Sources & Citations (NEW)
    sources = build_sources_section(person)
    if sources:
        sections.append(sources)

    # 11. Research Notes
    research = build_research_section(person)
    if research:
        sections.append(research)

    return sections
