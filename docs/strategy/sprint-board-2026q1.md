# Family Book Sprint Board - 2026 Q1

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

## Proof Obligations for the Next Execution Cycle

### FB-002

- Prove an invited member can enter the system without manual database work
- Prove admins can manage accounts through supported flows

### FB-003

- Prove one active member can see another active member's shared content
- Prove the media and tree surfaces follow the same sharing model
- Prove unauthenticated users still cannot access content

### FB-004

- Prove the richer family-history fields and tagged content are truly persisted
- Prove the new model is exposed through supported APIs, not only templates

## Open Policy Questions to Watch

- Whether medical history should remain shared to all active family members long-term
- Whether contact information needs later field-level restrictions
- Whether broad collaborative editing requires version history in the same phase or the next

## PM Instruction

Do not start new feature surface work outside the committed packet order unless a blocker or new decision changes the product contract.
