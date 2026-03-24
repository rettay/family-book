# Task Packet - FB-007 Version History, Revert, and Moderation Controls

## Objective

Add launch-grade edit history, reversible recovery, and light admin moderation controls so broad family collaboration stays trustworthy instead of fragile.

## Why / KPI

- Sprint 01 made Family Book collaborative.
- Sprint 02 made the shared record explorable.
- Sprint 03 made the timeline expressive and visible.
- The next gap is trust: once many family members can edit shared records, the product needs inspectable history and a safe way to undo mistakes or moderate problematic content.

Primary KPI:
- improve **Collaborative Family Loop Success Rate (CFLSR)** by reducing the rate of collaboration-breaking mistakes that require manual database intervention.

Secondary KPI:
- reduce irreversible-mutation risk on shared family records.

## Scope

- In scope:
  - persisted revision history for launch-critical collaborative entities
  - readable history surfaces or APIs for supported entities
  - revert/restore flows for supported entity types
  - soft-delete or equivalent recoverable behavior where needed for destructive edits
  - admin moderation controls for problematic shared content in launch scope
  - focused tests and browser evidence for edit history and recovery flows
- Out of scope:
  - a full editorial approval queue
  - user bans, family-role redesign, or ACL segmentation
  - encryption redesign or backup-system work
  - arbitrary rollback for every historical model in the repo
  - public-facing moderation or trust-and-safety tooling

## Task Type

- Product-control and data-integrity packet

## Dependencies and Ordering Assumptions

- Depends on `FB-002` invite/account/admin foundation being complete
- Depends on `FB-003` flat-family collaboration being live
- Depends on `FB-004` and `FB-006` because people and moments are now broad collaborative surfaces
- Should execute before `FB-009` encryption hardening because the runtime mutation model needs to be truthful first

## Constraints

- Shared family editing remains the launch model; Sprint 04 must not reintroduce graph-distance or narrow per-user ownership rules.
- Recovery behavior must be explicit and auditable, not hidden admin-only database surgery.
- Version history should be grounded in persisted revisions or snapshots, not inferred from coarse audit text.
- Moderation scope must stay narrow enough to verify well.

## Recommended Launch Scope Within This Packet

- Must support revision history and revert/restore for:
  - people
  - moments
- Should support moderation controls for:
  - moments
  - media metadata or visibility state
- If builder must narrow further, preserve:
  - person history
  - moment history
  - admin recoverability for destructive timeline mistakes

## Implementation Notes

- Likely files:
  - `app/models/audit.py`
  - new revision/moderation models under `app/models/`
  - `app/services/audit_service.py`
  - new revision/moderation service layer under `app/services/`
  - `app/routes/persons.py`
  - `app/routes/moments.py`
  - `app/routes/media.py`
  - `app/routes/pages.py`
  - `app/templates/person.html`
  - `app/templates/home.html`
  - `app/templates/admin.html`
  - `tests/test_api.py`
  - `tests/test_moments.py`
  - `tests/test_media.py`
  - new focused tests for revision and moderation behavior
  - Playwright/browser flow harness updates
- Validation commands:
  - targeted pytest for history/revert/moderation flows
  - `uv run python -m compileall app`
  - Playwright/browser evidence for visible recovery behavior

## Evaluation Environment

- Task:
  establish trustworthy collaborative recovery and moderation for shared family content
- Verifier:
  focused API tests plus rendered UI/browser evidence for history and revert behavior
- Reference/oracle:
  `foundation/V1_PRODUCT_REQUIREMENTS.md`
  `foundation/COLLABORATION_AND_PRIVACY.md`
- Expected evidence:
  a member edit creates revision history, another authorized user can inspect the history, an admin can revert a supported change, and destructive mistakes are recoverable without manual database repair
- Known failure modes / reward hacks:
  - audit rows exist but do not support actual restore behavior
  - revert works only for the latest happy path and corrupts related data
  - history is visible only to admins even though collaboration is shared
  - moderation merely hides UI cards without changing API visibility
  - soft-delete breaks tree, timeline, or media integrity
- Verifiability class:
  `bounded-judgment`
- Context policy:
  keep entity support narrow and explicit; prefer strong evidence on fewer entities over shallow pseudo-support everywhere

## Acceptance Criteria

- [x] Supported person and moment edits create persisted, inspectable history entries with actor and timestamp context.
- [x] An authorized user can retrieve and view recent revision history for supported entities through a supported API or UI surface.
- [x] An admin can revert at least one supported person change and one supported moment change without direct database manipulation.
- [x] A destructive mistake in launch scope becomes recoverable through supported app behavior rather than irreversible delete semantics.
- [x] Admin moderation controls can suppress problematic shared content in supported scope and restore it when appropriate.
- [x] Focused tests and browser evidence prove the history and recovery behavior works across at least two authenticated users.

## Definition of Done

- [x] Acceptance criteria satisfied
- [x] Validation evidence attached
- [x] Revert behavior verified against at least one wrong-variant or negative-case path
- [x] Recoverability behavior does not require manual database edits
- [x] Moderation behavior is reflected in both API and rendered surfaces for supported entities

## Risk and Verification Notes

- Complexity hotspots:
  - choosing a revision model that is restorable without excessive coupling
  - handling deletes/restores without orphaning relationships or media references
  - keeping moderation semantics separate from account/access semantics
- Likely shallow-pass failure modes:
  - “history” implemented as audit log display only
  - revert path that rewrites one row but leaves dependent surfaces stale
  - moderation implemented only in templates, not APIs
  - restore path that works for one entity type and silently corrupts another
- Required verification depth:
  - negative-case coverage for unsupported revert targets or invalid revision IDs
  - at least one multi-user flow showing one member edits and another inspects the result
  - browser evidence for a visible revert or moderation outcome
- Sufficient discriminative power means:
  the verifier must fail if revision history is cosmetic, if revert is admin-database-only in spirit, or if moderated content still leaks through supported APIs

## Execution Budget

- Builder may explore:
  - whether to extend the current audit model or add explicit revision tables
  - whether soft-delete is per-entity or normalized through a moderation status field
  - the thinnest UI necessary to expose trustworthy history and revert behavior
- Builder must escalate if:
  - revision semantics require redefining the flat-family collaboration model
  - supported entity scope cannot be kept to people and moments without breaking product truthfulness
  - data-model changes would block `FB-009` or require a backup/restore redesign
- Material scope drift:
  - broad approval workflows
  - field-level permissions
  - generalized moderation across every content type in the codebase
- Proof obligations before review:
  - revision data is persisted, not merely derived
  - revert changes live product state in a user-visible way
  - supported destructive actions are recoverable through the app

## Closeout Evidence

- Focused verification:
  - `uv run pytest tests/test_api.py tests/test_moments.py tests/test_auth.py -q` -> `98 passed`
  - `uv run pytest tests/test_media.py -q` -> `18 passed`
  - `uv run python -m compileall app` -> success
  - `make test-ui-playwright` -> success
- Audit follow-up:
  - person reverts no longer mutate account login state
  - deleted people no longer leak through moment cards or tagged-media metadata
  - deleted people cannot be invited or state-toggled through admin account flows
- Governance evidence:
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json` -> `17 PASS`, `0 FAIL`, `8 WARN`
