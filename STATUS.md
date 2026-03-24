# Family Book Status

## Overall State

Family Book is in **shared-collaboration rebuild**.

The product contract reset is complete, and the first four implementation sprints now align the runtime with the intended collaborative family-wiki model: invite-based onboarding, flat shared visibility for active members, richer persisted family-history content, discovery surfaces, a usable shared timeline layer, and recoverable collaboration controls.

Sprint 01 through Sprint 07 are closed.

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
- Focused Sprint 04 verification:
  - `uv run pytest tests/test_api.py tests/test_moments.py tests/test_auth.py -q`
  - Result at closeout: `98 passed`
  - `uv run pytest tests/test_media.py -q`
  - Result at closeout: `18 passed`
- Focused Sprint 05 verification:
  - `uv run pytest tests/test_protection_service.py tests/test_revision_service.py tests/test_security_guardrails.py tests/test_schema_models.py tests/test_phase3.py tests/test_auth.py -q`
  - Result at closeout: `54 passed`
- Focused Sprint 06 verification:
  - `uv run pytest tests/test_theme.py tests/test_auth.py tests/test_phase3.py -q`
  - Result at closeout: `45 passed`
- Focused Sprint 07 verification:
  - `uv run pytest tests/test_config.py tests/test_security_guardrails.py tests/test_schema_models.py tests/test_phase3.py tests/test_auth.py tests/test_models.py -q`
  - Result at closeout: `78 passed`
- Browser flow baseline:
  - `make test-ui-playwright`
  - Result at closeout: success
  - Screenshot artifacts: `/Users/cheech/code/family-book/output/playwright/family-book-flow`
- Syntax smoke check:
  - `uv run python -m compileall app tests`
  - Result: success
- CodeMap governance baseline:
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at Sprint 07 closeout: `17 PASS`, `0 FAIL`, `8 WARN`
- Known repo-wide baseline before this sprint work:
  - `uv run pytest -q`
  - Result observed earlier: `143 passed, 2 failed, 1 xfailed`

## Current Risks

- Browser-flow evaluation exists now, but it is still a focused smoke layer rather than full cross-browser coverage
- Critical security-sensitive modules still have residual CodeMap warnings around observability, complexity, and a few untested central modules

## Current Priority Order

1. Expand browser-based regression coverage beyond the current core flow set
2. Tighten release confidence around staging-to-production acceptance
3. Pay down remaining CodeMap observability warnings in core modules
4. Reassess where richer visual regression evidence is worth the maintenance cost

## Sprint State

- Closed sprints:
  - `S01 - Shared Collaboration Reset`
  - `S02 - Tree and Discovery Foundation`
  - `S03 - Timeline and Family Moments Expansion`
- `S04 - Version History, Revert, and Moderation Controls`
- `S05 - Encryption and Backup Hardening Pass`
- `S06 - Theme Customization and Branding Controls`
- `S07 - Observability and Coverage Hardening`
- Next recommended sprint: `S08 - Browser Regression Expansion and Release Confidence`
- Sprint 07 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s07.md`
- Sprint 07 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s07.md`
- Sprint 07 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s07.md`
- Sprint 06 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s06.md`
- Sprint 06 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s06.md`
- Sprint 06 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s06.md`
- Sprint 05 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s05.md`
- Sprint 05 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s05.md`
- Sprint 05 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s05.md`
- Sprint 04 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s04.md`
- Sprint 04 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s04.md`
- Sprint 04 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s04.md`
- Sprint 03 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s03.md`
- See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
