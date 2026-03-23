# Family Book Status

## Overall State

Family Book is in **shared-collaboration rebuild**.

The product contract reset is complete, and the first three implementation sprints now align the runtime with the intended collaborative family-wiki model: invite-based onboarding, flat shared visibility for active members, richer persisted family-history content, discovery surfaces, and a usable shared timeline layer.

Sprint 01, Sprint 02, and Sprint 03 are closed.

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
- Focused Sprint 03 verification:
  - `uv run pytest tests/test_moments.py tests/test_media.py tests/test_api.py -q`
  - Result at closeout: `92 passed`
  - `uv run pytest tests/test_phase1_edge_cases.py -q`
  - Result at closeout: `15 passed, 1 xfailed`
- Browser flow baseline:
  - `make test-ui-playwright`
  - Result at closeout: success
  - Screenshot artifacts: `/Users/cheech/code/family-book/output/playwright/family-book-flow`
- Syntax smoke check:
  - `uv run python -m compileall app`
  - Result: success
- Known repo-wide baseline before this sprint work:
  - `uv run pytest -q`
  - Result observed earlier: `143 passed, 2 failed, 1 xfailed`

## Current Risks

- Broad collaborative editing still lacks version history and revert controls
- Sensitive-data handling needs explicit policy, not implicit behavior
- Browser-flow evaluation exists now, but it is still a focused smoke layer rather than full cross-browser coverage

## Current Priority Order

1. Open Sprint 04 around version history, revert, and moderation controls
2. Clarify and harden sensitive-data policy and encryption guarantees
3. Return to admin-facing theme customization and branding controls
4. Expand browser-based regression coverage beyond the current core flow set

## Sprint State

- Closed sprints:
  - `S01 - Shared Collaboration Reset`
  - `S02 - Tree and Discovery Foundation`
  - `S03 - Timeline and Family Moments Expansion`
- Next recommended sprint: `S04 - Version History, Revert, and Moderation Controls`
- Sprint 04 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s04.md`
- Sprint 04 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s04.md`
- Sprint 03 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s03.md`
- See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
