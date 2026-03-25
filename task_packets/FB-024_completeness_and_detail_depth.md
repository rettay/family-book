# FB-024: Completeness Prompts and Sidebar Detail Depth

## Objective

Turn missing data into actionable contribution invitations and make the tree sidebar Details tab the complete person-editing surface so members rarely need to detour to the full edit page.

## Why / KPI

Directly improves CFLSR by solving two remaining friction points from the genealogy review: (a) the app shows what exists but doesn't motivate members to fill gaps — surfacing completeness prompts converts passive viewers into active contributors, and (b) the sidebar Details tab still requires page navigation for common fields like gender, death date, and burial details — expanding the sidebar removes the context-switch cost that kills editing momentum.

## Scope

### In scope

**Slice 1: Per-Person Completeness Prompts in Sidebar**

- Add data-gap detection to the sidebar overview tab that checks for missing:
  - Birth date (`birth_date_raw`)
  - Photo (`photo_url`)
  - Bio (`bio`)
  - Birth place (`birth_place`)
  - Gender (`gender`)
- Render each gap as an actionable prompt: "No birth date — add one?" that either switches to the Details tab or opens the relevant field
- Prompts only appear for persons the current user `can_manage`
- Prompts are grouped in a "Complete this profile" section between the richness metrics and the bio section
- Style prompts as inviting, not as error states — use secondary button style with a gentle call-to-action
- Existing prompts (no stories, no photos, no parents, etc.) remain in the workspace prompts section below
- No backend changes required for this slice

**Slice 2: Sidebar Details Tab Field Expansion**

- Expand the Details tab form to include all commonly-edited person fields in collapsible sections:
  - **Identity section** (existing): first_name, last_name, nickname, branch — add: patronymic, birth_last_name, gender (select), name_display_order (select)
  - **Dates section** (new collapsible): birth_date_raw, birth_date_precision (select), death_date_raw, death_date_precision (select), is_living (checkbox)
  - **Places section** (existing birth_place/residence expanded): birth_place, birth_country_code, residence_place, residence_country_code, burial_place, burial_country_code, burial_cemetery_name, burial_plot_number
  - **Notes section** (existing bio/research_notes): bio, research_notes — move to own collapsible
  - **Contact section** (new collapsible): contact_whatsapp, contact_telegram, contact_signal, contact_email
  - **Languages** (new): comma-separated input similar to edit page
- Use HTML `<details>/<summary>` for collapsible sections — progressive disclosure without JS complexity
- Each section starts collapsed except Identity (always open) and whichever section contains the field the user navigated to via a completeness prompt
- Update `saveTreePerson()` in tree.js to include all new fields in the PUT request
- Update `nullableFields` array in tree.js to include all new nullable fields

**Slice 3: Family-Level Completeness Summary API**

- Add `GET /api/completeness` endpoint that returns aggregated gap counts:
  ```json
  {
    "total_persons": 25,
    "gaps": {
      "no_birth_date": 8,
      "no_photo": 15,
      "no_bio": 12,
      "no_birth_place": 10,
      "no_gender": 6,
      "no_stories": 18,
      "no_media": 14
    }
  }
  ```
- Only counts active, visible persons accessible to the current user
- Excludes the root person from gap counts (root is a structural placeholder)
- No frontend surface for the completeness API in this sprint (frontend is a candidate for S19 admin dashboard)

### Out of scope

- Family-level completeness dashboard UI (deferred — API only in this sprint)
- Per-field source citations (G-07, deferred to S23)
- Medical history in sidebar (sensitive field, stays on edit page)
- Completeness score percentage or gamification elements
- Person page completeness indicators (sidebar only)

## Dependencies

- Sprint 17 tree sidebar and research notes must be stable (confirmed: S17 closed, pass)
- No external service dependencies
- No new data model fields

## Task Type

Feature development (frontend + API)

## Likely Files

### Slice 1 (Completeness Prompts)
- `app/templates/partials/person_sidebar.html` — completeness prompts section in overview tab
- `app/static/css/main.css` — prompt styling

### Slice 2 (Sidebar Detail Expansion)
- `app/templates/partials/person_sidebar.html` — expanded Details tab form with collapsible sections
- `app/static/js/tree.js` — update `saveTreePerson()` and `nullableFields`
- `app/static/css/main.css` — collapsible section styling

### Slice 3 (Completeness API)
- `app/routes/persons.py` — new `/api/completeness` endpoint
- `app/schemas.py` — CompletenessResponse schema (optional, can use dict)

## Local Validation Commands

```bash
# Syntax check
uv run python -m compileall app tests

# API tests
uv run pytest tests/test_api.py tests/test_pages.py -q

# Full suite
uv run pytest -q

# Browser flow
make test-ui-playwright

# CodeMap governance
uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json
```

## Acceptance Criteria

### Slice 1: Per-Person Completeness Prompts
1. The sidebar overview tab shows a "Complete this profile" section when the person has any missing data gaps (birth date, photo, bio, birth place, gender)
2. Each gap prompt is an actionable button that switches to the Details tab
3. Completeness prompts only appear for persons the current user can manage
4. When a person has no missing data, the completeness section is hidden (no empty container)
5. Existing workspace prompts (no stories, no photos, no parents) remain unchanged

### Slice 2: Sidebar Details Tab Field Expansion
6. The Details tab contains collapsible sections for Identity, Dates, Places, Notes, Contact, and Languages
7. Gender is editable as a select dropdown (male/female/other) in the Identity section
8. Death date and is_living are editable in the Dates section
9. Burial details (place, country, cemetery, plot) are editable in the Places section
10. Contact fields (WhatsApp, Telegram, Signal, email) are editable in the Contact section
11. Languages are editable as a comma-separated input
12. Saving the form successfully persists all new fields via the existing `PUT /api/persons/{id}` endpoint
13. The `nullableFields` array in tree.js includes all new nullable fields

### Slice 3: Family-Level Completeness API
14. `GET /api/completeness` returns a JSON object with `total_persons` and `gaps` counts
15. The endpoint requires authentication
16. The endpoint excludes root person and hidden persons from counts
17. Gap categories include: `no_birth_date`, `no_photo`, `no_bio`, `no_birth_place`, `no_gender`, `no_stories`, `no_media`

### Regression
18. Existing tree interactions (node click, sidebar tabs, search, graph mode, moments/media) remain functional
19. `uv run pytest -q` passes with no new failures
20. `make test-ui-playwright` passes
21. CodeMap governance shows no new FAIL results

## Definition of Done

All acceptance criteria pass. Validation commands are reproducible and passing. Sidebar completeness prompts and expanded details are demonstrated in the browser. Completeness API returns correct gap counts. No P0/P1 issues remain in scope. CFLSR is preserved or improved.

## Evaluation Environment

- **Task:** Feature development across frontend and API
- **Verifier:** Automated tests (pytest) plus manual browser evidence for sidebar interactions
- **Reference/oracle:** UX North Star principles (empty states as invitations, progressive disclosure, in-context editing)
- **Expected evidence:** Test results, sidebar screenshots showing completeness prompts and expanded detail sections, API response showing correct gap counts
- **Known failure modes / reward hacks:**
  - Completeness prompts that appear but don't navigate to the correct field
  - Collapsible sections that break the save form (partial form data)
  - Completeness API that counts root person or hidden persons in gaps
  - New sidebar fields that are rendered but not wired into the save function
- **Verifiability class:** `bounded-judgment` (sidebar UX requires visual inspection, API is deterministic)
- **Context policy:** Builder should read the current person_sidebar.html, tree.js saveTreePerson function, and the Person model before starting.

## Risk and Verification Notes

### Complexity hotspots
- Collapsible `<details>/<summary>` sections inside a form: the form submission must still collect all fields from all sections regardless of open/closed state. HTML forms do this natively, but verify.
- `saveTreePerson()` already handles `nullableFields` — adding more fields must extend the array without breaking existing save behavior.
- Completeness API must use the same access control as the persons list endpoint.

### Likely shallow-pass failure modes
- Sidebar fields rendered but not in the save payload (visual-only, no persistence)
- Completeness prompts that show for non-managing users
- Completeness API that returns counts for all persons regardless of access control

### Required verification depth
- Save round-trip: edit a new field in sidebar, save, reload sidebar, verify persistence
- Completeness prompt: verify a prompt disappears after filling the gap
- API: verify gap counts match manual inspection of seed data

### What counts as sufficient discriminative power
- At least one completeness prompt appears and disappears after filling the gap
- At least one new sidebar field saves and persists correctly
- Completeness API excludes root person

## Execution Budget

### Builder may explore autonomously
- CSS styling for collapsible sections and completeness prompts
- Ordering and grouping of sidebar fields within sections
- Debounce or validation patterns for new form fields

### Requires escalation
- Any change to the Person model or new database fields
- Any change to access control logic
- Any change to the revision snapshot schema

### Material scope drift
- Adding a completeness dashboard UI (API only in this sprint)
- Adding gamification or scoring
- Adding medical history to the sidebar
- Changing the sidebar tab structure

### Proof obligations before review
- Sidebar screenshots showing completeness prompts and expanded details
- API response from completeness endpoint with correct counts
- Save round-trip evidence for at least 3 new fields
- Passing test suite
