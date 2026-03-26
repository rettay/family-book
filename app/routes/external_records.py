"""External genealogy record search endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.models.person import Person
from app.services.external_records import (
    ALL_SOURCES,
    SearchParams,
    search_all_sources,
    source_results_to_dict,
)
from app.services.cemla_client import (
    search_cemla,
    build_cemla_url,
    cemla_result_to_api_dict,
)

router = APIRouter(prefix="/api/external-records", tags=["external-records"])
logger = logging.getLogger(__name__)


@router.get("/search")
async def search_external_records(
    person_id: str | None = Query(None, description="Person ID to pre-fill search from"),
    q: str = Query("", description="Freeform search query override"),
    source: str = Query("", description="Single source to search (empty = all)"),
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Search external genealogy databases for records matching a person."""
    params = SearchParams(query=q)

    if person_id:
        from sqlalchemy import select
        result = await db.execute(
            select(Person).where(Person.id == person_id, Person.lifecycle_state == "active")
        )
        person = result.scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        params.first_name = person.first_name or ""
        params.last_name = person.last_name or ""
        params.birth_date = person.birth_date or ""
        params.birth_place = person.birth_place or ""

    if not params.query and not params.first_name and not params.last_name:
        raise HTTPException(status_code=400, detail="Provide person_id or query parameter")

    if source and source in ALL_SOURCES:
        # Search a single source
        fn = ALL_SOURCES[source]
        result = await fn(params)
        return {"sources": [source_results_to_dict(result)]}

    # Search all sources in parallel
    results = await search_all_sources(params)
    return {"sources": [source_results_to_dict(r) for r in results]}


@router.get("/cemla")
async def search_cemla_records(
    surname: str = Query(..., min_length=1, description="Passenger surname"),
    given_name: str = Query("", description="Passenger given name"),
    year_from: str = Query("", description="Year range start"),
    year_to: str = Query("", description="Year range end"),
    current_user: Person = Depends(require_auth),
):
    """Search CEMLA Argentine immigration records."""
    result = await search_cemla(surname, given_name, year_from, year_to)
    return {
        "results": [cemla_result_to_api_dict(r) for r in result.results],
        "total_count": result.total_count,
        "error": result.error,
        "fallback_url": result.fallback_url,
        "used_cache": result.used_cache,
    }
