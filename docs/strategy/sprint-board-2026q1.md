# Family Book Sprint Board - 2026 Q1

## Closed Sprint

### `S10 - Readability and Responsive Polish`

Status: Closed

### Sprint Goal

Improve readability, scanability, and narrow-screen usability across the main Family Book surfaces so the product feels calmer and easier to use after the critical accessibility work from Sprint 09.

### Why This Sprint Exists

The next highest-value UX work is the lower-severity but still meaningful polish from the UI/UX review: small and muted metadata, cramped admin and control rows on smaller screens, and feed/media presentation that still feels denser and jumpier than it should.

### Committed Packet

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 12 | FB-013 | Readability and Responsive Polish | P2 | done |

## Packet Sequence Rationale

### FB-013 now

The severe operability bugs are closed, which makes this the right point to improve legibility, spacing, and visual stability without competing with more urgent accessibility work.

### FB-014 after UX polish

Maintainability debt still matters, but the next most user-visible payoff is readability and responsive comfort on the main Family Book surfaces.

## Sprint Exit Criteria

The sprint is successful when all are true:

- metadata and helper text are easier to read
- known cramped admin/action rows behave acceptably on narrow screens
- feed media causes less visible layout jump
- the browser regression lane stays green and Sprint 09 accessibility behaviors remain intact

## Exit Result

- Exit result: `pass`
- Builder implemented the readability, responsive, and scanability polish across the main Family Book surfaces on `main`
- Auditor initially flagged localization regression and remaining mobile form compression, and Builder corrected both before final closeout
- Focused closeout baseline:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - result: `15 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `19 PASS`, `0 FAIL`, `6 WARN`

## Recommended Next Sprint

- next sprint to be selected
- likely direction: continue from `FB-014` maintainability work or pick the next highest-value product surface based on manual staging review

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
