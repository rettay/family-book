# Task Packet - FB-133 Research Page Beta Gating and Source Health UI

Status: Done

## Objective

Make the Research page honest about source confidence and per-source availability while keeping it available for founder use.

## Why / KPI

Production searches for `cutroni` and `maglio` only return one Antenati hit and lead to an unhelpful flow. The feature should stop presenting low-confidence/guided links as robust search results before broader user exposure.

## Scope

- In scope:
  - beta/low-confidence banner on Research page
  - per-source status: configured, not configured, no results, error
  - distinguish real search results from guided lookup links
  - UI for optional API-key sources
  - source-level error display in results partial
- Out of scope:
  - hiding the page from founder/admin users
  - adding Brave/Google Search API
  - full research workflow redesign
  - paid records integrations

## Likely Files

- `app/routes/research.py`
- `app/routes/external_records.py`
- `app/services/research_service.py`
- `app/services/external_records.py`
- `app/templates/research.html`
- `app/templates/partials/research_results.html`
- `locales/en.json`
- `locales/es.json`
- `locales/ru.json`
- `tests/test_research.py`
- `tests/test_external_records.py`
- `tests/test_pages.py`

## Acceptance Criteria

- [x] Research page shows a beta/low-confidence notice.
- [x] Results show per-source `configured`, `not configured`, `no results`, or `error` state.
- [x] Guided lookup links are labeled differently from real search results.
- [x] Unconfigured API-key sources do not silently disappear.
- [x] Source errors are visible enough to debug without pretending a search succeeded.
- [x] The page remains accessible for current founder/admin use.
- [x] Research result-count copy is localized for required locales.

## Validation Commands

- `uv run pytest tests/test_research.py tests/test_external_records.py tests/test_pages.py -q`
- `git diff --check`

## Definition of Done

- [x] Research page is honest about being beta/low-confidence.

## Builder Evidence

- Changed surfaces: `research_workspace`, `app/templates/research.html`, `app/templates/partials/research_results.html`, `app/services/research_service.py`, `app/services/external_records.py`.
- Resolved personas/scenarios: `genealogy_researcher`, `family_admin`; `search_external_records`, `inspect_result_details`, `save_or_follow_up_on_candidate_record`.
- Structural check: `uv run pytest tests/test_research.py tests/test_external_records.py tests/test_pages.py -q` covers beta/status rendering, guided lookup labeling, unconfigured-source visibility, and Spanish result-count localization.
- Rendered check: `make test-ui-playwright` includes `S47a research page renders beta and source health framing` and `S47a research page covers Spanish locale`.
- Visual artifact: `output/playwright/family-book-flow/screenshots/s47a-research-beta-sources.png`.
- Visual artifact: `output/playwright/family-book-flow/screenshots/s47a-research-beta-sources-es.png`.
- Sprint evidence: `docs/strategy/sprint-closeout-s47a.md`.
