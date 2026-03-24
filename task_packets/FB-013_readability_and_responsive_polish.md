# Task Packet - FB-013 Readability and Responsive Polish

## Objective

Improve the lower-severity but still meaningful readability, responsive-layout, and scanability issues identified in the UI/UX review without reopening core accessibility and interaction work.

## Why / KPI

- The UI/UX review found a second tier of issues that are not hard blockers but still reduce ease of use, especially for older family members and on smaller screens.
- These are better handled as a bounded follow-on packet rather than folded into the critical accessibility sprint.

Primary KPI:
- reduce readability and mobile-friction complaints across the main product surfaces.

Secondary KPI:
- improve scannability and perceived stability on content-heavy pages.

## Scope

- In scope:
  - metadata typography sizing and muted-text readability improvements
  - mobile wrapping and spacing in crowded admin/action rows
  - feed media aspect reservation to reduce layout shift
  - small touch-target and spacing polish where the current controls are cramped
  - review of minor Family Book-specific empty, helper, and secondary-action presentation states
- Out of scope:
  - critical accessibility bugs already covered by FB-012
  - full visual redesign
  - theme-system redesign
  - feature additions

## Task Type

- UX polish / responsive readability packet

## Dependencies and Ordering Assumptions

- Best sequenced after FB-012 so critical operability issues are not competing with polish work.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - metadata typography sizing and muted secondary-text legibility on content-heavy pages
  - mobile and narrow-screen wrapping for admin actions, settings rows, and other crowded control groups
  - feed media aspect reservation so moments do not visibly jump as media loads
- Should improve:
  - scanability of cards, helper text, and secondary action groupings on home, people, person, and admin surfaces
  - touch comfort for compact controls that are currently too dense on smaller screens
  - small empty/helper states where better spacing or hierarchy reduces hesitation
- Must re-run:
  - focused browser verification against home, people, person, admin, tree, and map surfaces
  - targeted pytest for any template or route changes needed to support the polish work
  - CodeMap to confirm the sprint does not introduce new governance failures

## Implementation Notes

- Likely files:
  - `app/static/css/main.css`
  - `app/templates/home.html`
  - `app/templates/people.html`
  - `app/templates/person.html`
  - `app/templates/person_edit.html`
  - `app/templates/person_new.html`
  - `app/templates/admin.html`
  - `app/templates/settings.html`
  - `app/templates/partials/moment_card.html`
  - `app/templates/partials/people_grid.html`
  - `app/templates/partials/media_gallery.html`
  - `app/templates/base.html`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  improve readability, responsive comfort, and scanability on the main Family Book surfaces
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  the recent UI/UX review follow-on findings
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  denser surfaces become easier to read and use on smaller screens without changing product behavior
- Known failure modes / reward hacks:
  - making the UI look “cleaner” while leaving mobile cramping unresolved
  - tweaking colors or themes instead of fixing legibility and spacing
  - introducing layout churn that harms the browser baseline
- Verifiability class:
  `readability-and-responsive-polish`
- Context policy:
  optimize for practical readability and scanability, especially for older family members and mobile use

## Acceptance Criteria

- [ ] The smallest metadata and helper text styles are raised to a more legible baseline.
- [ ] Known cramped admin/action rows wrap or stack acceptably on narrow screens.
- [ ] Feed media reserves enough space to reduce visible layout jump.
- [ ] The packet improves readability and scanability without altering core product behavior.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Focused visual/browser verification captured
- [ ] No critical accessibility work displaced by this packet
