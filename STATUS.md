# Family Book Status

## Overall State

Family Book is in **power-user genealogy depth**.

22 sprints closed (S01-S22). The product is a full-featured collaborative family wiki with tree workspace, multimedia archive, family timeline, calendar, relationship calculator, GEDCOM import, external record search, genetic profiles, structured medical conditions, and a family health dashboard. All V1 product requirements are met. The next sprint targets genealogy research credibility: source citations, evidence classification, and date intelligence.

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
- Focused Sprint 18 verification:
  - `uv run pytest -q`
  - Result at closeout: `265 passed, 0 failed`
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

- Browser coverage is a targeted confidence layer, not a full cross-browser or visual-regression matrix
- CodeMap still shows structural warnings in a few critical modules
- CEMLA HTML scraping is inherently fragile and requires ongoing maintenance
- Genetic and medical data is the most sensitive content — flat family access model may need revisiting
- The AI memorial long-horizon feature now has all prerequisites met (G-19, G-22, G-23) — scheduling it requires ethical consent framework design

## Current Priority Order

1. Execute `S30 - Map Truthfulness and Place Intelligence`
2. Preserve test and browser baselines while tightening high-trust geography and location-entry flows
3. Queue research UX overhaul after the map/location truthfulness loop is coherent
4. Keep broader platform completeness and architectural cleanup behind member-facing trust improvements

## Sprint State

- Recently closed: `S29 - Calendar as Primary Surface and Family Calendar Discovery`
- Planning: `S30 - Map Truthfulness and Place Intelligence`
- Candidate: `S31 - Research UX Overhaul and Test Infrastructure`
- See `backlog.md`, `docs/strategy/kanban-2026q1.md`, `docs/strategy/sprint-board-2026q1.md`
