# Task Packet - FB-077 Left Panel Cleanup

## Objective

Simplify the tree left panel to only Search and Display Preferences, and update the collapse/expand toggle labels to be clear and descriptive.

## Why / KPI

- The left panel has controls that most users never touch (tree tools, analyze tree, etc.). They add visual noise and push the useful controls down.
- The toggle label "Show tree tools" is vague. "Expand Family Tree Settings" / "Hide Family Tree Settings" is clearer.
- CFLSR improves when the tree workspace feels clean and focused.

## Scope

- In scope:
  - Change collapsed label from "Show tree tools" to "Expand Family Tree Settings"
  - Change expanded state to show "Hide Family Tree Settings" with left-arrow chevron
  - Remove all left panel sections EXCEPT:
    - Search (the family member search input)
    - Display Preferences (show names, nicknames, photos, dates, flags checkboxes + save button)
  - Remove: "Navigate tree" (fit tree, round view, current focus, center root, return to focus), "Analyze tree" (relationship calculator), and any other sections
  - Keep the collapse/expand persistence (localStorage)
  - i18n for the new toggle labels across 5 locales
- Out of scope:
  - Changing the Display Preferences controls themselves
  - Moving controls to other locations
  - Right sidebar changes

## Task Type

- member-facing UI simplification

## Likely Files

- `app/templates/tree.html` (panel sections, toggle button)
- `app/static/js/tree.js` (toggle logic, label text)
- `app/static/css/main.css` (panel styles if needed)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## Acceptance Criteria

- [ ] Collapsed panel shows "Expand Family Tree Settings" with right-arrow chevron.
- [ ] Expanded panel shows "Hide Family Tree Settings" with left-arrow chevron.
- [ ] Left panel contains only Search and Display Preferences sections.
- [ ] Navigate tree, Analyze tree, and other sections are removed.
- [ ] Collapse/expand state persists across page reloads.
- [ ] i18n for toggle labels across 5 locales.
- [ ] No regression on search or display preferences functionality.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
