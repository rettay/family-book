"""External genealogy record search — free API clients.

Integrates with:
- Chronicling America (USA newspapers, no auth)
- NARA Catalog (USA federal records, no auth)
- Trove (Australian newspapers, API key)
- DPLA (USA cross-institutional archives, API key)
- FamilySearch (all countries, OAuth 2 — stub for now)
- Antenati (Italian civil records, IIIF — guided lookup)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Simple in-memory TTL cache: key -> (timestamp, data)
_cache: dict[str, tuple[float, list[dict]]] = {}
_CACHE_TTL = 24 * 60 * 60  # 24 hours


def _cache_key(source: str, params: dict) -> str:
    raw = f"{source}:{sorted(params.items())}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _get_cached(source: str, params: dict) -> list[dict] | None:
    key = _cache_key(source, params)
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < _CACHE_TTL:
        return entry[1]
    if entry:
        del _cache[key]
    return None


def _set_cached(source: str, params: dict, data: list[dict]) -> None:
    key = _cache_key(source, params)
    _cache[key] = (time.time(), data)


@dataclass
class SearchParams:
    first_name: str = ""
    last_name: str = ""
    birth_date: str = ""
    birth_place: str = ""
    query: str = ""  # freeform override


@dataclass
class SearchResult:
    source: str
    title: str
    date: str = ""
    location: str = ""
    snippet: str = ""
    url: str = ""
    record_type: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class SourceResults:
    source: str
    results: list[SearchResult] = field(default_factory=list)
    total_count: int = 0
    error: str = ""
    available: bool = True


# ---------------------------------------------------------------------------
# Chronicling America (Library of Congress — USA newspapers)
# ---------------------------------------------------------------------------

async def search_chronicling_america(params: SearchParams) -> SourceResults:
    """Search digitized US newspapers 1777–1963."""
    source = "chronicling_america"
    query = params.query or f"{params.first_name} {params.last_name}".strip()
    if not query:
        return SourceResults(source=source, error="No search query")

    search_params = {"andtext": query, "format": "json", "page": "1"}
    cached = _get_cached(source, search_params)
    if cached is not None:
        return SourceResults(source=source, results=[SearchResult(**r) for r in cached], total_count=len(cached))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://chroniclingamerica.loc.gov/search/pages/results/",
                params=search_params,
            )
            resp.raise_for_status()
            data = resp.json()

        items = data.get("items", [])[:20]
        results = []
        for item in items:
            results.append(SearchResult(
                source=source,
                title=item.get("title", "Untitled"),
                date=item.get("date", ""),
                location=item.get("state", [""])[0] if isinstance(item.get("state"), list) else "",
                snippet=item.get("ocr_eng", "")[:200],
                url=item.get("url", ""),
                record_type="newspaper",
            ))

        _set_cached(source, search_params, [_result_to_dict(r) for r in results])
        return SourceResults(source=source, results=results, total_count=data.get("totalItems", len(results)))

    except Exception as e:
        logger.warning("Chronicling America search failed: %s", e)
        return SourceResults(source=source, error=str(e))


# ---------------------------------------------------------------------------
# NARA Catalog (National Archives — USA federal records)
# ---------------------------------------------------------------------------

async def search_nara(params: SearchParams) -> SourceResults:
    """Search National Archives catalog."""
    source = "nara"
    query = params.query or f"{params.first_name} {params.last_name}".strip()
    if not query:
        return SourceResults(source=source, error="No search query")

    search_params = {"q": query, "limit": "20"}
    cached = _get_cached(source, search_params)
    if cached is not None:
        return SourceResults(source=source, results=[SearchResult(**r) for r in cached], total_count=len(cached))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://catalog.archives.gov/api/v2/",
                params=search_params,
            )
            resp.raise_for_status()
            data = resp.json()

        body = data.get("body", {})
        hits = body.get("hits", {}).get("hits", [])[:20] if isinstance(body, dict) else []
        results = []
        for hit in hits:
            src = hit.get("_source", {})
            desc = src.get("description", {})
            results.append(SearchResult(
                source=source,
                title=desc.get("title", "Untitled") if isinstance(desc, dict) else str(desc)[:100],
                date=str(desc.get("productionDateArray", [{}])[0].get("proposableQualifiableDate", {}).get("logicalDate", "")) if isinstance(desc, dict) and desc.get("productionDateArray") else "",
                location="National Archives",
                url=f"https://catalog.archives.gov/id/{hit.get('_id', '')}",
                record_type=desc.get("levelOfDescription", "record") if isinstance(desc, dict) else "record",
            ))

        _set_cached(source, search_params, [_result_to_dict(r) for r in results])
        total = body.get("hits", {}).get("total", {}).get("value", len(results)) if isinstance(body, dict) else len(results)
        return SourceResults(source=source, results=results, total_count=total)

    except Exception as e:
        logger.warning("NARA search failed: %s", e)
        return SourceResults(source=source, error=str(e))


# ---------------------------------------------------------------------------
# Trove (National Library of Australia — newspapers)
# ---------------------------------------------------------------------------

async def search_trove(params: SearchParams) -> SourceResults:
    """Search digitized Australian newspapers."""
    source = "trove"
    settings = get_settings()
    api_key = getattr(settings, "TROVE_API_KEY", "")
    if not api_key:
        return SourceResults(source=source, available=False, error="Trove API key not configured")

    query = params.query or f"{params.first_name} {params.last_name}".strip()
    if not query:
        return SourceResults(source=source, error="No search query")

    search_params = {"q": query, "category": "newspaper", "encoding": "json", "n": "20", "key": api_key}
    cached = _get_cached(source, {"q": query, "category": "newspaper"})
    if cached is not None:
        return SourceResults(source=source, results=[SearchResult(**r) for r in cached], total_count=len(cached))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.trove.nla.gov.au/v3/result",
                params=search_params,
            )
            resp.raise_for_status()
            data = resp.json()

        category = data.get("category", [{}])
        records = []
        if isinstance(category, list) and category:
            records = category[0].get("records", {}).get("article", [])[:20]

        results = []
        for rec in records:
            results.append(SearchResult(
                source=source,
                title=rec.get("heading", "Untitled"),
                date=rec.get("date", ""),
                location=rec.get("title", {}).get("value", "") if isinstance(rec.get("title"), dict) else "",
                snippet=rec.get("snippet", "")[:200],
                url=rec.get("troveUrl", ""),
                record_type="newspaper",
            ))

        _set_cached(source, {"q": query, "category": "newspaper"}, [_result_to_dict(r) for r in results])
        total_str = category[0].get("records", {}).get("total", "0") if isinstance(category, list) and category else "0"
        return SourceResults(source=source, results=results, total_count=int(total_str) if str(total_str).isdigit() else len(results))

    except Exception as e:
        logger.warning("Trove search failed: %s", e)
        return SourceResults(source=source, error=str(e))


# ---------------------------------------------------------------------------
# DPLA (Digital Public Library of America)
# ---------------------------------------------------------------------------

async def search_dpla(params: SearchParams) -> SourceResults:
    """Search across 4,000+ US libraries, archives, and museums."""
    source = "dpla"
    settings = get_settings()
    api_key = getattr(settings, "DPLA_API_KEY", "")
    if not api_key:
        return SourceResults(source=source, available=False, error="DPLA API key not configured")

    query = params.query or f"{params.first_name} {params.last_name}".strip()
    if not query:
        return SourceResults(source=source, error="No search query")

    search_params = {"q": query, "page_size": "20", "api_key": api_key}
    cached = _get_cached(source, {"q": query})
    if cached is not None:
        return SourceResults(source=source, results=[SearchResult(**r) for r in cached], total_count=len(cached))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.dp.la/v2/items",
                params=search_params,
            )
            resp.raise_for_status()
            data = resp.json()

        docs = data.get("docs", [])[:20]
        results = []
        for doc in docs:
            src = doc.get("sourceResource", {})
            title = src.get("title", ["Untitled"])
            if isinstance(title, list):
                title = title[0] if title else "Untitled"
            date_val = src.get("date", [{}])
            if isinstance(date_val, list) and date_val:
                date_val = date_val[0].get("displayDate", "") if isinstance(date_val[0], dict) else str(date_val[0])
            else:
                date_val = ""
            provider = doc.get("provider", {}).get("name", "") if isinstance(doc.get("provider"), dict) else ""
            results.append(SearchResult(
                source=source,
                title=str(title),
                date=str(date_val),
                location=provider,
                url=doc.get("isShownAt", ""),
                record_type=str(src.get("type", "item")),
            ))

        _set_cached(source, {"q": query}, [_result_to_dict(r) for r in results])
        return SourceResults(source=source, results=results, total_count=data.get("count", len(results)))

    except Exception as e:
        logger.warning("DPLA search failed: %s", e)
        return SourceResults(source=source, error=str(e))


# ---------------------------------------------------------------------------
# FamilySearch (stub — requires OAuth 2 app registration)
# ---------------------------------------------------------------------------

async def search_familysearch(params: SearchParams) -> SourceResults:
    """FamilySearch historical record search (stub).

    Full integration requires OAuth 2 app registration and user authentication.
    For now, returns a helpful link to search FamilySearch directly.
    """
    source = "familysearch"
    query = f"{params.first_name} {params.last_name}".strip()
    if not query:
        return SourceResults(source=source, error="No search query")

    # Build a direct search URL for the user
    import urllib.parse
    fs_params = {"q.givenName": params.first_name, "q.surname": params.last_name}
    if params.birth_date:
        fs_params["q.birthLikeDate.from"] = params.birth_date[:4]
        fs_params["q.birthLikeDate.to"] = params.birth_date[:4]
    if params.birth_place:
        fs_params["q.birthLikePlace"] = params.birth_place

    search_url = "https://www.familysearch.org/search/record/results?" + urllib.parse.urlencode(fs_params)

    results = [SearchResult(
        source=source,
        title=f"Search FamilySearch for {query}",
        snippet="FamilySearch requires a free account. Click to search their historical records directly.",
        url=search_url,
        record_type="link",
    )]

    return SourceResults(source=source, results=results, total_count=1)


# ---------------------------------------------------------------------------
# Antenati (Italian civil records — guided IIIF lookup)
# ---------------------------------------------------------------------------

async def search_antenati(params: SearchParams) -> SourceResults:
    """Antenati guided lookup for Italian civil records.

    Not a search API — provides links to browse digitized registers
    by comune and year range.
    """
    source = "antenati"
    place = params.birth_place or params.query
    if not place:
        return SourceResults(source=source, error="Birth place required for Antenati lookup")

    # Antenati has a browsable catalog — provide direct link
    import urllib.parse
    base_url = "https://www.antenati.san.beniculturali.it/search-registry/"
    search_url = base_url + "?" + urllib.parse.urlencode({"comune": place})

    results = [SearchResult(
        source=source,
        title=f"Browse Antenati registers for {place}",
        snippet="Browse digitized Italian civil records (birth, marriage, death registers). Antenati provides IIIF image access to original documents.",
        url=search_url,
        record_type="link",
    )]

    return SourceResults(source=source, results=results, total_count=1)


# ---------------------------------------------------------------------------
# Parallel search across all sources
# ---------------------------------------------------------------------------

ALL_SOURCES = {
    "chronicling_america": search_chronicling_america,
    "nara": search_nara,
    "trove": search_trove,
    "dpla": search_dpla,
    "familysearch": search_familysearch,
    "antenati": search_antenati,
}


async def search_all_sources(params: SearchParams) -> list[SourceResults]:
    """Run searches across all configured sources in parallel."""
    tasks = [fn(params) for fn in ALL_SOURCES.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    source_results = []
    for source_name, result in zip(ALL_SOURCES.keys(), results):
        if isinstance(result, Exception):
            logger.warning("Search source %s raised: %s", source_name, result)
            source_results.append(SourceResults(source=source_name, error=str(result)))
        else:
            source_results.append(result)

    return source_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result_to_dict(r: SearchResult) -> dict:
    return {
        "source": r.source,
        "title": r.title,
        "date": r.date,
        "location": r.location,
        "snippet": r.snippet,
        "url": r.url,
        "record_type": r.record_type,
    }


def source_results_to_dict(sr: SourceResults) -> dict:
    return {
        "source": sr.source,
        "results": [_result_to_dict(r) for r in sr.results],
        "total_count": sr.total_count,
        "error": sr.error,
        "available": sr.available,
    }
