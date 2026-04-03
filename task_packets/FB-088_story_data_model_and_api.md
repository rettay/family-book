# Task Packet - FB-088 Story Data Model and API

## Objective

Create the `Story` model, Alembic migration, and full CRUD API for person stories — wiki-style attributed entries with a title, rich-text body, and author attribution.

## Why / KPI

- Family Book currently has no way for members to share attributed narratives about a person. The bio field is a single editor-owned block. Stories let any member contribute their own memory or account without overwriting anyone else's.
- This directly increases CFLSR: more contribution surfaces mean more family members can complete the loop (sign in → view → contribute → be seen).
- The data model must be designed with future voice/audio attachment in mind, but only text is implemented this sprint.

## Scope

**In scope:**
- `app/models/story.py` — new `Story` SQLAlchemy model
  - `id` (UUID, PK)
  - `person_id` (FK → Person.id, non-null)
  - `title` (Text, non-null)
  - `body` (Text, HTML rich text, sanitized server-side)
  - `author_person_id` (FK → Person.id, non-null — set to current_user's linked Person on create)
  - `audio_media_id` (FK → Media.id, nullable — reserved for future voice; no logic this sprint)
  - `source` (Text, nullable — "user:{person_id}")
  - `created_at`, `updated_at` (TimestampMixin)
- Alembic migration: `stories` table
- Register `Story` in `app/models/__init__.py`
- API endpoints in `app/routes/wiki.py` (or a new `app/routes/stories.py`):
  - `GET  /api/wiki/{slug}/stories` — list all stories for person, ordered `created_at DESC`
  - `POST /api/wiki/{slug}/stories` — create story (any authenticated member)
  - `GET  /api/wiki/{slug}/stories/{story_id}` — single story (for edit-form prefill)
  - `PUT  /api/wiki/{slug}/stories/{story_id}` — update story (wiki-style: any authenticated member)
  - `DELETE /api/wiki/{slug}/stories/{story_id}` — delete story (admin or original author only)
- HTML sanitization: `body` field must pass through `sanitize_html()` on write (same as bio)
- Audit logging: `AuditLog` entry on create, update, delete (entity_type="story")
- i18n keys in all 5 locales (see i18n section below)
- `source` set to `"user:{author_person_id}"` on create

**Out of scope:**
- Audio playback UI (audio_media_id is modeled but not wired to any UI)
- Story revision history (future)
- Story ordering / pinning controls
- Story search or filtering

## Task Type

- Data model + backend API

## Dependencies

- Requires `Person` and `Media` models (both exist)
- FB-089 depends on this packet completing first

## Likely Files

- `app/models/story.py` (new)
- `app/models/__init__.py` (register Story)
- `alembic/versions/XXXX_add_stories_table.py` (new migration)
- `app/routes/wiki.py` or `app/routes/stories.py` (new endpoints)
- `app/main.py` (include stories router if extracted)
- `app/services/sanitization.py` (verify `sanitize_html` is importable — no change expected)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## i18n Keys Required

```
stories.section_title        → "Stories"
stories.add_story            → "Add Story"
stories.edit_story           → "Edit Story"
stories.delete_story         → "Delete Story"
stories.story_title_label    → "Title"
stories.story_body_label     → "Story"
stories.story_by             → "by {name}"
stories.story_empty          → "No stories yet. Be the first to add one."
stories.save                 → "Save Story"
stories.cancel               → "Cancel"
stories.delete_confirm       → "Delete this story?"
stories.count_one            → "1 story"
stories.count_many           → "{n} stories"
```

## Local Validation Commands

```bash
# Run migration
uv run alembic upgrade head

# Check table exists
sqlite3 /data/family.db ".schema stories"

# Run tests
uv run pytest tests/test_wiki.py -v
uv run pytest tests/ -k "story" -v

# Verify i18n parity
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] `stories` table created by Alembic migration with correct columns and FKs.
- [ ] `GET /api/wiki/{slug}/stories` returns a JSON array of stories (empty list if none), ordered newest-first. Each entry includes `id`, `title`, `body`, `author_name` (from linked Person), `created_at`.
- [ ] `POST /api/wiki/{slug}/stories` creates a story attributed to the calling user's Person. Returns the created story. Any authenticated member can call this (not admin-gated).
- [ ] `PUT /api/wiki/{slug}/stories/{story_id}` updates title and body. Any authenticated member can edit any story (wiki-style). Body is sanitized through `sanitize_html()`.
- [ ] `DELETE /api/wiki/{slug}/stories/{story_id}` returns 204. Only original author or admin can delete; non-author non-admin gets 403.
- [ ] `body` HTML is sanitized on every write; raw script tags are stripped.
- [ ] AuditLog entry recorded for create, update, delete with `entity_type="story"`.
- [ ] `audio_media_id` column exists and is nullable; no API logic references it beyond storage.
- [ ] All 13 i18n keys present in all 5 locales.
- [ ] `uv run pytest tests/test_i18n.py` passes without new missing-key failures.

## Risk and Verification Notes

- **Author attribution on write:** `current_user` in routes is a `Person` — use `current_user.id` directly as `author_person_id`. Confirm `require_auth` returns `Person` not a `User` model.
- **Wiki-style editing:** Any member can edit any story. This is intentional (confirmed by product). Do NOT add author-only edit guards.
- **Delete guard:** Only original author OR admin can delete. Test with a third member who is neither author nor admin — must get 403.
- **Sanitization:** The `sanitize_html` function must be called before persisting `body`. Verify it strips `<script>` and `onerror=` attributes.
- **`author_name` in list response:** Requires a join to Person. Use SQLAlchemy relationship or explicit join — do not trigger N+1 for list endpoints.
- **Migration safety:** `audio_media_id` FK to Media — add as nullable with no constraint enforcement at DB level if Media FK causes issues on cascade delete (use `SET NULL` or nullable with no cascade).

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Modes | Verifiability |
|---|---|---|---|---|---|
| Table created | `sqlite3` schema check | Alembic migration | `stories` table with correct columns | Migration skipped or column missing | Direct |
| Create story | POST via test client | DB row count | 201 response, row in DB | Silently fails, wrong author_id | Direct |
| Edit by non-author | PUT from third-party member | 200 response | Story body updated, not 403 | Guard incorrectly blocks | Direct |
| Delete by non-author non-admin | DELETE from third-party | 403 response | No row deleted | Guard missing | Direct |
| Sanitization | POST with `<script>` in body | GET response | Script tag absent in response | Sanitize not called | Direct |
| Audit log | Create/update/delete | AuditLog query | 1 entry per mutation | Audit call missing | Direct |
| i18n parity | `test_i18n.py` | All locale files | Zero key-mismatch failures | Key missing in one locale | Direct |

## Definition of Done

- [ ] Acceptance criteria all satisfied
- [ ] `uv run alembic upgrade head` runs cleanly
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] i18n keys in all 5 locales
- [ ] No N+1 queries on the list endpoint
