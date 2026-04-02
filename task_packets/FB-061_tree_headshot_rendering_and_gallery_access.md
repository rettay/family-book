# Task Packet - FB-061 Tree Headshot Rendering and Gallery Access

## Objective

Make uploaded headshots reliably visible on tree node circles, provide a clear "Set as headshot" action from every surface where media is displayed, and ensure the per-person media gallery is discoverable from the tree sidebar and wiki page.

## Why / KPI

- Users have uploaded photos and set headshots but tree nodes render empty circles instead of the photo. The image fails silently with no fallback.
- The "Set as headshot" action exists in code but is not visible or reachable from the tree sidebar where most users interact with media.
- The type-organized media gallery (Photos/Videos/Recordings/Documents) is not linked from the tree sidebar, making it undiscoverable.
- CFLSR degrades when contributors upload photos expecting to see them on the tree and nothing changes.

Primary KPI:
- every person with a photo_url renders their headshot on the tree node circle, with graceful fallback when loading fails.

Secondary KPI:
- any family member can set a headshot from the tree sidebar and immediately see it reflected on the tree.

## Scope

- In scope:
  - **diagnose and fix the root cause** of tree node photos not rendering — this may be an SVG image loading issue, a variant URL 404 for pre-existing media, a race condition, or a data issue where photo_url is not set despite upload
  - ensure the onerror fallback chain works in production (variant/thumb → /file → initials) by testing with the real production database and a person who has media uploaded
  - add a visible "Set as headshot" button in the tree sidebar media tab for image items
  - add a link from the tree sidebar to the full per-person media gallery (wiki page gallery section)
  - ensure the wiki person page renders the type-organized gallery sections (Photos/Videos/Recordings/Documents) when media exists
  - verify that `uploadProfilePhoto()` on the person edit page correctly sets `photo_url` AND that the tree re-renders with the new photo on next load
  - write a Playwright test with a seeded person that has `photo_url` set, verifying the tree node renders an `<image>` element (not just initials)
  - i18n the "Set as headshot" button label across en, es, ru, it, zh
- Out of scope:
  - cloud storage migration
  - variant backfill migration script (existing media without variants should still work via fallback)
  - global /gallery page

## Task Type

- member-facing rendering fix and UX enhancement

## Dependencies and Ordering Assumptions

- Depends on S33 (FB-057 variant pipeline and FB-058 gallery must exist).
- Independent of other S34 packets.

## Changed Surfaces

- `tree_workspace` (node rendering, sidebar media tab, sidebar gallery link)
- `wiki_person` (gallery sections visibility)
- `person_edit` (profile photo upload verification)

## Target Personas

- Primary: `contributing_member`, `family_admin`
- Safety: `mobile_first_relative`

## Required Scenario IDs

- `view_headshot_on_tree_node`
- `set_headshot_from_tree_sidebar`
- `navigate_to_person_gallery_from_tree`
- `upload_photo_and_see_it_on_tree`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`

## Likely Files

- `app/static/js/tree.js` (renderNode photo fallback, createMediaNode headshot button, sidebar gallery link)
- `app/templates/wiki_person.html` (verify gallery sections render)
- `app/templates/partials/media_gallery.html` (verify headshot star renders)
- `app/templates/person_edit.html` (verify uploadProfilePhoto sets photo_url)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/ui/playwright-flow-checks.sh` (new test: tree node with photo_url renders image)
- `tests/ui/playwright_seed.py` (seed a person with photo_url and a media file on disk)
- `tests/test_pages.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_media.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`
- `make test-ui-playwright` (if Playwright is available)

## Evaluation Environment

- Task:
  make tree headshots render reliably, headshot action reachable, gallery discoverable
- Verifier:
  Playwright test with seeded photo_url person, deterministic page-load assertions
- Reference/oracle:
  the screenshot at screenshots/Screenshot 2026-03-30 at 12.59.28 PM.png showing the bug — Ross's sidebar shows his photo but his tree node is empty
- Expected evidence:
  Playwright test proves tree node renders `<image>` element when photo_url is set; headshot button visible in sidebar; gallery link navigates to wiki
- Known failure modes / reward hacks:
  - SVG image element appended but image fails to load silently (the exact current bug)
  - headshot button exists but clicking it doesn't update the tree node until full page reload
  - gallery link exists but wiki page doesn't render gallery sections because media_list isn't passed to template
  - Playwright test passes because it checks DOM element existence but not actual image rendering
- Verifiability class:
  `bounded-judgment`
- Context policy:
  fix the actual rendering bug first, then enhance UX; verify with real browser behavior, not just DOM assertions

## UI Review Requirements

- Structural oracle:
  - tree node with photo_url has an SVG `<image>` element with valid href
  - sidebar media items for images have a headshot action button
  - sidebar has a link to the person's gallery
- Browser oracle:
  - Playwright test with seeded person + photo_url + media file on disk
  - image actually renders in the circle (not just DOM present)
- Visual/persona oracle:
  - `contributing_member` uploads photo, sets headshot, sees it on tree
  - `mobile_first_relative` can find the gallery from the tree sidebar

## Acceptance Criteria

- [ ] Tree node circle renders the headshot image when person.photo_url is set and the media file exists.
- [ ] If the image fails to load, the tree node falls back to showing initials (not an empty circle).
- [ ] Tree sidebar media tab shows a "Set as headshot" button on each image item.
- [ ] Clicking "Set as headshot" in the sidebar updates person.photo_url AND the tree node re-renders with the photo.
- [ ] Tree sidebar includes a link to the person's full media gallery (wiki page or dedicated gallery view).
- [ ] Wiki person page renders type-organized gallery sections when the person has media.
- [ ] Person edit page "Change Photo" correctly sets photo_url and the tree reflects it on next load.
- [ ] "Set as headshot" button label is i18n'd across en, es, ru, it, zh.
- [ ] Playwright test with seeded photo_url person verifies the tree node has an `<image>` element.
- [ ] Mobile layout: headshot button and gallery link are reachable on narrow viewport.

## Risk and Verification Notes

- Complexity hotspots:
  - SVG `<image>` loading behavior varies by browser — onerror may not fire in all cases
  - pre-existing media without variants needs the fallback chain to work (variant/thumb → legacy thumbnail → /file)
  - tree re-render after headshot change may require explicit tree data reload, not just sidebar refresh
- Likely shallow-pass failure modes:
  - DOM element exists but image still doesn't render (wrong URL, auth cookie not sent with SVG image request)
  - headshot button appears but tree doesn't update until full page refresh
  - gallery link opens wiki page but gallery section is empty because media isn't loaded
- Required verification depth:
  - Playwright with seeded data + real file on disk
  - manual browser verification on production
- Sufficient discriminative power means:
  test should fail if tree node shows initials when photo_url is set and media file exists on disk.

## Execution Budget

- Builder may explore:
  - whether the SVG image issue is related to cookie authentication (SVG image requests may not include cookies in some browsers)
  - whether using a data: URL or blob URL instead of an authenticated endpoint would be more reliable for tree node photos
  - whether the tree needs an explicit data reload after headshot change (not just sidebar refresh)
- Builder must escalate if:
  - SVG `<image>` cannot reliably load authenticated URLs across browsers (may need to pre-fetch and use data URLs)
  - the wiki gallery sections don't render because the template wiring is missing
- Material scope drift:
  - variant backfill, global gallery page, upload UX changes
- Proof obligations before review:
  - tree node renders photo in browser (not just DOM assertion)
  - headshot action round-trips correctly
  - gallery is reachable from sidebar

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass (pytest + Playwright if available)
- [ ] i18n parity maintained
- [ ] No empty circles on tree for persons with valid photo_url and media file
- [ ] Auditor verifies with production screenshot showing headshot on tree node
