# Task Packet - FB-056 Person Edit Form Polish and Bio Integration

## Objective

Complete the person edit form overhaul by integrating inline Trix rich-text bio editing, replacing JSON textareas for education/career/organizations with structured card-based editing, adding an ISO 639-1 searchable language combobox, and polishing section organization and field ordering.

## Why / KPI

- The bio field is currently a plain textarea in the edit form while the wiki editor uses Trix. Education, career, and organizations are raw JSON textareas that no normal user would edit.
- CFLSR improves when contributors can write a rich bio and add education/career data through a natural form interface rather than editing JSON.

Primary KPI:
- make biography and life-story editing accessible to non-technical family members.

Secondary KPI:
- replace freeform language strings with ISO 639-1 controlled vocabulary for consistent data.

## Scope

- In scope:
  - replace bio textarea with inline Trix rich-text editor (same component already used in wiki section editor)
  - replace education JSON textarea with structured card-based editing (institution, degree, field_of_study, year_start, year_end, notes)
  - replace career JSON textarea with structured card-based editing (employer, title, year_start, year_end, location, notes)
  - replace organizations JSON textarea with structured card-based editing (name, role, year_joined, year_left, notes)
  - add ISO 639-1 languages reference data (`app/data/languages.py`) with top 50 languages
  - replace language tag input with searchable combobox that searches by code and display name
  - social platform icon/badge rendering for social account cards (from FB-054)
  - section reordering for logical flow (Identity → Life → Contact → Addresses → Social → Memorial → Story → Education/Career → Physical/Genetic → Medical → Source)
  - i18n for all new labels
- Out of scope:
  - data model changes (done in FB-053)
  - multi-value phone/email/social card creation (done in FB-054)
  - address schema and Places changes (done in FB-055)
  - wiki section editor changes (existing behavior preserved)
  - admixture and medical_conditions card editing (keep as JSON textareas for now; these are power-user fields)

## Task Type

- member-facing form UX enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-054 (card-based editing pattern must be established).
- Can proceed independently of FB-055 (addresses).

## Changed Surfaces

- `person_edit`

## Target Personas

- Primary: `contributing_member`, `genealogy_researcher`
- Safety: `mobile_first_relative`, `family_admin`

## Required Scenario IDs

- `write_rich_biography`
- `add_education_entry`
- `add_career_entry`
- `select_languages_from_vocabulary`
- `save_without_losing_context`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`, `ru`

## Likely Files

- `app/templates/person_edit.html`
- `app/data/languages.py` (new file: ISO 639-1 reference data)
- `app/routes/pages.py` (pass languages list to template context)
- `app/static/css/main.css`
- `locales/en.json`, `locales/es.json`, `locales/ru.json`
- `tests/test_pages.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  polish the edit form with rich text bio, structured life-story editing, and controlled language vocabulary
- Verifier:
  structural review, page-load assertions, i18n checks
- Reference/oracle:
  wiki section editor for Trix pattern; existing card-based pattern from FB-054 for education/career
- Expected evidence:
  page-load tests pass, Trix editor renders for bio, education/career cards render with structured fields, languages combobox populates from ISO data
- Known failure modes / reward hacks:
  - Trix editor loads but content is not serialized on form submission
  - education cards render but JSON serialization format differs from what the API expects
  - language combobox shows codes instead of display names
  - section reordering breaks existing field bindings
- Verifiability class:
  `bounded-judgment`
- Context policy:
  reuse existing Trix CDN and initialization pattern from wiki_edit_section.html; do not add new dependencies

## UI Review Requirements

- Structural oracle:
  - confirm Trix editor initializes for bio field
  - confirm education/career/org cards follow the same pattern as phone/email/social cards
  - confirm languages combobox uses ISO data
- Browser oracle:
  - Trix toolbar renders and bio content persists through save
  - education entry add/remove works and data round-trips
  - language search finds matches by name and code
- Visual/persona oracle:
  - `contributing_member` can write a formatted bio paragraph
  - `genealogy_researcher` can add education and career entries naturally
  - `mobile_first_relative` can navigate the form sections without getting lost
- Required artifacts:
  - test output
  - i18n key coverage confirmation

## Acceptance Criteria

- [ ] Bio field uses Trix rich-text editor inline in the edit form.
- [ ] Bio content from Trix serializes correctly to the API on save and round-trips on reload.
- [ ] Education entries use structured card-based editing (not JSON textarea).
- [ ] Career entries use structured card-based editing (not JSON textarea).
- [ ] Organizations entries use structured card-based editing (not JSON textarea).
- [ ] Languages use a searchable combobox backed by ISO 639-1 data (top 50 languages minimum).
- [ ] Language search works by both display name and ISO code.
- [ ] Social account cards display platform-specific icon or badge where available.
- [ ] Form sections are ordered logically: Identity → Life → Contact → Addresses → Social → Memorial → Story → Education/Career → Physical/Genetic → Medical → Source.
- [ ] i18n keys exist for all new labels in en, es, ru.
- [ ] All existing fields that were working before continue to work.

## Risk and Verification Notes

- Complexity hotspots:
  - Trix editor initialization timing vs form submission serialization
  - education/career card rendering must match the exact Pydantic schema field names
  - section reordering risk: breaking hidden field bindings or JS event listeners
- Likely shallow-pass failure modes:
  - Trix renders but content lost on save
  - language combobox shows ISO codes without display names
  - section reorder breaks memorial toggle or address rendering
- Required verification depth:
  - page-load + bio round-trip + education round-trip + language selection
- Sufficient discriminative power means:
  tests should fail if bio content is lost on save, or if education entries don't match schema.

## Execution Budget

- Builder may explore:
  - Trix initialization pattern from wiki_edit_section.html for reuse
  - whether platform icons can come from Unicode/emoji or require SVG assets
- Builder must escalate if:
  - Trix CDN version conflicts with existing wiki section editor usage
  - education/career schema requires changes to support the card UI
- Material scope drift:
  - data model changes, address changes, wiki editor changes
- Proof obligations before review:
  - bio round-trip proven
  - education/career round-trip proven
  - languages selection proven
  - no existing field regressions

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions on person edit form
- [ ] The form is usable by a non-technical family member without editing JSON
