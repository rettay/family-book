# Sprint Slices - S50 Activation and Migration

## Slice Order

1. `S50-1 Hosted First-Run Activation`
2. `S50-2 GEDCOM Migration Confidence`
3. `S50-3 Invite Handoff And First Contribution`
4. `S50-4 Mobile Share Inbox`
5. `S50-5 Closeout And Follow-Up Capture`

## `S50-1 Hosted First-Run Activation`

### Goal

Get a new hosted archive owner to visible first value in one session.

### Packets

- `FB-120`

### Scope

- define onboarding state and completion milestones
- route new hosted archive owners into onboarding until complete or skipped
- support manual start and GEDCOM start
- capture first-person, first-media, and first-invite milestones
- make progress resumable across browser restarts

### Acceptance Checks

- Owner is routed into onboarding on first run.
- Onboarding can be skipped or resumed safely.
- Manual-start path adds self and close relatives cleanly.
- Activation milestones are tracked without private content.

## `S50-2 GEDCOM Migration Confidence`

### Goal

Make GEDCOM import feel safe enough for an existing genealogy user to continue in Family Book.

### Packets

- `FB-121`

### Scope

- add import batch detail and review surface
- summarize duplicates, unsupported fields, missing key facts, and likely cleanup tasks
- link cleanup items to relevant profiles or filters
- provide rollback, quarantine, or equivalent safe-recovery behavior for failed imports

### Acceptance Checks

- Import results remain reviewable after completion.
- Cleanup checklist is specific and actionable.
- Failed or partial import output can be contained safely.
- Duplicate and failure paths are covered in tests.

## `S50-3 Invite Handoff And First Contribution`

### Goal

Help invited relatives understand their permissions and make a safe first contribution.

### Packets

- `FB-122`

### Scope

- explain role and visibility on the invite surface
- land invitees in a role-aware first contribution prompt
- differentiate viewer, member, and steward actions
- optionally route high-risk edits into review if policy requires it
- record invite activation events without leaking private content

### Acceptance Checks

- Invite page explains what the user can see and edit.
- Claimed invite lands in a contextual first action, not a generic archive drop-in.
- Lower-privilege users cannot over-contribute through the new flow.
- Conversion and first-contribution events are auditable.

## `S50-4 Mobile Share Inbox`

### Goal

Turn mobile share capture into structured archive intake if the core activation work finishes early enough.

### Packets

- `FB-123`

### Scope

- create media inbox items from the PWA share target
- attach inbox items to people and tagged relatives
- support caption/date/location enrichment during review
- support reject/delete and clear mobile error states

### Acceptance Checks

- Share target creates inbox items instead of loose files.
- Inbox items can be reviewed, attached, or deleted.
- Access control prevents attachment to unauthorized profiles.
- Mobile success and failure states are understandable.

## `S50-5 Closeout And Follow-Up Capture`

### Goal

Close the sprint with a usable activation story and a clear line into engagement work.

### Scope

- update packet evidence and sprint board
- document activation outcomes and unresolved migration gaps
- queue any post-sprint follow-ups around richer import cleanup or deeper media capture
- keep `FB-110` image-build verification visible as a separate ops follow-up

### Acceptance Checks

- Sprint closeout exists under `docs/strategy/`.
- Board clearly shows S50 status and the next planned sprint.
- Any deferred activation or media-capture follow-ups are separated from S51 engagement work.
- `git diff --check` passes.

## Validation Baseline

- `uv run pytest tests/test_onboarding.py tests/test_imports.py tests/test_auth.py tests/test_pages.py -q`
- `uv run pytest tests/test_gedcom_parser.py tests/test_access_control.py tests/test_media.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Recommended Builder Order

1. `FB-120`
2. `FB-121`
3. `FB-122`
4. `FB-123`
