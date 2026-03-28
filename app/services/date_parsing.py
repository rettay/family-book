"""Shared date parsing: raw human/GEDCOM date strings → (iso, precision).

Used by the GEDCOM importer and by the person create/update routes
to auto-derive ISO `birth_date` / `death_date` from raw input.
"""

from __future__ import annotations

import re

# GEDCOM and English month names → month number
_MONTHS = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    # Full English names
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
    "JUNE": "06", "JULY": "07", "AUGUST": "08",
    "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12",
}

# Prefixes that mark approximate dates
_APPROX_PREFIXES = (
    "ABT ", "ABOUT ", "CIRCA ", "EST ", "CAL ",
    "BEF ", "BEFORE ", "AFT ", "AFTER ", "~",
)

# Pattern: "March 15, 1985" or "March 1985" or "15 March 1985"
_NATURAL_DMY = re.compile(
    r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$"
)
_NATURAL_MDY = re.compile(
    r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$"
)
_NATURAL_MY = re.compile(
    r"^([A-Za-z]+)\s+(\d{4})$"
)
_SLASH_YMD = re.compile(r"^(\d{1,4})/(\d{1,2})/(\d{1,4})$")


def parse_date_raw_to_iso(raw: str | None) -> tuple[str | None, str | None]:
    """Parse a raw date string into (iso_date, precision).

    Returns (None, None) when the input is empty or unparseable.

    Handles:
    - ISO passthrough: "1985-03-15" → ("1985-03-15", "exact")
    - GEDCOM: "15 MAR 1985", "MAR 1985", "1985"
    - English: "March 15, 1985", "15 March 1985", "March 1985"
    - Approximate prefixes: ~, about, circa, abt, before, after, est, cal
    - Year-only: "1985"
    """
    if not raw or not raw.strip():
        return None, None

    text = raw.strip()

    # Detect approximate prefix
    precision: str | None = None
    upper = text.upper()
    for prefix in _APPROX_PREFIXES:
        if upper.startswith(prefix):
            text = text[len(prefix):].strip()
            precision = "approximate"
            break

    # ISO passthrough: already YYYY-MM-DD or YYYY-MM or YYYY
    iso_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if iso_match:
        return text, precision or "exact"

    iso_ym = re.match(r"^(\d{4})-(\d{2})$", text)
    if iso_ym:
        return text, precision or "month"

    # GEDCOM / natural language parsing
    clean = text.upper()
    parts = clean.split()

    # "15 MAR 1985" (day month year)
    if len(parts) == 3:
        # Try day-month-year
        day, mon, year = parts
        mon_num = _MONTHS.get(mon[:3])
        if mon_num and year.isdigit() and day.isdigit():
            iso = f"{year}-{mon_num}-{day.zfill(2)}"
            return iso, precision or "exact"

    # Natural: "March 15, 1985" or "March 15 1985"
    m = _NATURAL_MDY.match(text.strip())
    if m:
        month_name, day, year = m.group(1), m.group(2), m.group(3)
        mon_num = _MONTHS.get(month_name.upper()[:3])
        if mon_num:
            iso = f"{year}-{mon_num}-{day.zfill(2)}"
            return iso, precision or "exact"

    # Natural: "15 March 1985"
    m = _NATURAL_DMY.match(text.strip())
    if m:
        day, month_name, year = m.group(1), m.group(2), m.group(3)
        mon_num = _MONTHS.get(month_name.upper()[:3])
        if mon_num:
            iso = f"{year}-{mon_num}-{day.zfill(2)}"
            return iso, precision or "exact"

    # "MAR 1985" or "March 1985"
    if len(parts) == 2:
        mon, year = parts
        mon_num = _MONTHS.get(mon[:3])
        if mon_num and year.isdigit():
            iso = f"{year}-{mon_num}"
            return iso, precision or "month"

    # Natural: "March 1985" (with original casing)
    m = _NATURAL_MY.match(text.strip())
    if m:
        month_name, year = m.group(1), m.group(2)
        mon_num = _MONTHS.get(month_name.upper()[:3])
        if mon_num:
            iso = f"{year}-{mon_num}"
            return iso, precision or "month"

    # Year-only: "1985"
    if len(parts) == 1 and parts[0].isdigit() and len(parts[0]) == 4:
        return parts[0], precision or "year"

    # Slash dates: 07/29/1947, 29/07/1947, 1947/07/29
    m = _SLASH_YMD.match(text)
    if m:
        left, middle, right = m.group(1), m.group(2), m.group(3)
        if len(left) == 4:
            return f"{left}-{middle.zfill(2)}-{right.zfill(2)}", precision or "exact"
        if len(right) == 4:
            first = int(left)
            second = int(middle)
            year = right
            if first > 12 and second <= 12:
                day, month = first, second
            elif second > 12 and first <= 12:
                month, day = first, second
            else:
                month, day = first, second
            return f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}", precision or "exact"

    # Unparseable but had approximate prefix
    if precision:
        return None, precision

    return None, None
