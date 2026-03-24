# Sprint Plan - S10 Readability and Responsive Polish

## Sprint

- Name: `S10 - Readability and Responsive Polish`
- Status: Planned
- Primary packet: `FB-013 Readability and Responsive Polish`
- Follow-on packet candidate: `FB-014 Architecture and Maintainability Hardening`

## Sprint Goal

Improve readability, scanability, and small-screen usability across the main Family Book surfaces so the product feels easier to read and calmer to navigate after Sprint 09’s critical accessibility fixes.

## Why This Sprint

The critical operability failures are now closed. The next highest-value UX work is the second tier from the UI/UX review: metadata text that is still too small or muted, crowded action rows and admin layouts on narrow screens, and media/feed presentation that still creates unnecessary visual instability or density. This sprint keeps the momentum on user-facing quality without drifting into a redesign or reopening deeper architectural work.

## Must-Have Outcomes

- Metadata and helper text are easier to read, especially on content-heavy views.
- Narrow-screen layouts wrap or stack acceptably in the admin dashboard, settings surfaces, and other crowded controls.
- Feed media reserves enough space to reduce visible layout shift and improve scanability.
- The sprint improves polish without weakening the accessibility baseline or browser confidence lane from Sprint 09.

## Acceptance Criteria

1. The smallest metadata and helper text styles are raised to a more legible baseline on the main Family Book pages.
2. Known cramped action rows and admin/settings controls wrap or stack acceptably on narrow screens.
3. Feed and card media reserve space well enough to reduce visible jump during load.
4. The main browser flow still passes after the polish work and does not regress the new accessibility behaviors.
5. The sprint improves readability and scanability without changing core product behavior or reopening resolved accessibility defects.

## In Scope

- typography sizing and muted-text legibility
- metadata and helper-text scanability on home, people, person, and admin surfaces
- mobile/narrow-screen wrapping for admin rows, settings controls, and compact action groups
- feed media aspect reservation and related layout-stability polish
- small spacing and touch-comfort improvements where the UI is currently too dense
- focused browser and CodeMap verification

## Out of Scope

- broad visual redesign
- theme-system redesign
- new product features
- deep architecture refactors
- major information-architecture changes
- critical accessibility work already closed in Sprint 09

## Implementation Order

1. Execute Slice 1: typography and metadata legibility.
2. Execute Slice 2: mobile and admin responsiveness.
3. Execute Slice 3: feed media stability and scanability polish.
4. Validate with browser checks, focused pytest, and staging/manual review on narrow screens.

## Execution Slices

### Slice 1 - Typography and Metadata Legibility

- Goal:
  raise the readability floor for metadata, timestamps, helper text, and other secondary content
- Scope:
  typography scale, muted text contrast/weight usage, line-height, and dense card metadata groupings
- Must prove:
  supporting text is easier to read without making the UI feel oversized or noisy

### Slice 2 - Mobile and Admin Responsiveness

- Goal:
  reduce cramped interactions on small screens and in dense admin surfaces
- Scope:
  admin dashboard rows, settings actions, filters, compact control groups, and touch-target spacing where needed
- Must prove:
  narrow-screen users can operate these surfaces without layout collisions or compressed controls

### Slice 3 - Feed Media Stability and Scanability Polish

- Goal:
  make content-heavy surfaces feel calmer and easier to scan
- Scope:
  feed media aspect reservation, card spacing, media grouping rhythm, and related small polish on home/person surfaces
- Must prove:
  image-heavy flows feel more stable and less jumpy during normal browsing

## Proof Obligations

- The sprint must preserve the Sprint 09 accessibility contract while improving polish.
- Browser verification must stay green on the main member/admin flows.
- The work should stay bounded to readability, spacing, responsive behavior, and visual stability.
- The sprint should not drift into feature work or a broad redesign.

## Risks To Watch

- increasing visual polish churn without fixing the actual dense or cramped areas
- reducing contrast or readability in the name of “cleaner” styling
- breaking the newly hardened browser flow through template/CSS regressions
- using theme changes to mask layout problems instead of fixing structure and spacing

## Exit Target

Sprint 10 is complete when Family Book is materially easier to read and use on smaller screens, especially on metadata-heavy and admin-heavy surfaces, while the Sprint 09 accessibility baseline remains intact.
