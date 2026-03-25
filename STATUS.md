# Family Book Status

## Overall State

Family Book is in **genealogy-workflow expansion**.

The product contract reset and tree-workspace foundation are complete (Sprints 01-17). The tree is the primary workspace with tabbed sidebar, moments/media authoring, graph-mode relationship editing, rich storytelling, in-tree search with zoom-to-node, research notes per person, and improved person page content hierarchy. Sprint 17 delivered tree discovery and research foundation. Sprint 18 is in planning, targeting completeness prompts and sidebar detail expansion.

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
- Focused Sprint 16 verification:
  - `uv run python -m compileall app tests`
  - Result at closeout: success
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - Result at closeout: `70 passed`
  - `uv run pytest tests/test_moments.py tests/test_media.py -q`
  - Result during implementation: `55 passed`
  - `make test-ui-playwright`
  - Result at closeout: success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`
  - Result at closeout: `17 PASS`, `0 FAIL`, `8 WARN`
- Focused Sprint 17 verification:
  - `uv run pytest -q`
  - Result at closeout: `262 passed, 0 failed, 0 xfailed`
  - `uv run pytest tests/test_api.py tests/test_pages.py -q`
  - Result at closeout: `70 passed`
  - `uv run pytest tests/test_moments.py tests/test_media.py -q`
  - Result at closeout: `55 passed`
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

- Browser coverage is materially stronger but still a targeted confidence layer rather than a full cross-browser or visual-regression matrix
- CodeMap still shows structural warnings around dependency cycles, hidden coupling, observability gaps, and ownership concentration in a few critical modules
- The genealogy-review triage has grown to 21 gaps across 3 tiers plus a long-horizon AI feature; sequencing them without scope creep requires disciplined sprint boundaries
- Video/audio playback is broken on the frontend despite backend support — uploaded videos render as broken images, audio can't be uploaded from UI at all
- External record integration (S19) introduces multiple third-party API dependencies; rate limiting, caching, and graceful degradation are required
- CEMLA HTML scraping is inherently fragile and requires a fallback strategy
- FamilySearch OAuth 2 introduces token storage security requirements
- GEDCOM parsing must handle encoding variants and vendor-specific extensions

## Current Priority Order

1. Execute Sprint 18 (completeness prompts, sidebar detail expansion)
2. Preserve browser, accessibility, and staging-review confidence while expanding research-workflow support
4. Execute Sprint 19 (GEDCOM import, external record search, CEMLA) — the integration foundation
5. Execute Sprint 20 (family calendar, relationship calculator) once S19 lands
6. Execute Sprint 21 (multimedia playback, timeline, branch filtering) — completes the archive story and enables voice recordings for AI memorial
7. Keep architecture cleanup behind user-facing genealogy-workflow value unless it blocks product progress

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
  - `S15 - Rich Family Storytelling and Multi-Item Authoring`
  - `S16 - Tree Graph Editing and Relationship Modeling`
  - `S17 - Tree Discovery and Research Foundation`
- Planning: `S18 - Completeness Prompts and Sidebar Detail Depth`
- Candidate: `S19 - External Record Integration Foundation`
- Primary integration packet: `/Users/cheech/code/family-book/task_packets/FB-023_external_record_integration_foundation.md`
- Sprint 16 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s16.md`
- Sprint 16 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s16.md`
- Sprint 16 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s16.md`
- Primary packet: `/Users/cheech/code/family-book/task_packets/FB-021_tree_graph_editing_and_relationship_modeling.md`
- Sprint 15 plan: `/Users/cheech/code/family-book/docs/strategy/sprint-plan-s15.md`
- Sprint 15 slices: `/Users/cheech/code/family-book/docs/strategy/sprint-slices-s15.md`
- Sprint 15 closeout: `/Users/cheech/code/family-book/docs/strategy/sprint-closeout-s15.md`
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
