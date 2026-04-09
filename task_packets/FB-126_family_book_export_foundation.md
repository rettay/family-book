# Task Packet - FB-126 Family Book Export Foundation

Status: Done

## Objective

Generate a giftable family-book draft from selected people, stories, events, and media.

## Why / KPI

Storyworth and Remento prove that physical or printable outputs motivate payment. Family Book should start with a digital export before print fulfillment.

## Scope

- In scope:
  - book project model
  - selection of people, sections, stories, and media
  - Markdown and PDF draft export
  - table of contents and basic cover page
  - provenance/source notes where available
  - visibility-respecting export
- Out of scope:
  - print fulfillment
  - professional layout editor
  - AI-written full biographies

## Likely Files

- `app/models/book.py`
- `app/routes/book_export.py`
- `app/services/book_export_service.py`
- `app/templates/book_export.html`
- `tests/test_book_export.py`
- `docs/ops/book-export.md`

## Acceptance Criteria

- [x] User can create a book draft from selected people/stories/media.
- [x] Markdown export works.
- [x] PDF export works or has a documented staged fallback.
- [x] Export respects permissions and private media settings.
- [x] Output includes provenance/source notes when present.

## Validation Commands

- `uv run pytest tests/test_book_export.py tests/test_access_control.py -q`
- `git diff --check`

## Definition of Done

- [x] Product has a giftable deliverable for paid conversion.

## Builder Notes

- Export projects are stored in `app/models/book.py`.
- Output is generated on demand by `app/services/book_export_service.py`.
- Download access is restricted to the project creator, and generated files are not retained on disk.
- Operational notes are documented in `docs/ops/book-export.md`.

## Verification

- `uv run pytest tests/test_book_export.py tests/test_pages.py -q`
- `git diff --check`
