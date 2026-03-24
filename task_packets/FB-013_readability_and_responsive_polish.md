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

## Acceptance Criteria

- [ ] The smallest metadata and helper text styles are raised to a more legible baseline.
- [ ] Known cramped admin/action rows wrap or stack acceptably on narrow screens.
- [ ] Feed media reserves enough space to reduce visible layout jump.
- [ ] The packet improves readability and scanability without altering core product behavior.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Focused visual/browser verification captured
- [ ] No critical accessibility work displaced by this packet
