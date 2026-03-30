# Task Packet - FB-058 Media Gallery and Headshot Management

## Objective

Build per-person media gallery sections organized by type (Photos, Videos, Recordings, Documents) with count badges, lazy-loaded thumbnails using the new variant pipeline, an improved lightbox, and a "Set as headshot" action for any photo.

## Why / KPI

- The current media display is a flat grid with no type separation, no lazy loading, and no way to set a headshot from the gallery. Family members must go to the edit page to change a profile photo.
- CFLSR improves when contributors can browse media by type, quickly identify content, and set profile headshots without leaving the gallery context.

Primary KPI:
- make per-person media browsable and actionable from the wiki and tree sidebar.

Secondary KPI:
- reduce page load weight by serving thumb variants instead of full images.

## Scope

- In scope:
  - per-person gallery with four collapsible sections: Photos, Videos, Recordings, Documents
  - count badges on each section header
  - photos: thumbnail grid (200px squares from thumb variant), click opens lightbox with medium variant, download button for original
  - videos: poster frame thumbnail + play icon, click opens HTML5 video player in lightbox
  - audio: player rows with title, duration badge, native `<audio>` controls
  - documents: PDF icon tile with filename, click opens in new tab
  - lazy-loading thumbnails with `loading="lazy"` attribute
  - "Set as headshot" star action on each photo in the gallery — PUTs `Person.photo_url`
  - current headshot shows filled star / "Current headshot" badge
  - update wiki_person.html to include gallery sections
  - update tree sidebar media tab to use variant thumbnails
  - global family gallery page at `/gallery` with type/person/date filters and HTMX pagination
  - i18n for new labels in en, es, ru, it, zh
- Out of scope:
  - upload experience changes (FB-059)
  - soft delete / visibility enforcement (FB-060)
  - face detection or bounding box tagging (deferred)

## Task Type

- member-facing gallery UX enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-057 (variant pipeline and new media fields must exist).
- FB-059 and FB-060 are independent of this packet.

## Changed Surfaces

- `wiki_person` (gallery sections added)
- `tree_workspace` (media tab uses variants)
- `gallery` (new top-level page)

## Target Personas

- Primary: `contributing_member`, `genealogy_researcher`
- Safety: `mobile_first_relative`, `family_admin`

## Required Scenario IDs

- `browse_person_media_by_type`
- `set_headshot_from_gallery`
- `browse_global_family_gallery`
- `view_media_in_lightbox`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`

## Likely Files

- `app/templates/wiki_person.html`
- `app/templates/partials/media_gallery.html` (rewrite)
- `app/templates/gallery.html` (new)
- `app/routes/pages.py` (gallery route)
- `app/static/js/main.js` (lightbox improvements)
- `app/static/js/tree.js` (variant thumbnail URLs)
- `app/static/css/main.css`
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/test_pages.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  build type-organized media galleries with headshot management and variant-based lazy loading
- Verifier:
  structural review, page-load assertions, i18n checks
- Reference/oracle:
  existing media_gallery.html partial and lightbox as baseline
- Expected evidence:
  page-load tests pass, gallery sections render by type, headshot action works, variant URLs used
- Known failure modes / reward hacks:
  - gallery renders but uses full-size images instead of variants (performance regression)
  - headshot action works but doesn't update tree nodes until page reload
  - global gallery page renders but filters don't work
  - mobile gallery clips thumbnails or hides sections
- Verifiability class:
  `bounded-judgment`
- Context policy:
  use existing lightbox pattern; do not introduce new JS libraries for gallery rendering

## Acceptance Criteria

- [ ] Per-person gallery shows four collapsible sections (Photos, Videos, Recordings, Documents) with count badges.
- [ ] Photo thumbnails use the thumb variant (200px), not the original file.
- [ ] Lightbox loads medium variant first, with download button for original.
- [ ] Video entries show poster frame thumbnail with play icon overlay.
- [ ] Audio entries show title, duration badge, and native player controls.
- [ ] "Set as headshot" action on each photo updates `Person.photo_url`.
- [ ] Current headshot shows a visual indicator (filled star or badge).
- [ ] Global `/gallery` page renders with type, person, date, and uploader filters.
- [ ] Gallery pagination via HTMX (24 items per page).
- [ ] Tree sidebar media tab uses variant thumbnails.
- [ ] i18n keys exist for all new labels across en, es, ru, it, zh.
- [ ] Mobile layout renders gallery grid without horizontal overflow.

## Risk and Verification Notes

- Complexity hotspots:
  - lightbox must handle images, videos, and audio differently
  - headshot action must update both the gallery star indicator and the person's wiki infobox
  - global gallery filtering + pagination must not load all media at once
- Likely shallow-pass failure modes:
  - gallery renders flat (not by type)
  - variant URLs 404 because variant wasn't generated for existing media
- Required verification depth:
  - page-load + headshot round-trip + i18n + mobile layout
- Sufficient discriminative power means:
  tests should fail if gallery uses original images or if headshot action doesn't persist.

## Execution Budget

- Builder may explore:
  - CSS grid vs flexbox for thumbnail layout
  - whether to backfill variants for existing media during migration or on first request
- Builder must escalate if:
  - variant backfill for existing media requires a long-running migration script
- Material scope drift:
  - upload UX changes, soft delete, access control enforcement
- Proof obligations before review:
  - gallery type sections render with correct counts
  - headshot round-trips correctly
  - variant URLs resolve for newly uploaded media

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions on wiki, tree sidebar, or media endpoints
