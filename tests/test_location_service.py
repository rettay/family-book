from app.services.location_service import (
    lookup_known_place,
    normalize_country_code,
    resolve_location,
)


def test_normalize_country_code_accepts_names_and_aliases():
    assert normalize_country_code("Canada") == "CA"
    assert normalize_country_code("usa") == "US"
    assert normalize_country_code("GBR") == "GB"


def test_lookup_known_place_matches_seeded_city():
    assert lookup_known_place("Toronto", "Canada") == (43.6532, -79.3832)


def test_lookup_known_place_does_not_cross_country_when_explicit_country_is_supplied():
    assert lookup_known_place("Toronto", "US") is None


async def test_resolve_location_uses_known_place_catalog_without_google():
    resolved = await resolve_location(
        place="Barcelona",
        country_code="Spain",
    )

    assert resolved.country_code == "ES"
    assert resolved.latitude == 41.3874
    assert resolved.longitude == 2.1686
    assert resolved.source == "known_place_catalog"


async def test_resolve_location_preserves_explicit_country_when_catalog_city_is_known_elsewhere():
    resolved = await resolve_location(
        place="Toronto",
        country_code="US",
    )

    assert resolved.country_code == "US"
    assert resolved.latitude is None
    assert resolved.longitude is None
    assert resolved.source is None
