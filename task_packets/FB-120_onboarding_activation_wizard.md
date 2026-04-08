# Task Packet - FB-120 Onboarding Activation Wizard

Status: Proposed

## Objective

Create a first-run workflow that gets a family steward to visible value in under 15 minutes.

## Why / KPI

Paid conversion depends on fast activation: create archive, add/import relatives, upload media, and invite someone.

## Scope

- In scope:
  - first-run state model
  - add self and close relatives
  - choose GEDCOM import or manual start
  - upload first media item
  - invite first relative
  - activation event tracking without sensitive content
  - resumable wizard
- Out of scope:
  - full tutorial system
  - billing checkout redesign
  - AI story generation

## Likely Files

- `app/models/onboarding.py`
- `app/routes/onboarding.py`
- `app/templates/onboarding.html`
- `app/templates/tree.html`
- `app/services/audit_service.py`
- `tests/test_onboarding.py`
- `tests/test_pages.py`

## Acceptance Criteria

- [ ] New archive owner is routed to onboarding until first-run is complete or skipped.
- [ ] Wizard supports manual add and GEDCOM import paths.
- [ ] Wizard records first media and first invite milestones.
- [ ] Wizard can be resumed after closing the browser.
- [ ] Activation events avoid storing private content.

## Validation Commands

- `uv run pytest tests/test_onboarding.py tests/test_pages.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [ ] A new user can reach first value in one session.
