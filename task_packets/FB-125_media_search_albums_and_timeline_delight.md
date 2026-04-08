# Task Packet - FB-125 Media Search, Albums, and Timeline Delight

Status: Proposed

## Objective

Make uploaded media easy and enjoyable to browse through search, albums, and timeline filters.

## Why / KPI

The media pipeline is a competitive strength, but users need retrieval and presentation before it feels lovable.

## Scope

- In scope:
  - album/collection model
  - gallery search by title, caption, description, person, date, source, and album
  - timeline filter by decade/person/album
  - empty states and "add to album" flows
  - performance checks with realistic media volume
- Out of scope:
  - face clustering
  - OCR/transcription search
  - object storage migration

## Likely Files

- `app/models/media.py`
- `app/routes/media.py`
- `app/services/media_queries.py`
- `app/templates/partials/media_gallery.html`
- `app/templates/timeline.html`
- `tests/test_media.py`
- `tests/test_multimedia.py`

## Acceptance Criteria

- [ ] User can create/edit/delete albums.
- [ ] Gallery search works across core media metadata.
- [ ] Media can be added/removed from albums.
- [ ] Timeline/gallery respect access control.
- [ ] Query performance is acceptable on seeded large gallery data.

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_multimedia.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [ ] Media browsing becomes a reason to use the product.
