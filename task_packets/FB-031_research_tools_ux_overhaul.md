# FB-031: Research Tools UX Overhaul

## Objective

Transform the current "External Records" feature from a buried sidebar tab with visible error states into a polished, top-level "Research" experience with cleaner source management, per-person saved records, and a clear empty state when external APIs aren't configured.

## Why / KPI

**CFLSR impact:** High. The genealogy-researcher persona is first-class, but the current research tools undermine that claim. The "External Records" naming is wrong (users think "research", not "external records"). Unconfigured sources show raw error messages ("API key not configured") instead of being hidden. The entire feature is buried in the sidebar Records tab — a researcher has to click a tree node, open the sidebar, scroll to the Records tab, then find the search section. Per-person research results are ephemeral — there's no way to save a promising external record to a person's profile for later follow-up.

**Gap reference:** User feedback (2026-03-26). Builds on existing external records infrastructure (S19, FB-023).

## In Scope

### Rename and promote

- **Rename "External Records" to "Research"** across all surfaces (sidebar tab label, route names, i18n keys, CSS classes)
- **Top-level nav item:** "Research" alongside Tree, Moments, Calendar, Timeline, Health
- **Research index page** (`/research`): Landing page showing available sources with status, recent searches, and quick-search entry point
- **Per-person research link:** From person wiki page (FB-030) and person profile, link to pre-filtered research for that person

### Source management and error handling

- **Hide unconfigured sources** instead of showing error messages. If TROVE_API_KEY or DPLA_API_KEY aren't set, those sources simply don't appear in the UI
- **Source status indicator:** On the research index page, show which sources are available and a brief description of each (coverage area, data type)
- **Graceful degradation:** When no external sources are configured at all, show a friendly message explaining what the feature does and how to configure it (admin-only hint)

### Per-person saved records

- **Save button on search results:** Each external record result gets a "Save to [Person Name]" action
- **Saved records model:** New `SavedRecord` model linking an external record (title, URL, source, snippet, date_found) to a Person
- **Saved records display:** On the person's research section (sidebar + profile page), show saved records as a curated list
- **Delete saved record:** Remove a previously saved record

### Cleaner interface

- **Unified search:** Single search bar at the top, with source filter chips below (instead of separate buttons per source)
- **Result cards:** Cleaner result rendering with source badge, title, snippet, date, and save action
- **CEMLA integration:** Keep the dedicated CEMLA form but integrate it into the research page layout rather than a separate sidebar section

## Out of Scope (this packet)

- New external source integrations (stick with existing 6 sources + CEMLA)
- AI-assisted record analysis or extraction
- Bulk record import from external databases
- Citation linking (handled by FB-028 / S23)
- OAuth integration for FamilySearch (remains link-out)

## Dependencies

- Existing external records infrastructure (S19, FB-023)
- Person model with all current fields
- Optional: FB-030 (wiki pages) for cross-linking — but can ship independently

## Acceptance Criteria

### Naming and Navigation
- [ ] "Research" appears in main nav (replaces "External Records" language everywhere)
- [ ] GET /research returns research index page
- [ ] Research index shows available sources with descriptions
- [ ] Unconfigured sources are hidden (no error messages visible)

### Search Experience
- [ ] Unified search bar with source filter chips
- [ ] Pre-populated search when accessed from a person context
- [ ] Results render as clean cards with source badge
- [ ] CEMLA form integrated into research page

### Saved Records
- [ ] Users can save an external record to a person
- [ ] Saved records appear on person profile and sidebar
- [ ] Users can delete a saved record
- [ ] Saved records persist across sessions (database-backed)

### Cross-Links
- [ ] Person profile links to research (pre-filtered)
- [ ] Tree sidebar Records tab links to research page
- [ ] Root person restrictions maintained

## Likely Files

| File | Change |
|------|--------|
| `app/routes/external_records.py` | Rename, add saved records CRUD, add research page |
| `app/models/saved_record.py` | New model: SavedRecord |
| `app/templates/research.html` | New template: research index/search page |
| `app/templates/partials/person_sidebar.html` | Rename tab, link to research page, show saved records |
| `app/templates/person.html` | Research section with saved records |
| `app/static/js/tree.js` | Update function names, add save-record action |
| `app/static/css/main.css` | Research page styling, result cards, source chips |
| `app/main.py` | Register updated router |
| `app/templates/base.html` | Add Research nav link |
| `app/services/external_records.py` | Add source availability check (hide unconfigured) |
| `alembic/versions/XXXX_add_saved_records.py` | Migration |
| `locales/en.json`, `es.json`, `ru.json` | Rename keys, add new research keys |
| `tests/test_research.py` | New test file |

## Complexity

High. This touches the existing external records infrastructure (rename + restructure), adds a new model (SavedRecord), a new top-level page, and changes the search UX. Estimated 2-3 slices within a sprint.

## Definition of Done

- "Research" replaces "External Records" across all surfaces
- Research has a top-level nav entry and index page
- Unconfigured sources are hidden, not errored
- Users can save and manage external records per person
- All tests pass, i18n parity maintained
