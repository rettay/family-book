# Task Packet - FB-079 Sidebar Details Form and Visual Polish

## Objective

Make the Details tab feel like a reading surface that transitions smoothly into editing — hide empty fields by default, reduce visual chrome, and increase whitespace for a calmer interface.

## Why / KPI

- The Details tab currently shows all ~40 fields at once, most empty. This creates a form wall that discourages casual browsing.
- Card outlines and section borders add visual weight without aiding comprehension. Subtle background fills and whitespace grouping are lighter.
- The sidebar is 340px wide — every pixel of chrome is costly.
- CFLSR improves when the editing surface feels inviting rather than intimidating.

## Scope

- In scope:
  - **3.5 Hide empty sections by default**: In the Details tab, show only sections that have non-empty fields. Add an "Edit more details" expander at the bottom that reveals all empty sections for editing. When a user starts editing, empty fields within a visible section remain visible until the section is collapsed.
  - **3.6 Reduce chrome**:
    - Replace card outlines (border: 1px solid) with subtle background fills (e.g., rgba(45,80,22,0.03)) only where grouping is meaningful.
    - Remove borders from label+input stacks — use only whitespace separation.
    - Increase spacing between sections (margin-bottom from 12px to 20px).
    - Reduce font weight on section headings (from bold to medium/600).
    - Soften the tab strip: reduce border weight, use an underline indicator instead of a bordered tab.
  - Apply visual polish consistently across all sidebar tabs, not just Details.
- Out of scope:
  - Structural changes to tab layout (done in FB-078)
  - Left panel changes (done in FB-077)
  - Adding new fields or changing data model

## Task Type

- member-facing visual polish

## Likely Files

- `app/templates/partials/person_sidebar.html` (section visibility, expander)
- `app/static/js/tree.js` (toggle empty sections, "edit more" logic)
- `app/static/css/main.css` (border removal, background fills, whitespace, tab styles)
- `locales/en.json` + other locales ("Edit more details" label)

## Acceptance Criteria

- [ ] Details tab shows only sections with non-empty fields by default.
- [ ] "Edit more details" expander at the bottom reveals empty sections.
- [ ] Card outlines replaced with subtle background fills where grouping is meaningful.
- [ ] Label+input stacks have no borders, only whitespace separation.
- [ ] Section spacing increased for visual breathing room.
- [ ] Section headings use lighter font weight.
- [ ] Tab strip uses underline indicator, reduced border weight.
- [ ] Visual polish consistent across all sidebar tabs.
- [ ] i18n for "Edit more details" label across 5 locales.
- [ ] No functional regression.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] Sidebar feels like a reading surface, not a form
