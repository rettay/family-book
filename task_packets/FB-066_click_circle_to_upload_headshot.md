# Task Packet - FB-066 Click Circle to Upload Headshot

## Objective

Make the person avatar circle (on the tree sidebar and person edit page) a direct upload trigger — clicking it opens a file picker and the selected image auto-sets as the person's headshot.

## Why / KPI

- Setting a headshot currently requires: navigate to Media tab → upload → click the star button. Most users won't discover this flow.
- The avatar circle is the most natural affordance for "add a photo of this person" but it currently does nothing (sidebar) or requires a separate button (edit page).
- CFLSR improves when the shortest path to a common action is the most obvious one.

## Scope

- In scope:
  - **Tree sidebar avatar**: clicking the avatar circle (initials or existing photo) opens a file picker. Selected image uploads and auto-sets as headshot. The sidebar avatar and tree node update to show the new photo.
  - **Person edit page avatar**: clicking the avatar circle triggers the same upload flow (currently only the button below does this). Add a visual affordance (camera overlay on hover) so the click target is discoverable.
  - **Tree node camera icon**: already works — clicking the camera icon on photo-less nodes triggers upload. No change needed.
  - Upload goes through the existing `startMediaUploadWorkflow` with `autoSetHeadshot: 'always'`.
  - After upload, refresh the sidebar avatar and tree node photo.
  - i18n for any new tooltip/label text.
- Out of scope:
  - Cropping or resizing before upload
  - Replacing the existing Media tab upload flow (this is an additional shortcut, not a replacement)
  - Multi-file upload from the avatar click (single file only)

## Task Type

- member-facing UX shortcut

## Dependencies

- None. Independent of other S35 packets.

## Likely Files

- `app/templates/partials/person_sidebar.html` (avatar div — add click handler + camera overlay, ~lines 14-21)
- `app/templates/person_edit.html` (avatar div — add click handler + camera overlay, ~lines 50-56)
- `app/static/js/tree.js` (wire sidebar avatar click to upload workflow)
- `app/static/js/main.js` (may need a lightweight single-file upload path that skips the full modal for headshot-only uploads)
- `app/static/css/main.css` (camera overlay hover styles)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task: make avatar circles clickable upload triggers
- Verifier: Playwright or manual test — click avatar, select file, verify headshot is set
- Reference/oracle: existing camera icon on tree nodes as interaction model
- Expected evidence: clicking sidebar avatar opens file picker; photo uploads and sets as headshot
- Known failure modes:
  - Click handler conflicts with existing sidebar interactions
  - Upload succeeds but avatar doesn't refresh (shows old initials until page reload)
  - Camera overlay obscures the existing photo making it hard to see
- Verifiability class: `bounded-judgment`
- Context policy: additive shortcut; don't break existing upload paths

## Acceptance Criteria

- [ ] Clicking the tree sidebar avatar circle opens a file picker (single image).
- [ ] Selected image uploads and auto-sets as the person's headshot.
- [ ] Sidebar avatar updates immediately to show the new photo.
- [ ] Tree node updates to show the new headshot after sidebar refresh.
- [ ] Avatar shows a camera/upload overlay on hover to indicate clickability.
- [ ] Clicking the person edit page avatar circle triggers the same upload flow.
- [ ] Only users who can manage the person see the click affordance.
- [ ] i18n for any new tooltip text across en, es, ru, it, zh.
- [ ] Existing upload paths (Media tab, Change Photo button) still work.

## Risk and Verification Notes

- The sidebar avatar click must not conflict with the existing node click → open sidebar flow. The avatar is INSIDE the sidebar (already open), so there's no conflict.
- On the person edit page, the avatar click must not conflict with the "Change Photo" button below it — they should do the same thing.
- Consider: should clicking an EXISTING photo also trigger re-upload (replace headshot)? Yes — the camera overlay should appear on hover for both empty and photo avatars.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No regression on existing upload/headshot flows
