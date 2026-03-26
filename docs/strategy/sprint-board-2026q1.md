# Family Book Sprint Board - 2026 Q1

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
