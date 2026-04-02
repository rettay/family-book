# Task Packet - FB-070 Sidebar Label Tightening and Placeholder Polish

## Objective

Audit and tighten all labels in the tree sidebar Details tab — replace verbose labels with concise text and add helpful placeholder hints so the narrow sidebar feels less like a government form.

## Why / KPI

- The sidebar is 340px wide. Verbose labels like "Date of birth (text)" waste space and create visual clutter.
- Placeholders like "Jan 15, 1950" or "Boston, MA" guide input without taking up label space.
- CFLSR improves when the editing surface feels clean and inviting rather than overwhelming.

## Scope

- In scope:
  - Audit all labels in the tree sidebar Details tab
  - Shorten labels (e.g., "Birth date" → "Born", "Residence" → "Lives in")
  - Add descriptive placeholders to text inputs and date fields
  - Remove redundant section headers where context is obvious
  - Update i18n keys across en, es, ru, it, zh
  - Ensure the person edit page labels stay unchanged (full form can be more verbose)
- Out of scope:
  - Restructuring the sidebar sections or tab layout
  - Removing fields
  - Auto-save (separate packet)

## Task Type

- member-facing copy polish

## Likely Files

- `app/templates/partials/person_sidebar.html` (label text, placeholder attributes)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## Acceptance Criteria

- [ ] Sidebar Detail labels are concise (no label exceeds ~15 characters).
- [ ] Text inputs have helpful placeholder hints.
- [ ] Date fields have format hint placeholders.
- [ ] Place fields have example placeholders.
- [ ] i18n keys updated across 5 locales.
- [ ] No functional regression — field names and data binding unchanged.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
