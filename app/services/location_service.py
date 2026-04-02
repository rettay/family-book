from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

import httpx
import pycountry

from app.config import get_settings


@dataclass(frozen=True)
class ResolvedLocation:
    place: str | None
    country_code: str | None
    latitude: float | None
    longitude: float | None
    source: str | None


KNOWN_PLACE_COORDINATES: dict[tuple[str, str], tuple[float, float]] = {
    ("austin", "US"): (30.2672, -97.7431),
    ("barcelona", "ES"): (41.3874, 2.1686),
    ("boston", "US"): (42.3601, -71.0589),
    ("chicago", "US"): (41.8781, -87.6298),
    ("dallas", "US"): (32.7767, -96.7970),
    ("denver", "US"): (39.7392, -104.9903),
    ("guadalajara", "MX"): (20.6597, -103.3496),
    ("mexico city", "MX"): (19.4326, -99.1332),
    ("phoenix", "US"): (33.4484, -112.0740),
    ("portland", "US"): (45.5152, -122.6784),
    ("salem", "US"): (44.9429, -123.0351),
    ("seattle", "US"): (47.6062, -122.3321),
    ("springfield", "US"): (39.7817, -89.6501),
    ("toronto", "CA"): (43.6532, -79.3832),
}

_COUNTRY_ALIASES = {
    "england": "GB",
    "great britain": "GB",
    "russia": "RU",
    "south korea": "KR",
    "north korea": "KP",
    "u.k.": "GB",
    "uk": "GB",
    "u.s.": "US",
    "u.s.a.": "US",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
    "viet nam": "VN",
}


def _ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_value = re.sub(r"[^a-z0-9,\s]+", " ", ascii_value)
    ascii_value = re.sub(r"\s+", " ", ascii_value)
    return ascii_value.strip(" ,")


def normalize_place_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    return text or None


def _lookup_country_by_name(value: str) -> str | None:
    slug = _ascii_slug(value)
    if not slug:
        return None
    alias = _COUNTRY_ALIASES.get(slug)
    if alias:
        return alias

    fuzzy_match = None
    if len(value) > 2:
        try:
            fuzzy_match = pycountry.countries.search_fuzzy(value)[0]
        except LookupError:
            fuzzy_match = None

    for lookup in (
        pycountry.countries.get(name=value),
        pycountry.countries.get(alpha_2=value.upper()),
        pycountry.countries.get(alpha_3=value.upper()),
        pycountry.countries.get(common_name=value),
        pycountry.countries.get(official_name=value),
        fuzzy_match,
    ):
        if lookup is not None:
            return lookup.alpha_2
    return None


def normalize_country_code(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) == 2 and text.isalpha():
        candidate = text.upper()
        return candidate if pycountry.countries.get(alpha_2=candidate) else None
    if len(text) == 3 and text.isalpha():
        country = pycountry.countries.get(alpha_3=text.upper())
        return country.alpha_2 if country else None
    return _lookup_country_by_name(text)


def coerce_coordinate(value: object, *, latitude: bool) -> float | None:
    if value in (None, ""):
        return None
    try:
        coordinate = float(value)
    except (TypeError, ValueError):
        return None
    if latitude and -90 <= coordinate <= 90:
        return round(coordinate, 6)
    if not latitude and -180 <= coordinate <= 180:
        return round(coordinate, 6)
    return None


def infer_country_code(place: str | None, country_code: str | None) -> str | None:
    normalized_country = normalize_country_code(country_code)
    if normalized_country:
        return normalized_country
    normalized_place = normalize_place_text(place)
    if not normalized_place or "," not in normalized_place:
        return None
    trailing_token = normalized_place.rsplit(",", 1)[-1].strip()
    return normalize_country_code(trailing_token)


def lookup_known_place(place: str | None, country_code: str | None) -> tuple[float, float] | None:
    normalized_place = normalize_place_text(place)
    normalized_country = normalize_country_code(country_code)
    if not normalized_place:
        return None

    place_slug = _ascii_slug(normalized_place)
    primary_slug = place_slug.split(",", 1)[0].strip()

    if normalized_country:
        match = KNOWN_PLACE_COORDINATES.get((primary_slug, normalized_country))
        if match:
            return match
        return None

    unique_match: tuple[float, float] | None = None
    for (known_slug, _known_country), coordinates in KNOWN_PLACE_COORDINATES.items():
        if known_slug == primary_slug:
            if unique_match is not None:
                return None
            unique_match = coordinates
    return unique_match


def _extract_country_code(address_components: list[dict]) -> str | None:
    for component in address_components:
        types = component.get("types") or []
        if "country" in types:
            return normalize_country_code(component.get("short_name"))
    return None


async def google_geocode_place(
    place: str | None,
    country_code: str | None = None,
) -> ResolvedLocation | None:
    settings = get_settings()
    normalized_place = normalize_place_text(place)
    if not normalized_place or not settings.google_geocoding_enabled:
        return None

    normalized_country = normalize_country_code(country_code)
    params = {
        "address": normalized_place,
        "key": settings.google_maps_server_api_key_value,
    }
    if normalized_country:
        params["components"] = f"country:{normalized_country}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params=params,
        )
        response.raise_for_status()
        payload = response.json()

    if payload.get("status") != "OK" or not payload.get("results"):
        return None

    result = payload["results"][0]
    geometry = result.get("geometry", {}).get("location", {})
    latitude = coerce_coordinate(geometry.get("lat"), latitude=True)
    longitude = coerce_coordinate(geometry.get("lng"), latitude=False)
    if latitude is None or longitude is None:
        return None

    resolved_country = _extract_country_code(result.get("address_components") or [])
    return ResolvedLocation(
        place=normalized_place,
        country_code=resolved_country or normalized_country,
        latitude=latitude,
        longitude=longitude,
        source="google_geocode",
    )


async def resolve_location(
    *,
    place: str | None,
    country_code: str | None,
    latitude: object = None,
    longitude: object = None,
) -> ResolvedLocation:
    normalized_place = normalize_place_text(place)
    normalized_country = infer_country_code(normalized_place, country_code)
    resolved_latitude = coerce_coordinate(latitude, latitude=True)
    resolved_longitude = coerce_coordinate(longitude, latitude=False)

    if normalized_place is None:
        return ResolvedLocation(
            place=None,
            country_code=normalized_country,
            latitude=None,
            longitude=None,
            source=None,
        )

    if resolved_latitude is not None and resolved_longitude is not None:
        return ResolvedLocation(
            place=normalized_place,
            country_code=normalized_country,
            latitude=resolved_latitude,
            longitude=resolved_longitude,
            source="provided_coordinates",
        )

    known_coordinates = lookup_known_place(normalized_place, normalized_country)
    if known_coordinates:
        return ResolvedLocation(
            place=normalized_place,
            country_code=normalized_country,
            latitude=known_coordinates[0],
            longitude=known_coordinates[1],
            source="known_place_catalog",
        )

    geocoded = await google_geocode_place(normalized_place, normalized_country)
    if geocoded is not None:
        return geocoded

    return ResolvedLocation(
        place=normalized_place,
        country_code=normalized_country,
        latitude=None,
        longitude=None,
        source=None,
    )
