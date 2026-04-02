# FB-030: Person Wiki Pages

## Objective

Create a Wikipedia-style biographical page for each person in the family, accessible as a top-level "Wiki" feature alongside Tree, Moments, and Calendar. Each person gets a structured, human-readable article with templated sections, a canonical URL, and bidirectional data flow with the person's structured fields.

## Why / KPI

**CFLSR impact:** High. The current person profile page is a data form — useful for editing but not for reading. A wiki page turns each person into a narrative that family members want to read and share. The structured section template (Early Life, Personal Life, Career, Later Life) guides contributors to write meaningful content, not just fill fields. The canonical URL (`/wiki/{slug}`) makes every person linkable from anywhere — moments, stories, external documents, even printed materials.

**Gap reference:** User feedback (2026-03-26). Builds on existing bio, obituary, education[], career[], organizations[] fields.

## In Scope

### Phase 1: Wiki page shell and section rendering

- **New top-level nav item:** "Wiki" alongside Tree, Moments, Calendar, Timeline
- **Wiki index page** (`/wiki`): Alphabetical list of all accessible persons with search/filter
- **Person wiki page** (`/wiki/{person-slug}`): Wikipedia-style biographical article
- **Person slug generation:** `{first_name}-{last_name}-{short_id}` (e.g., `maria-santos-abc123`), stored on Person model
- **Templated sections** assembled from existing fields:
  - **Infobox** (right sidebar): photo, full name, born, died, age, birthplace, residence, branch
  - **Summary** (lead paragraph): Auto-generated from name, dates, places
  - **Early Life**: birth info, birthplace, parents (from ParentChild relationships)
  - **Education**: from `education[]` array
  - **Career**: from `career[]` array
  - **Personal Life**: partnerships (from Partnership model), children (from ParentChild)
  - **Organizations**: from `organizations[]` array
  - **Later Life**: residence, health overview (if any medical conditions)
  - **Death & Legacy**: death date, burial info, obituary text
  - **Research Notes**: from `research_notes` field
- **Edit mode:** Each section is editable — clicking "edit" on a section opens a form that writes back to the underlying structured fields
- **Empty section handling:** Sections with no data show a subtle "Add [section name]" prompt, not blank space

### Phase 2 (future sprint): Rich content and cross-linking

- Freeform wiki content per section (beyond structured fields)
- Cross-person wiki links (`[[Maria Santos]]` syntax)
- Section history/revisions
- Print-friendly layout
- Wiki-style "what links here" reverse lookup

## Out of Scope (this packet)

- Rich text / markdown editing within sections
- AI-assisted content generation or field extraction from narrative text
- Photo gallery within the wiki page (use existing media surfaces)
- Phase 2 features listed above

## Dependencies

- Person model with all current fields (S01-S22)
- ParentChild and Partnership models for relationship sections
- Education, career, organizations JSON arrays (S21)
- Obituary field (S21)

## Acceptance Criteria

### Wiki Index
- [ ] GET /wiki returns alphabetical list of accessible persons
- [ ] Search/filter by name works
- [ ] Hidden persons excluded for non-admin members
- [ ] Root person name redacted

### Person Wiki Page
- [ ] GET /wiki/{slug} returns Wikipedia-style biographical page
- [ ] Infobox renders with photo, dates, places
- [ ] All templated sections render from structured data
- [ ] Empty sections show "Add [section]" prompt
- [ ] Edit button on each section opens edit form
- [ ] Edits write back to person structured fields via API
- [ ] Slug is auto-generated on person creation
- [ ] Slug is unique and URL-safe
- [ ] Old slugs redirect if name changes (or slug is immutable)

### Navigation
- [ ] "Wiki" appears in main nav
- [ ] Person profile page links to wiki page
- [ ] Tree sidebar links to wiki page
- [ ] Wiki page links back to tree node

## Likely Files

| File | Change |
|------|--------|
| `app/models/person.py` | Add `slug` column |
| `app/routes/wiki.py` | New route file |
| `app/templates/wiki_index.html` | New template |
| `app/templates/wiki_person.html` | New template (Wikipedia-style layout) |
| `app/static/css/main.css` | Wiki page styling (infobox, sections, edit buttons) |
| `app/main.py` | Register wiki router |
| `app/templates/base.html` | Add Wiki nav link |
| `app/schemas.py` | Add slug to PersonDetail |
| `alembic/versions/XXXX_add_person_slug.py` | Migration |
| `locales/en.json`, `es.json`, `ru.json` | Wiki section labels |
| `tests/test_wiki.py` | New test file |

## Complexity

High. This is a multi-file feature with a new route, two templates, a Wikipedia-style CSS layout, slug management, section assembly logic, and edit forms that write back to structured fields. Estimated 2-3 slices within a sprint.

## Definition of Done

- Every person has a wiki page at `/wiki/{slug}`
- Wiki index lists all accessible persons
- Sections render from existing structured data
- Edit mode writes back to person fields
- Nav link present, cross-links from tree and person page
- All tests pass, i18n parity maintained
