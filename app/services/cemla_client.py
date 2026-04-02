"""CEMLA immigration record search client.

CEMLA (Centro de Estudios Migratorios Latinoamericanos) hosts 4.4M
Argentine immigration records. No API available — we provide a pre-filled
search URL as the primary approach, with optional HTML parsing if the
site structure is stable.

Rate limited to max 2 requests per minute to respect the nonprofit.
Results cached for 7 days.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

# Rate limiting: track last request timestamp
_last_request_time: float = 0.0
_MIN_INTERVAL = 30.0  # 2 per minute = 30 seconds apart

# Cache with 7-day TTL
_cemla_cache: dict[str, tuple[float, list[dict]]] = {}
_CEMLA_CACHE_TTL = 7 * 24 * 60 * 60  # 7 days

# CEMLA search URL
CEMLA_SEARCH_URL = "https://cemla.com/buscador/"


@dataclass
class CemlaResult:
    passenger_name: str = ""
    ship_name: str = ""
    arrival_date: str = ""
    departure_port: str = ""
    arrival_port: str = ""
    nationality: str = ""
    source_url: str = ""


@dataclass
class CemlaSearchResponse:
    results: list[CemlaResult] = field(default_factory=list)
    total_count: int = 0
    error: str = ""
    fallback_url: str = ""
    used_cache: bool = False


def _cache_key(surname: str, given_name: str, year_from: str, year_to: str) -> str:
    raw = f"cemla:{surname.lower()}:{given_name.lower()}:{year_from}:{year_to}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _get_cached(surname: str, given_name: str, year_from: str, year_to: str) -> list[dict] | None:
    key = _cache_key(surname, given_name, year_from, year_to)
    entry = _cemla_cache.get(key)
    if entry and (time.time() - entry[0]) < _CEMLA_CACHE_TTL:
        return entry[1]
    if entry:
        del _cemla_cache[key]
    return None


def _set_cached(surname: str, given_name: str, year_from: str, year_to: str, data: list[dict]) -> None:
    key = _cache_key(surname, given_name, year_from, year_to)
    _cemla_cache[key] = (time.time(), data)


def build_cemla_url(surname: str, given_name: str = "", year_from: str = "", year_to: str = "") -> str:
    """Build a pre-filled CEMLA search URL."""
    import urllib.parse
    params = {}
    if surname:
        params["apellido"] = surname
    if given_name:
        params["nombre"] = given_name
    if year_from:
        params["anio_desde"] = year_from
    if year_to:
        params["anio_hasta"] = year_to
    return CEMLA_SEARCH_URL + ("?" + urllib.parse.urlencode(params) if params else "")


async def search_cemla(
    surname: str,
    given_name: str = "",
    year_from: str = "",
    year_to: str = "",
) -> CemlaSearchResponse:
    """Search CEMLA immigration records.

    Primary approach: provide a pre-filled search URL for the user.
    If the site structure is detected as stable, attempt HTML parsing.
    Falls back gracefully to link-out.
    """
    global _last_request_time

    if not surname:
        return CemlaSearchResponse(error="Surname is required")

    fallback_url = build_cemla_url(surname, given_name, year_from, year_to)

    # Check cache
    cached = _get_cached(surname, given_name, year_from, year_to)
    if cached is not None:
        return CemlaSearchResponse(
            results=[CemlaResult(**r) for r in cached],
            total_count=len(cached),
            fallback_url=fallback_url,
            used_cache=True,
        )

    # Rate limit check
    now = time.time()
    if now - _last_request_time < _MIN_INTERVAL:
        return CemlaSearchResponse(
            fallback_url=fallback_url,
            error="Rate limited — please use the direct link to search CEMLA",
        )

    # Attempt HTML fetch and parse
    try:
        _last_request_time = now

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(
                CEMLA_SEARCH_URL,
                params={
                    "apellido": surname,
                    "nombre": given_name,
                    "anio_desde": year_from,
                    "anio_hasta": year_to,
                },
                headers={"User-Agent": "FamilyBook/1.0 (genealogy research tool)"},
            )
            resp.raise_for_status()

        results = _parse_cemla_html(resp.text)
        if results:
            result_dicts = [_result_to_dict(r) for r in results]
            _set_cached(surname, given_name, year_from, year_to, result_dicts)
            return CemlaSearchResponse(
                results=results,
                total_count=len(results),
                fallback_url=fallback_url,
            )

        # HTML parsed but no results found — could be empty or structure changed
        return CemlaSearchResponse(
            fallback_url=fallback_url,
            error="No results found. Try searching CEMLA directly using the link below.",
        )

    except Exception as e:
        logger.warning("CEMLA search failed, using fallback: %s", e)
        return CemlaSearchResponse(
            fallback_url=fallback_url,
            error=f"Could not reach CEMLA — use the direct search link below.",
        )


def _parse_cemla_html(html: str) -> list[CemlaResult]:
    """Best-effort parse of CEMLA search results HTML.

    CEMLA's site structure may change at any time. If parsing fails,
    we return an empty list and the caller uses the fallback URL.
    """
    results = []
    try:
        # Look for table rows with passenger data
        # This is intentionally conservative — we'd rather return empty
        # and fall back to the link than mis-parse data
        import re

        # Look for result table rows (common pattern: <tr> with <td> cells)
        table_match = re.search(r'<table[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            return results

        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match.group(1), re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 4:
                # Strip HTML tags from cell contents
                clean = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                result = CemlaResult(
                    passenger_name=clean[0] if len(clean) > 0 else "",
                    ship_name=clean[1] if len(clean) > 1 else "",
                    arrival_date=clean[2] if len(clean) > 2 else "",
                    departure_port=clean[3] if len(clean) > 3 else "",
                    arrival_port=clean[4] if len(clean) > 4 else "",
                    nationality=clean[5] if len(clean) > 5 else "",
                    source_url=CEMLA_SEARCH_URL,
                )
                results.append(result)
    except Exception as e:
        logger.debug("CEMLA HTML parsing failed: %s", e)

    return results


def _result_to_dict(r: CemlaResult) -> dict:
    return {
        "passenger_name": r.passenger_name,
        "ship_name": r.ship_name,
        "arrival_date": r.arrival_date,
        "departure_port": r.departure_port,
        "arrival_port": r.arrival_port,
        "nationality": r.nationality,
        "source_url": r.source_url,
    }


def cemla_result_to_api_dict(r: CemlaResult) -> dict:
    return _result_to_dict(r)
