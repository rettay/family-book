# Family Book Sprint Board - 2026 Q1

## Current Sprint

### `S43 - Tree Interaction Polish + Media Editing`

Status: Closed

### Sprint Goal

Make the tree a first-class editing surface for names and relationships. Give users flexible sidebar layout. Enable basic photo editing and audio/voice playback in the family record.

### Why This Sprint Next

S42 closed the stories contribution loop. S43 deepens the tree as a workspace (UX North Star) and lowers the barrier for non-technical family members to contribute and curate media.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 97 | FB-097 | Fix Tree Panel Toggle Label | P0 | done |
| 92 | FB-092 | Inline Tree Node Name Edit | P0 | done |
| 93 | FB-093 | Relationship Edit from Tree | P1 | done |
| 94 | FB-094 | Sidebar Popup, Resize, and Dock | P1 | done |
| 95 | FB-095 | Photo Editing — Crop, Rotate, Resize | P1 | done |
| 96 | FB-096 | Audio Upload, Playback, and TTS | P2 | done |

### Sprint Exit Criteria

- Tree panel toggle tab correctly shows "Hide…" when open and "Expand…" when closed (done)
- Double-click a tree node → inline name edit overlay; save updates label in place
- Right-click a node → "Edit relationships" → change kind or remove with inline confirm
- Tree sidebar can be popped out as a floating panel, dragged, resized, and re-docked
- Photo edit (crop/rotate/resize) available on upload and on existing gallery photos
- Audio files accepted as media; play back on story cards and in the gallery
- TTS "Listen" button on story cards (Web Speech API, hidden if unsupported)
- `uv run pytest tests/` passes with coverage for new endpoints
- i18n parity maintained

### Outcome

All 6 packets shipped. 23 new tests pass (18 builder + 5 new tree i18n parity). Sidebar resize handle added to address auditor P1. TTS button hidden on unsupported browsers. `edit-image` now updates `file_hash` on replacement. Merged to `codex/staging` 2026-04-05, audited and closed 2026-04-05.

---

## Closed Sprint

### `S42 - Person Stories`

Status: Closed

### Sprint Goal

Any family member can write titled, wiki-style stories attributed to any person. Stories live on the Family Bio page as a full read experience. The tree sidebar shows a count that links back to the stories section.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 88 | FB-088 | Story Data Model and API | P0 | done |
| 89 | FB-089 | Story Authoring UI on Wiki Page | P0 | done |
| 90 | FB-090 | Story Count in Tree Sidebar | P1 | done |
| 91 | FB-091 | Fix Flaky "Adoptive Kind" Playwright Test | P2 | done |

### Outcome

All 4 packets shipped. 27 story tests pass (17 builder + 10 adversarial probes). i18n parity maintained across 5 locales. Flaky Playwright test fixed with targeted `waitForFunction`. Merged to `codex/staging` 2026-04-02, audited and closed 2026-04-03.

---

## Closed Sprint

### `S41 - UAT/Staging Pipeline`

Status: Closed

### Sprint Goal

Establish a staging environment with comprehensive demo data, a promotion workflow with manual approval gate, and an acceptance checklist — so production deploys only happen after staging verification. This is the last infrastructure sprint before the stories feature.

### Why This Sprint Next

Real family members are on production. Every push to main auto-deploys with no testing buffer. The stories feature and tree-native Phase 2 both need safe testing before they reach real users. This sprint builds the safety net.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 83 | FB-083 | Staging Environment Configuration | P0 | done |
| 84 | FB-084 | Promotion Workflow and CI Gate | P0 | done |
| 85 | FB-085 | Staging Acceptance Checklist | P1 | done |
| 86 | FB-086 | Comprehensive Demo Seed Data | P1 | done |
| 87 | FB-087 | Developer Workflow Documentation | P2 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S41-1 | Railway staging env vars, volume verification, first deploy | done |
| S41-2 | CI manual approval gate for production, promotion guide | done |
| S41-3 | Staging acceptance checklist (quick + full) | done |
| S41-4 | ~100 person comprehensive seed with international names | done |
| S41-5 | Developer workflow docs, CLAUDE.md update | done |

### Sprint Exit Criteria

- staging environment boots and serves pages at a staging URL
- pushing to codex/staging auto-deploys to staging
- pushing to main triggers quality checks then waits for manual approval before production deploy
- staging acceptance checklist exists (quick 5-item + full 30-item versions)
- ~100 person demo seed runs on staging with international names, complex relations, diverse ages
- developer workflow documented end-to-end
- CLAUDE.md updated to reference new workflow

---

## Closed Sprint

### `S40 - Tree Context Menu (Phase 1: Tree-Native Interactions)`

Status: Closed

### Sprint Goal

Add a right-click / long-press context menu on tree nodes, replacing hover-only buttons with a discoverable, mobile-friendly interaction surface. Phase 1 of the tree-native interactions initiative.

### Why This Sprint Next

Current tree interactions require sidebar detours for common actions. The context menu puts the top 7 actions one right-click away. Hover-only buttons (camera icon, plus button) are invisible on mobile — the context menu replaces them with long-press.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 81 | FB-081 | Tree Node Context Menu | P0 | done |
| 82 | FB-082 | Remove Node Hover Buttons | P1 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S40-1 | Context menu: right-click/long-press, 7 actions, keyboard nav, positioning, i18n | done |
| S40-2 | Remove camera icon and plus button overlays from nodes | done |

### Sprint Exit Criteria

- right-click on node shows floating context menu with 7 actions
- long-press on mobile shows the same menu
- menu is keyboard navigable and stays within viewport
- hover-only camera/plus buttons removed from nodes
- context menu does not interfere with graph mode
- i18n parity maintained

### Horizon: Tree-Native Interactions Phases 2-4

See `docs/strategy/tree-native-interactions-roadmap.md` for the full initiative plan:
- Phase 2: Inline node editing card (click node → floating edit card, not sidebar)
- Phase 3: Canvas relationship creation (drag-to-connect nodes)
- Phase 4: Remove left panel, float all controls (full-width tree)

Phases 2-4 require UAT/staging pipeline before implementation.

---

## Closed Sprint

### `S39 - Ancestor Branch View`

Status: Closed

### Sprint Goal

Add ancestor branch filtering so users can focus on a single person's lineage within the family tree, reducing visual noise from unrelated branches.

### Why This Sprint Next

Direct user request: a family member wants to see only a specific branch of the tree. With the tree growing as more family members contribute, focused exploration is essential for usability.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 80 | FB-080 | Ancestor Branch View | P0 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S39-1 | Client-side ancestor collection, tree filtering, banner, URL state, sidebar button, i18n | done |

### Sprint Exit Criteria

- clicking "View ancestors" on a person filters the tree to their ancestors + partners
- a banner shows "Showing ancestors of {name}" with "Show full tree" to exit
- URL updates to ?ancestors_of={id} and is bookmarkable
- loading a page with ?ancestors_of applies the filter on initial render
- i18n parity maintained

---

## Closed Sprint

### `S38 - Tree Sidebar Redesign`

Status: Closed

### Sprint Goal

Transform the tree sidebar from a form-heavy wall into a reading surface that answers "who is this person?" in under 2 seconds, with editing as a smooth secondary mode.

### Design Principle

Sidebar is a reading surface first, editing surface second. Primary job is fast orientation — who is this person, how are they related? Editing slides in as a secondary mode, not the default state.

### Why This Sprint Next

Direct user feedback: the sidebar is overwhelming. Too many sections, too many empty fields, too much chrome. Family members opening a person node want quick orientation, not a 40-field form. This redesign makes the tree workspace feel welcoming for non-technical family members.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 77 | FB-077 | Left Panel Cleanup | P1 | done |
| 78 | FB-078 | Sidebar Identity and Orientation Redesign | P0 | done |
| 79 | FB-079 | Sidebar Details Form and Visual Polish | P1 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S38-1 | Left panel: strip to Search + Preferences, update toggle labels | done |
| S38-2 | Right sidebar: identity elevation, completeness collapse, tab unification | done |
| S38-3 | Details form: hide empty sections, reduce chrome, whitespace polish | done |

### Sprint Exit Criteria

- left panel shows only Search and Display Preferences
- collapse/expand labels read "Expand/Hide Family Tree Settings"
- sidebar identity block (name, photo, key relationships) visible above tabs without scrolling
- completeness shows "X of Y complete" with chevron expander
- "What Should Happen Next" removed, actions merged into completeness items
- tab content uses subtle h3 headings, no card borders
- Details tab hides empty sections by default with "Edit more details" expander
- reduced visual chrome: no card outlines, subtle background fills, more whitespace
- tab strip uses underline indicator

---

## Closed Sprint

### `S37 - Auth Visibility and Invite Reliability`

Status: Closed

### Sprint Goal

Give the admin full visibility into login activity and invite delivery, surface active sessions, set up Resend for email invites, and fix error messages so family members can successfully access the app.

### Why This Sprint Next

Real family members are actively using the site and reporting access issues. The admin has no tools to diagnose what's happening — no login timestamps, no invite delivery tracking, no session visibility. This must be fixed before adding new features or infrastructure.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 72 | FB-072 | Login Tracking and Admin Visibility | P0 | todo |
| 73 | FB-073 | Persist Invite Delivery Status | P0 | todo |
| 74 | FB-074 | Admin Session Visibility | P1 | todo |
| 75 | FB-075 | Resend Setup and Invite Email Polish | P1 | todo |
| 76 | FB-076 | Login and Invite Claim Error UX | P1 | todo |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S37-1 | last_login_at, login/logout audit, admin login column | todo |
| S37-2 | Invite delivery persistence, admin badges, resend button | todo |
| S37-3 | Admin session list, device parsing, session revocation | todo |
| S37-4 | HTML invite email, Resend config, copy-link fallback | todo |
| S37-5 | Login/invite error messages, failed attempt logging | todo |

### Sprint Exit Criteria

- admin can see when each person last logged in
- login/logout events appear in the audit log
- invite delivery status persisted and visible on admin dashboard
- admin can see active sessions per person with device/IP info
- admin can revoke sessions
- invite email is polished HTML with branding
- Resend is configured (or setup documented)
- login and invite claim pages show clear, actionable error messages
- failed auth attempts logged to audit trail

---

## Closed Sprint

### `S36 - Person Enrichment and Sidebar Polish`

Status: Closed

### Sprint Goal

Add place history timeline to person records, wire language autocomplete, introduce auto-save on sidebar fields, tighten sidebar labels, and extend Places autocomplete to the tree sidebar. Last sprint shipping directly to production — S37 will establish a UAT/staging pipeline.

### Why This Sprint Next

Direct user feedback: people move over time and a single residence field isn't enough; language input has no autocomplete guidance; the sidebar save button is too far from the action; labels are verbose for a narrow panel. These are the remaining high-friction UX gaps before shifting focus to infrastructure.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 67 | FB-067 | Place History Timeline | P0 | todo |
| 68 | FB-068 | Language Input Autocomplete | P1 | todo |
| 69 | FB-069 | Auto-Save Person Fields | P1 | todo |
| 70 | FB-070 | Sidebar Label Tightening and Placeholder Polish | P2 | todo |
| 71 | FB-071 | Sidebar Place Autocomplete | P2 | todo |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S36-1 | PlaceHistoryEntry data model, migration, card editors, wiki section | done |
| S36-2 | Language autocomplete from languages.json | done |
| S36-3 | Debounced auto-save on sidebar person fields | done |
| S36-4 | Sidebar label audit and placeholder polish | done |
| S36-5 | Google Places autocomplete on sidebar place fields | done (already wired) |

### Sprint Exit Criteria

- person records support multiple place history entries with date ranges and descriptions
- language input offers autocomplete from the languages vocabulary
- sidebar fields auto-save with debounce and visual feedback
- sidebar labels are concise with helpful placeholders
- sidebar place fields have Google Places autocomplete when configured
- i18n parity maintained

---

### `S35 - Media UX Cleanup`

Status: Closed

### Sprint Goal

Simplify the upload experience by removing the purpose selector, add delete buttons so users can remove media, and make the avatar circle a one-click headshot upload shortcut.

### Why This Sprint Next

Direct user feedback: purpose field confuses contributors, no way to delete media without admin help, and the headshot upload path is too many steps. These are the highest-friction media UX gaps blocking comfortable daily use.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 64 | FB-064 | Remove Purpose Selector from Upload UI | P1 | done |
| 65 | FB-065 | Media Delete Buttons | P0 | done |
| 66 | FB-066 | Click Circle to Upload Headshot | P1 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S35-1 | Remove purpose dropdown from upload forms | done |
| S35-2 | Add delete button with confirmation to all media surfaces | done |
| S35-3 | Make avatar circles clickable upload triggers | done |

### Sprint Exit Criteria

- upload forms have no purpose dropdown; uploads default to "memory"
- media items show a delete button (trash) on sidebar, wiki gallery, and global gallery
- clicking delete shows confirmation then removes the item
- clicking the sidebar avatar circle opens a file picker and auto-sets as headshot
- clicking the person edit page avatar does the same
- avatar shows a camera overlay on hover
- i18n parity maintained across en, es, ru, it, zh

---

## Closed Sprint

### `S34 - Media Polish and Platform Completeness`

Status: Closed

### Sprint Goal

Fix tree headshot rendering so uploaded photos display reliably on tree nodes, make the headshot action and gallery discoverable from the tree sidebar, add pre-upload metadata entry with progress bars, and build the global family gallery with variant backfill for existing media.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 61 | FB-061 | Tree Headshot Rendering and Gallery Access | P0 | done |
| 62 | FB-062 | Upload Metadata Panel and Progress Bars | P1 | done |
| 63 | FB-063 | Global Family Gallery and Variant Backfill | P1 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S34-1 | Fix tree headshot rendering, sidebar headshot action, gallery link | done |
| S34-2 | Pre-upload metadata panel, progress bars | done |
| S34-3 | Global /gallery page, variant backfill | done |

### Audit Notes

First audit found 2 P0, 2 P1, 1 P2 defects. All resolved in-sprint:
- P0: missing person_id in wiki template context (broken upload/headshot on wiki gallery)
- P0: gallery Load More appended duplicate section headers (flattened to chronological grid)
- P1: blob URL memory leak in tree photo cache (added clearTreePhotoCache on loadTree)
- P1: extra fetch in headshot auto-set (pass known photo_url from treeData)
- P2: N+1 gallery queries (pre-computed accessible IDs, SQL-level filters)

483 pass / 0 new regressions. i18n parity across 5 locales.

---

## Closed Sprint

### `S33 - Media Management Enhancement`

Status: Closed

### Sprint Goal

Make family media a trustworthy, organized archive by adding image variants and video/audio metadata extraction, building type-organized per-person galleries with headshot management, enhancing the upload experience with multi-file support and progress indication, and implementing soft-delete with visibility controls and admin moderation.

### Why This Sprint Next

Media is the most emotionally valuable content in a family archive — photos, videos, and voice recordings are irreplaceable. The current media system stores files but provides no organized browsing, no recovery from accidental deletion, no progress feedback on large uploads, and no way to set a profile headshot from the gallery. These gaps directly reduce trust and contribution frequency.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 57 | FB-057 | Media Data Model and Variant Pipeline | P0 | todo |
| 58 | FB-058 | Media Gallery and Headshot Management | P1 | todo |
| 59 | FB-059 | Media Upload Experience Enhancement | P1 | todo |
| 60 | FB-060 | Media Soft Delete and Access Control | P1 | todo |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S33-1 | Data model: new columns, variant generation, audio/video metadata extraction | todo |
| S33-2 | Gallery: per-person type sections, headshot management, lightbox improvements | todo |
| S33-3 | Upload: multi-file, progress indication, metadata entry, person tagging | todo |
| S33-4 | Access control: visibility field, soft delete, admin moderation queue | todo |

### Sprint Exit Criteria

The sprint is successful when all are true:

- image uploads generate thumb, medium, and original variants served through authenticated endpoints
- video uploads have a poster frame thumbnail and extracted duration
- audio uploads have extracted duration
- per-person media galleries show type-organized sections with count badges
- any photo can be set as a person's headshot from the gallery
- a global /gallery page allows browsing all family media with filters
- multi-file uploads work with per-file progress indication
- uploaders can add title, description, and person tags before confirming upload
- non-admin deletion is soft (visibility = hidden), admin can restore or permanently purge
- per-media visibility (family/private/hidden) is enforced on all serving endpoints
- admin moderation queue surfaces recently hidden items
- all access control table rows are tested with positive and negative assertions
- i18n parity maintained across en, es, ru, it, zh
- test and browser baselines remain intact

### Verification Expectations

- Structural lane:
  - variant generation tested with deterministic assertions
  - access control table fully covered with per-row tests
- Rendered-behavior lane:
  - page-load tests for gallery sections, /gallery page
  - headshot round-trip via API
- Visual/persona lane:
  - `contributing_member` can upload photos and set headshot
  - `mobile_first_relative` can browse gallery on mobile
  - `family_admin` can moderate hidden media

### Risks to Watch

- ffmpeg adds Docker image size — must be worth it for poster frames and duration
- variant backfill for existing media may be needed (on-demand or migration)
- soft delete changes the mental model of what "delete" means for non-admins
- multi-file upload with progress requires XMLHttpRequest instead of fetch

### Deferred Beyond S33

| ID | Title | Reason |
|---|---|---|
| — | Cloud storage migration (S3/R2) | Premature for a single-family app on Railway |
| — | PDF page-1 thumbnail | Low priority, PDFs render as icon tiles |
| — | Face detection / bounding box tags | Future feature, scaffolded but not built |
| — | Drag-and-drop upload zone | Nice-to-have, standard file picker works |
| — | Auto-purge lifecycle policy | Needs cron job infrastructure, defer to ops |

### Context

- Packet files:
  - `task_packets/FB-057_media_data_model_and_variant_pipeline.md`
  - `task_packets/FB-058_media_gallery_and_headshot_management.md`
  - `task_packets/FB-059_media_upload_experience_enhancement.md`
  - `task_packets/FB-060_media_soft_delete_and_access_control.md`

---

## Closed Sprint

### `S32 - Person Details Enhancement`

Status: Closed

### Sprint Goal

Upgrade the person edit form from single-field contact storage and raw JSON textareas to multi-value card-based editing for phones, emails, social accounts, and life-story fields, with structured address capture via Google Places auto-population, inline rich-text bio editing, and ISO 639-1 controlled language vocabulary.

### Why This Sprint Next

The person edit form is the primary surface for data contribution, but it currently limits contributors to one phone, one email, six hardcoded social fields, freeform language strings, and raw JSON for education/career. These constraints directly block complete person records and hurt CFLSR because contributors either can't record what they know or need to edit JSON to do so.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 53 | FB-053 | Person Contact and Identity Data Model Enhancement | P0 | todo |
| 54 | FB-054 | Multi-Value Contact and Social Edit UX | P1 | todo |
| 55 | FB-055 | Structured Addresses and Places Auto-Population | P1 | todo |
| 56 | FB-056 | Person Edit Form Polish and Bio Integration | P1 | todo |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S32-1 | Data model: new columns, Pydantic sub-models, migration, API handling | todo |
| S32-2 | Frontend: multi-value phone/email/social/name-history card editing | todo |
| S32-3 | Addresses: structured subfields and Places auto-population | todo |
| S32-4 | Polish: Trix bio editor, structured education/career cards, languages combobox | todo |

### Sprint Exit Criteria

The sprint is successful when all are true:

- person records support multiple phone numbers, email addresses, and social accounts with add/remove editing
- existing single-field contact data is migrated to the new arrays without data loss
- addresses capture structured subfields with Google Places auto-population and graceful fallback
- the bio field uses inline rich-text editing matching the wiki editor
- education, career, and organizations use structured card-based editing instead of JSON textareas
- languages use ISO 639-1 controlled vocabulary via searchable combobox
- all new labels are localized in en, es, and ru
- test and browser baselines remain intact
- existing person data is preserved through migration

### Verification Expectations

- Structural lane:
  - schema validation tests for all new Pydantic sub-models
  - API round-trip tests for new multi-value fields
- Rendered-behavior lane:
  - page-load tests confirm form renders with new card-based controls
  - form submission round-trips multi-value data correctly
- Visual/persona lane:
  - `contributing_member` can add phones, emails, education entries naturally
  - `genealogy_researcher` can record complete contact and life-story data
  - `mobile_first_relative` can reach all controls on narrow viewport

### Risks to Watch

- migration of encrypted contact fields requires careful decrypt/re-encrypt handling
- form serialization complexity increases significantly with multiple card types
- section reordering could break existing JS event bindings
- Trix editor initialization timing vs form submission

### Deferred Beyond S32

| ID | Title | Reason |
|---|---|---|
| FB-031 | Research Tools UX Overhaul | Lower priority than person data capture improvements |
| G-11 | Fan Chart | Platform completeness, not data-capture blocker |
| G-12 | Duplicate Detection | Platform completeness |

### Context

- Packet files:
  - `task_packets/FB-053_person_contact_and_identity_data_model_enhancement.md`
  - `task_packets/FB-054_multi_value_contact_and_social_edit_ux.md`
  - `task_packets/FB-055_structured_addresses_and_places_auto_population.md`
  - `task_packets/FB-056_person_edit_form_polish_and_bio_integration.md`

---

## Closed Sprint

### `S31 - Tree Relationship Correction and Repair`

Status: In Progress

### Sprint Goal

Make the tree trustworthy when members make genealogy mistakes by adding canonical relationship-correction primitives and exposing clear edit, reverse, and remove actions on the existing relationship cards.

### Why This Sprint Next

The tree is already the primary workspace, but relationship correction still has a critical blind spot: a user can create or remove links, yet a mistaken parent-child direction is not directly fixable from the UI. That leaves the most trust-sensitive part of the product behaving like a prototype. The next sprint should therefore make correction of family structure mistakes explicit and safe before broader research or completeness work.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 51 | FB-051 | Relationship Correction Primitives and API Truth | P0 | in_progress |
| 52 | FB-052 | Tree Relationship Correction and Editing Flow | P1 | in_progress |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S31-1 | Canonical parent-child update and reverse primitives | in_progress |
| S31-2 | Tree relationship-card edit, reverse, and remove flow | in_progress |

### Sprint Exit Criteria

The sprint is successful when all are true:

- existing parent-child relationships can be updated without requiring a user-visible delete-and-recreate workaround
- parent-child relationships can be reversed atomically when safe and reject ancestry cycles when unsafe
- existing partnership relationships remain editable through a truthful update path
- the tree sidebar exposes clear edit, reverse, and remove actions for existing relationship cards
- relationship correction remains usable on desktop and mobile
- i18n parity is maintained for any new member-facing copy across `en`, `es`, and `ru`
- the canonical tree, relationship calculator, calendar, and map views all reflect corrected relationship state because the source relationship rows are updated
- test and browser baselines remain intact

### Verification Expectations

- Structural lane:
  - CodeMap over `tree_workspace`
- Rendered-behavior lane:
  - deterministic Playwright checks for parent-child edit, reverse, and remove flows
- Visual/persona lane:
  - persona-backed desktop and mobile review for `contributing_member`, `family_admin`, and `mobile_first_relative`

### Risks to Watch

- reverse direction can be implemented incorrectly if cycle checking still includes the row being reversed
- correction controls can become more confusing if they overlap badly with the existing replace-on-tree flow
- the UI can appear to save while leaving stale sidebar grouping unless post-save refresh is correct

### Deferred Beyond S31

| ID | Title | Reason |
|---|---|---|
| FB-031 | Research Tools UX Overhaul | Lower leverage than repairing canonical relationship trust right now |
| FB-032 | i18n Test Parity | Still important, but not the immediate blocker after tree correction |

### Context

- Packet files:
  - `task_packets/FB-051_relationship_correction_primitives_and_api_truth.md`
  - `task_packets/FB-052_tree_relationship_correction_and_editing_flow.md`

---

## Closed Sprint

### `S30 - Map Truthfulness and Place Intelligence`

Status: Closed

### Sprint Goal

Make `/map` feel truthful and operational instead of decorative by establishing the Google Maps runtime contract, tightening place entry with autocomplete and normalized country capture, persisting coordinates for real marker placement, and making family-distribution semantics legible enough to support future kinship layers.

### Why This Sprint Next

The repo already has a Google-backed map provider contract in config, but the live map still falls back to country centroids and the person/location forms are manual free-text fields with no place intelligence. That means the product can show a prettier basemap once a key is configured, but not a more truthful family map. This is a direct hit to CFLSR because locations are one of the main ways families orient themselves in the shared record, and the current capture flow makes that data hard to enter accurately. The next sprint should therefore connect location entry, normalized place data, and map rendering into one coherent loop.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 47 | FB-047 | Google Maps Platform Contract and Railway Runtime Setup | P0 | todo |
| 48 | FB-048 | Place Autocomplete and Country Normalization Across Person Surfaces | P1 | todo |
| 49 | FB-049 | Coordinate Persistence and Truthful Map Marker Placement | P1 | todo |
| 50 | FB-050 | Kinship-Aware Map Semantics and Family Distribution Readability | P2 | todo |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S30-1 | Google Maps runtime contract and deploy setup | planned |
| S30-2 | Place autocomplete and normalized country capture | planned |
| S30-3 | Persisted coordinates and truthful markers | planned |
| S30-4 | Kinship-aware map semantics and family distribution readability | planned |

### Sprint Exit Criteria

The sprint is successful when all are true:

- Railway/runtime configuration supports split Google credentials via `GOOGLE_MAPS_BROWSER_API_KEY` and `GOOGLE_MAPS_SERVER_API_KEY`, with legacy `GOOGLE_MAPS_API_KEY` fallback during migration, plus optional `GOOGLE_MAPS_MAP_ID`
- map behavior degrades truthfully when Google config is absent and switches cleanly to the Google provider when present
- person create/edit and tree quick-edit place fields support place lookup/autocomplete where configured and remain usable without it
- country codes are normalized and validated rather than relying on members to know ISO alpha-2 inputs
- the map no longer plots only country centroids when normalized coordinates are available for a person’s residence or burial location
- map markers communicate at least the core semantic distinction between residence, burial, and future kinship grouping in a readable way
- the implementation preserves a clear path to future “where is my family” relation-distance views without inventing fake kinship data
- desktop and mobile both remain usable for map viewing and location entry
- i18n parity is maintained for any new member-facing map or place-entry copy across `en`, `es`, and `ru`
- test and browser baselines remain intact

### Verification Expectations

- Structural lane:
  - CodeMap over `map_view`, `person_edit`, and any expanded tree/location surfaces for each packet
- Rendered-behavior lane:
  - deterministic Playwright checks for Google/fallback provider behavior, autocomplete/location normalization behavior, real marker placement, and mobile map/location-entry usability
- Visual/persona lane:
  - persona-backed desktop and mobile review for `contributing_member`, `genealogy_researcher`, `family_admin`, and `mobile_first_relative`

### Risks to Watch

- Places/autocomplete can become UI-only sugar if the normalized result is not persisted into truthful person fields
- Google provider setup can drift into a misleading multi-key contract if runtime docs and code are not aligned
- geocoding and coordinate persistence can introduce false precision if the app stores guessed points without a clear source of truth
- kinship-aware map work can overreach into a full social-graph visualization if packet boundaries are not enforced
- mobile place-entry flows can become cluttered if autocomplete or fallback states are not explicitly validated

### Deferred Beyond S29

| ID | Title | Reason |
|---|---|---|
| G-15 | Calendar notifications / reminders | Useful but lower leverage than map/location truthfulness right now |
| G-16 | Week view / multi-view calendar modes | No longer the next UX blocker after S29 |
| G-17 | Persistent subscription tracking / favorites | Nice-to-have, lower leverage than map/place correctness |
| FB-031 | Research Tools UX Overhaul | Important but lower priority than truthful map/location capture |
| FB-032 | i18n Test Parity | Should still land, but can ship after the new map/place copy stabilizes |

### Context

- Packet files:
  - `task_packets/FB-047_google_maps_platform_contract_and_runtime_setup.md`
  - `task_packets/FB-048_place_autocomplete_and_country_normalization_across_person_surfaces.md`
  - `task_packets/FB-049_coordinate_persistence_and_truthful_map_marker_placement.md`
  - `task_packets/FB-050_kinship_aware_map_semantics_and_family_distribution_readability.md`

---

## Closed Sprint

### `S27 - Tree Interaction UX and Form Polish`

Status: Closed

### Sprint Goal

Reduce UX friction on the tree and person edit surfaces: replace the inconsistent left panel toggle with a compact pill/tab matching the right sidebar, add node-level "add relative" plus buttons, make the toolbar "Add Person" button inline instead of navigating away, unify the dual-mode date input into a single smart field with calendar helper, and clean up duplicate CSS for the language autocomplete.

### Why This Sprint Next

User testing after S26 identified five concrete friction points on the tree and edit surfaces. All are frontend-only (no backend/model changes), low-to-medium risk, and directly improve the tree-as-workspace experience for the genealogy-researcher persona.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| — | — | Tree Interaction UX and Form Polish (5 slices) | P2 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S27-1 | Left panel toggle — match right sidebar pattern | done |
| S27-2 | Node-level "add relative" plus button | done |
| S27-3 | Toolbar add person — inline sidebar form | done |
| S27-4 | Unified smart date input | done |
| S27-5 | Language autocomplete CSS cleanup | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- left panel collapse button is a compact pill (top-right inside panel), expand is a small tab (left edge of canvas) — matches right sidebar
- hover over tree node reveals + circle below node; click opens sidebar Relationships tab
- toolbar Add Person opens sidebar form; fill name and Create adds person to tree without navigation
- empty tree shows prominent + CTA that opens the create form
- date input is a single text field with calendar icon helper and live precision badge
- form always sends birth_date_raw/death_date_raw; server parses to ISO
- clearing a date field clears both raw and ISO values (no orphaned data)
- language autocomplete works with no duplicate CSS between inline and main.css
- i18n parity maintained across all 3 locales (en, es, ru)
- test baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented all 5 slices on `main`
- Round 1 audit: NEEDS WORK — 2 P1 (Playwright broken reference, date-clear regression), 2 P2 (duplicate CSS, hardcoded form labels)
  - Builder fixed all 4 defects
- Round 2 audit: PASS WITH FOLLOW-UPS — 1 P2 (server-side date-clear orphan), 1 P3 (pre-existing hardcoded search hints)
  - Builder fixed both defects
- Round 3 audit: PASS — all 6 prior defects verified resolved, no new P0/P1/P2 findings
  - 3 pre-existing P3/P4 findings noted (unused search-hint data attribute, ~15 hardcoded English strings in left panel, dead .moment CSS) — backlog items, not S27 regressions
- Focused closeout baseline:
  - `uv run pytest -q`: **445 passed, 0 failed**
  - `uv run pytest tests/test_i18n.py -q`: **3 passed** (locale parity)
  - Test count delta: 445 → 445 (no backend changes, test count unchanged from S26)
  - Commit: `cf2009c`

### Context

- Plan file: `.claude/plans/spicy-bouncing-llama.md`
- Key files changed: `tree.html`, `tree.js`, `person_edit.html`, `main.css`, `persons.py`, 3 locale files

---

## Closed Sprint

### `S26 - Platform Completeness: Tree Fix, Social Fields, Add/Remove Person`

Status: Closed

### Sprint Goal

Fix the critical tree traversal bug that left nodes disconnected, add social/contact profile fields, implement freeform date auto-parsing, and provide clear add/remove person affordances across tree and wiki surfaces. Continues the platform-completeness work started in S26a (collapsible tree panel, wiki biography enhancement).

### Why This Sprint Next

FB-035 cleaned up the UI surface. S26a (commit 75c11a9) delivered wiki biography enhancements and the collapsible tree panel. The remaining work was: a P0 tree BFS bug that prevented relationship lines from rendering when people are connected as parents of the root node, missing social profile fields on create/edit, no freeform date parsing, and zero UI for adding or removing people from tree/wiki views.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 33 | FB-033 | Collapsible Tree Controls Panel | P2 | done |
| 34 | FB-034 | Wiki Biography Enhancement and Rich Text Editor | P1 | done |
| — | — | Tree traversal fix + social fields + add/remove person UX | P0–P2 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S26-1 | Collapsible Tree Controls Panel (FB-033) | done |
| S26-2 | Wiki Section Structure Enhancement (FB-034) | done |
| S26-3 | Trix Rich Text Editor Integration (FB-034) | done |
| S26-4 | Structured Form Editing for JSON Arrays (FB-034) | done |
| S26-5 | Tree bi-directional BFS traversal fix (P0 bug) | done |
| S26-6 | Social profile fields, contact fields, burial details | done |
| S26-7 | Freeform date auto-parsing to ISO on save | done |
| S26-8 | Add Person buttons on tree toolbar and wiki index | done |
| S26-9 | Remove Person UI with server-side root guard | done |
| S26-10 | Research page HTMX partial and GEDCOM cleanup | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- left tree controls panel has a collapse/expand toggle matching the right sidebar pattern
- collapse state persists across page reloads via localStorage
- wiki pages display all 11 sections when data exists
- Trix WYSIWYG editor loads for rich text fields in wiki edit mode
- HTML is sanitized server-side via nh3 before storage
- education, career, and organization entries edited via structured form fields
- tree BFS walks both parentToChildren and childToParents — all connected nodes reachable
- relationship lines render correctly for all connected people including root-parent edges
- social profiles (Instagram, Facebook, X, LinkedIn, TikTok, YouTube) on create/edit/wiki
- contact fields (WhatsApp, Telegram, Signal, email) and burial details on edit form
- freeform date strings auto-parsed to ISO on create and update
- "Add Person" button visible on wiki index and tree toolbar
- "Remove Person" visible to admins on person edit and wiki person pages
- DELETE /api/persons/{id} rejects is_root with 403
- delete JS uses data-attribute pattern (no Jinja-in-JS interpolation)
- shared delete-person.js — zero duplicated function bodies
- i18n parity maintained across all 3 locales (en, es, ru)
- root person redaction maintained across all surfaces
- test baselines remain intact

### Exit Result

- Exit result: `pass`
- Phase 1 (S26a): Builder implemented FB-033 + FB-034 on `main` (commit 75c11a9)
  - First audit: PASS WITH REQUIRED FIXES — 1 P1, 8 P2, 16 P3
  - Re-audit: FAIL — 3 P1 in render/revert paths, 4 P2
  - Builder fixed all real findings (3 P1, 1 P2)
  - Final re-audit: PASS
- Phase 2 (S26b): Builder implemented tree fix, social fields, date parsing, add/remove UX (commit 3ba06a2)
  - First audit: NEEDS WORK — 7 findings (1 P0, 1 P1, 2 P2, 3 P3)
    - F-C1 (P0): No server-side is_root guard on DELETE endpoint
    - F-C2 (P1): XSS via backslash in display_name JS interpolation
    - F-B1 (P2): SVG icon path geometry malformed
    - F-C3 (P2): Danger zone text hardcoded English, not i18n
    - F-A1 (P3): pcKindLookup miss on reversed edges
    - F-B2 (P3): Inline styles vs CSS class conventions
    - F-C4 (P3): Duplicated deletePerson() across templates
  - Builder fixed all 7 findings
  - Re-audit: PASS — all findings verified, adversarial XSS probes clear
- Focused closeout baseline:
  - `uv run pytest -q`: **445 passed, 0 failed**
  - `uv run pytest tests/test_i18n.py -q`: **3 passed** (locale parity)
  - Test count delta: 401 → 445 (44 new tests across both phases)
  - New modules: `app/services/date_parsing.py`, `app/static/js/delete-person.js`
  - New dependency (phase 1): `nh3` (Rust-based HTML sanitizer)
  - Migration: `alembic/versions/c27a_social_fields_date_backfill.py`

### Deferred to S27

| ID | Title | Reason |
|---|---|---|
| G-11 | Fan Chart / Pedigree View | High complexity, alternative D3 layout |
| G-12 | Duplicate Person Detection and Merge | High complexity, fuzzy matching + merge UX |
| G-14 | Print / Export Family Sheet | Medium complexity, PDF library decision pending |

### Resolved Questions

| Question | Decision |
|---|---|
| Trix CDN source? | jsDelivr — pinned to trix@2.1.18 with SRI hashes, MIT license |
| Delete person XSS mitigation? | Data-attribute pattern with shared JS file — no Jinja-in-JS interpolation |
| Root person delete protection? | Server-side 403 guard + client-side conditional rendering |
| G-12 + data-quality dashboard? | Deferred to S27 scoping |
| G-14 PDF library? | Deferred to S27 scoping |
| G-11 descendant fan? | Deferred to S27 scoping |

### Context

- Task packets: `task_packets/FB-033_collapsible_tree_controls_panel.md`, `task_packets/FB-034_wiki_biography_enhancement_and_rich_text_editor.md`
- Sanitization module: `app/services/sanitization.py`
- Date parsing service: `app/services/date_parsing.py`
- Shared delete JS: `app/static/js/delete-person.js`
- Wiki service: `app/services/wiki_service.py`
- Wiki routes: `app/routes/wiki.py`

---

## Closed Interstitial

### `FB-035 - UI Cleanup: Rebrand Wiki, Remove Moments/People/Health`

Status: Closed

### What This Is

An interstitial cleanup between S25 and S26. Not a full sprint — a focused product-hygiene pass that tightened navigation and removed three redundant feature surfaces.

### Changes Delivered

| # | Change | Scope |
|---|--------|-------|
| 1 | Rebrand "Wiki" → "Family Bios" | i18n only — 3 locales updated, no URL changes |
| 2 | Remove Health Dashboard page | Routes, service, template, tests deleted |
| 3 | Remove People listing/detail pages | Routes, templates deleted; `/people/{id}/edit`, `/card`, `/new` preserved |
| 4 | Remove Moments feature entirely | Models, routes, services, templates, JS, tests, i18n cleaned; 3 DB tables dropped |

### Impact

- 59 files changed, -5,502 / +83 lines (net -5,419)
- 3 database tables dropped (moments, moment_reactions, moment_comments)
- Migration: `alembic/versions/b48cf4579cfc_drop_moments_tables.py`
- Nav reduced to: Tree, Family Bios, Map, Calendar, Timeline, Research, Admin, Settings

### Audit Trail

- Builder delivered all 4 changes
- Auditor found 8 findings (2 P1, 1 P2, 5 P3)
- Builder fixed all 8 findings
- Re-audit: PASS — 1 pre-existing P3 noted (root person slug gap in test fixtures), non-blocking
- CodeMap check: PASS (12 passed, 13 warnings — all pre-existing)

### Closeout Baseline

- `uv run pytest -q`: **401 passed, 0 failed**
- `uv run pytest tests/test_i18n.py -q`: **3 passed** (locale parity)
- `codemap check .`: **PASS** (12 pass, 13 warn, 0 fail)
- Test count delta: 475 → 401 (74 tests removed with deleted features, no regressions)

### Context

- Plan file: `.claude/plans/spicy-bouncing-llama.md`

---

## Closed Sprint

### `S25 - Research UX Overhaul and Test Infrastructure`

Status: Closed

### Sprint Goal

Transform the buried "External Records" feature into a polished top-level "Research" experience with cleaner source management, per-person saved records, and graceful degradation for unconfigured sources. Add i18n test parity infrastructure to catch locale key mismatches automatically.

### Why This Sprint Next

S24 delivered tree photo headshots and person wiki pages — the two highest-CFLSR visual and narrative improvements. The research tools (shipped in S19) remain the weakest link for the genealogy-researcher persona: wrong naming, visible error states for unconfigured APIs, no way to save external records, and the feature is buried in a sidebar tab. FB-031 promotes "Research" to a top-level experience. The i18n parity test (FB-032) closes a pre-existing gap identified during the S24 audit — there are no automated checks that locale files stay in sync.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 31 | FB-031 | Research Tools UX Overhaul | P1 | done |
| 32 | FB-032 | i18n Test Parity | P2 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S25-1 | Research Rename, Index Page, and Source Visibility (FB-031) | done |
| S25-2 | Saved Records Model and Per-Person Research (FB-031) | done |
| S25-3 | Unified Search UX and Cross-Links (FB-031) | done |
| S25-4 | i18n Test Parity (FB-032) | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- "Research" replaces "External Records" across all surfaces (nav, routes, templates, i18n)
- GET /research returns a research index page with available source descriptions
- unconfigured sources are hidden, not shown with error messages
- unified search bar with source filter chips replaces per-source buttons
- users can save an external record to a person (database-backed)
- saved records appear on person profile and sidebar
- users can delete a saved record
- person profile and wiki page link to pre-filtered research
- root person restrictions maintained on research page
- CEMLA form integrated into research page layout
- a test exists that validates all 3 locale files have matching key sets
- test baselines remain intact, i18n parity maintained

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 25 on `main`
- Auditor issued PASS WITH FOLLOW-UPS — all acceptance criteria evaluated, 2 findings:
  - S25-F01 (P1): Root person name leak in research template — `/research?person_id={root_id}` exposed root person's real first_name/last_name. Fixed by nulling `person_context` when `is_root`.
  - S25-F02 (P2): Hardcoded "Researching:" string not i18n'd — replaced with `{{ t('research.researching') }}` key in all 3 locales.
- All fixes re-audited: PASS — no remaining findings
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `475 passed, 0 failed`
  - 15 new tests added (up from 460 baseline)
  - i18n parity: all 3 locales (en, es, ru) have matching key sets
  - Migration: `alembic/versions/08f77a386981_add_saved_records_table.py`

### Context

- Task packets: `task_packets/FB-031_research_tools_ux_overhaul.md`, `task_packets/FB-032_i18n_test_parity.md`
- Research routes: `app/routes/research.py`
- Research service: `app/services/research_service.py`
- SavedRecord model: `app/models/saved_record.py`

---

## Closed Sprint

### `S24 - Tree Photo Headshots and Person Wiki Pages`

Status: Closed

### Sprint Goal

Make the family tree visually inviting by adding photo contribution prompts on photo-less nodes, and turn structured person data into readable Wikipedia-style biographical pages with a new top-level Wiki feature.

### Why This Sprint Next

S23 delivered source citations, evidence classification, and date intelligence for the genealogy-researcher persona. S24 pivots to user-facing delight and narrative depth: tree nodes that invite photo contribution (the most natural "I can help" moment), and wiki pages that transform disconnected data fields into readable family stories. These are the highest-CFLSR visual and narrative improvements available. Research UX (FB-031) is deferred to S25 to keep this sprint focused.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 29 | FB-029 | Tree Photo Headshots and Add-Photo Prompt | P2 | done |
| 30 | FB-030 | Person Wiki Pages | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S24-1 | Tree Photo Headshots and Add-Photo Prompt (FB-029) | done |
| S24-2 | Wiki Page Foundation — Slug, Index, and Read-Only Rendering (FB-030) | done |
| S24-3 | Wiki Page Interactivity — Section Editing and Cross-Links (FB-030) | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- tree nodes without photos show an add-photo affordance (camera/plus icon, hover-reveals)
- clicking the add-photo affordance opens the photo upload flow for that person
- after upload the tree node re-renders with the new photo
- the add-photo prompt is touch-accessible on mobile
- every person has a slug field for URL-safe wiki paths
- GET /wiki returns an alphabetical index of accessible persons with search/filter
- GET /wiki/{slug} returns a Wikipedia-style biographical page with infobox and templated sections
- sections render from existing structured data (dates, places, education, career, organizations, obituary, relationships)
- empty sections show "Add [section]" prompts that link to editing
- edit buttons on sections open forms that write back to person structured fields via API
- "Wiki" appears in main nav
- person profile and tree sidebar link to wiki page
- wiki page links back to tree node
- hidden persons excluded, root person redacted
- test baselines remain intact, i18n parity maintained

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 24 on `main`
- Auditor issued PASS WITH FOLLOW-UPS — all acceptance criteria met, 2 findings:
  - S24-F01 (P1): `can_edit` UX bug — wiki edit buttons used non-existent `access.can_edit` attribute, fell back to `is_admin` only. Fixed to `access.can_manage`
  - S24-F02 (P2): Missing tests — `test_wiki_index_excludes_hidden` and `test_wiki_edit_unauthorized` not implemented. Added both tests
- All fixes committed in same sprint cycle
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `460 passed, 0 failed`
  - 21 new tests added (up from 439 baseline)
  - i18n parity: all 3 locales (en, es, ru) have matching key sets
  - Migration: `alembic/versions/b919e1b33636_add_person_slug.py`

### Context

- Plan file: `.claude/plans/s24-tree-photos-and-wiki-pages.md`
- Task packets: `task_packets/FB-029_tree_photo_headshots_and_add_photo_prompt.md`, `task_packets/FB-030_person_wiki_pages.md`
- Wiki service: `app/services/wiki_service.py`
- Wiki routes: `app/routes/wiki.py`

---

## Closed Sprint

### `S23 - Source Citations, Evidence, and Date Intelligence`

Status: Closed

### Sprint Goal

Make Family Book credible for serious genealogy research by adding per-person source citations with confidence levels, distinguishing documentary evidence from memory media, and computing age context at life events.

### Why This Sprint Exists

Sprint 22 completed the person-model depth expansion (physical attributes, genetic profile, medical conditions, health dashboard). The next product gap was research credibility: genealogy researchers need to cite their sources, classify media as evidence vs. memory, and see computed ages at life events. Sprint 23 addresses gaps G-07 (source citations), G-09 (evidence classification), and G-13 (date intelligence).

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 28 | FB-028 | Source Citations, Evidence, and Date Intelligence | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S23-1 | Source Citations and Confidence | done |
| S23-2 | Media Purpose Classification | done |
| S23-3 | Date Intelligence and Age Display | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- person records support source_detail (free-text provenance) and confidence (confirmed/probable/uncertain/unknown)
- confidence field is validated with proper 422 on invalid values
- media uploads support purpose classification (memory/document/evidence) with default and PATCH update
- invalid purpose values return 422
- person detail API returns computed current_age for living persons and age_at_death for deceased persons
- year-only precision dates do not compute age (returns null)
- timeline birth/death event labels include age context
- revision snapshots include source_detail and confidence
- root person redaction maintained for new fields
- i18n parity across all 3 locales
- test baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 23 on `main`
- 1 defect found during test run: revision snapshot missing source_detail/confidence — fixed before commit
- Auditor issued PASS WITH FOLLOW-UPS — all 23 acceptance criteria evaluated (23 PASS, 0 FAIL)
  - S23-F01 (P3): Media purpose NULL on pre-existing records — fixed with backfill migration
  - S23-F02 (P3): Confidence defaults to None vs packet-specified "unknown" — accepted as better design, no change
  - S23-F03 (P3): Sidebar media upload missing purpose selector — fixed with select + JS wiring
- All fixes re-audited: PASS — no remaining findings
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `439 passed, 0 failed`
  - 35 new tests added (up from 404 baseline)
  - i18n parity: all 3 locales (en, es, ru) have matching key sets
  - Playwright (pre-existing): `31 PASS, 0 FAIL`

### Context

- Plan file: `.claude/plans/s23-source-citations-evidence-date-intelligence.md`
- Task packet: `task_packets/FB-028_source_citations_evidence_and_date_intelligence.md`
- Migration: `alembic/versions/9e0aa75cb010_add_source_citation_confidence_and_.py`
- Date intelligence service: `app/services/date_intelligence_service.py`

---

## Closed Sprint

### `S22 - Genetic Profile, Physical Attributes, and Family Health Intelligence`

Status: Closed

### Sprint Goal

Close the remaining person-model depth gaps (physical attributes from G-22 deferred, genetic profile and structured medical conditions from G-23) and build a family health dashboard that surfaces hereditary patterns across family members.

### Why This Sprint Exists

Sprint 21 shipped multimedia playback, family timeline, and life story fields (obituary, education, career, organizations). The deferred G-22 item (physical attributes) and the full G-23 gap (genetic profile, structured medical conditions, health dashboard) represent the final content-depth expansion before pivoting to power-user research credibility features.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 27 | FB-027 | Genetic Profile, Physical Attributes, and Family Health Intelligence | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S22-1 | Physical Attributes + Genetic Profile | done |
| S22-2 | Structured Medical Conditions | done |
| S22-3 | Family Health Dashboard | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- person records support height, weight, eye_color, hair_color, blood_type as structured fields
- person records support maternal/paternal haplogroups, DNA test provider, and admixture array
- person records support structured medical conditions with onset, status, severity, hereditary line
- genetic and medical data is encrypted at rest via EncryptedText
- a family health dashboard shows shared conditions, haplogroup distribution, and blood type distribution
- revision snapshots include all new fields with proper encryption
- access control enforced for all new fields
- i18n parity across all 3 locales
- test baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 22 on `main`
- Auditor issued PASS WITH FOLLOW-UPS on S22 — 3 findings:
  - S22-F01 (P1): Encrypted genetic fields leaked in history endpoint snapshots — fixed
  - S22-F02 (P2): admixture/medical_conditions stored unencrypted in revision snapshots — fixed
  - S22-F03 (P3): Inconsistent None handling in update_person JSON arrays — fixed
- Auditor issued PASS WITH FOLLOW-UPS on S21 final pass — 7 findings:
  - S21-F01 (HIGH): Lineage person ID not access-checked — fixed
  - S21-F02 (MEDIUM): Hidden partner names leaked via "?" in timeline — fixed
  - S21-F03 (MEDIUM): Missing mime_type in moment media dict — fixed
  - S21-F04 (CRITICAL GAP): Branch filtering untested — 3 tests added
  - S21-F05 (MEDIUM GAP): No death/marriage event tests — 3 tests added
  - S21-F06 (LOW): Year range validation — no-op, FastAPI handles via int type
  - S21-F07 (LOW): Autoplay browser compat — cosmetic, no action
- All fixes re-audited: PASS — no remaining findings
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `404 passed, 0 failed`
  - i18n parity: all 3 locales (en, es, ru) have matching key sets
  - Playwright (pre-existing): `31 PASS, 0 FAIL`

### Context

- Plan file: `.claude/plans/spicy-bouncing-llama.md`
- Gap triage: `docs/strategy/genealogy-review-triage.md` (G-22 deferred, G-23)
- Migration: `alembic/versions/9dc8ffc2dc25_add_physical_genetic_medical_fields.py`

---

## Closed Sprint

### `S21 - Multimedia, Timeline, and Life Story Depth`

Status: Closed

### Sprint Goal

Close the content depth gaps so Family Book becomes a full multimedia family archive with narrative history: play video/audio, view documents, browse a chronological family timeline, and capture structured life-story data on person records.

### Why This Sprint Exists

Sprint 20 shipped the family calendar, relationship calculator, and visual edge types. The next product bottleneck was content depth: the backend accepted video/audio but the frontend couldn't play them, there was no chronological timeline view, and person records lacked structured life-story fields. Sprint 21 closes these gaps.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 26 | FB-026 | Multimedia, Timeline, and Life Story Depth | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S21-1 | Rich Multimedia Playback | done |
| S21-2 | Family Timeline with Branch Filtering | done |
| S21-3 | Life Story Fields | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- video and audio media play inline in gallery, moments, sidebar, and lightbox
- PDF documents can be uploaded and linked from media surfaces
- a timeline page shows birth, death, marriage, and moment events chronologically with filters
- timeline supports branch and lineage filtering (ancestor/descendant)
- person records support obituary, education, career, and organizations as structured fields
- life story fields are validated with typed sub-models and max_length constraints
- access control enforced: hidden persons and admin-only moments excluded from member timeline
- root person redaction maintained across all new surfaces
- test baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 21 on `main`
- Auditor issued PASS WITH FOLLOW-UPS on initial review — 5 findings:
  - F-1 (P2): Missing member_client timeline tests
  - F-2 (P2): Life story JSON arrays unconstrained (list[dict])
  - F-3 (P2): Obituary field no max_length
  - F-4 (P3): Timeline total was post-pagination count
  - F-5 (P3): Partnership query loaded all rows, filtered in Python
- Builder fixed all 5 defect findings before closeout:
  - F-1: Added 4 new tests (member access, hidden person exclusion, admin-only moment exclusion, pre-pagination total)
  - F-2: Created typed Pydantic sub-models (EducationEntry, CareerEntry, OrganizationEntry) with field-level max_length
  - F-3: Added max_length=10000 to obituary in PersonCreate and PersonUpdate
  - F-4: Changed get_timeline_events to return tuple with pre-pagination total
  - F-5: Added DB-level .where() filtering on partnerships
- Final re-audit: PASS — all defect fixes verified, one cosmetic finding (unused or_ import, cleaned)
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `376 passed, 0 failed`
  - i18n parity: all 3 locales (en, es, ru) have matching key sets
  - Playwright (pre-existing): `31 PASS, 0 FAIL`

### Context

- Plan file: `.claude/plans/spicy-bouncing-llama.md`
- Gap triage: `docs/strategy/genealogy-review-triage.md` (G-19, G-08, G-20, G-22)

---

## Closed Sprint

### `S20 - Family Calendar and Relationship Intelligence`

Status: Closed

### Sprint Goal

Make Family Book a place families visit regularly by surfacing stored dates as a living calendar, computing human-readable relationship paths between any two people, and visually distinguishing relationship types on the tree.

### Why This Sprint Exists

Sprint 19 landed GEDCOM import, external record search, and CEMLA integration — turning Family Book into a research workspace. The next product bottleneck is recurring engagement and social delight: dates already stored in the system have no calendar surface, the graph data can answer "how are we related?" but no algorithm does, and relationship types (adoption, step, biological) all look identical on the tree. Sprint 20 turns stored data into features that make the app useful at family gatherings and worth visiting regularly.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 25 | FB-025 | Family Calendar and Relationship Intelligence | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S20-1 | Family Calendar | done |
| S20-2 | Relationship Calculator | done |
| S20-3 | Visual Relationship Types on Tree | done |

### Sprint Exit Criteria

The sprint is successful when all are true:

- a calendar page auto-populates from birth dates, death dates, partnership dates, and moments
- users can select any two people and see their relationship described in plain English
- the tree visually distinguishes biological, adoptive, step, and other relationship types
- root person redaction is maintained across all new surfaces
- browser, accessibility, and test baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 20 on `main`
- Auditor issued PASS WITH FOLLOW-UPS on initial review — all 28 acceptance criteria evaluated (27 PASS, 1 PARTIAL on dark theme)
- Builder fixed all follow-up defects before closeout:
  - P2: i18n gaps in calendar templates — added 25 calendar keys across 3 locales (en, es, ru), updated all templates to use `{{ t() }}`
  - P3: Jump-to-month selector missing — added `<select>` with HTMX month navigation
  - P3: Dark theme edge colors hardcoded — extracted 10 CSS custom properties in `:root` for edge and calendar dot colors
  - P3: Missing tests for date precision edge cases and moment events — added 5 new tests
  - P3: Graph adjacency not cached — deferred, acceptable for launch (O(n) where n is family size)
- Final re-audit: PASS — all defect fixes verified, adversarial probes clear
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `344 passed, 0 failed`
  - i18n parity: `273 keys, 3 locales, 0 mismatches`
  - Playwright (pre-existing): `31 PASS, 0 FAIL`

### Context

- Task packet: `task_packets/FB-025_family_calendar_and_relationship_intelligence.md`
- Gap triage: `docs/strategy/genealogy-review-triage.md` (G-16, G-06, G-15)
- Decision #12: Family calendar auto-populated from existing dates

## Closed Sprint

### `S19 - External Record Integration Foundation`

Status: Closed

### Sprint Goal

Give Family Book the ability to import existing family trees via GEDCOM and search free external genealogy databases (FamilySearch, newspapers, NARA, Antenati, CEMLA) so the app becomes a research workspace for families with roots in the USA, Australia, Argentina, and Italy.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 23 | FB-023 | External Record Integration Foundation | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S19-1 | GEDCOM Import | done |
| S19-2 | External Record Search Panel | done |
| S19-3 | CEMLA Immigration Record Search | done |

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 19 on `main`
- Auditor issued PASS WITH FOLLOW-UPS — all 27 acceptance criteria evaluated (22 PASS, 3 PARTIAL, 1 SKIP, 1 N/A)
- Builder fixed all follow-up defects before closeout:
  - P1: Root person name leak in external records API — added is_root guard returning 403
  - P1: Root person name leak in CEMLA form template — wrapped in `{% if not person.is_root %}` guard
  - P2: Added GedcomImportBatch model for first-class batch tracking
  - P2: Added XHR upload progress bar with percentage display
  - P2: Added two-phase GEDCOM import (preview with duplicate review → confirm)
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `319 passed, 0 failed`
  - `make test-ui-playwright`
  - result: `31 PASS, 0 FAIL`

### Context

- Integration packet: `task_packets/FB-023_external_record_integration_foundation.md`
- Gap triage: `docs/strategy/genealogy-review-triage.md` (G-10, G-17, G-18)
- Decision #11: External integration strategy

## Closed Sprint

### `S18 - Completeness Prompts and Sidebar Detail Depth`

Status: Closed

### Sprint Goal

Turn missing data into contribution invitations and make the tree sidebar the complete editing surface so members rarely need to detour to the full edit page.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 22 | FB-024 | Completeness Prompts and Sidebar Detail Depth | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S18-1 | Per-Person Completeness Prompts in Sidebar | done |
| S18-2 | Sidebar Details Tab Field Expansion | done |
| S18-3 | Family-Level Completeness Summary API | done |

### Exit Result

- Exit result: `pass with follow-ups`
- Builder implemented Sprint 18 on `main`
- Auditor issued PASS WITH FOLLOW-UPS — all 21 acceptance criteria met, no P0/P1 findings
- Follow-up F-01 (P2): gender completeness prompt navigated to wrong sidebar section — fixed and pushed before closeout
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `265 passed, 0 failed`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

---

## Closed Sprint

### `S17 - Tree Discovery and Research Foundation`

Status: Closed

### Sprint Goal

Make the family tree navigable at scale and establish research-workflow support so genealogy-focused family members can use Family Book as their primary working tool rather than a display layer for research done elsewhere.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 20 | FB-022 | Tree Discovery and Research Foundation | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S17-1 | Tree Search and Navigate-to-Node | done |
| S17-2 | Person Page Content Hierarchy | done |
| S17-3 | Research Notes Per Person | done |

### Exit Result

- Exit result: `pass with follow-ups`
- Builder implemented Sprint 17 on `main`
- Auditor issued PASS WITH FOLLOW-UPS — all 21 acceptance criteria met, no P0/P1 findings
- Follow-ups: F-04 (medium) content hierarchy section order differs from packet prescription (Moments at position ~8 vs prescribed position 3) — follow-up for S18 content tuning
- Test fixes included: fixed test_comments.py wrong ADMIN_ID, fixed xfail for empty names validation
- Focused closeout baseline:
  - `uv run pytest -q`
  - result: `262 passed, 0 failed, 0 xfailed`
  - `uv run pytest tests/test_api.py tests/test_pages.py -q`
  - result: `70 passed`
  - `uv run pytest tests/test_moments.py tests/test_media.py -q`
  - result: `55 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Closed Sprint

### `S16 - Tree Graph Editing and Relationship Modeling`

Status: Closed

### Sprint Goal

Make the tree editable at the graph level so members can create, connect, correct, and understand family relationships directly from the tree workspace without falling back to older detour flows.

### Why This Sprint Exists

Sprint 13 through Sprint 15 made the tree a credible content and authoring workspace around one selected person. The next product gap is graph editing itself. Users can now enrich people and stories from the tree, but core relationship changes still feel more mechanical than direct. Sprint 16 exists to make the tree itself feel like the place where family structure gets edited and corrected.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 19 | FB-021 | Tree Graph Editing and Relationship Modeling | P1 | done |

## Packet Sequence Rationale

### FB-021 now

The next highest-value move is to make family-graph editing feel direct and trustworthy from the tree itself, rather than only improving content around already-existing people.

### Cleanup remains secondary

The warning-only structural debt still matters, but the stronger product bottleneck is relationship editing friction, graph correction friction, and the remaining need to leave the tree for structural changes.

## Sprint Exit Criteria

The sprint is successful when all are true:

- members can add and connect people from the tree with less sidebar/form friction
- members can create or correct parent, child, and partner relationships directly from tree context
- relationship review and correction flows are understandable and safer than today’s add-only mechanics
- browser, accessibility, and CodeMap baselines remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented Sprint 16 on `codex/s16-tree-graph-editing`
- Auditor found three graph-editing defects in replace semantics and graph-mode state handling, and the builder corrected them before final signoff
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - result: `70 passed`
  - `uv run pytest tests/test_moments.py tests/test_media.py -q`
  - result during implementation: `55 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Closed Sprint

### `S15 - Rich Family Storytelling and Multi-Item Authoring`

Status: Closed

### Sprint Goal

Make the tree workspace strong enough for richer family-history capture by supporting better in-tree story composition, grouped media/story workflows, and clearer shared family event authoring.

### Why This Sprint Exists

Sprint 13 and Sprint 14 fixed the biggest context-switching and shallow-workspace problems. The next bottleneck was richer family-history composition. Many real memories are not a single text post or a single upload; they are a story with a few photos, a set of people, and a shared event context. Sprint 15 existed to make the tree better at capturing those richer units without drifting into a full editor rewrite or a brand-new content model.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 18 | FB-020 | Rich Family Storytelling and Multi-Item Authoring | P1 | done |

### Packet Sequence Rationale

#### FB-020 now

The next highest-value move was to make tree-native storytelling deeper and more cohesive so members could capture richer family history as one task instead of multiple disconnected actions.

#### Structural cleanup still stays behind user-facing workflow value

The remaining warning-only structural debt still matters, but the product bottleneck was still content-authoring depth and quality inside the tree workspace rather than another internal cleanup sprint.

### Sprint Exit Criteria

The sprint is successful when all are true:

- members can create richer stories from the tree with more than one media item
- grouped story/media review feels coherent in the tree sidebar
- shared family event authoring is clearer and more first-class than tagged-person afterthoughts
- browser, accessibility, and CodeMap baselines remain intact

### Exit Result

- Exit result: `pass`
- Builder implemented Sprint 15 on `codex/s15-rich-storytelling`
- Auditor found three correctness defects in failure and shared-event review paths, and the builder corrected them before final signoff
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - result during implementation: `123 passed`
  - `uv run pytest tests/test_moments.py tests/test_pages.py tests/test_media.py -q`
  - result after audit follow-up: `73 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

### Recommended Next Sprint

- `Sprint 16 - to be defined`
- Focus: choose the next highest-value product improvement after the richer tree storytelling baseline established in Sprint 15
## Closed Sprint

### `S14 - Family Content and Relationship Authoring`

Status: Closed

### Sprint Goal

Make the tree workspace feel like the real operating surface for family history work by deepening metric views, keeping more story/media actions in-tree, and making relationship authoring clearer and more complete.

### Why This Sprint Exists

Sprint 13 solved the biggest context-switching problem, but your product assessment still holds at the next layer down: the tree now opens the right doors, but some of those rooms are still shallow. Counts and empty states need to lead into richer content browsing, and relationship editing needs to feel more intentional than form mechanics.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 17 | FB-019 | Family Content and Relationship Authoring | P1 | done |

## Packet Sequence Rationale

### FB-019 now

The highest-value next move is to complete the tree workspace loop: not just opening content from the tree, but browsing, adding, and adjusting that content in a way that feels rich enough to keep members there.

### Structural cleanup remains secondary

The warning-only structural debt still matters, but the product bottleneck is still workflow depth and authoring quality on the tree surface, not the absence of another backend capability.

## Sprint Exit Criteria

The sprint is successful when all are true:

- metric workspaces open richer in-tree content rather than shallow counters
- members can add or review more family content from the tree without bouncing into the old fallback flows
- relationship authoring is easier to understand, search, and maintain from tree context
- browser, accessibility, and CodeMap baselines remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented the richer tree-content and relationship-authoring flows on `codex/s14-family-authoring`
- Auditor accepted the sprint without requiring a follow-up defect pass
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - result: `121 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Recommended Next Sprint

- `S15 - Rich Family Storytelling and Multi-Item Authoring`
- Focus: build on the stronger tree workspace by improving how stories, notes, and media collections are composed, reviewed, and connected across people instead of only within a single selected sidebar context

## Closed Sprint

### `S13 - Tree Workspace 2.0`

Status: Closed

### Sprint Goal

Turn the tree into the place where members actively enrich family data by making metrics actionable, restructuring the sidebar into a usable workspace, and supporting tree-native stories, media, inline edits, and relationship linking.

### Why This Sprint Exists

The latest product assessment identified the real problem clearly: the tree is strong visually, but it still behaves like a launching pad into CRUD flows rather than the hub where work happens. Sprint 13 exists to close that gap without drifting into a full redesign or graph-editing experiment.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 16 | FB-018 | Tree Workspace Interaction Overhaul | P1 | done |

## Packet Sequence Rationale

### FB-018 now

The next highest-value move is to make the tree metrics, sidebar, and relationship flows genuinely actionable so users can stay in the tree for meaningful family enrichment work.

### Structural cleanup after the tree workspace reset

Post-integration structural cleanup still matters, but the current product bottleneck is usability and context switching, not lack of technical capability.

## Sprint Exit Criteria

The sprint is successful when all are true:

- tree sidebar metrics are actionable rather than decorative
- members can add stories or media from the tree context
- common person edits happen inline from the tree workspace
- relationship linking scales beyond raw full-family dropdowns
- browser, accessibility, and CodeMap baselines remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented the full tree workspace overhaul and Auditor required one small follow-up pass for metric-state correctness and note feedback copy
- Builder corrected the moments-metric reset behavior, added note-specific success feedback, and extended browser coverage for the story-to-moments state transition before final audit signoff
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - result: `120 passed`
  - `uv run pytest tests/test_pages.py -q`
  - result: `16 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Recommended Next Sprint

- `S14 - Family Content and Relationship Authoring`
- Focus: keep building on the tree workspace by making the new metric surfaces richer, reducing remaining CRUD detours, and improving content depth and relationship workflows from the same context

## Closed Sprint

### `S12 - External Integrations and Confidence Hardening`

Status: Closed

### Sprint Goal

Land the next high-value external integrations while preserving release confidence through targeted hardening of the central modules Sprint 12 depends on.

### Why This Sprint Exists

Family Book now has a stronger tree-centered workflow, but the map and invite-delivery surfaces still lack real integration depth. Google Maps and Resend are the next product-value unlocks, and the remaining CodeMap warnings in access control and schemas should be tightened in the same sprint so those integrations do not reduce release confidence.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 14 | FB-016 | External Integrations: Google Maps and Email Delivery | P1 | done |
| 15 | FB-014 | Architecture and Maintainability Hardening | P1 | done |

## Packet Sequence Rationale

### FB-016 now

The highest-value next product move is to make the map and invite flows feel real by integrating the external systems the product already implies.

### FB-014 alongside FB-016

Sprint 11 increased attention on the tree/access/schema layer, so the remaining CodeMap debt should be pulled into Sprint 12 as targeted hardening rather than left as a disconnected cleanup sprint.

## Sprint Exit Criteria

The sprint is successful when all are true:

- Google Maps is integrated with truthful fallback behavior
- Resend-backed invite delivery works in configured environments
- central-module confidence improves for the access/schema paths touched by the integrations
- browser, staging, and CodeMap baselines remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented Sprint 12 on `main` and Auditor required one follow-up pass for the configured Google Maps and outbound email paths
- Builder corrected the Google Maps keyboard regression, added retry behavior for loader failures, and escaped outbound invite email HTML before final audit signoff
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_email_delivery.py tests/test_auth.py tests/test_pages.py tests/test_config.py tests/test_access_control.py tests/test_schema_models.py -q`
  - result: `52 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Closed Sprint

### `S11 - Tree as Primary Workspace`

Status: Closed

### Sprint Goal

Make the family tree the main Family Book workspace so members can browse, recognize, edit, and grow the family graph directly from the tree.

### Why This Sprint Exists

The tree is the product’s strongest conceptual surface, and users explicitly wanted it to become more personal, editable, and operational. This sprint converted that product direction into the default post-login experience while keeping Google Maps and Resend out of scope.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 13 | FB-015 | Tree as Primary Workspace | P1 | done |

## Packet Sequence Rationale

### FB-015 now

The tree was already the strongest concept in Family Book, so the highest-value next product move was to turn it into the primary workspace rather than leave it as a passive visualization.

### External integrations after the tree shift

Google Maps and Resend matter, but they were intentionally kept out of Sprint 11 so the tree-first workflow could land coherently.

## Sprint Exit Criteria

The sprint is successful when all are true:

- authenticated users land on the tree
- tree nodes feel more personal and informative
- routine person edits and relationship creation can happen in tree context
- browser and accessibility baselines remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented the tree-first workspace and audit follow-up on `main`
- Auditor initially flagged `return_to`, moments filter targeting, inline-clear behavior, and hidden-name fallback regressions, and Builder corrected all four before final closeout
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - result: `62 passed`
  - `uv run pytest tests/test_moments.py -q`
  - result: `35 passed`
  - `uv run pytest tests/test_theme.py -q`
  - result: `5 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `16 PASS`, `0 FAIL`, `9 WARN`

## Recommended Next Sprint

- `S12 - External Integrations and Confidence Hardening`
- Primary packet: `FB-016 External Integrations: Google Maps and Email Delivery`
- Supporting packet: `FB-014 Architecture and Maintainability Hardening`

## Closed Sprint

### `S09 - Accessibility and Interaction Hardening`

Status: Closed

### Sprint Goal

Fix the highest-severity UI/UX and accessibility issues found in the Family Book code review so the core product flows are keyboard reachable, overlays behave correctly, and dynamic/form interactions are more understandable in real use.

### Why This Sprint Exists

The latest review found concrete operability failures in the current UI: modal/sidebar/lightbox focus behavior, mouse-only tree and map interaction, weak dynamic-content feedback, and inconsistent form labeling. These are blocking quality issues on the main family-facing surfaces, so the next sprint should close them before returning to structural maintainability debt.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 11 | FB-012 | Accessibility and Interaction Hardening | P1 | done |

### Follow-On Candidate

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 12 | FB-013 | Readability and Responsive Polish | P2 | candidate |

## Packet Sequence Rationale

### FB-012 first

The highest-value remaining quality gap is no longer release evidence alone; it is the fact that major Family Book surfaces still have concrete accessibility and interaction problems that affect real usage.

### FB-013 after critical operability fixes

Readability and responsive polish matter, but they should not dilute the more important overlay, keyboard, and dynamic-feedback work.

## Sprint Exit Criteria

The sprint is successful when all are true:

- the critical overlay and keyboard failures from the UI/UX review are fixed
- HTMX-driven updates and core forms communicate state more clearly
- browser verification demonstrates real improvement in the main flows
- the sprint closes the highest-severity review findings without drifting into redesign work

## Exit Result

- Exit result: `pass`
- Builder implemented Sprint 09 accessibility fixes and a follow-up quick-win DOM replacement cleanup on `main`
- Auditor identified focus-return, browser-harness reporting, and proof-obligation gaps in the first review
- Builder corrected those issues and the final audit accepted the sprint for closeout
- Focused closeout baseline:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - result: `14 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `19 PASS`, `0 FAIL`, `6 WARN`

## Recommended Next Sprint

- `S10 - Readability and Responsive Polish`
- Primary packet candidate: `FB-013 Readability and Responsive Polish`
- Rationale: the highest-severity operability failures are now closed, so the next highest-value UX work is improving readability, touch comfort, and small-screen scanability without reopening major architecture or access-control scope.

## Closed Sprint

### `S01 - Shared Collaboration Reset`

Status: Closed

### Sprint Goal

Establish the product and execution contract for Family Book, then sequence the first implementation packets required to turn the current codebase into a functioning collaborative family wiki.

### Why This Sprint Exists

The main blocker is not lack of code. It is that the current implementation and tests are aligned to the wrong product model. This sprint exists to fix the operating assumptions first so engineering work can proceed without reinforcing the wrong behavior.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 0 | FB-001 | Product Contract and Operating System Bootstrap | P0 | done |
| 1 | FB-002 | Account, Invite, and Admin Foundation | P0 | done |
| 2 | FB-003 | Flat Family Access and Shared Visibility Reset | P0 | done |
| 3 | FB-004 | Rich Person Record and Tagged Family Content Foundation | P1 | done |

### Stretch Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 4 | FB-005 | Tree Preferences, Filters, and Map Foundation | P2 | todo |

## Packet Sequence Rationale

### FB-002 first

Without reliable invites, account linking, and admin controls, the family boundary is undefined and no collaborative workflow is trustworthy.

### FB-003 second

Once membership works, the product has to behave like a shared family space. This packet changes the runtime from restrictive graph-distance behavior to the intended collaborative model.

### FB-004 third

Only after the collaboration spine works should the data model be expanded to support the richer family-history content the product promises.

### FB-005 after the spine is stable

Tree personalization and map exploration are valuable, but they sit on top of account, visibility, and data-model correctness.

## Sprint Exit Criteria

The sprint is successful when all are true:

- Canonical product and execution docs exist and are the active source of truth
- The next packet is clearly selected and executable
- The build sequence is scoped tightly enough that Builder and Auditor can work without product ambiguity

## Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/shared-collaboration-reset`
- Auditor follow-up defects were fixed and re-audited
- Focused verification baseline at closeout:
  - `uv run pytest tests/test_models.py tests/test_api.py tests/test_auth.py tests/test_media.py tests/test_moments.py tests/test_phase1_edge_cases.py -q`
  - result: `117 passed, 1 xfailed`

## Recommended Next Sprint

- `S02 - Tree and Discovery Foundation`
- Primary packet: `FB-005 Tree Preferences, Filters, and Map Foundation`
- Rationale: the collaboration spine now exists, so the next highest-value user-facing work is making the shared family data easier to explore, filter, and visualize.
- Planning artifact: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s02.md`
- Execution slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s02.md`

## Closed Sprint

### `S02 - Tree and Discovery Foundation`

Status: Closed

### Sprint Goal

Make the shared family record practically explorable through persisted tree preferences, supported tree filters, and a first authenticated map view.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 4 | FB-005 | Tree Preferences, Filters, and Map Foundation | P2 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S02-1 | Tree Preference Persistence | done |
| S02-2 | Tree Filters | done |
| S02-3 | Authenticated Map Foundation | done |

### Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/shared-collaboration-reset`
- Auditor follow-up defects were fixed
- Focused verification at closeout:
  - `uv run pytest tests/test_api.py tests/test_models.py -q`
  - result: `56 passed`
  - `uv run python -m compileall app`
  - result: success

### Recommended Next Sprint

- `S03 - Timeline and Family Moments Expansion`
- Primary packet: `FB-006 Timeline and Family Moments Expansion`
- Rationale: the collaboration and discovery spine now exist; the next product-value step is making family history richer through stories, notes, tagged multi-person moments, and a more useful time-based view.

### Planning Artifacts

- Sprint plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s03.md`
- Sprint slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s03.md`
- Task packet: `/Users/cheech/code/family-book/task_packets/FB-006_timeline_and_family_moments_expansion.md`

## Closed Sprint

### `S03 - Timeline and Family Moments Expansion`

Status: Closed

### Sprint Goal

Make Family Book feel like a living family archive by improving stories, notes, and multi-person moments across the home feed and person timelines.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 5 | FB-006 | Timeline and Family Moments Expansion | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S03-1 | Timeline Query and Ordering Hardening | done |
| S03-2 | Rich Moments Authoring and Tagged Events | done |
| S03-3 | Home and Person Timeline Integration | done |

### Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/shared-collaboration-reset`
- Auditor follow-up defects were fixed
- Focused verification at closeout:
  - `uv run pytest tests/test_moments.py tests/test_media.py tests/test_api.py -q`
  - result: `92 passed`
  - `uv run pytest tests/test_phase1_edge_cases.py -q`
  - result: `15 passed, 1 xfailed`
  - `uv run python -m compileall app`
  - result: success
  - `make test-ui-playwright`
  - result: success

### Recommended Next Sprint

- `S04 - Version History, Revert, and Moderation Controls`
- Primary packet: `FB-007 Version History, Revert, and Moderation Controls`
- Rationale: now that shared editing and timeline authoring are real, the next product-control gap is edit history, rollback, and moderation support.

### Planning Artifacts

- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s03.md`
- Task packet to author next: `FB-007 Version History, Revert, and Moderation Controls`

## Closed Sprint

### `S04 - Version History, Revert, and Moderation Controls`

Status: Closed

### Sprint Goal

Make broad family collaboration trustworthy by adding inspectable edit history, reversible recovery for core shared records, and narrow admin moderation controls for problematic content.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 6 | FB-007 | Version History, Revert, and Moderation Controls | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S04-1 | Revision Capture and History Retrieval | done |
| S04-2 | Revert and Recoverable Delete | done |
| S04-3 | Moderation Controls for Shared Content | done |

### Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/shared-collaboration-reset`
- Auditor follow-up defects were fixed
- Focused verification at closeout:
  - `uv run pytest tests/test_api.py tests/test_moments.py tests/test_auth.py -q`
  - result: `98 passed`
  - `uv run pytest tests/test_media.py -q`
  - result: `18 passed`
  - `uv run python -m compileall app`
  - result: success
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

### Recommended Next Sprint

- `S05 - Encryption and Backup Hardening Pass`
- Primary packet: `FB-009 Encryption and Backup Hardening Pass`
- Rationale: Family Book now has broad shared editing plus recovery controls, so the next highest-risk product gap is protecting sensitive data and making backup/restore guarantees explicit.

### Planning Artifacts

- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s04.md`
- Task packet to author next: `FB-009 Encryption and Backup Hardening Pass`

## Closed Sprint

### `S05 - Encryption and Backup Hardening Pass`

Status: Closed

### Sprint Goal

Make Family Book credible for sensitive family data by adding a truthful protection contract for the highest-risk fields, proving backup and restore behavior, and tightening launch-default runtime hardening.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 7 | FB-009 | Encryption and Backup Hardening Pass | P1 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S05-1 | Data Protection Contract | done |
| S05-2 | Backup and Restore Truthfulness | done |
| S05-3 | Operational Hardening | done |

### Why This Sprint Next

Family Book now supports broad collaboration, recovery, and moderation. That makes sensitive stored data and deployment truthfulness the next real product risk. Sprint 05 closes that gap by turning encryption scope, restore guarantees, and launch-default hardening into explicit, testable behavior instead of operator assumptions.

### Planning Artifacts

- Sprint plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s05.md`
- Sprint slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s05.md`
- Task packet: `/Users/cheech/code/family-book/task_packets/FB-009_encryption_and_backup_hardening_pass.md`
- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s05.md`

## Closed Sprint

### `S06 - Theme Customization and Branding Controls`

Status: Closed

### Sprint Goal

Make Family Book feel owner-operated through admin-managed theme tokens, minimal branding controls, and staging-based visual acceptance before production.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 8 | FB-008 | Theme Customization and Branding Controls | P2 | done |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S06-1 | Theme Token Contract and Persistence | done |
| S06-2 | Admin Theme Controls | done |
| S06-3 | Surface Rollout and Staging Acceptance | done |

### Why This Sprint Next

Family Book now has collaboration, discovery, recovery, protection, and a working staging-to-production release lane. The next product gap is making the app feel like a real family-owned deployment rather than a hardcoded default theme.

### Planning Artifacts

- Sprint plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s06.md`
- Sprint slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s06.md`
- Task packet: `/Users/cheech/code/family-book/task_packets/FB-008_theme_customization_and_branding_controls.md`
- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s06.md`

## Proof Obligations for the Next Execution Cycle

### FB-010

- Prove attack-surface helpers and security middleware have direct tests
- Prove the remaining critical central modules have explicit coverage
- Prove the next hardening sprint improves CodeMap warning count rather than only moving work around

## Planned Sprint

### `S07 - Observability and Coverage Hardening`

Status: Planned

### Sprint Goal

Raise the reliability floor of Family Book by adding direct tests for risky runtime plumbing, improving coverage in central modules, and reducing the remaining high-signal CodeMap warnings.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 9 | FB-010 | Observability and Coverage Hardening | P1 | planned |

### Planned Slices

| Slice | Title | Status |
|---|---|---|
| S07-1 | Attack-Surface Test Hardening | planned |
| S07-2 | Critical-Module Coverage Expansion | planned |
| S07-3 | Observability and Complexity Hardening | planned |

### Why This Sprint Next

Family Book’s product surface is now broad enough that the highest-value remaining work is runtime trust. The current CodeMap warnings are concentrated in security-sensitive helpers, central config/schema paths, and a few runtime hotspots that deserve direct tests and modest observability improvements before the next broad feature sprint.

### Planning Artifacts

- Sprint plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s07.md`
- Sprint slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s07.md`
- Task packet: `/Users/cheech/code/family-book/task_packets/FB-010_observability_and_coverage_hardening.md`

## Open Policy Questions to Watch

- Whether medical history should remain shared to all active family members long-term
- Whether contact information needs later field-level restrictions
- Whether theme controls should later expand into logo assets or stay intentionally minimal
- How much observability should be added without overcomplicating the self-hosted runtime

## PM Instruction

Do not start new feature surface work outside the committed packet order unless a blocker or new decision changes the product contract.

## Closed Sprint

### `S07 - Observability and Coverage Hardening`

Status: Closed

### Sprint Goal

Raise the reliability floor of Family Book by adding direct tests for risky runtime plumbing, improving coverage in central modules, and reducing the remaining high-signal CodeMap warnings.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 9 | FB-010 | Observability and Coverage Hardening | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S07-1 | Attack-Surface Test Hardening | done |
| S07-2 | Critical-Module Coverage Expansion | done |
| S07-3 | Observability and Complexity Hardening | done |

### Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/s07-observability-hardening`
- Auditor found no blocking defects in the final review
- Focused verification at closeout:
  - `uv run pytest tests/test_config.py tests/test_security_guardrails.py tests/test_schema_models.py tests/test_phase3.py tests/test_auth.py tests/test_models.py -q`
  - result: `78 passed`
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

### Recommended Next Sprint

- `S09 - Architecture and Maintainability Hardening`
- Primary packet candidate: `FB-012 Architecture and Maintainability Hardening`
- Rationale: Sprint 08 materially improved release confidence and promotion discipline. The next highest-leverage work is structural: remove the remaining dependency cycle, reduce hidden coupling, and harden the remaining attack-surface and observability debt that CodeMap still flags.

### Planning Artifacts

- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s07.md`

## Closed Sprint

### `S08 - Browser Regression Expansion and Release Confidence`

Status: Closed

### Sprint Goal

Increase confidence in Family Book releases by broadening browser automation coverage, establishing a clear staging acceptance contract, and making the release evidence required for `main` promotion easy to inspect.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 10 | FB-011 | Browser Regression Expansion and Release Confidence | P1 | done |

### Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S08-1 | Playwright Coverage Expansion | done |
| S08-2 | Staging Acceptance Contract | done |
| S08-3 | Release Evidence and Promotion Gate | done |

### Exit Result

- Exit result: `pass`
- Builder implementation completed on `codex/s08-release-confidence`
- Auditor found no blocking defects in the final review
- Focused verification at closeout:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - result: `7 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

### Planning Artifacts

- Sprint plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s08.md`
- Sprint slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s08.md`
- Task packet: `/Users/cheech/code/family-book/task_packets/FB-011_browser_regression_expansion_and_release_confidence.md`
- Sprint closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s08.md`
