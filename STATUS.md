# Family Book Status

## Overall State

Family Book is in **shared-collaboration rebuild**.

The product contract reset is complete, and the first implementation sprint now aligns the runtime with the intended collaborative family-wiki model: invite-based onboarding, flat shared visibility for active members, and richer persisted family-history content.

Sprint 01 and Sprint 02 are closed.

## North Star

- **Primary KPI:** Collaborative Family Loop Success Rate (CFLSR)
- **Definition:** percentage of invited active family members who can:
  1. sign in,
  2. see shared family content,
  3. make a change,
  4. have another member see that change correctly.

## Current Baseline

- Focused Sprint 01 verification:
  - `uv run pytest tests/test_models.py tests/test_api.py tests/test_auth.py tests/test_media.py tests/test_moments.py tests/test_phase1_edge_cases.py -q`
  - Result at closeout: `117 passed, 1 xfailed`
- Focused Sprint 02 verification:
  - `uv run pytest tests/test_api.py tests/test_models.py -q`
  - Result at closeout: `56 passed`
- Syntax smoke check:
  - `uv run python -m compileall app`
  - Result: success
- Known repo-wide baseline before this sprint work:
  - `uv run pytest -q`
  - Result observed earlier: `143 passed, 2 failed, 1 xfailed`

## Current Risks

- Multi-user collaboration not proven end to end
- Timeline/storytelling depth is still underpowered relative to the intended family-wiki product
- Broad collaborative editing still lacks version history and revert controls
- Sensitive-data handling needs explicit policy, not implicit behavior

## Current Priority Order

1. Open Sprint 03 around timeline and family moments expansion
2. Add version history and moderation controls for broad collaborative editing
3. Clarify and harden sensitive-data policy and encryption guarantees
4. Return to admin-facing theme customization and branding controls

## Sprint State

- Closed sprints:
  - `S01 - Shared Collaboration Reset`
  - `S02 - Tree and Discovery Foundation`
- Next recommended sprint: `S03 - Timeline and Family Moments Expansion`
- Sprint 03 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s03.md`
- See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
