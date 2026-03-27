"""Tests for app.services.date_parsing — shared date string parser."""

import pytest
from app.services.date_parsing import parse_date_raw_to_iso


class TestISOPassthrough:
    def test_full_iso(self):
        assert parse_date_raw_to_iso("1985-03-15") == ("1985-03-15", "exact")

    def test_year_month_iso(self):
        assert parse_date_raw_to_iso("1985-03") == ("1985-03", "month")


class TestGEDCOMFormats:
    def test_day_month_year(self):
        assert parse_date_raw_to_iso("15 MAR 1985") == ("1985-03-15", "exact")

    def test_month_year(self):
        assert parse_date_raw_to_iso("MAR 1985") == ("1985-03", "month")

    def test_year_only(self):
        assert parse_date_raw_to_iso("1985") == ("1985", "year")


class TestEnglishFormats:
    def test_month_day_year(self):
        assert parse_date_raw_to_iso("March 15, 1985") == ("1985-03-15", "exact")

    def test_month_day_year_no_comma(self):
        assert parse_date_raw_to_iso("March 15 1985") == ("1985-03-15", "exact")

    def test_day_month_year_english(self):
        assert parse_date_raw_to_iso("15 March 1985") == ("1985-03-15", "exact")

    def test_month_year_english(self):
        assert parse_date_raw_to_iso("March 1985") == ("1985-03", "month")

    def test_january(self):
        assert parse_date_raw_to_iso("January 1, 2000") == ("2000-01-01", "exact")


class TestApproximatePrefixes:
    def test_tilde(self):
        iso, prec = parse_date_raw_to_iso("~1960")
        assert iso == "1960"
        assert prec == "approximate"

    def test_about(self):
        iso, prec = parse_date_raw_to_iso("about 1960")
        assert iso == "1960"
        assert prec == "approximate"

    def test_circa(self):
        iso, prec = parse_date_raw_to_iso("circa March 1960")
        assert iso == "1960-03"
        assert prec == "approximate"

    def test_before(self):
        iso, prec = parse_date_raw_to_iso("before 1900")
        assert iso == "1900"
        assert prec == "approximate"

    def test_after_with_date(self):
        iso, prec = parse_date_raw_to_iso("AFT 15 JAN 1920")
        assert iso == "1920-01-15"
        assert prec == "approximate"

    def test_abt_gedcom(self):
        iso, prec = parse_date_raw_to_iso("ABT 1875")
        assert iso == "1875"
        assert prec == "approximate"


class TestEdgeCases:
    def test_empty(self):
        assert parse_date_raw_to_iso("") == (None, None)

    def test_none(self):
        assert parse_date_raw_to_iso(None) == (None, None)

    def test_whitespace(self):
        assert parse_date_raw_to_iso("   ") == (None, None)

    def test_garbage(self):
        assert parse_date_raw_to_iso("not a date") == (None, None)
