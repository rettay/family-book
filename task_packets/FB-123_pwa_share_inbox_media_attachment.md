# Task Packet - FB-123 PWA Share Inbox and Media Attachment

Status: Done

## Objective

Finish the PWA share target by creating reviewable media inbox items instead of orphan files.

## Why / KPI

Mobile sharing is a low-friction way to add family memories. The current share endpoint saves a file and notes that Media/Moment creation is deferred.

## Scope

- In scope:
  - media inbox model
  - share target creates inbox item with file metadata and uploader
  - attach inbox item to person and optional tagged people
  - add title/caption/date/location during review
  - delete/reject inbox item
  - mobile upload progress/error states
- Out of scope:
  - native mobile app
  - background camera-roll sync
  - automatic face recognition

## Likely Files

- `app/pwa/routes.py`
- `app/models/media.py`
- `app/routes/media.py`
- `app/services/media_service.py`
- `app/templates/media_inbox.html`
- `tests/test_media.py`
- `tests/test_pages.py`

## Acceptance Criteria

- [x] PWA share target creates a persisted inbox item.
- [x] Inbox item can be attached to a person and converted to Media.
- [x] Inbox item can be rejected/deleted.
- [x] Access control prevents users from attaching media to unauthorized profiles.
- [x] Mobile flow has clear success/failure copy.

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_pages.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Evidence

- `app/models/media.py`
- `app/pwa/routes.py`
- `app/routes/pages.py`
- `app/templates/media_inbox.html`
- `tests/test_media.py`
- `tests/test_pages.py`

## Definition of Done

- [x] Mobile sharing creates archive value instead of loose files.
