# Family Book Status

## Overall State

Family Book is in **shared-collaboration rebuild**.

The product contract reset is complete, and the first implementation sprint now aligns the runtime with the intended collaborative family-wiki model: invite-based onboarding, flat shared visibility for active members, and richer persisted family-history content.

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
  - Result: `113 passed, 1 xfailed`
- Syntax smoke check:
  - `uv run python -m compileall app`
  - Result: success
- Known repo-wide baseline before this sprint work:
  - `uv run pytest -q`
  - Result observed earlier: `143 passed, 2 failed, 1 xfailed`

## Current Risks

- Product contract drift between older specs and desired launch behavior
- Access/privacy rules coded for a different product model
- Multi-user collaboration not proven end to end
- Media and richer family-history content under-modeled relative to the desired product
- Sensitive-data handling needs explicit policy, not implicit behavior

## Current Priority Order

1. Audit and harden the implemented Sprint 01 collaboration spine
2. Add user-facing tree customization, filtering, and map support
3. Add version history and moderation controls for broad collaborative editing
4. Clarify and harden sensitive-data policy and encryption guarantees

## Active Sprint

See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
