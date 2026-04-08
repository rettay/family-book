"""Research service — source availability and metadata."""

from __future__ import annotations

from app.config import get_settings

# Source definitions with metadata
_SOURCE_DEFINITIONS = [
    {
        "id": "chronicling_america",
        "name": "Chronicling America",
        "description": "Digitized US newspapers 1777-1963 from the Library of Congress",
        "coverage": "United States",
        "requires_key": False,
        "mode": "search",
    },
    {
        "id": "nara",
        "name": "NARA Catalog",
        "description": "US National Archives federal records, documents, and photographs",
        "coverage": "United States",
        "requires_key": False,
        "mode": "search",
    },
    {
        "id": "trove",
        "name": "Trove",
        "description": "Australian newspapers, books, images, and archives",
        "coverage": "Australia",
        "requires_key": True,
        "env_var": "TROVE_API_KEY",
        "mode": "search",
    },
    {
        "id": "dpla",
        "name": "DPLA",
        "description": "Digital Public Library of America — 4,000+ US libraries and archives",
        "coverage": "United States",
        "requires_key": True,
        "env_var": "DPLA_API_KEY",
        "mode": "search",
    },
    {
        "id": "familysearch",
        "name": "FamilySearch",
        "description": "Historical records from the world's largest genealogy organization",
        "coverage": "Worldwide",
        "requires_key": True,
        "env_var": "FAMILYSEARCH_APP_KEY",
        "mode": "search",
    },
    {
        "id": "antenati",
        "name": "Antenati",
        "description": "Digitized Italian civil records — birth, marriage, and death registers",
        "coverage": "Italy",
        "requires_key": False,
        "mode": "guided_lookup",
    },
    {
        "id": "cemla",
        "name": "CEMLA",
        "description": "Centro de Estudios Migratorios Latinoamericanos — Argentine immigration passenger lists",
        "coverage": "Argentina",
        "requires_key": False,
        "mode": "guided_lookup",
    },
]


def get_available_sources() -> list[dict]:
    """Return source metadata with configuration status."""
    settings = get_settings()
    sources = []
    for defn in _SOURCE_DEFINITIONS:
        source = {
            "id": defn["id"],
            "name": defn["name"],
            "description": defn["description"],
            "coverage": defn["coverage"],
            "configured": True,
            "mode": defn["mode"],
        }
        if defn.get("requires_key"):
            env_var = defn["env_var"]
            value = getattr(settings, env_var, "")
            source["configured"] = bool(value)
        sources.append(source)
    return sources
