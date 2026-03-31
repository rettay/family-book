# Task Packet - FB-067 Place History Timeline

## Objective

Add a residence history field to person records so users can track where someone lived over time, with date ranges and descriptions (e.g., "Boston, 1995–2003, attended MIT").

## Why / KPI

- The current single `residence_place` field only captures where someone lives now. Family researchers need the full timeline.
- Place history is one of the most common genealogy data points — it connects people to events, education, career, and each other.
- CFLSR improves when the family record captures the richness of a person's life journey, not just their current state.

## Scope

- In scope:
  - New `PlaceHistoryEntry` Pydantic sub-model: place, country_code, from_year, to_year, description, place_latitude, place_longitude, place_id, is_current
  - New `_place_history` JSON text column on Person model (same pattern as education/career)
  - Alembic migration for the new column
  - Card-based editing in the person edit page (same pattern as education/career cards)
  - Card-based editing in the tree sidebar Details tab
  - Wiki person page section displaying place history chronologically
  - Google Places autocomplete on the place field within each card (if Places enabled)
  - i18n across en, es, ru, it, zh
- Out of scope:
  - Map visualization of place history (future — integrate with /map page)
  - Automatic migration of existing residence_place into place_history
  - Timeline page integration

## Task Type

- data model enhancement + member-facing UI

## Likely Files

- `app/schemas.py` (PlaceHistoryEntry)
- `app/models/person.py` (place_history JSON column + property)
- `alembic/versions/` (new migration)
- `app/routes/persons.py` (accept place_history in PUT)
- `app/templates/person_edit.html` (card editor section)
- `app/templates/partials/person_sidebar.html` (card editor in Details tab)
- `app/services/wiki_service.py` (place history wiki section)
- `app/templates/wiki_person.html` (render place history)
- `locales/*.json` (new keys)
- `tests/test_api.py` or `tests/test_pages.py`

## Acceptance Criteria

- [ ] PlaceHistoryEntry sub-model with place, country_code, from_year, to_year, description, coordinates, is_current.
- [ ] Person model has place_history JSON column with getter/setter.
- [ ] Alembic migration adds the column.
- [ ] Person edit page has card-based place history editor (add/remove cards).
- [ ] Tree sidebar Details tab has place history card editor.
- [ ] Wiki person page renders place history chronologically.
- [ ] Google Places autocomplete works on place fields within cards (when enabled).
- [ ] PUT /api/persons/{id} accepts place_history array.
- [ ] i18n keys across 5 locales.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Migration runs cleanly
- [ ] i18n parity maintained
