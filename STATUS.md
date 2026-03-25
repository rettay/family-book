# Family Book Status

## Overall State

Family Book is in **shared-collaboration rebuild**.

The product contract reset is complete, and the first four implementation sprints now align the runtime with the intended collaborative family-wiki model: invite-based onboarding, flat shared visibility for active members, richer persisted family-history content, discovery surfaces, a usable shared timeline layer, and recoverable collaboration controls.

Sprint 01 through Sprint 14 are closed. Sprint 14 deepened the tree workspace so metric panels, in-tree content review, and relationship maintenance now feel closer to a primary operating surface instead of thin wrappers around older routes. Sprint 15 is now planned to deepen the authoring side of that same workspace with richer stories, grouped media, and clearer shared event flows.

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
- Focused Sprint 08 verification:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - Result at closeout: `7 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
- Focused Sprint 09 verification:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - Result at closeout: `14 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
- Focused Sprint 10 verification:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - Result at closeout: `15 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at closeout: `19 PASS`, `0 FAIL`, `6 WARN`
- Browser flow baseline:
  - `make test-ui-playwright`
  - Result at closeout: success
  - Screenshot artifacts: `/Users/cheech/code/family-book/output/playwright/family-book-flow`
- Focused Sprint 12 verification:
  - `uv run pytest tests/test_email_delivery.py tests/test_auth.py tests/test_pages.py tests/test_config.py tests/test_access_control.py tests/test_schema_models.py -q`
  - Result at closeout: `52 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at closeout: `17 PASS`, `0 FAIL`, `8 WARN`
- Focused Sprint 13 verification:
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - Result during implementation: `120 passed`
  - `uv run pytest tests/test_pages.py -q`
  - Result after audit follow-up: `16 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at closeout: `17 PASS`, `0 FAIL`, `8 WARN`
- Focused Sprint 14 verification:
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - Result at closeout: `121 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at closeout: `17 PASS`, `0 FAIL`, `8 WARN`
- Syntax smoke check:
  - `uv run python -m compileall app tests`
  - Result: success
- CodeMap governance baseline:
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at Sprint 09 closeout: `19 PASS`, `0 FAIL`, `6 WARN`
- Known repo-wide baseline before this sprint work:
  - `uv run pytest -q`
  - Result observed earlier: `143 passed, 2 failed, 1 xfailed`

## Current Risks

- Browser coverage is now materially stronger, but it is still a targeted confidence layer rather than a full cross-browser or visual-regression matrix
- CodeMap still shows structural warnings around dependency cycles, hidden coupling, observability gaps, and ownership concentration in a few critical modules
- The next major product value gap is broader family authoring depth beyond the current tree sidebar: richer cross-person storytelling, better multi-item content workflows, and clearer shared family event authoring still sit ahead of the current tree workspace
- CodeMap still points to structural warning-only debt in observability, ownership concentration, hidden coupling, and the settings/theme-service cycle even though governance remains passing

## Current Priority Order

1. Execute Sprint 15 to deepen rich tree-native storytelling, grouped media handling, and shared family event authoring
2. Preserve browser, accessibility, and staging-review confidence while expanding the tree workspace further
3. Reduce remaining warning-only structural debt where it directly supports user-facing confidence
4. Keep broader architecture cleanup behind user-facing value unless it blocks product progress

## Sprint State

- Closed sprints:
  - `S01 - Shared Collaboration Reset`
  - `S02 - Tree and Discovery Foundation`
  - `S03 - Timeline and Family Moments Expansion`
  - `S04 - Version History, Revert, and Moderation Controls`
  - `S05 - Encryption and Backup Hardening Pass`
  - `S06 - Theme Customization and Branding Controls`
  - `S07 - Observability and Coverage Hardening`
  - `S08 - Browser Regression Expansion and Release Confidence`
  - `S09 - Accessibility and Interaction Hardening`
  - `S10 - Readability and Responsive Polish`
  - `S11 - Tree as Primary Workspace`
  - `S12 - External Integrations and Confidence Hardening`
  - `S13 - Tree Workspace 2.0`
  - `S14 - Family Content and Relationship Authoring`
- Planned sprint:
  - `S15 - Rich Family Storytelling and Multi-Item Authoring`
- Sprint 15 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s15.md`
- Sprint 15 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s15.md`
- Primary packet: `/Users/cheech/code/family-book/task_packets/FB-020_rich_family_storytelling_and_multi_item_authoring.md`
- Sprint 14 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s14.md`
- Sprint 14 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s14.md`
- Sprint 14 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s14.md`
- Sprint 13 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s13.md`
- Sprint 13 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s13.md`
- Sprint 13 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s13.md`
- Sprint 12 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s12.md`
- Sprint 12 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s12.md`
- Sprint 12 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s12.md`
- See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
