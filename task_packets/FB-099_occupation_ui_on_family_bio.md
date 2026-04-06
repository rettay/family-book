# Task Packet - FB-099 Occupation UI on Family Bio

## Objective

Add an "Occupation History" section to the Family Bio page (`/wiki/{slug}`) that displays a person's full career timeline and lets any family member add, edit, or remove roles — using HTMX inline editing consistent with the rest of the bio page.

## Why / KPI

- FB-098 adds the data model and API but provides no way to view or enter occupation data from the browser. This packet closes the loop.
- The occupation timeline is one of the most evocative parts of a family history — "great-grandmother was a seamstress in Sicily before emigrating" is the kind of detail that makes a family record feel real rather than clinical.
- CFLSR improves when members can contribute structured facts without needing admin access.

## Scope

**In scope:**
- New "Occupation History" section in `app/templates/wiki_person.html`, positioned between the Life Story section and the Stories section
- Current role (end_date IS NULL) displayed prominently as the section headline with a large-ish title and optional employer below it
- Past roles listed as a compact timeline beneath the current role:
  - Format: `{title}` at `{employer}` · `{start_date} – {end_date}` (use locale key `occupation.present` when end_date is null)
  - If no employer, omit the "at {employer}" part
- "Add Role" button visible to all authenticated members — opens an inline HTMX form
- Form fields:
  - **Job Title** (required text input, `name="title"`)
  - **Employer / Organization** (optional text input, `name="employer"`)
  - **Start** (optional text input, `name="start_date"`, free text — e.g. "1985" or "June 1985")
  - **End** (optional text input, `name="end_date"`, free text — hidden when checkbox below is checked)
  - **"Currently in this role"** checkbox — when checked, `end_date` is omitted from the POST/PUT payload (server treats missing or empty end_date as null = current)
- Edit button on each role card — swaps card to edit form (prefilled), inline via HTMX
- Remove button on each role card — admin only (rendered conditionally server-side) — confirm step before DELETE
- Empty state: `t('occupation.empty')` with an "Add Role" button
- New partials:
  - `app/templates/partials/wiki_occupation_card.html` — single role card (used in list and as HTMX swap target)
  - `app/templates/partials/wiki_occupation_form.html` — add/edit form with all fields
- Display the existing `career[]` JSON prose entries (if any) below the structured timeline as a "Career Notes" subsection — do not remove or alter this data; just render it read-only beneath the new structured section
- Pass `occupations` list from the wiki route to template context (fetched from `GET /api/persons/{id}/occupations` or direct DB query in the route)
- i18n: use all 15 keys from FB-098

**Out of scope:**
- Tree display of occupation (FB-100)
- Inline date picker — free text is intentional (genealogical dates are often imprecise: "circa 1920", "early 1960s")
- Reordering roles (order is determined by start_date and end_date logic server-side)
- Occupation search or filtering across the family

## Task Type

- Member-facing UI — wiki/bio page enhancement

## Dependencies

- FB-098 must be complete (model, migration, and API must exist)

## Target Personas

- `contributing_member` — adds their grandparent's occupation from memory or a document; free-text dates are essential for imprecise historical data
- `genealogy_researcher` — enters multiple historical roles with sourced dates; needs the timeline to be scannable and accurate
- `mobile_first_relative` — reads the occupation timeline on a phone; must be legible on narrow viewport without horizontal overflow
- `family_admin` — removes incorrect or duplicate entries

## Changed Surfaces

- `GET /wiki/{slug}` — new Occupation History section added to person bio page
- `GET /api/persons/{person_id}/occupations` — called to populate section (or fetched inline in the route)
- `POST`, `PUT`, `DELETE /api/persons/{person_id}/occupations/*` — called via HTMX actions

## Likely Files

- `app/templates/wiki_person.html` (add Occupation History section)
- `app/templates/partials/wiki_occupation_card.html` (new)
- `app/templates/partials/wiki_occupation_form.html` (new)
- `app/routes/wiki.py` (fetch occupations and pass to wiki_person context)
- `app/static/css/main.css` (occupation section styles, timeline layout, card styles)
- `locales/en.json` + 4 others (keys added in FB-098; no new keys needed here)

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual: visit /wiki/{slug} for a person
# Verify: "Occupation History" section present; empty state if no roles
# Add a role with "Currently in this role" checked — confirm it appears as current
# Add a past role — confirm it appears in the timeline below the current role
# Edit a past role — confirm the form prefills correctly, save updates in place
# Remove a role as admin — confirm confirm step, then row disappears

uv run pytest tests/test_occupation_ui.py -v
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] `/wiki/{slug}` renders an "Occupation History" section between Life Story and Stories.
- [ ] Empty state (`t('occupation.empty')`) and "Add Role" button are shown when no roles exist.
- [ ] Current role (end_date IS NULL) is displayed prominently at the top of the section.
- [ ] Past roles are displayed as a compact timeline list, ordered start_date descending.
- [ ] Dates are formatted as `{start_date} – {end_date}`, with `t('occupation.present')` when end_date is null.
- [ ] "Add Role" button is visible to any authenticated member.
- [ ] Add form submits via HTMX; the new role card appears without a full page reload.
- [ ] "Currently in this role" checkbox hides the End date field and omits end_date from the payload.
- [ ] Edit button on each card opens an inline prefilled form. Saving updates the card in place via HTMX.
- [ ] Remove button is visible only to admins. Clicking shows a confirm step. Confirming sends DELETE and removes the card.
- [ ] Non-admin members do NOT see the Remove button.
- [ ] If `career[]` prose entries exist on the person, they are rendered read-only below the structured timeline as "Career Notes."
- [ ] Section is readable on 390px mobile viewport (no horizontal overflow, all controls accessible).
- [ ] No full page reload required for add, edit, or delete operations.

## Structural Oracle

- `#wiki-occupation-section` present in DOM on page load
- `[data-occupation-id]` card count matches occupation list length
- `[data-wiki-occupation-empty]` visible only when list length is 0
- Current role card has a visually distinct treatment (e.g. class `occupation-card--current`)
- Add form contains `input[name="title"]`, `input[name="employer"]`, `input[name="start_date"]`, `input[name="end_date"]`, `input[type="checkbox"][name="currently_in_role"]`
- Remove button has `data-admin-only` or is absent for non-admin users

## Risk and Verification Notes

- **"Currently in this role" checkbox UX:** When checked, the End date field must be hidden (JS toggle or HTMX swap) and the form must not submit an `end_date` value. If the field is hidden but still in the DOM, use `disabled` attribute so it is excluded from the form submission. Do not rely on the server to ignore a submitted non-empty `end_date`.
- **Prefill for edit form:** The edit form must pre-check "Currently in this role" if `end_date` is null. The JS or server-side template must detect this and check the box, hide the End field, accordingly.
- **HTMX swap targets:** Each role card must have a unique `id` attribute (e.g. `id="occupation-{{ occ.id }}"`) for HTMX to swap the correct element. The add form should swap into a dedicated `#occupation-add-slot` container.
- **career[] coexistence:** The existing `career[]` entries on Person are unstructured prose. Render them read-only as a flat list or paragraph block below the occupation timeline. Do not try to merge or parse them — they are legacy data and users can migrate them manually.
- **N+1 guard:** The wiki route must not issue a separate DB query per occupation record. Fetch all occupations for the person in one query and pass them to the template.
- **Date display:** Dates are stored as free text (user-entered). Render them as-is — do not attempt to parse or reformat. Only substitute `t('occupation.present')` for null end_date.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Section renders | Visit `/wiki/{slug}` | DOM `#wiki-occupation-section` | Section present | Section absent or admin-gated |
| Empty state | Visit page, 0 roles | `[data-wiki-occupation-empty]` | Empty state text visible | Always hidden |
| Add current role | Submit form, checkbox checked | Card appears, no reload | Role shown as current | Full reload, or end_date set incorrectly |
| Add past role | Submit form with end_date | Card in timeline | Role in list below current | Sorted incorrectly |
| Edit prefill | Click Edit on past role | Form appears prefilled | All fields populated | Blank form |
| Currently-in-role checkbox on edit | Edit a current role | Checkbox pre-checked, End hidden | Correct pre-state | Checkbox unchecked, End shown |
| Remove (admin) | Click Remove as admin | Confirm step, then card gone | Card removed | No confirm, or card stays |
| Remove (non-admin) | Visit as member | No Remove button visible | Button absent | Button present |
| Mobile layout | 390px viewport | No overflow | Legible, no clipping | Controls off-screen |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] i18n parity maintained (no new keys; all 15 from FB-098 consumed correctly)
- [ ] HTMX add/edit/delete flows manually verified on dev server
- [ ] Mobile layout verified at 390px
- [ ] career[] notes render correctly when present and are absent when career[] is empty
