# Family Book Codebase Briefing

Purpose: dense technical orientation for collaborators working against the current repo.

## 1. What Family Book Is Right Now

Family Book is a Python/FastAPI application for a private family tree and archive. It already contains a non-trivial backend, server-rendered UI, media upload flow, auth/session handling, access-control logic, backups, i18n, and a D3-based tree view.

This is not a trivial prototype. It is salvageable. The main issue is product-model mismatch, not total technical absence.

## 2. Current Stack

- Backend: FastAPI
- Database: SQLite via SQLAlchemy async + Alembic
- Frontend: Jinja2 templates + HTMX + vanilla JS + D3
- Auth: session cookie backed by DB session rows
- Media: files on disk under `DATA_DIR/media`, served through authenticated endpoints

Key runtime files:

- `app/main.py`
- `app/database.py`
- `app/access_control.py`
- `app/routes/persons.py`
- `app/routes/tree.py`
- `app/routes/media.py`
- `app/routes/auth_routes.py`
- `app/services/auth_service.py`
- `app/services/media_service.py`

## 3. Current Product-Behavior Mismatch

The biggest issue is that the codebase currently implements a much more restrictive access model than the intended collaborative product.

Examples:

- `app/access_control.py` computes graph-distance access for people
- non-admin, non-self users typically get `can_view=True` but `can_view_profile=False`
- media visibility follows person visibility
- person creation is admin-only in `app/routes/persons.py`

This means the app can look "broken" to real users even when the current code and tests are behaving as designed.

## 4. Tests and Health Baseline

Current automated baseline from repo inspection:

- Command: `uv run pytest -q`
- Result: `143 passed, 2 failed, 1 xfailed`

Observed failures were branding/naming drift, not evidence of a collapsed runtime.

Interpretation:

- the repo has meaningful automated coverage
- the test suite is asserting the current restrictive model
- future product-reset work will need to rewrite tests, not just code

## 5. Important Current Contracts

### Auth

- Session cookie name is `session`
- Google login links an external identity to an existing family profile by email match
- unknown users are rejected rather than freely provisioned

### Media

- uploads go through `/api/media`
- media files are stored under `DATA_DIR/media`
- media is served through `/api/media/{id}/file`
- thumbnails are generated for images

### Tree

- tree data comes from `/api/tree`
- the tree view is rendered client-side by `app/static/js/tree.js`

## 6. Main Near-Term Risks

- product docs and runtime behavior diverge
- access-control layer conflicts with collaborative family-wiki direction
- normal member flows are underpowered relative to intended product
- person/content model does not yet cover the desired richness of family history
- multi-user collaboration is not yet proven by end-to-end tests

## 7. Recommended First Change Areas

1. Accounts/invites/admin management foundation
2. Flat family access reset for people, tree, and media
3. Rich person/content model expansion
4. Tree preferences and filters
5. Map support

## 8. Working Rule

Treat the current implementation as a useful codebase with the wrong launch contract, not as throwaway code.
