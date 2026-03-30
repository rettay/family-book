# Task Packet - FB-062 Upload Metadata Panel and Progress Bars

## Objective

Add a pre-upload metadata panel that lets users enter title, description, taken_at date, and person tags before confirming an upload, with per-file progress bars for large uploads.

## Why / KPI

- The current upload flow accepts files immediately with no opportunity to add metadata. Contributors must edit title/description after upload in a separate step, which most skip.
- Large video uploads (up to 250MB) show no progress indication — the user has no idea if the upload is working or stalled.
- CFLSR improves when contributors can describe and tag media in a single step, and when large uploads give confidence through visible progress.

Primary KPI:
- reduce friction for media contribution by combining upload and metadata entry into one step.

Secondary KPI:
- improve large-file upload confidence with progress bars.

## Scope

- In scope:
  - after file selection (before upload starts), show a preview panel with:
    - thumbnail preview for images (from File API)
    - title input field per file
    - description textarea per file
    - taken_at date picker per file
    - person tag typeahead (search family members, chip display)
  - for batch uploads: shared metadata that applies to all files, with per-file override
  - per-file progress bars using XMLHttpRequest upload.onprogress
  - progress bar UI: inline under each file preview showing percentage
  - cancel button to abort upload in progress
  - send title, description, taken_at, and tagged_person_ids with each POST /api/media
  - update POST /api/media to accept title and description form fields
  - mobile-friendly: preview panel and progress bars must work on narrow viewport
  - i18n for new labels across en, es, ru, it, zh
- Out of scope:
  - drag-and-drop upload zone
  - presigned direct-to-bucket uploads
  - gallery rendering changes
  - variant backfill

## Task Type

- member-facing upload UX enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-057 (media model has title and description fields).
- Independent of FB-061.

## Changed Surfaces

- `tree_workspace` (media upload tab)
- `person_edit` (profile photo upload)

## Target Personas

- Primary: `contributing_member`, `mobile_first_relative`
- Safety: `family_admin`

## Required Scenario IDs

- `upload_photo_with_title_and_description`
- `upload_video_with_progress_bar`
- `tag_family_members_at_upload`
- `batch_upload_with_shared_metadata`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`

## Likely Files

- `app/static/js/tree.js` (upload form enhancement)
- `app/static/js/main.js` (uploadMedia enhancement)
- `app/routes/media.py` (accept title, description in POST)
- `app/static/css/main.css` (progress bar styles)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/test_media.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  add pre-upload metadata entry and progress indication
- Verifier:
  API test that title/description persist through upload, page-load assertions for progress bar markup
- Reference/oracle:
  existing uploadTreeMedia() and uploadMedia() as baseline
- Expected evidence:
  test output showing title/description round-trip; progress bar elements in DOM
- Known failure modes / reward hacks:
  - metadata panel appears but data isn't sent with upload request
  - progress bar renders but doesn't update (stuck at 0%)
  - person typeahead makes excessive API calls (missing debounce)
- Verifiability class:
  `bounded-judgment`
- Context policy:
  extend existing upload functions; do not introduce new JS libraries

## Acceptance Criteria

- [ ] After file selection, a preview panel appears showing selected files before upload starts.
- [ ] Each file has title, description, and taken_at fields in the preview panel.
- [ ] Person tag typeahead searches family members and displays as chips.
- [ ] Per-file progress bars update during upload (not 0% → 100% jump).
- [ ] Title and description are sent with POST /api/media and persisted on the Media record.
- [ ] POST /api/media accepts optional title and description form fields.
- [ ] Batch uploads can share metadata across all files.
- [ ] Cancel button aborts in-progress upload.
- [ ] Mobile layout: preview panel is usable on narrow viewport.
- [ ] i18n keys exist for all new labels in en, es, ru, it, zh.

## Risk and Verification Notes

- Complexity hotspots:
  - preview panel must appear after file selection but before upload — requires intercepting the normal flow
  - progress bars need XMLHttpRequest (not fetch) for upload.onprogress
  - person typeahead must debounce API calls
- Likely shallow-pass failure modes:
  - preview panel exists but upload starts immediately without waiting for confirm
  - progress bar present but never updates
- Required verification depth:
  - API round-trip for title/description + page-load + i18n
- Sufficient discriminative power means:
  test should fail if title/description are not persisted or if progress bar markup is missing.

## Execution Budget

- Builder may explore:
  - File API for client-side image thumbnail preview
  - whether to upload files sequentially or in parallel
  - debounce timing for person typeahead (200-300ms recommended)
- Builder must escalate if:
  - progress indication requires a dependency not already in the project
- Material scope drift:
  - drag-and-drop, gallery rendering, variant backfill
- Proof obligations before review:
  - title/description round-trip proven via API test
  - progress bar updates observed in browser

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions on existing upload paths
