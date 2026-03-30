# Task Packet - FB-059 Media Upload Experience Enhancement

## Objective

Enhance the media upload flow with multi-file selection, per-file progress bars, pre-upload metadata entry (title, description, taken_at, person tags), and client-side type validation to make contributing family media fast and organized.

## Why / KPI

- The current upload accepts one file at a time with no progress indication, no metadata entry before upload, and no person tagging at upload time. Contributors must edit metadata after upload in a separate step.
- CFLSR improves when family members can upload a batch of photos with descriptions and tags in a single flow, see progress for large video uploads, and catch rejected file types before waiting.

Primary KPI:
- reduce friction for batch media contribution by combining upload and metadata entry into one step.

Secondary KPI:
- improve large-file upload experience with visible progress indication.

## Scope

- In scope:
  - multi-file selection: `multiple` attribute on file inputs in tree sidebar and person edit
  - client-side type detection: check `file.type` against allowed MIME list, reject immediately with clear error
  - per-file progress bars using `XMLHttpRequest` `upload.onprogress`
  - pre-upload metadata panel: after file selection, show preview with title input, description textarea, taken_at date picker per file
  - batch metadata: shared title prefix / description / taken_at for all files, with per-file override
  - person tagging at upload time: typeahead search over family members using existing persons API
  - chip-style display for tagged persons
  - mobile: ensure file inputs work with camera roll picker, touch-friendly metadata panel
  - `capture="environment"` attribute for direct camera capture on mobile
  - i18n for new upload labels in en, es, ru, it, zh
- Out of scope:
  - drag-and-drop upload zone (nice-to-have, defer)
  - presigned direct-to-bucket uploads (not needed with local filesystem)
  - gallery rendering changes (FB-058)
  - soft delete (FB-060)

## Task Type

- member-facing upload UX enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-057 (variant generation should exist so newly uploaded media gets variants).
- Independent of FB-058 and FB-060.

## Changed Surfaces

- `tree_workspace` (media upload tab)
- `person_edit` (profile photo upload)
- `media_gallery` (upload section if present)

## Target Personas

- Primary: `contributing_member`, `mobile_first_relative`
- Safety: `family_admin`, `genealogy_researcher`

## Required Scenario IDs

- `upload_batch_photos_with_metadata`
- `upload_video_with_progress`
- `tag_family_members_at_upload`
- `reject_unsupported_file_type`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`

## Likely Files

- `app/static/js/tree.js` (upload functions)
- `app/static/js/main.js` (uploadMedia function)
- `app/templates/person_edit.html` (profile photo upload)
- `app/templates/partials/media_gallery.html` (upload section)
- `app/static/css/main.css`
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/test_pages.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  enhance upload with multi-file, progress, metadata, and tagging
- Verifier:
  structural review, page-load assertions, i18n checks
- Reference/oracle:
  existing uploadTreeMedia() in tree.js as baseline
- Expected evidence:
  page-load tests, multi-file input renders, progress bar markup exists, person typeahead works
- Known failure modes / reward hacks:
  - multi-file input accepts files but only uploads the first one
  - progress bar renders but doesn't update
  - metadata panel appears but data isn't sent with upload request
  - person tagging UI works but tagged IDs aren't included in POST
- Verifiability class:
  `bounded-judgment`
- Context policy:
  extend existing upload functions; do not introduce new JS libraries or frameworks

## Acceptance Criteria

- [ ] File inputs accept multiple files in tree sidebar and gallery upload.
- [ ] Client-side type validation rejects unsupported MIME types with clear error before upload.
- [ ] Per-file progress bars show upload progress for each file.
- [ ] Pre-upload metadata panel allows title, description, and taken_at entry per file.
- [ ] Batch metadata can be set once and applied to all files with per-file override.
- [ ] Person tagging typeahead at upload time includes tagged IDs in POST body.
- [ ] Mobile file input supports camera roll and `capture="environment"` for direct capture.
- [ ] i18n keys exist for all new upload labels in en, es, ru, it, zh.
- [ ] Large video upload (50MB+) shows meaningful progress indication.

## Risk and Verification Notes

- Complexity hotspots:
  - sequential multi-file upload with per-file progress and error handling
  - metadata panel must appear after file selection but before upload starts
  - typeahead must search persons API without excessive requests (debounce)
- Likely shallow-pass failure modes:
  - multi-file UI exists but uploads fail silently for files after the first
  - progress bar present but shows 0% → 100% jump (no intermediate updates)
- Required verification depth:
  - page-load + i18n + structural review of upload JS
- Sufficient discriminative power means:
  tests should fail if multi-file selection doesn't work or if metadata isn't transmitted.

## Execution Budget

- Builder may explore:
  - whether to upload files sequentially or in parallel (sequential recommended for simplicity)
  - XMLHttpRequest vs fetch + ReadableStream for progress
- Builder must escalate if:
  - progress indication requires a new dependency
- Material scope drift:
  - gallery rendering, soft delete, presigned uploads
- Proof obligations before review:
  - multi-file upload demonstrated
  - progress bar updates observed
  - metadata transmitted in API request

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions on existing upload paths
