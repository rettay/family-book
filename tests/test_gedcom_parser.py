"""Tests for GEDCOM 5.5.1 parser."""

import pytest

from app.importers.gedcom_parser import (
    GedcomIndividual,
    GedcomParseResult,
    _detect_encoding,
    _parse_date_to_raw_and_iso,
    _parse_name,
    _gender_map,
    parse_gedcom,
)


# ── Name parsing ──────────────────────────────────────────────────────

class TestParseName:
    def test_standard_name(self):
        first, last, maiden = _parse_name("John /Smith/")
        assert first == "John"
        assert last == "Smith"
        assert maiden == ""

    def test_name_with_suffix(self):
        first, last, maiden = _parse_name("John /Smith/ Jr")
        assert first == "John Jr"
        assert last == "Smith"

    def test_name_without_slashes(self):
        first, last, maiden = _parse_name("John Smith")
        assert first == "John"
        assert last == "Smith"

    def test_single_name(self):
        first, last, maiden = _parse_name("Madonna")
        assert first == "Madonna"
        assert last == ""

    def test_empty_name(self):
        first, last, maiden = _parse_name("")
        assert first == ""
        assert last == ""

    def test_compound_first_name(self):
        first, last, maiden = _parse_name("Maria Elena /Garcia/")
        assert first == "Maria Elena"
        assert last == "Garcia"


# ── Date parsing ─────────────────────────────────────────────────────

class TestParseDateToRawAndIso:
    def test_full_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("15 MAR 1920")
        assert raw == "15 MAR 1920"
        assert iso == "1920-03-15"
        assert precision == "exact"

    def test_month_year(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("JAN 1850")
        assert iso == "1850-01"
        assert precision == "month"

    def test_year_only(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("1776")
        assert iso == "1776"
        assert precision == "year"

    def test_approximate_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("ABT 1890")
        assert raw == "ABT 1890"
        assert iso == "1890"
        assert precision == "approximate"

    def test_before_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("BEF 15 JUN 1900")
        assert iso == "1900-06-15"
        assert precision == "approximate"

    def test_after_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("AFT 1945")
        assert iso == "1945"
        assert precision == "approximate"

    def test_empty_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("")
        assert raw == ""
        assert iso is None
        assert precision is None

    def test_unparseable_date(self):
        raw, iso, precision = _parse_date_to_raw_and_iso("between 1920 and 1930")
        assert raw == "between 1920 and 1930"
        assert iso is None
        assert precision == "approximate"


# ── Gender mapping ───────────────────────────────────────────────────

class TestGenderMap:
    def test_male(self):
        assert _gender_map("M") == "male"

    def test_female(self):
        assert _gender_map("F") == "female"

    def test_other(self):
        assert _gender_map("X") == "other"

    def test_empty(self):
        assert _gender_map("") is None


# ── Encoding detection ───────────────────────────────────────────────

class TestDetectEncoding:
    def test_utf8_bom(self):
        assert _detect_encoding(b"\xef\xbb\xbf0 HEAD") == "utf-8-sig"

    def test_char_utf8(self):
        content = b"0 HEAD\n1 CHAR UTF-8\n"
        assert _detect_encoding(content) in ("utf-8", "utf-8-sig")

    def test_char_ansel(self):
        content = b"0 HEAD\n1 CHAR ANSEL\n"
        assert _detect_encoding(content) == "ansel"

    def test_default_utf8(self):
        content = b"0 HEAD\n1 SOUR Test\n"
        assert _detect_encoding(content) == "utf-8"


# ── Full parser ──────────────────────────────────────────────────────

MINIMAL_GEDCOM = b"""0 HEAD
1 SOUR TestApp
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Giovanni /Rossi/
1 SEX M
1 BIRT
2 DATE 15 MAR 1890
2 PLAC Naples, Italy
1 DEAT
2 DATE 10 JAN 1965
0 @I2@ INDI
1 NAME Maria /Bianchi/
1 SEX F
1 BIRT
2 DATE 1 JUN 1895
2 PLAC Rome, Italy
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 5 MAY 1920
2 PLAC Naples, Italy
1 CHIL @I3@
0 @I3@ INDI
1 NAME Luigi /Rossi/
1 SEX M
1 BIRT
2 DATE 10 FEB 1921
2 PLAC Naples, Italy
0 TRLR
"""


class TestParseGedcom:
    def test_minimal_gedcom(self):
        result = parse_gedcom(MINIMAL_GEDCOM)
        assert len(result.errors) == 0
        assert len(result.individuals) == 3
        assert len(result.families) == 1

    def test_individuals_parsed_correctly(self):
        result = parse_gedcom(MINIMAL_GEDCOM)
        giovanni = next(i for i in result.individuals if i.xref == "I1")
        assert giovanni.first_name == "Giovanni"
        assert giovanni.last_name == "Rossi"
        assert giovanni.gender == "male"
        assert giovanni.birth is not None
        assert giovanni.birth.date == "15 MAR 1890"
        assert giovanni.birth.place == "Naples, Italy"
        assert giovanni.death is not None
        assert giovanni.death.date == "10 JAN 1965"

    def test_family_parsed_correctly(self):
        result = parse_gedcom(MINIMAL_GEDCOM)
        fam = result.families[0]
        assert fam.husband_xref == "I1"
        assert fam.wife_xref == "I2"
        assert len(fam.children_xrefs) == 1
        assert fam.children_xrefs[0] == "I3"
        assert fam.marriage is not None
        assert fam.marriage.date == "5 MAY 1920"

    def test_invalid_header(self):
        result = parse_gedcom(b"This is not a GEDCOM file")
        assert len(result.errors) > 0
        assert "HEAD" in result.errors[0]

    def test_file_too_large(self):
        result = parse_gedcom(b"0 HEAD\n" * 100, max_size_bytes=100)
        assert len(result.errors) > 0
        assert "size" in result.errors[0].lower()

    def test_string_input(self):
        text = MINIMAL_GEDCOM.decode("utf-8")
        result = parse_gedcom(text)
        assert len(result.individuals) == 3

    def test_note_parsing(self):
        gedcom = b"""0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME Test /Person/
1 NOTE First line of note
2 CONT Second line
2 CONC and more text
0 TRLR
"""
        result = parse_gedcom(gedcom)
        assert len(result.individuals) == 1
        assert "First line" in result.individuals[0].note
        assert "Second line" in result.individuals[0].note
        assert "and more text" in result.individuals[0].note

    def test_burial_event(self):
        gedcom = b"""0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME Test /Person/
1 BURI
2 PLAC Cemetery, Town
0 TRLR
"""
        result = parse_gedcom(gedcom)
        assert result.individuals[0].burial is not None
        assert result.individuals[0].burial.place == "Cemetery, Town"

    def test_empty_individuals(self):
        gedcom = b"""0 HEAD
1 SOUR Test
0 TRLR
"""
        result = parse_gedcom(gedcom)
        assert len(result.individuals) == 0
        assert len(result.families) == 0
        assert len(result.errors) == 0

    def test_latin1_encoding(self):
        content = "0 HEAD\n1 CHAR ANSI\n0 @I1@ INDI\n1 NAME Jos\xe9 /Garc\xeda/\n0 TRLR\n"
        raw = content.encode("latin-1")
        result = parse_gedcom(raw)
        assert len(result.individuals) == 1
        assert "Jos" in result.individuals[0].first_name
