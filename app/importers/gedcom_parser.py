"""GEDCOM 5.5.1 parser for Family Book.

Parses INDI (individual) and FAM (family) records from GEDCOM files
and returns structured dicts ready for import into the Person and
relationship models.
"""

from __future__ import annotations

import codecs
import io
import re
from dataclasses import dataclass, field


# ANSEL to Unicode mapping for the most common diacritics
_ANSEL_COMBINING: dict[int, str] = {
    0xE0: "\u0309",  # hook above
    0xE1: "\u0300",  # grave
    0xE2: "\u0301",  # acute
    0xE3: "\u0302",  # circumflex
    0xE4: "\u0303",  # tilde
    0xE5: "\u0304",  # macron
    0xE6: "\u0306",  # breve
    0xE7: "\u0307",  # dot above
    0xE8: "\u0308",  # diaeresis
    0xE9: "\u030C",  # caron
    0xEA: "\u030A",  # ring above
    0xF0: "\u0327",  # cedilla
    0xF1: "\u0328",  # ogonek
    0xF2: "\u0323",  # dot below
}


def _decode_ansel(raw: bytes) -> str:
    """Best-effort ANSEL to Unicode conversion."""
    result: list[str] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if b in _ANSEL_COMBINING:
            # ANSEL combining marks precede the base character
            if i + 1 < len(raw):
                base = chr(raw[i + 1])
                result.append(base + _ANSEL_COMBINING[b])
                i += 2
                continue
        result.append(chr(b) if b < 0x80 else chr(b))
        i += 1
    return "".join(result)


def _detect_encoding(raw: bytes) -> str:
    """Detect GEDCOM file encoding from the CHAR tag or BOM."""
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    head = raw[:2048]
    # Look for CHAR tag in header
    for line in head.split(b"\n"):
        stripped = line.strip()
        if b"CHAR" in stripped.upper():
            val = stripped.split(b" ")[-1].decode("ascii", errors="replace").upper().strip()
            if "UTF" in val or "UNICODE" in val:
                return "utf-8"
            if "ANSEL" in val:
                return "ansel"
            if "ASCII" in val:
                return "ascii"
    # Default: try UTF-8, fall back to latin-1
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


@dataclass
class GedcomEvent:
    event_type: str = ""  # BIRT, DEAT, MARR, etc.
    date: str = ""
    place: str = ""


@dataclass
class GedcomIndividual:
    xref: str = ""
    first_name: str = ""
    last_name: str = ""
    maiden_name: str = ""
    gender: str = ""
    birth: GedcomEvent | None = None
    death: GedcomEvent | None = None
    burial: GedcomEvent | None = None
    note: str = ""
    fam_spouse: list[str] = field(default_factory=list)
    fam_child: list[str] = field(default_factory=list)


@dataclass
class GedcomFamily:
    xref: str = ""
    husband_xref: str = ""
    wife_xref: str = ""
    children_xrefs: list[str] = field(default_factory=list)
    marriage: GedcomEvent | None = None


@dataclass
class GedcomParseResult:
    individuals: list[GedcomIndividual] = field(default_factory=list)
    families: list[GedcomFamily] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


_NAME_RE = re.compile(r"^(.*?)\s*/(.+?)/\s*(.*)$")


def _parse_name(raw_name: str) -> tuple[str, str, str]:
    """Parse GEDCOM NAME value: 'First /Last/ Suffix' -> (first, last, maiden)."""
    m = _NAME_RE.match(raw_name)
    if m:
        first = m.group(1).strip()
        last = m.group(2).strip()
        suffix = m.group(3).strip()
        if suffix:
            first = f"{first} {suffix}".strip()
        return first, last, ""
    # No surname delimiters
    parts = raw_name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:]), ""
    return raw_name.strip(), "", ""


def _parse_date_to_raw_and_iso(date_str: str) -> tuple[str, str | None, str | None]:
    """Convert GEDCOM date to (raw, iso_date, precision).

    Returns (raw_string, iso_date_or_none, precision_or_none).
    Delegates to the shared date_parsing service.
    """
    raw = date_str.strip()
    if not raw:
        return "", None, None

    from app.services.date_parsing import parse_date_raw_to_iso
    iso, precision = parse_date_raw_to_iso(raw)
    # GEDCOM fallback: any non-empty unparseable string → approximate
    if iso is None and precision is None:
        precision = "approximate"
    return raw, iso, precision


def _gender_map(sex: str) -> str | None:
    s = sex.strip().upper()
    if s == "M":
        return "male"
    if s == "F":
        return "female"
    if s:
        return "other"
    return None


def parse_gedcom(content: bytes | str, max_size_bytes: int = 10 * 1024 * 1024) -> GedcomParseResult:
    """Parse a GEDCOM file and return structured individuals and families.

    Args:
        content: Raw bytes or decoded string of the GEDCOM file.
        max_size_bytes: Maximum file size in bytes (default 10MB).

    Returns:
        GedcomParseResult with individuals, families, and any errors.
    """
    result = GedcomParseResult()

    if isinstance(content, bytes):
        if len(content) > max_size_bytes:
            result.errors.append(f"File exceeds maximum size of {max_size_bytes // (1024*1024)}MB")
            return result
        encoding = _detect_encoding(content)
        if encoding == "ansel":
            text = _decode_ansel(content)
        else:
            text = content.decode(encoding, errors="replace")
    else:
        text = content

    # Validate GEDCOM header
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or "HEAD" not in lines[0]:
        result.errors.append("Invalid GEDCOM file: missing HEAD record")
        return result

    # Parse line-by-line
    parsed_lines: list[tuple[int, str, str]] = []
    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        parts = raw_line.split(" ", 2)
        if not parts[0].isdigit():
            continue
        level = int(parts[0])
        tag = parts[1] if len(parts) > 1 else ""
        value = parts[2] if len(parts) > 2 else ""
        parsed_lines.append((level, tag, value))

    individuals: dict[str, GedcomIndividual] = {}
    families: dict[str, GedcomFamily] = {}

    i = 0
    while i < len(parsed_lines):
        level, tag, value = parsed_lines[i]

        if level == 0 and value == "INDI":
            # tag is the xref like @I1@
            xref = tag.strip("@")
            indi = GedcomIndividual(xref=xref)
            i += 1
            current_event: GedcomEvent | None = None
            current_sub = ""

            while i < len(parsed_lines) and parsed_lines[i][0] > 0:
                sl, st, sv = parsed_lines[i]

                if sl == 1:
                    current_event = None
                    current_sub = st

                    if st == "NAME":
                        first, last, maiden = _parse_name(sv)
                        if not indi.first_name:
                            indi.first_name = first
                            indi.last_name = last
                            indi.maiden_name = maiden
                    elif st == "SEX":
                        indi.gender = _gender_map(sv) or ""
                    elif st == "BIRT":
                        current_event = GedcomEvent(event_type="BIRT")
                        indi.birth = current_event
                    elif st == "DEAT":
                        current_event = GedcomEvent(event_type="DEAT")
                        indi.death = current_event
                    elif st == "BURI":
                        current_event = GedcomEvent(event_type="BURI")
                        indi.burial = current_event
                    elif st == "NOTE":
                        indi.note = sv
                    elif st == "FAMS":
                        indi.fam_spouse.append(sv.strip("@"))
                    elif st == "FAMC":
                        indi.fam_child.append(sv.strip("@"))

                elif sl == 2 and current_event is not None:
                    if st == "DATE":
                        current_event.date = sv
                    elif st == "PLAC":
                        current_event.place = sv

                elif sl == 2 and current_sub == "NAME":
                    if st == "_MARNM" or st == "SURN":
                        pass  # Already captured from NAME line
                    elif st == "GIVN" and not indi.first_name:
                        indi.first_name = sv

                elif sl == 2 and current_sub == "NOTE":
                    if st == "CONT":
                        indi.note += "\n" + sv
                    elif st == "CONC":
                        indi.note += sv

                i += 1

            individuals[xref] = indi

        elif level == 0 and value == "FAM":
            xref = tag.strip("@")
            fam = GedcomFamily(xref=xref)
            i += 1
            current_event = None

            while i < len(parsed_lines) and parsed_lines[i][0] > 0:
                sl, st, sv = parsed_lines[i]

                if sl == 1:
                    current_event = None
                    if st == "HUSB":
                        fam.husband_xref = sv.strip("@")
                    elif st == "WIFE":
                        fam.wife_xref = sv.strip("@")
                    elif st == "CHIL":
                        fam.children_xrefs.append(sv.strip("@"))
                    elif st == "MARR":
                        current_event = GedcomEvent(event_type="MARR")
                        fam.marriage = current_event

                elif sl == 2 and current_event is not None:
                    if st == "DATE":
                        current_event.date = sv
                    elif st == "PLAC":
                        current_event.place = sv

                i += 1

            families[xref] = fam

        else:
            i += 1

    result.individuals = list(individuals.values())
    result.families = list(families.values())
    return result
