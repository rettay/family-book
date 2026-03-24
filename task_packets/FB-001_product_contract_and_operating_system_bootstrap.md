# Task Packet - FB-001 Product Contract and Operating System Bootstrap

## Objective

Establish a canonical Family Book launch contract and a reusable execution system so future work is packetized against the collaborative family-wiki direction rather than the older speculative docs.

## Why / KPI

- Removes ambiguity about what product is being built.
- Creates a repeatable PM -> Builder -> Auditor workflow for the repo.
- Improves CFLSR indirectly by preventing future work from reinforcing the wrong access model.

## Scope

- In scope:
  - add a Family Book operating system and agent playbooks
  - define canonical product foundation docs
  - capture current codebase state in a briefing doc
  - create backlog, kanban, and first implementation packets
- Out of scope:
  - application runtime changes
  - schema changes
  - access-control rewrites

## Constraints

- Do not present broad future-state ideas as launch truth.
- Keep the launch contract aligned with the collaborative family-wiki direction.
- Keep the packet system lightweight and local to this repo.

## Implementation Notes

- Likely files:
  - `operating_system.md`
  - `pm.md`
  - `builder.md`
  - `auditor.md`
  - `STATUS.md`
  - `DECISIONS.md`
  - `backlog.md`
  - `foundation/PRODUCT_VISION.md`
  - `foundation/V1_PRODUCT_REQUIREMENTS.md`
  - `foundation/COLLABORATION_AND_PRIVACY.md`
  - `docs/CODEBASE_BRIEFING.md`
  - `docs/strategy/kanban-2026q1.md`
  - `task_packets/*.md`
- Validation commands:
  - `test -f /Users/cheech/code/family-book/operating_system.md`
  - `test -f /Users/cheech/code/family-book/foundation/PRODUCT_VISION.md`
  - `test -f /Users/cheech/code/family-book/docs/CODEBASE_BRIEFING.md`
  - `test -f /Users/cheech/code/family-book/backlog.md`

## Evaluation Environment

- Task: define product and execution documents
- Verifier: file existence plus cross-file coherence review
- Reference/oracle: the user's stated desired direction for Family Book
- Expected evidence: created docs and packetized execution plan
- Known failure modes / reward hacks:
  - copying Primer terminology without adapting it
  - writing vague feature wishlists instead of executable packets
  - leaving conflicting launch truth unresolved
- Verifiability class: `bounded-judgment`

## Acceptance Criteria

- [x] Family Book has a local operating-system document and role playbooks.
- [x] Family Book has canonical product foundation docs aligned with the collaborative family-wiki direction.
- [x] Family Book has a codebase briefing that distinguishes current implementation from desired launch behavior.
- [x] Family Book has a backlog, kanban board, and first task-packet set for implementation.

## Definition of Done

- [x] All acceptance criteria satisfied
- [x] Documents exist in repo
- [x] First implementation packets are ready for execution

## Implementation Summary

- Added a Family Book operating system with CFLSR as the primary KPI.
- Added PM, Builder, and Auditor playbooks adapted from Primer to this repo.
- Added canonical product foundation docs for vision, requirements, and flat shared-access policy.
- Added a codebase briefing that captures the current technical baseline and mismatch areas.
- Added backlog, kanban, and the first execution packets needed to implement the new direction.

## Files Changed

- `/Users/cheech/code/family-book/operating_system.md`
- `/Users/cheech/code/family-book/pm.md`
- `/Users/cheech/code/family-book/builder.md`
- `/Users/cheech/code/family-book/auditor.md`
- `/Users/cheech/code/family-book/STATUS.md`
- `/Users/cheech/code/family-book/DECISIONS.md`
- `/Users/cheech/code/family-book/backlog.md`
- `/Users/cheech/code/family-book/foundation/PRODUCT_VISION.md`
- `/Users/cheech/code/family-book/foundation/V1_PRODUCT_REQUIREMENTS.md`
- `/Users/cheech/code/family-book/foundation/COLLABORATION_AND_PRIVACY.md`
- `/Users/cheech/code/family-book/docs/CODEBASE_BRIEFING.md`
- `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`
- `/Users/cheech/code/family-book/task_packets/FB-001_product_contract_and_operating_system_bootstrap.md`
- `/Users/cheech/code/family-book/task_packets/FB-002_account_invite_and_admin_foundation.md`
- `/Users/cheech/code/family-book/task_packets/FB-003_flat_family_access_and_shared_visibility_reset.md`
- `/Users/cheech/code/family-book/task_packets/FB-004_rich_person_record_and_tagged_family_content_foundation.md`
- `/Users/cheech/code/family-book/task_packets/FB-005_tree_preferences_filters_and_map_foundation.md`

## Validation Evidence

- File existence validation planned after patch application

## Limitations / Follow-Ups

- This packet sets direction and execution structure only.
- Runtime behavior still needs implementation through subsequent packets.
