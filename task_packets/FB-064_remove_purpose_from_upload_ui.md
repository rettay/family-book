# Task Packet - FB-064 Remove Purpose Selector from Upload UI

## Objective

Remove the "Purpose" dropdown (memory/document/evidence) from all media upload surfaces so contributors see a cleaner upload flow focused on file, title, description, and tags.

## Why / KPI

- The purpose classification (memory/document/evidence) is not meaningful to family members uploading photos. It adds friction and confusion.
- Media type (photo/video/audio/document) is auto-detected from MIME type and is the natural organization axis.
- CFLSR improves when upload forms are simpler and contributors don't hesitate over unfamiliar categories.

## Scope

- In scope:
  - Remove the `<select name="purpose">` from the tree sidebar media upload form
  - Remove purpose extraction logic from `uploadTreeMedia()` in tree.js
  - Hardcode `purpose: 'memory'` as default in the upload workflow
  - Remove any purpose selector that appears in the upload metadata modal
  - Keep the `purpose` field in the data model and API (default "memory") for backward compatibility
  - Keep the existing purpose PATCH endpoint for admin use if needed
- Out of scope:
  - Removing the purpose column from the database
  - Changing the media gallery organization (already organized by media type)
  - Modifying the admin moderation queue

## Task Type

- member-facing UX simplification

## Dependencies

- None. Independent of other S35 packets.

## Likely Files

- `app/templates/partials/person_sidebar.html` (remove purpose select, ~lines 1090-1097)
- `app/static/js/tree.js` (remove purpose extraction in uploadTreeMedia, ~lines 3026-3032)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json` (remove purpose label keys if unused elsewhere)

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task: remove purpose selector from upload forms
- Verifier: page-load assertion that purpose select is absent; API test that upload still defaults to "memory"
- Reference/oracle: current upload forms as baseline
- Expected evidence: no `<select name="purpose">` in rendered upload forms; uploads still save with purpose="memory"
- Known failure modes: purpose field silently required by API (it isn't — defaults to "memory")
- Verifiability class: `deterministic`
- Context policy: remove UI only; preserve backend default

## Acceptance Criteria

- [ ] Tree sidebar media upload form has no purpose dropdown.
- [ ] Upload metadata modal has no purpose field.
- [ ] Uploaded media defaults to purpose="memory" without user input.
- [ ] Existing media with non-default purpose values are unaffected.
- [ ] No regression in upload flow (files still upload, metadata still persists).

## Risk and Verification Notes

- Low complexity — removing UI, not adding.
- Verify that no other surface relies on the purpose select being present.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] No upload regressions
