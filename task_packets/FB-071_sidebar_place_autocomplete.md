# Task Packet - FB-071 Sidebar Place Autocomplete

## Objective

Extend Google Places autocomplete to the birth_place, residence_place, and burial_place fields in the tree sidebar Details tab, so users get suggestions and auto-populated coordinates as they type.

## Why / KPI

- The person edit page already has Places autocomplete on address fields, but the tree sidebar (the primary editing surface) does not.
- Users editing in the sidebar must type exact place names with no guidance, and coordinates aren't captured.
- CFLSR improves when the most common editing surface has the same capabilities as the full form.

## Scope

- In scope:
  - Google Places autocomplete on birth_place, residence_place, and burial_place inputs in the tree sidebar Details tab
  - Auto-populate country_code and coordinates from the selected place suggestion
  - Graceful fallback when Google Places is not configured (manual text entry, no autocomplete)
  - Also wire autocomplete for place fields in the new place_history cards (FB-067)
- Out of scope:
  - Adding Places autocomplete to the wiki page (read-only surface)
  - Changing the person edit page Places behavior (already working)

## Task Type

- member-facing UX enhancement

## Dependencies

- Depends on FB-067 (place history cards) for the card-level autocomplete integration.
- Independent of FB-068, FB-069, FB-070.

## Likely Files

- `app/static/js/tree.js` (initializeTreeSidebar — wire Places on sidebar place inputs)
- `app/templates/partials/person_sidebar.html` (add data attributes for Places binding)
- `app/static/js/main.js` (shared Places initialization if needed)

## Acceptance Criteria

- [ ] Birth place input in sidebar shows Places autocomplete suggestions.
- [ ] Residence place input in sidebar shows Places autocomplete suggestions.
- [ ] Burial place input in sidebar shows Places autocomplete suggestions.
- [ ] Selecting a suggestion populates country_code and lat/lng hidden fields.
- [ ] Place history card place fields show Places autocomplete (when FB-067 is complete).
- [ ] Works when Google Places is configured; graceful no-op when not configured.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] No regression on existing Places behavior
