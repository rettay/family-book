# Task Packet - FB-068 Language Input Autocomplete

## Objective

Wire the language input on the person edit page and tree sidebar to a searchable autocomplete backed by the existing languages.json vocabulary, so users can find and select languages by typing instead of guessing ISO codes.

## Why / KPI

- The current language input accepts free text with no guidance. Users don't know what values are valid.
- languages.json already has 50+ languages with display names — this data just isn't exposed as autocomplete suggestions.
- CFLSR improves when data entry is guided rather than freeform.

## Scope

- In scope:
  - Autocomplete/combobox on the languages field in person edit page
  - Autocomplete on the languages field in tree sidebar Details tab
  - Search by language name (English, Spanish, etc.) — filter as user types
  - Multi-select: person can speak multiple languages (existing behavior)
  - Chip display for selected languages (existing behavior — enhance with autocomplete)
- Out of scope:
  - Adding new languages to languages.json
  - Language proficiency levels

## Task Type

- member-facing UX enhancement

## Likely Files

- `app/static/js/main.js` or `app/static/js/tree.js` (autocomplete logic)
- `app/templates/person_edit.html` (language input section)
- `app/templates/partials/person_sidebar.html` (language input in Details)
- `app/static/languages.json` (data source — already exists)

## Acceptance Criteria

- [ ] Typing in the language field shows filtered suggestions from languages.json.
- [ ] Selecting a suggestion adds it as a chip/tag.
- [ ] Multiple languages can be selected.
- [ ] Existing language chips can be removed.
- [ ] Works on both person edit page and tree sidebar.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] No regression on existing language field behavior
