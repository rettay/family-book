# Task Packet - FB-100 Occupation on Tree Nodes

## Objective

Add a `show_occupation` display preference to the tree and render the current occupation as a sub-label on tree nodes — alongside name, birth date, and country flag — giving researchers and family members an at-a-glance sense of who each person was professionally.

## Why / KPI

- The tree already shows names, birth years, and country flags as optional sub-labels. Occupation is the next most genealogically meaningful field — "farmer", "merchant", "schoolteacher" immediately contextualises a person's life and era.
- Occupation on the tree reinforces the UX North Star: the tree as a workspace and reading surface, not just a navigator. More data visible on the canvas means fewer sidebar round-trips.
- Default is off: this is power-user information that would clutter the tree for casual browsers.

## Scope

**In scope:**
- New `show_occupation` display preference in `tree.js` (default: `false`)
- `current_occupation` field already added to tree person payload by FB-098 — this packet consumes it
- When `show_occupation` is true and `person.current_occupation` is non-empty, render it as a sub-label below the name line (and below birth date / country flag if those are also enabled), using the same `.rel-label` text element pattern as existing sub-labels
- Truncate long occupation strings to 22 characters with a `…` suffix to prevent node overflow
- New preference toggle in the tree display preferences panel:
  - Checkbox: `id="pref-show-occupation"`, label `t('tree.show_occupation')`
  - Positioned after the existing "Show birth dates" toggle in the preferences panel
- Preference persisted to and restored from `localStorage` alongside other tree preferences
- One new i18n key in all 5 locales: `tree.show_occupation`

**Out of scope:**
- Showing employer, date range, or past occupations on the tree node (only current title)
- Editing occupation from the tree canvas (that is the role of the Family Bio page, FB-099)
- Occupation filtering or search on the tree
- Any change to the Family Bio page (FB-099)

## Task Type

- Member-facing UI — tree canvas and preferences panel

## Dependencies

- FB-098 must be complete (`current_occupation` field must be present in the tree person payload before this packet executes)
- FB-099 is independent of this packet (can run in parallel)

## Target Personas

- `genealogy_researcher` — primary user of this preference; wants to understand occupational patterns across generations
- `contributing_member` — may enable this to verify that occupation data they entered via the bio page is correctly reflected on the tree

## Changed Surfaces

- `GET /tree` — canvas rendering (new sub-label), preferences panel (new checkbox)

## Likely Files

- `app/static/js/tree.js` — add `show_occupation` to preferences object; read `person.current_occupation`; render sub-label in node drawing loop; save/restore preference from localStorage; wire checkbox
- `app/templates/tree.html` — add `pref-show-occupation` checkbox in the preferences panel
- `locales/en.json` + 4 others — one new key: `tree.show_occupation`

## i18n Keys Required

```
tree.show_occupation  →  "Show occupation"
```

(One key in the existing `"tree"` namespace. All other strings are handled by FB-098.)

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual flow:
# 1. Add an occupation for a person via the bio page (FB-099)
# 2. Open the tree, click the display preferences panel
# 3. Check "Show occupation" — the person's node should show their title below the name
# 4. Uncheck — label disappears immediately
# 5. Reload the page — preference is restored from localStorage

uv run pytest tests/test_s44_occupation.py -v
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] Tree display preferences panel contains a "Show occupation" checkbox (`id="pref-show-occupation"`).
- [ ] Checkbox defaults to unchecked (off).
- [ ] When checked, tree nodes for persons with a `current_occupation` show it as a sub-label below the name. Persons with no current occupation show no change.
- [ ] Occupation label is truncated to 22 characters with `…` if longer.
- [ ] When unchecked, occupation sub-labels are removed from all nodes (without a page reload — same pattern as show_birth_dates).
- [ ] Preference is saved to `localStorage` and correctly restored on next page load.
- [ ] One new i18n key (`tree.show_occupation`) present in all 5 locales.
- [ ] `uv run pytest tests/test_i18n.py` passes with no new missing-key failures.
- [ ] `uv run pytest tests/` passes (no regressions).

## Structural Oracle

- `#pref-show-occupation` checkbox exists in the preferences panel DOM
- Checking it and calling the render update causes `text.rel-label` elements with occupation content to appear on nodes that have `current_occupation`
- `person.current_occupation` is available on `treeData.persons` entries (via FB-098)
- localStorage key `treePrefShowOccupation` (or equivalent) is set after toggling the preference

## Risk and Verification Notes

- **`current_occupation` availability:** This packet assumes `current_occupation` is already on the tree person payload (FB-098). If FB-098 is not complete, this packet cannot be tested end-to-end. Builder should verify the field is present in the API response before implementing the rendering logic.
- **Label ordering:** The sub-label stack on a node is: name → [nickname] → [birth date] → [country flag] → [occupation]. Occupation goes last. The `nextTextY` accumulator pattern already handles stacking — just add the occupation block after the country flag block, following the exact same pattern.
- **Truncation:** Use `title.length > 22 ? title.slice(0, 21) + '…' : title`. Do not use CSS `text-overflow` on SVG text elements — it is not reliably supported. Truncate the string in JS before passing to `.text()`.
- **No-op when field is empty or null:** Guard with `if (preferences.show_occupation && person.current_occupation)` — do not render an empty text element.
- **Preference key naming:** Follow the existing localStorage key pattern used for other preferences (e.g. `treePrefShowBirthDates` or whatever pattern is in use). Check `tree.js` before naming the new key.
- **Render without full reload:** Toggling the checkbox should update the canvas immediately, not require a page reload. Follow the same pattern as `show_birth_dates`: the preference change triggers `applyPreferences()` which calls `render()` (or the label-update equivalent).

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Checkbox present | Load /tree | `#pref-show-occupation` in DOM | Checkbox visible in prefs panel | Checkbox absent or misnamed |
| Label appears | Check box; person has occupation | SVG node sub-label | Occupation text below name | No label, or label on all nodes |
| Label absent (no occupation) | Check box; person has no occupation | SVG node unchanged | No sub-label added | Empty label element added |
| Truncation | Person with 30-char title | Label text | First 21 chars + `…` | Full text overflows node |
| Toggle off | Uncheck box | SVG nodes | Occupation labels removed | Labels persist |
| localStorage | Toggle on, reload page | Checkbox state | Checkbox still checked | Preference reset to off |
| i18n | test_i18n.py | All locale files | Zero missing-key failures | Key missing in one locale |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] `tree.show_occupation` key in all 5 locales; `test_i18n.py` passes
- [ ] Manually verified: toggle on → labels appear; toggle off → labels disappear; reload → state preserved
- [ ] Truncation confirmed with a long occupation title
