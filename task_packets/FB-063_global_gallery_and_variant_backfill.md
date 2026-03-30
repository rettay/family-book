# Task Packet - FB-063 Global Family Gallery and Variant Backfill

## Objective

Build a top-level /gallery page showing all family media with type, person, date, and uploader filters, and run a one-time backfill to generate thumb/medium variants for all existing media that predates the variant pipeline.

## Why / KPI

- There is no central place to browse all family media across all people. Discovery is limited to per-person views.
- Media uploaded before S33 has no thumb/medium variants, so gallery thumbnails fall back to legacy 400px thumbnails or full-size images.
- CFLSR improves when family members can browse the entire family archive in one place and when all media loads quickly with proper variants.

Primary KPI:
- provide a single browsable view of all family media.

Secondary KPI:
- ensure all existing media has optimized variants for fast gallery loading.

## Scope

- In scope:
  - `/gallery` route rendering a top-level gallery page
  - filters: media type (photo/video/audio/document), person tag, date range, uploader
  - HTMX pagination (24 items per page, infinite scroll or "Load more" button)
  - reuse the type-organized gallery pattern from media_gallery.html
  - add `/gallery` to the nav bar across all locales
  - API endpoint: `GET /api/media/gallery` with filter query params and pagination
  - variant backfill management command: `uv run python -m app.backfill_variants` that:
    - scans all existing Media records
    - for each image without variants, generates thumb + medium
    - for each video without a poster, generates poster frame (if ffmpeg available)
    - logs progress and skips failures gracefully
  - i18n for gallery page labels and nav item
- Out of scope:
  - cloud storage migration
  - drag-and-drop upload on the gallery page
  - face detection or auto-tagging

## Task Type

- member-facing gallery page + backend maintenance script

## Dependencies and Ordering Assumptions

- Depends on FB-057 (variant pipeline) and FB-058 (gallery template pattern).
- Independent of FB-061 and FB-062.

## Changed Surfaces

- `gallery` (new top-level page)
- `nav` (new gallery link)

## Target Personas

- Primary: `contributing_member`, `genealogy_researcher`
- Safety: `mobile_first_relative`, `family_admin`

## Required Scenario IDs

- `browse_all_family_media`
- `filter_gallery_by_type`
- `filter_gallery_by_person`
- `paginate_gallery_results`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`

## Likely Files

- `app/templates/gallery.html` (new)
- `app/routes/pages.py` (gallery route)
- `app/routes/media.py` (gallery API endpoint with filters)
- `app/templates/base.html` (nav link)
- `app/backfill_variants.py` (new management command)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/test_pages.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_media.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`
- `uv run python -m app.backfill_variants --dry-run` (test backfill without writing)

## Evaluation Environment

- Task:
  build global gallery page with filters and backfill variants for existing media
- Verifier:
  page-load test for /gallery, API test for filter params, backfill dry-run test
- Reference/oracle:
  media_gallery.html partial as the rendering pattern
- Expected evidence:
  /gallery renders with filter controls, pagination works, backfill reports processed count
- Known failure modes / reward hacks:
  - gallery page renders but filters don't actually filter (always shows all media)
  - pagination loads same page repeatedly
  - backfill crashes on corrupt media files instead of skipping gracefully
- Verifiability class:
  `bounded-judgment`
- Context policy:
  reuse existing gallery partial pattern; backfill must be idempotent and safe to re-run

## Acceptance Criteria

- [ ] `/gallery` page renders showing all family media accessible to the current user.
- [ ] Type filter limits results to selected media type.
- [ ] Person filter limits results to media associated with selected person.
- [ ] Pagination loads 24 items per page with "Load more" or infinite scroll.
- [ ] `/gallery` link appears in the nav bar.
- [ ] Backfill command processes existing media and generates missing variants.
- [ ] Backfill skips already-processed media (idempotent).
- [ ] Backfill logs progress and skips failures gracefully.
- [ ] i18n keys exist for gallery labels and nav item in en, es, ru, it, zh.
- [ ] Mobile layout renders gallery grid without horizontal overflow.

## Risk and Verification Notes

- Complexity hotspots:
  - gallery API must respect media visibility (hidden/private filtered for non-admins)
  - pagination state across HTMX requests
  - backfill must handle corrupt/missing files without crashing
- Likely shallow-pass failure modes:
  - gallery loads all media regardless of filters
  - backfill generates variants but stores them in wrong directory
- Required verification depth:
  - page-load + API filter assertions + backfill dry-run
- Sufficient discriminative power means:
  test should fail if filters don't reduce result count or if backfill doesn't create variant files.

## Execution Budget

- Builder may explore:
  - HTMX infinite scroll vs explicit "Load more" button
  - whether to use offset-based or cursor-based pagination
  - backfill batch size and memory management for large media libraries
- Builder must escalate if:
  - gallery API query is too slow on large media tables (may need indexes)
- Material scope drift:
  - upload UX, face detection, cloud storage
- Proof obligations before review:
  - gallery page renders with working filters
  - backfill creates variant files on disk

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] Backfill is idempotent and safe to run on production
- [ ] No P0/P1 regressions
