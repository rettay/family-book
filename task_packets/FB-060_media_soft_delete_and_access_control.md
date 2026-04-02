# Task Packet - FB-060 Media Soft Delete and Access Control

## Objective

Implement media visibility enforcement (family/private/hidden), soft-delete for non-admins, permanent delete for admins, tag-self-removal, and an admin moderation queue for hidden media to make media management safe and recoverable.

## Why / KPI

- Current media deletion is immediate and permanent with no recovery path. There are no per-media visibility controls — all media inherits person visibility. Non-admins cannot moderate their own contributions.
- CFLSR improves when family members trust that accidental deletions are recoverable and that they have control over media they contributed.

Primary KPI:
- make media deletion safe by implementing soft-delete with admin recovery.

Secondary KPI:
- add per-media visibility so sensitive content can be shared selectively within the family.

## Scope

- In scope:
  - enforce `visibility` field on all media serving endpoints: `family` (all members), `private` (uploader + admin), `hidden` (admin only)
  - non-admin DELETE sets `visibility = "hidden"` (soft delete), does NOT remove files
  - admin DELETE permanently removes files and DB record
  - admin can restore hidden media (set visibility back to `family`)
  - any family member can remove their own ID from `tagged_person_ids` (PATCH endpoint)
  - any family member can request their own primary photo be unset (only for their own person record)
  - uploader can change visibility on their own media (family ↔ private)
  - admin moderation queue: `GET /api/admin/media/hidden` listing recently hidden items with restore/purge actions
  - admin moderation UI: simple table on admin page showing hidden media with restore and permanent delete buttons
  - protect primary photo: non-admin cannot soft-delete media that is another person's `photo_url`
  - update all media endpoints to check visibility before serving
  - update `can_view_media()` to respect the new visibility field
  - tests for each row in the access control table (see below)
- Out of scope:
  - lifecycle policy (auto-purge after 90 days) — deferred to cron job
  - gallery UI changes (FB-058 handles display)
  - upload changes (FB-059)

## Task Type

- backend access control and moderation enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-057 (visibility column must exist in the model).
- Independent of FB-058 and FB-059.

## Access Control Table to Implement

| Action | Uploader | Tagged Person | Any Member | Admin |
|---|---|---|---|---|
| View (family) | yes | yes | yes | yes |
| View (private) | yes | no | no | yes |
| View (hidden) | no | no | no | yes |
| Edit metadata | yes | no | no | yes |
| Tag people | yes | no | yes | yes |
| Remove own tag | — | yes | — | yes |
| Set own headshot | yes | yes (self) | no | yes |
| Soft delete | yes | no | no | yes |
| Permanent delete | no | no | no | yes |
| Change visibility | yes (own) | no | no | yes |

## Likely Files

- `app/access_control.py` (update `can_view_media`, add `can_edit_media`, `can_delete_media`)
- `app/routes/media.py` (enforce visibility, soft delete, admin endpoints)
- `app/models/media.py` (no changes — visibility added in FB-057)
- `app/templates/admin.html` (moderation queue section)
- `tests/test_media.py` (access control tests)
- `tests/test_access_control.py`

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_access_control.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  enforce media visibility, implement soft delete, build admin moderation
- Verifier:
  pytest assertions for every cell in the access control table
- Reference/oracle:
  existing `can_view_media()` and `can_manage_person()` patterns
- Expected evidence:
  test output showing permission checks pass/deny correctly for each role × action combination
- Known failure modes / reward hacks:
  - visibility field exists but endpoints don't check it (admin sees everything regardless)
  - soft delete sets visibility but old thumbnails still serve without auth check
  - uploader can change visibility on other people's uploads
  - primary photo protection is bypassed when directly calling DELETE API
- Verifiability class:
  `deterministic`
- Context policy:
  enforce on the server; do not rely on UI hiding for access control

## Acceptance Criteria

- [ ] `GET /api/media/{id}/file` returns 403 for private/hidden media when user lacks access.
- [ ] `DELETE /api/media/{id}` by non-admin sets `visibility = "hidden"` (soft delete).
- [ ] `DELETE /api/media/{id}?permanent=true` by admin removes files and DB record.
- [ ] Admin can restore hidden media via `PATCH /api/media/{id}` with `visibility: "family"`.
- [ ] `PATCH /api/media/{id}/untag` removes the current user's ID from `tagged_person_ids`.
- [ ] Uploader can change visibility of their own media between `family` and `private`.
- [ ] Non-admin cannot soft-delete media that is another person's `photo_url`.
- [ ] `GET /api/admin/media/hidden` returns hidden media for admin moderation.
- [ ] Admin page shows moderation queue with restore and permanent delete actions.
- [ ] Tests cover every row in the access control table with positive AND negative cases.
- [ ] Existing media that has no visibility field defaults to `family` (via migration default).

## Risk and Verification Notes

- Complexity hotspots:
  - visibility check must be applied consistently across file, thumbnail, variant, and metadata endpoints
  - soft delete must not orphan variants (files stay on disk until permanent delete)
  - primary photo protection edge case: what if uploader soft-deletes their own photo that someone else set as headshot?
- Likely shallow-pass failure modes:
  - visibility enforced on file endpoint but not on thumbnail/variant endpoints
  - admin moderation queue lists items but restore button doesn't work
  - permission tests only check happy path, not denial
- Required verification depth:
  - deterministic pytest with every access control cell tested both ways (allow and deny)
- Sufficient discriminative power means:
  tests should fail if any endpoint serves hidden content to non-admins or if soft delete becomes permanent.

## Execution Budget

- Builder may explore:
  - whether to add a `deleted_at` timestamp for soft-deleted media (to support lifecycle policy later)
  - whether primary photo protection should auto-unset the headshot or block the delete
- Builder must escalate if:
  - existing media without visibility needs a data migration beyond simple default
  - primary photo protection creates a circular dependency (user wants to delete but can't because it's someone's headshot)
- Material scope drift:
  - gallery UI, upload UX, lifecycle auto-purge
- Proof obligations before review:
  - all access control table cells tested
  - soft delete demonstrated (visibility changes, files preserved)
  - permanent delete demonstrated (files removed)
  - admin moderation queue functional

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] All tests pass with positive and negative permission cases
- [ ] No P0/P1 regressions in existing media serving
- [ ] Hidden media is invisible to non-admins across all serving endpoints
