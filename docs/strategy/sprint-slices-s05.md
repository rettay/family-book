# Sprint Slices - S05 Encryption and Backup Hardening Pass

## Slice Sequence

### S05-1 Data Protection Contract

Status: `planned`

- Objective:
  establish the truthful protection contract and implement field-level protection for the highest-risk stored fields
- Scope:
  sensitive-field inventory, encryption path, documentation, and focused persistence verification
- Deliverable:
  medical and direct-contact fields are protected through the normal app persistence path
- Verification:
  focused tests for encrypted persistence and supported read round-trips

### S05-2 Backup and Restore Truthfulness

Status: `planned`

- Objective:
  make backup and restore a supported, verifiable operator workflow
- Scope:
  backup path assumptions, restore procedure, retention/freshness truthfulness, and bounded restore verification
- Deliverable:
  a usable backup/restore contract with truthful health reporting
- Verification:
  focused restore-path tests or operator-path checks that prove a usable restored state

### S05-3 Operational Hardening

Status: `planned`

- Objective:
  align runtime defaults with the protection and durability contract
- Scope:
  docs exposure, trusted hosts, authenticated cache behavior, upload/download limits, and inbound webhook constraints
- Deliverable:
  launch-default runtime behavior is materially safer without changing the collaboration model
- Verification:
  focused tests plus governance/security review for the hardened runtime defaults

## Slice Rules

- Do not drift from field-level protection into full-database or client-side encryption.
- Do not turn backup truthfulness into a generalized infra/platform rewrite.
- Do not expand S05-3 into a full platform security program.
- Each slice should leave the app in a green, testable state before the next slice starts.

## Recommended Builder Order

1. `S05-1`
2. `S05-2`
3. `S05-3`

## PM Note

This sprint is about truthful protection, not security theater. Prefer narrow guarantees that the code can prove over broad promises the runtime cannot keep.
