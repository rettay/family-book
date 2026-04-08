# Task Packet - FB-134 External Research Source Link and Result Quality Fixes

Status: Partial

## Objective

Fix or demote broken external research links and establish a basic quality baseline for current searches.

## Why / KPI

Searches for `cutroni` and `maglio` return only one Antenati hit. Clicking it leads to a certificate error and redirect to `https://antenati.cultura.gov.it/`, forcing the user to search again. This wastes time and undermines trust.

## Scope

- In scope:
  - validate current Antenati URL format and current official endpoint
  - remove or demote Antenati if no useful deep link can be generated
  - verify Chronicling America and NARA searches in production-like environment
  - preserve query context in outbound links where possible
  - test `cutroni`, `maglio`, and baseline web-style query `maglio family`
  - prevent synthetic guided links from outranking real search results
- Out of scope:
  - full web search integration
  - Brave Search API unless separately approved
  - scraping search engines
  - building a record database
  - paid source integrations

## Likely Files

- `app/services/external_records.py`
- `app/services/research_service.py`
- `app/routes/research.py`
- `app/templates/partials/research_results.html`
- `tests/test_external_records.py`
- `tests/test_research.py`

## Acceptance Criteria

- [ ] Antenati no longer sends users through a certificate-error/redirect flow as if it were a useful result.
- [ ] Antenati is labeled as guided lookup or removed when it cannot deep-link.
- [ ] Searches for `cutroni` and `maglio` show honest per-source status.
- [ ] Known free sources either return real results or a clear no-results/error state.
- [ ] Result ranking does not let synthetic guided links dominate real results.
- [ ] Tests cover Antenati link generation/demotion behavior.

## Validation Commands

- `uv run pytest tests/test_external_records.py tests/test_research.py -q`
- `git diff --check`

## Definition of Done

- [ ] Research result links stop wasting user time.

## Implementation Note

- Partial S47a implementation corrected/demoted the Antenati guided lookup flow and stopped FamilySearch from appearing as a configured synthetic result.
- Remaining before full closeout: verify live Chronicling America and NARA result quality for `cutroni`, `maglio`, and `maglio family` in a production-like environment.
