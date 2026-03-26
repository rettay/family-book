"""Date intelligence service for computing ages and enriching person details."""

from __future__ import annotations

from datetime import date


def _parse_date_parts(date_str: str | None) -> date | None:
    """Parse an ISO 8601 date string to a date object. Returns None for unparseable values."""
    if not date_str:
        return None
    parts = date_str.split("-")
    try:
        if len(parts) >= 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        elif len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
    except (ValueError, IndexError):
        return None
    return None


def _precision_allows_age(precision: str | None) -> bool:
    """Only compute age for exact or month precision, not year-only or coarser."""
    if precision is None:
        return True  # No precision specified — assume exact
    return precision in ("exact", "month")


def compute_age(
    birth_date_str: str | None,
    reference_date_str: str | None,
    birth_precision: str | None = None,
    reference_precision: str | None = None,
) -> int | None:
    """Compute age in years between two dates."""
    if not _precision_allows_age(birth_precision):
        return None
    if not _precision_allows_age(reference_precision):
        return None
    birth = _parse_date_parts(birth_date_str)
    ref = _parse_date_parts(reference_date_str)
    if not birth or not ref:
        return None
    age = ref.year - birth.year
    if (ref.month, ref.day) < (birth.month, birth.day):
        age -= 1
    return age if age >= 0 else None


def compute_current_age(
    birth_date_str: str | None,
    birth_precision: str | None = None,
) -> int | None:
    """Compute current age for a living person."""
    if not _precision_allows_age(birth_precision):
        return None
    birth = _parse_date_parts(birth_date_str)
    if not birth:
        return None
    today = date.today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age if age >= 0 else None


def compute_age_at_death(
    birth_date_str: str | None,
    death_date_str: str | None,
    birth_precision: str | None = None,
    death_precision: str | None = None,
) -> int | None:
    """Compute age at death."""
    return compute_age(birth_date_str, death_date_str, birth_precision, death_precision)


def enrich_person_ages(person_dict: dict) -> dict:
    """Add current_age or age_at_death to a person detail dict."""
    birth_date = person_dict.get("birth_date")
    birth_precision = person_dict.get("birth_date_precision")
    death_date = person_dict.get("death_date")
    death_precision = person_dict.get("death_date_precision")
    is_living = person_dict.get("is_living", True)

    if not is_living and death_date:
        person_dict["age_at_death"] = compute_age_at_death(
            birth_date, death_date, birth_precision, death_precision
        )
    elif is_living and birth_date:
        person_dict["current_age"] = compute_current_age(birth_date, birth_precision)

    return person_dict
