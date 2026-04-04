# Task Packet - FB-090 Story Count in Tree Sidebar

## Objective

Show the number of stories attributed to a person in the tree sidebar overview, linking to the wiki page stories section, so users browsing the tree know at a glance whether a person has contributed narratives.

## Why / KPI

- The tree sidebar is the most-used surface for exploring a person's information. Surfacing a story count there creates a pull signal: members see "3 stories" and navigate to the wiki page to read them.
- This closes the discovery loop between the tree (where people browse) and the wiki (where stories live), directly supporting CFLSR.
- Low implementation cost: story count is a single COUNT query, piggybacks on the existing sidebar data flow.

## Scope

**In scope:**
- Add story count to the sidebar person panel overview area
- Display as a linked line: "N stories" (using `stories.count_one` / `stories.count_many` i18n keys from FB-088) — clicking navigates to `/wiki/{slug}#stories`
- Show only if count > 0; do not show the line for people with no stories (no "0 stories" noise)
- Pass `story_count` and `person_slug` to the sidebar template context from the sidebar route/endpoint
- Story count query: `SELECT COUNT(*) FROM stories WHERE person_id = ? ` (simple, no joins needed)
- `data-tree-sidebar-story-count` data attribute on the sidebar root element (parallel to existing `data-tree-sidebar-media-count`) for test targeting

**Out of scope:**
- Story list preview in sidebar (stories are read on the wiki page)
- Story creation from the sidebar (add story is on the wiki page only)
- Count for hidden/soft-deleted stories (if soft delete is added in future, filter then; not needed now)

## Task Type

- Member-facing UI — tree sidebar enhancement (minor)

## Dependencies

- FB-088 must be complete (stories table must exist for the COUNT query)
- FB-089 does not block this packet, but both should be deployed together for the full feature to be useful

## Target Personas

- `contributing_member` — sees the count and is invited to read; may navigate to wiki page
- `genealogy_researcher` — uses the sidebar to assess person completeness; story count is meaningful signal

## Changed Surfaces

- `GET /tree` sidebar panel (person_sidebar partial, loaded via HTMX when a node is clicked)

## Likely Files

- `app/templates/partials/person_sidebar.html` (add story count line in overview/identity section)
- `app/routes/tree.py` or wherever the sidebar partial route lives — add story count query and pass to context
- `locales/en.json` and 4 other locales (keys already added in FB-088: `stories.count_one`, `stories.count_many`)

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Confirm sidebar renders story count
# Visit /tree, click a person who has stories (add one via wiki page first)
# Sidebar should show "N stories" link

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] When a person has 1 or more stories, the tree sidebar overview shows "N stories" using the correct i18n plural form.
- [ ] When a person has 0 stories, no story count line is shown.
- [ ] The "N stories" text is a link navigating to `/wiki/{slug}#stories`.
- [ ] `data-tree-sidebar-story-count` attribute is set on the sidebar root element with the integer count.
- [ ] Story count is correct after a new story is added via the wiki page (requires sidebar reload to refresh — that is acceptable).
- [ ] No N+1 query: story count is fetched in a single COUNT query per sidebar load.
- [ ] i18n: count uses `stories.count_one` for 1, `stories.count_many` (with `{n}`) for 2+.

## Risk and Verification Notes

- **Sidebar context flow:** Find where `person_metrics` or similar is assembled for the sidebar — story count should be added alongside `media_count`. If it is assembled inline in the route, add a single `COUNT` query there. If there is a service layer, add a helper there.
- **Slug availability in sidebar context:** The sidebar needs `person.slug` to build the wiki link. Confirm the sidebar context already has the full Person object (it does — `person` is passed). Use `person.slug` directly.
- **Plural form:** `stories.count_many` should be `"{n} stories"` — substitute `n` in the template with `story_count`. For languages with complex plural rules, the `{n}` token is sufficient for now; do not introduce a plural-forms system.
- **Zero stories:** The condition `if story_count > 0` should gate the entire line — do not render a grayed-out "0 stories" line as that adds noise without value.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Count shown for person with stories | Click node in sidebar | `data-tree-sidebar-story-count` ≥ 1 | "N stories" link visible | Line absent |
| Count hidden for person with 0 stories | Click node with no stories | Line absent from DOM | No story count line | "0 stories" shown |
| Link target | Click "N stories" | URL fragment | Navigates to `#stories` on wiki page | Link broken or missing `#stories` |
| i18n: singular | 1 story | "1 story" (count_one key) | Singular form used | "1 stories" |
| i18n: plural | 3 stories | "3 stories" (count_many key) | Plural form used | "3 story" |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] i18n parity maintained
- [ ] Manually verified on dev server: sidebar shows count for a person with stories, no line for person without
