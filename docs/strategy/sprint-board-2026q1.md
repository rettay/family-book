# Family Book Sprint Board - 2026 Q1

## Active Sprint

### `S01 - Shared Collaboration Reset`

Status: Active

### Sprint Goal

Establish the product and execution contract for Family Book, then sequence the first implementation packets required to turn the current codebase into a functioning collaborative family wiki.

### Why This Sprint Exists

The main blocker is not lack of code. It is that the current implementation and tests are aligned to the wrong product model. This sprint exists to fix the operating assumptions first so engineering work can proceed without reinforcing the wrong behavior.

### Committed Packets

| Order | ID | Title | Priority | Status |
|---|---|---|---:|---|
| 0 | FB-001 | Product Contract and Operating System Bootstrap | P0 | done |
| 1 | FB-002 | Account, Invite, and Admin Foundation | P0 | todo |
| 2 | FB-003 | Flat Family Access and Shared Visibility Reset | P0 | todo |
| 3 | FB-004 | Rich Person Record and Tagged Family Content Foundation | P1 | todo |

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
