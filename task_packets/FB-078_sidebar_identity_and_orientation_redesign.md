# Task Packet - FB-078 Sidebar Identity and Orientation Redesign

## Objective

Restructure the tree sidebar so it serves as a reading surface first — name, photo, and key relationships visible instantly — with editing as a secondary mode that slides in rather than being always present.

## Why / KPI

- The current sidebar is form-heavy. Opening a person node shows a wall of tabs, sections, and form fields. Users can't answer "who is this person?" in under 2 seconds.
- The "Complete This Profile" checklist takes up prime screen real estate with a list of items. A compact progress indicator is sufficient.
- "What Should Happen Next" duplicates the checklist. Merging them removes redundancy.
- The tab strip AND section headers inside each tab create two layers of navigation. One layer is enough.
- CFLSR improves when family members can quickly orient themselves on the tree without feeling overwhelmed.

## Scope

- In scope:
  - **3.1 Collapse completeness checklist**: Replace the expanded item list with a single progress line: "3 of 5 fields complete" with a chevron to expand. On expansion, each item is a tappable link that opens the right edit flow (e.g., clicking "Add birth date" switches to Details tab and focuses the field).
  - **3.2 Unify tab/section navigation**: Keep the top-level tabs (Overview, Details, Relationships, Media, Research). Inside each tab, replace card-bordered section headers with subtle `<h3>`-style headings separated by whitespace only. No card outlines or borders around sections.
  - **3.3 Elevate identity above fold**: Pin name, photo (clickable avatar), and the 2-3 most important relationship links (partner name, children names) above the tab strip. This identity block is always visible regardless of which tab is active. Move the "Set as focus" / "Return to focus" / "Center root" controls into a compact row below the identity block.
  - **3.4 Remove "What Should Happen Next"**: Delete this section entirely. Its suggested actions (Add first photo, Add parent, etc.) are merged into the completeness indicator items as tappable links.
- Out of scope:
  - Details form field visibility changes (separate packet FB-079)
  - Visual polish / border reduction (separate packet FB-079)
  - Left panel changes (separate packet FB-077)

## Task Type

- member-facing UI restructure

## Likely Files

- `app/templates/partials/person_sidebar.html` (major restructure)
- `app/static/js/tree.js` (completeness toggle, action links, identity block)
- `app/static/css/main.css` (section heading styles, identity pinning, tab cleanup)
- `locales/en.json` + other locales (completeness progress label, any new keys)

## Acceptance Criteria

- [ ] Identity block (name, photo, key relationships) is visible above the tab strip without scrolling.
- [ ] Completeness indicator shows "X of Y complete" with a chevron; expands to show items on click.
- [ ] Each completeness item is a tappable link that navigates to the right edit flow.
- [ ] "What Should Happen Next" section is removed.
- [ ] Tab content sections use subtle h3 headings with whitespace, not card borders.
- [ ] Tabs (Overview, Details, Relationships, Media, Research) still work correctly.
- [ ] "Set as focus" / "Return to focus" / "Center root" controls are compact, below identity.
- [ ] No functional regression on any sidebar tab.

## Risk and Verification Notes

- This is a significant template restructure. Test all 5 tabs after changes.
- The completeness indicator requires counting non-empty fields — verify the count logic handles all field types.
- Identity block pinning must not break the scrollable tab content below.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] All 5 sidebar tabs functional
- [ ] i18n parity maintained
