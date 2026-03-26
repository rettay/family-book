# FB-028: Source Citations, Evidence, and Date Intelligence

## Objective

Make Family Book credible for serious genealogy research by adding per-person source citations with confidence levels, distinguishing documentary evidence from memory media, and computing age context at life events.

## Why / KPI

**CFLSR impact:** These three features target the "genealogy buff power user" persona — the family member who does the research, enters the data, and motivates others to contribute. Without source citations, the family record lacks research credibility. Without evidence classification, uploaded documents are indistinguishable from vacation photos. Without date intelligence, the app misses the most natural context ("Maria was 23 when she married"). Together these make the difference between a display layer and a research workspace.

**Gap references:** G-07 (source citations), G-09 (document attachment as evidence), G-13 (date math and age display)

## In Scope

### Slice 1: Source Citations and Confidence

- Add `source_detail` (String, 500 chars) to Person model — free-text provenance ("1940 US Census via Ancestry.com", "Aunt Maria at Thanksgiving 2019")
- Add `confidence` (String enum: confirmed, probable, uncertain, unknown) to Person model — defaults to `unknown`
- Neither field is encrypted (source citations are research data, not PII)
- Include both fields in revision snapshots, access control, create/update routes
- Surface in tree sidebar Details tab (Identity section), person profile page, person edit page
- Add to all 3 locales (en, es, ru)
- Add to `PERSON_MUTABLE_FIELDS` in revision service

### Slice 2: Document vs. Evidence Media Classification

- Add `purpose` field to Media model (String enum: memory, document, evidence) — defaults to `memory`
- Migration: single column add to `media` table
- Update media upload flow to include purpose selector (radio buttons or dropdown)
- Update media gallery template to show a visual indicator for documents/evidence (icon or badge)
- Update sidebar media section to optionally filter by purpose
- Add `purpose` to media API responses and media upload/edit endpoints
- Surface document/evidence distinction in person page media section

### Slice 3: Date Math and Age Display

- Create `app/services/date_intelligence_service.py` with functions:
  - `compute_age(birth_date: str, reference_date: str) -> int | None` — years between two dates
  - `compute_current_age(birth_date: str) -> int | None` — age if living
  - `compute_age_at_death(birth_date: str, death_date: str) -> int | None`
  - `enrich_person_ages(person: dict) -> dict` — adds `current_age` or `age_at_death` to person detail
- Add age display to person profile page: "(age 87)" next to birth date, or "(1920-2000, age 80)" for deceased
- Add age context to timeline events: "Maria born (would be 105 today)" or "Jose passed away (age 73)"
- Handle date precision: only compute age for exact or year-month precision, not year-only
- Add age to person API detail response as computed fields
- Add to tree node tooltip (optional enhancement)

## Out of Scope

- Per-field source citations (e.g., "source for birth date" vs "source for death date") — future enhancement
- Automated source verification or external API lookups for citations
- Media OCR or automatic document classification
- Age computation for partial dates (year-only precision)
- Contact expansion (phone_numbers[], addresses[]) from G-22 — deferred separately

## Dependencies

- Person model (S01-S22) — well-established, pattern clear
- Media model (S01) — adding a column follows existing migration pattern
- Timeline service (S21) — date math integrates with event labels
- Date parsing already exists in `timeline_service._parse_date()` — reuse or extract

## Likely Files to Change

### Slice 1
| File | Change |
|------|--------|
| `app/models/person.py` | Add `source_detail`, `confidence` columns |
| `app/schemas.py` | Add fields to PersonCreate, PersonUpdate, PersonDetail |
| `app/access_control.py` | Add 2 entries to `_detail_profile_payload` |
| `app/services/revision_service.py` | Add to PERSON_MUTABLE_FIELDS + serialize/apply |
| `app/routes/persons.py` | Add to create/update/history |
| `app/templates/partials/person_sidebar.html` | Add to Identity section |
| `app/templates/person.html` | Add source citation display section |
| `app/templates/person_edit.html` | Add source_detail textarea + confidence select |
| `app/static/js/tree.js` | Add to saveTreePerson nullableFields |
| `locales/en.json`, `es.json`, `ru.json` | Add ~8 keys |

### Slice 2
| File | Change |
|------|--------|
| `app/models/media.py` | Add `purpose` column |
| `app/routes/media.py` | Accept purpose in upload/update |
| `app/schemas.py` | Add purpose to media schemas |
| `app/templates/partials/media_gallery.html` | Show purpose badge |
| `app/templates/partials/person_sidebar.html` | Purpose indicator in media tab |
| `locales/en.json`, `es.json`, `ru.json` | Add ~6 keys |
| `alembic/versions/XXXX_add_source_and_purpose_fields.py` | Single migration |

### Slice 3
| File | Change |
|------|--------|
| `app/services/date_intelligence_service.py` | New service file |
| `app/schemas.py` | Add computed age fields to PersonDetail |
| `app/routes/persons.py` | Enrich person detail with age |
| `app/services/timeline_service.py` | Add age context to event labels |
| `app/templates/person.html` | Show age next to dates |
| `locales/en.json`, `es.json`, `ru.json` | Add ~5 keys |

### New Files
| File | Purpose |
|------|---------|
| `alembic/versions/XXXX_add_source_and_purpose_fields.py` | Migration for source_detail, confidence, purpose |
| `app/services/date_intelligence_service.py` | Age computation logic |
| `tests/test_source_citations.py` | Slice 1 tests |
| `tests/test_media_purpose.py` | Slice 2 tests |
| `tests/test_date_intelligence.py` | Slice 3 tests |

## Local Validation Commands

```bash
uv run alembic upgrade head
uv run pytest -q                          # Full suite must pass
uv run pytest tests/test_source_citations.py -q
uv run pytest tests/test_media_purpose.py -q
uv run pytest tests/test_date_intelligence.py -q
uv run pytest tests/test_i18n.py -q       # Locale parity
```

## Acceptance Criteria

### Slice 1: Source Citations and Confidence
- [ ] POST /api/persons with source_detail and confidence returns 201 with round-trip
- [ ] PUT /api/persons/{id} updates source_detail and confidence
- [ ] GET /api/persons/{id} returns source_detail and confidence
- [ ] Confidence field accepts only: confirmed, probable, uncertain, unknown
- [ ] Invalid confidence value returns 422
- [ ] Root person returns null for source_detail, default for confidence
- [ ] Revision snapshot includes source_detail and confidence
- [ ] Tree sidebar Identity section shows source_detail and confidence
- [ ] Person profile page shows citation section when source_detail is present
- [ ] Person edit page has source_detail textarea and confidence dropdown

### Slice 2: Document vs. Evidence Media Classification
- [ ] POST /api/media/upload accepts optional purpose parameter (memory, document, evidence)
- [ ] Default purpose is "memory" when not specified
- [ ] GET /api/media/{id} returns purpose field
- [ ] PUT /api/media/{id} can update purpose
- [ ] Media gallery shows visual indicator for document/evidence items
- [ ] Invalid purpose value returns 422

### Slice 3: Date Math and Age Display
- [ ] GET /api/persons/{id} returns current_age for living persons with birth_date
- [ ] GET /api/persons/{id} returns age_at_death for deceased persons with birth and death dates
- [ ] Age is null when birth_date_precision is "year" only
- [ ] Age computes correctly for exact and year-month precision
- [ ] Person profile page displays age in parentheses next to birth date
- [ ] Timeline birth events include current age or "would be X today" context
- [ ] Timeline death events include age at death

## Definition of Done

- All acceptance criteria pass
- `uv run pytest -q` passes with 0 failures (target: ~425+ tests)
- i18n parity across all 3 locales
- No new encrypted fields (source citations are research data, not PII)
- Single migration for all schema changes
- Existing test suite unbroken

## Evaluation Environment

- SQLite test database (auto-created by conftest.py)
- admin_client and member_client fixtures for role-based testing
- Seed data with root person for redaction tests
