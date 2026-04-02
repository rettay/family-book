# Task Packet - FB-057 Media Data Model and Variant Pipeline

## Objective

Add visibility, processing status, title, and description fields to the Media model, implement image variant generation (thumb/medium), video poster frame extraction, and audio duration extraction to make media records complete and gallery-ready.

## Why / KPI

- The current media system stores files but lacks visibility controls, processing status, and multiple image sizes. Gallery performance depends on small thumbnails; video/audio entries show no duration or poster frame.
- CFLSR improves when family members can browse media quickly (small thumbnails load fast) and understand what they're looking at (video posters, audio durations) without downloading full files.

Primary KPI:
- enable variant-based media serving so galleries load fast and display type-appropriate previews.

Secondary KPI:
- add visibility and processing status fields to support soft-delete and async processing in later packets.

## Scope

- In scope:
  - new Media columns: `title` (String 300), `description` (Text, migrated from `caption`), `visibility` (String 20, default "family"), `processing_status` (String 20, default "ready")
  - remove unused `is_profile` column
  - Alembic migration with data migration: copy existing `caption` values to `description`
  - image variant generation at upload time: `thumb` (200x200 square crop) and `medium` (800px max) in addition to existing 400px thumbnail
  - new storage layout: `media/variants/{media_id}/thumb.jpg`, `media/variants/{media_id}/medium.jpg`
  - keep existing `media/thumbnails/{media_id}.jpg` as backward-compatible alias for thumb variant
  - video poster frame extraction via subprocess `ffmpeg` call (best-effort, graceful fallback)
  - audio duration extraction via `mutagen` library
  - populate `duration_seconds` field for audio and video uploads
  - new API endpoint: `GET /api/media/{media_id}/variant/{variant}` serving thumb, medium, or poster
  - add `Cache-Control: private, max-age=3600` to file and variant serving responses
  - add `ffmpeg` to Dockerfile
  - add `mutagen` to pyproject.toml
  - update `PersonUpdate`/`PersonCreate` schemas if needed
  - tests for variant generation, duration extraction, new endpoint, migration
- Out of scope:
  - gallery UI changes (FB-058)
  - upload UX changes (FB-059)
  - soft delete behavior (FB-060)
  - cloud storage migration (deferred)
  - PDF page-1 thumbnail (deferred — low priority)

## Task Type

- backend data-model, processing pipeline, and API enhancement

## Dependencies and Ordering Assumptions

- No blocking dependencies. S32 work is on person details, not media.
- FB-058, FB-059, FB-060 all depend on this packet.

## Likely Files

- `app/models/media.py`
- `app/services/media_service.py`
- `app/services/io_limits.py`
- `app/routes/media.py`
- `alembic/versions/` (new migration)
- `Dockerfile` (add ffmpeg)
- `pyproject.toml` (add mutagen)
- `tests/test_media.py`
- `tests/test_multimedia.py`

## Validation Commands

- `uv run python -m compileall app tests`
- `uv run pytest tests/test_media.py tests/test_multimedia.py -q`
- `uv run alembic upgrade head`

## Evaluation Environment

- Task:
  add media model fields, generate image variants, extract video/audio metadata
- Verifier:
  pytest assertions on variant generation, duration extraction, API response, migration
- Reference/oracle:
  existing thumbnail generation in media_service.py as baseline pattern
- Expected evidence:
  test output showing variant files created, duration populated, new fields in API response
- Known failure modes / reward hacks:
  - variants generated but not served through new endpoint
  - ffmpeg call blocks the upload request for large videos
  - duration_seconds populated for images (should be null)
  - migration drops caption data instead of copying to description
  - visibility field exists but no endpoint enforces it (enforcement is FB-060)
- Verifiability class:
  `deterministic`
- Context policy:
  stay within media service and API layer; do not touch gallery templates or upload UX

## Acceptance Criteria

- [ ] Media model has `title`, `description`, `visibility`, `processing_status` columns with correct defaults.
- [ ] Migration copies existing `caption` values to `description` without data loss.
- [ ] Image uploads generate thumb (200x200 crop) and medium (800px max) variants in `media/variants/{id}/`.
- [ ] `GET /api/media/{id}/variant/{variant}` serves thumb, medium, and poster variants with auth check.
- [ ] Video uploads extract a poster frame via ffmpeg (or skip gracefully if ffmpeg unavailable).
- [ ] Audio uploads populate `duration_seconds` via mutagen.
- [ ] Video uploads populate `duration_seconds` via ffmpeg (or skip gracefully).
- [ ] File and variant serving responses include `Cache-Control: private, max-age=3600`.
- [ ] Dockerfile includes ffmpeg.
- [ ] `is_profile` column is removed from Media model.
- [ ] Existing media files and thumbnails remain functional (backward compatible).
- [ ] Tests cover variant generation, duration extraction, new endpoint, and migration.

## Risk and Verification Notes

- Complexity hotspots:
  - ffmpeg subprocess timing (must not block request for large videos — use timeout)
  - backward compatibility with existing `media/thumbnails/` path
  - migration of caption → description for existing records
- Likely shallow-pass failure modes:
  - variants generated but old thumbnail endpoint breaks
  - ffmpeg installed but not on PATH in Docker
- Required verification depth:
  - deterministic pytest with positive and negative cases
- Sufficient discriminative power means:
  tests should fail if variants aren't created, duration isn't extracted, or migration loses data.

## Execution Budget

- Builder may explore:
  - whether to generate variants synchronously or in a background thread
  - ffmpeg timeout value for poster frame extraction
  - mutagen API for duration extraction across audio formats
- Builder must escalate if:
  - ffmpeg adds >50MB to Docker image and alternative approaches exist
  - mutagen cannot handle a common audio format in ALLOWED_MIME_TYPES
- Material scope drift:
  - gallery UI changes, upload UX changes, soft delete enforcement
- Proof obligations before review:
  - all variant types generated and served
  - duration populated for audio and video
  - migration preserves existing data

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] All tests pass
- [ ] Migration is reversible
- [ ] No P0/P1 regressions in existing media endpoints
- [ ] Dockerfile builds successfully with ffmpeg
