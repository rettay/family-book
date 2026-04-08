# Sprint Closeout - S47a Product Stabilization Before Commercialization

Status: Closed

Audit result: PASS

## Scope Completed

- `FB-132`: timeline filter consistency and error-state fix.
- `FB-133`: research beta gating and source health UI.
- `FB-131`: tree sidebar popout collapse/dock fix.
- `FB-134`: partial Antenati/guided-link demotion only; full source quality work remains queued.
- `FB-130`: not completed; broader overlay/panel contract remains queued.

## Outcome

- Timeline filters now handle `All Events`, plural event aliases, and the reported `1880` to `2002` range without bogus content-load errors.
- Research now presents beta/low-confidence framing, source health states, guided-lookup labeling, and localized result-count copy.
- Popped-out tree sidebar collapse now docks instead of closing.
- Full Playwright lane passed after adding S47a-specific English, Spanish, and mobile evidence.

## Persona And Scenario Resolution

- `tree_workspace`: `contributing_member`, `family_admin`; safety persona `mobile_first_relative`; scenarios `find_person_in_tree`, `open_sidebar_and_edit_overview`, `add_relative_from_tree_context`.
- `moments_and_timeline`: `contributing_member`; safety persona `mobile_first_relative`; scenarios `add_story_or_note`, `view_recent_family_activity`.
- `research_workspace`: `genealogy_researcher`; safety persona `family_admin`; scenarios `search_external_records`, `inspect_result_details`, `save_or_follow_up_on_candidate_record`.

## Structural Evidence

- `uv run pytest tests/test_timeline.py tests/test_research.py tests/test_external_records.py tests/test_pages.py tests/test_s43_features.py -q`
- `bash -n tests/ui/playwright-flow-checks.sh`
- `git diff --check`
- `uv run python -m json.tool locales/en.json`
- `uv run python -m json.tool locales/es.json`
- `uv run python -m json.tool locales/ru.json`
- `uv run python -m json.tool locales/it.json`
- `uv run python -m json.tool locales/zh.json`

## Rendered-Behavior Evidence

- `make test-ui-playwright`
- Browser summary: `output/playwright/family-book-flow/summary.md`
- Trace/video artifacts: `output/playwright/family-book-flow/traces/`

## Visual Evidence

- Timeline filters: `output/playwright/family-book-flow/screenshots/s47a-timeline-filters.png`
- Timeline filters, Spanish mobile: `output/playwright/family-book-flow/screenshots/s47a-timeline-filters-mobile-es.png`
- Research beta/source health: `output/playwright/family-book-flow/screenshots/s47a-research-beta-sources.png`
- Research beta/source health, Spanish: `output/playwright/family-book-flow/screenshots/s47a-research-beta-sources-es.png`
- Tree sidebar docked after popped-out collapse: `output/playwright/family-book-flow/screenshots/s47a-sidebar-docked-after-collapse.png`

## Notes

- The Playwright harness now neutralizes host Google Maps environment variables with `PENDING_SETUP` so the SVG map baseline is deterministic.
- The create-person browser flow now waits for the expected `/tree?focus=` URL instead of `networkidle`.
- The tree sidebar has both a static regression assertion for the floating collapse/dock contract and a rendered browser check that invokes the popped-out collapse path.
- S47a timeline and research evidence now covers the required Spanish locale; timeline also has a mobile viewport assertion and screenshot.
