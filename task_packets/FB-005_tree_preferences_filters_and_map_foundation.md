# Task Packet - FB-005 Tree Preferences, Filters, and Map Foundation

## Objective

Add the first launch-grade personalization and exploration layer for Family Book through saved tree preferences, tree filters, and map-view foundation.

## Why / KPI

- Once shared collaboration works, the next value layer is helping members explore the family record in ways that match their needs.
- User-specific tree controls are part of the intended product, not a stretch gimmick.

## Scope

- In scope:
  - saved tree display preferences
  - tree filters for launch-critical fields
  - map-view data/API foundation
  - tests for preference persistence and filtered outputs
- Out of scope:
  - external geocoding integrations
  - polished cartographic design beyond launch utility
  - broad analytics or recommendation features

## Constraints

- Preferences must be per-user, not global.
- Filters must operate on persisted, supported fields only.
- Map work must remain private and authenticated.

## Implementation Notes

- Likely files:
  - `app/models/` additions for user preferences if needed
  - `app/routes/tree.py`
  - `app/routes/pages.py`
  - `app/static/js/tree.js`
  - new map route/template/static assets as needed
  - `tests/test_api.py`
  - UI/browser validation harness
- Validation commands:
  - targeted pytest command for tree/preferences routes
  - browser or UI-harness evidence for map and tree behavior

## Evaluation Environment

- Task: user-specific tree/map exploration features
- Verifier: API tests plus rendered UI evidence
- Reference/oracle: `foundation/V1_PRODUCT_REQUIREMENTS.md`
- Expected evidence: preferences persist per user, filters affect outputs correctly, map data renders for authorized members
- Known failure modes / reward hacks:
  - controls exist in UI but do not persist
  - filters are cosmetic only
  - map leaks data or uses unauthenticated endpoints
- Verifiability class: `bounded-judgment`

## Acceptance Criteria

- [ ] Users can persist their own tree display preferences.
- [ ] Users can filter the tree by launch-supported attributes.
- [ ] The app exposes an authenticated map-view foundation for launch-supported person/location data.
- [ ] Tests or browser evidence show the feature works for one user without mutating another user's preferences.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] Preference persistence and map privacy verified
