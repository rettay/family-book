# Sprint Closeout - S51 Lovable Engagement

Status: Closed

Audit result: PASS

## Scope Delivered

- `FB-124` prompt campaigns, prompt responses, weekly digest assembly, and digest preferences
- `FB-125` albums, gallery search/source/album filters, and timeline memory filters for decade/person/album
- `FB-126` family-book project model with Markdown and PDF draft export

## Outcome

- Staff can send prompt campaigns to selected relatives and capture responses as stories or media inbox contributions.
- Prompt campaigns now fail closed if the chosen subject person is not visible to every selected recipient.
- Weekly digests can be sent from the prompts workspace and only include content visible to each recipient.
- Digest delivery can be disabled from settings.
- Gallery browsing now supports search, source filtering, album filtering, and album creation/add flows.
- Timeline now supports memory events plus decade/person/album filters.
- Staff can generate family-book drafts and download both Markdown and PDF outputs.
- Family-book downloads are generated on demand for the project creator and are not retained as durable export files on disk.

## Verification

- `uv run pytest tests/test_prompts.py tests/test_book_export.py -q`
  - `10 passed`
- `uv run pytest tests/test_prompts.py tests/test_book_export.py tests/test_email_delivery.py tests/test_pages.py tests/test_access_control.py tests/test_media.py tests/test_multimedia.py tests/test_timeline.py tests/test_migrations.py -q`
  - `127 passed`
- `uv run pytest tests/test_prompts.py tests/test_email_delivery.py tests/test_book_export.py tests/test_media.py tests/test_multimedia.py tests/test_timeline.py tests/test_pages.py tests/test_migrations.py -q`
  - `112 passed`
- `make test-ui-playwright`
  - passed
  - artifacts: `output/playwright/family-book-flow`
- `uv run python -m py_compile app/models/prompts.py app/models/book.py app/routes/prompts.py app/routes/book_export.py app/services/prompt_service.py app/services/book_export_service.py app/routes/media.py app/routes/pages.py app/routes/timeline.py app/services/timeline_service.py app/services/media_queries.py app/main.py`
  - passed
- `git diff --check`
  - passed
