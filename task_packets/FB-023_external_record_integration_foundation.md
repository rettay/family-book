# FB-023: External Record Integration Foundation

## Objective

Give Family Book the ability to import existing family trees and search free external genealogy databases so the app becomes a research workspace — not just a display layer for work done elsewhere.

## Why / KPI

Directly improves CFLSR by removing the biggest onboarding barrier (no import path for existing research) and the biggest research-workflow gap (no external record search from within the app). A genealogist with 15 years of research in Ancestry needs GEDCOM import to even consider switching. A researcher working on Argentine-Italian immigration needs CEMLA and Antenati access without leaving Family Book.

## Scope

### In scope

**Slice 1: GEDCOM Import**

- Parse GEDCOM 5.5.1 files (the de facto standard used by Ancestry, FamilySearch, MyHeritage, Gramps, Legacy, RootsMagic)
- Map INDI (individual) records to Person model:
  - NAME → first_name, last_name, maiden name
  - BIRT → birth_date, birth_place, birth_date_precision
  - DEAT → death_date, death_place
  - SEX → gender
  - NOTE → bio or research_notes
- Map FAM (family) records to ParentChild and Partnership:
  - HUSB/WIFE → Partnership
  - CHIL → ParentChild
  - MARR → partnership dates
- Track import as a batch (ImportBatch model already exists) with `source = 'gedcom_import'`
- Handle common encoding variants: UTF-8, ANSEL, Latin-1
- Upload UI: file picker on tree page or admin page, progress indicator, summary of imported records
- Conflict handling: detect potential duplicates by name + birth date match, present for user review before creating
- Validation: reject files > 10MB, reject malformed GEDCOM headers, show clear error messages
- GEDCOM export is NOT in scope for this sprint (deferred)

**Slice 2: External Record Search Panel**

- Add an "External Records" tab or section accessible from:
  - Tree sidebar (new tab alongside Overview, Details, Moments, Media, Relationships)
  - Person profile page
- Pre-fill search with the selected person's name, birth date, birth place
- Integrate the following free APIs (server-side proxy for API keys and rate limiting):

  **FamilySearch API** (all countries)
  - OAuth 2 authentication (user links their free FamilySearch account once)
  - Search historical records by name, date, place
  - Display results with record type, date, location, and link to full record on FamilySearch
  - Rate limit: respect FamilySearch throttling (currently ~40 requests/minute)

  **Chronicling America API** (USA newspapers)
  - No auth required
  - Search digitized US newspapers 1777-1963 by keyword
  - Display results with newspaper name, date, page, and link to full page image
  - Endpoint: `https://chroniclingamerica.loc.gov/search/pages/results/`

  **Trove API** (Australian newspapers)
  - Free API key (instant registration)
  - Search digitized Australian newspapers by keyword
  - Display results with newspaper name, date, snippet, and link to full article
  - Endpoint: `https://api.trove.nla.gov.au/v3/result`

  **NARA Catalog API** (USA federal records)
  - No auth required
  - Search National Archives catalog: census, military, immigration, naturalization, land patents
  - Display results with record group, series, title, date range, and link to digitized image if available
  - Endpoint: `https://catalog.archives.gov/api/v2/`

  **Antenati IIIF** (Italian civil records)
  - No auth required
  - Not a search API — provide a guided lookup by comune name + year range
  - User selects comune from a dropdown or types it, selects year range
  - Display IIIF manifest links to browse digitized civil registers (birth, marriage, death)
  - Optional: embed a lightweight IIIF image viewer (Mirador or OpenSeadragon) for inline viewing

  **DPLA API** (USA cross-institutional archives)
  - Free API key
  - Search across 4,000+ US libraries, archives, and museums
  - Display results with institution, title, date, type, and link
  - Endpoint: `https://api.dp.la/v2/items`

- Each source has a collapsible section in the panel showing result count and top results
- "Search all" button triggers parallel queries to all configured sources
- Individual "search [source]" buttons for targeted lookups
- Results are read-only — they link out to the external source for full viewing
- Caching: cache search results for 24 hours per person + source combination to reduce API calls

**Slice 3: CEMLA Immigration Record Search**

- Server-side integration with CEMLA's website (`cemla.com`)
- Search by surname, given name, and optional year range
- Implementation approach (in priority order):
  1. **Direct HTML parsing**: if CEMLA's search form submits to a stable endpoint, parse the HTML response for passenger list results
  2. **Headless browser**: if the site requires JavaScript rendering, use Playwright (already in the project for testing) to execute the search and extract results
  3. **Link-out fallback**: if scraping proves too fragile, provide a pre-filled URL that opens CEMLA's search in a new tab
- Display results: passenger name, ship name, arrival date, port of departure, port of arrival, nationality
- Rate limiting: max 2 requests per minute to CEMLA (be respectful of a nonprofit resource)
- Caching: cache results for 7 days per search query
- Graceful degradation: if CEMLA is unreachable or page structure changes, show a helpful message with a direct link to CEMLA's search page

### Out of scope

- GEDCOM export (deferred — import is the priority)
- GEDCOM 7.0 support (5.5.1 covers ~95% of exports from major platforms)
- FamilySearch tree sync (two-way sync is far more complex than search; defer)
- WikiTree API integration (lower priority; defer to later sprint)
- Internet Archive integration (results are books/documents, not structured records; defer)
- Paid API integrations (Ancestry, MyHeritage, Findmypast — no public APIs available)
- Automatic record attachment to person fields (user manually decides what to save)
- Find A Grave, BillionGraves (no APIs; could add link-out later)

## Dependencies

- Sprint 17 tree search and research notes must be stable (S17 introduces the research-workflow foundation this builds on)
- Sprint 18 completeness prompts provide the "missing data" signals that motivate external record search
- FamilySearch API requires app registration (free, ~1 week approval)
- Trove API requires key registration (free, instant)
- DPLA API requires key registration (free, instant)
- No paid dependencies

## Task Type

Feature development (backend integration + frontend UI + file parsing + migration)

## Likely Files

### Slice 1 (GEDCOM Import)
- `app/importers/gedcom_parser.py` — new GEDCOM parser module
- `app/routes/imports.py` — upload endpoint and import status
- `app/services/import_service.py` — batch import orchestration, duplicate detection
- `app/templates/partials/gedcom_upload.html` — upload UI partial
- `app/static/js/tree.js` — import trigger from tree page (if placed there)
- `app/models/imports.py` — ImportBatch already exists; may need adjustments

### Slice 2 (External Record Search)
- `app/services/external_records.py` — new service: API client for each source
- `app/routes/external_records.py` — new route: proxy search requests
- `app/static/js/tree.js` — external records sidebar tab
- `app/templates/partials/external_records.html` — search panel template
- `app/templates/person.html` — external records section on person page
- `app/static/css/main.css` — external records panel styling

### Slice 3 (CEMLA)
- `app/services/cemla_client.py` — new service: CEMLA HTML parser
- `app/routes/external_records.py` — CEMLA search endpoint (added to same route module)
- `app/templates/partials/external_records.html` — CEMLA results display

### Shared
- `alembic/versions/` — migration if any model changes needed for caching or FamilySearch OAuth tokens
- `.env.example` — new env vars for API keys (FAMILYSEARCH_APP_KEY, TROVE_API_KEY, DPLA_API_KEY)
- `app/config.py` — new config entries for API keys and rate limits

## Local Validation Commands

```bash
# Syntax check
uv run python -m compileall app tests

# Migration (if any)
uv run alembic upgrade head

# API tests
uv run pytest tests/test_api.py tests/test_pages.py -q

# GEDCOM parser tests
uv run pytest tests/test_gedcom_parser.py -q

# External records integration tests
uv run pytest tests/test_external_records.py -q

# Moments/media regression
uv run pytest tests/test_moments.py tests/test_media.py -q

# Browser flow
make test-ui-playwright

# CodeMap governance
uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json
```

## Acceptance Criteria

### Slice 1: GEDCOM Import
1. A user can upload a GEDCOM 5.5.1 file and see a progress indicator during processing
2. INDI records are correctly mapped to Person records (name, birth date, death date, gender, places)
3. FAM records are correctly mapped to ParentChild and Partnership relationships
4. Imported records have `source = 'gedcom_import'` and are associated with an ImportBatch
5. Potential duplicates (matching name + birth date) are flagged for user review before creation
6. Files with invalid headers or exceeding 10MB are rejected with clear error messages
7. Common encoding variants (UTF-8, ANSEL, Latin-1) are handled without data corruption

### Slice 2: External Record Search
8. An "External Records" panel is accessible from the tree sidebar for any selected person
9. The panel pre-fills the person's name, birth date, and birth place into search fields
10. FamilySearch search returns historical record results with type, date, location, and link
11. Chronicling America search returns newspaper results with title, date, and page link
12. Trove search returns Australian newspaper results with title, date, and article link
13. NARA Catalog search returns federal record results with series, title, date, and link
14. Antenati provides a guided comune + year lookup with links to IIIF manifests
15. DPLA search returns cross-institutional results with institution, title, and link
16. Each source section shows result count and is independently collapsible
17. Results are cached for 24 hours per person + source combination
18. API failures for one source do not prevent other sources from displaying results

### Slice 3: CEMLA Immigration Search
19. CEMLA search accepts surname, given name, and optional year range
20. Results display passenger name, ship name, arrival date, departure port, arrival port, and nationality
21. Requests to CEMLA are rate-limited to max 2 per minute
22. Results are cached for 7 days per search query
23. If CEMLA is unreachable or returns unexpected HTML, a helpful fallback message with direct link is shown

### Regression
24. Existing tree interactions (node click, sidebar tabs, graph mode, moments/media, search) remain functional
25. `make test-ui-playwright` passes
26. `uv run pytest tests/test_api.py tests/test_pages.py -q` passes
27. CodeMap governance shows no new FAIL results

## Definition of Done

All acceptance criteria pass. Validation commands are reproducible and passing. Browser evidence demonstrates GEDCOM upload and external record search working with real rendered behavior. No P0/P1 issues remain in scope. CFLSR is preserved or improved.

## Evaluation Environment

- **Task:** Feature development with external API integration, file parsing, and web scraping
- **Verifier:** Automated tests (pytest) for GEDCOM parsing and API client behavior, plus browser evidence for upload and search UI
- **Reference/oracle:** UX North Star principles (tree-as-workspace, in-context editing), external API documentation
- **Expected evidence:**
  - GEDCOM import: test with a sample .ged file (small, ~20 persons) showing correct Person and relationship creation
  - External records: test with a known person name showing results from at least 3 sources
  - CEMLA: test with a known surname showing parsed results or graceful fallback
  - Browser screenshots showing the external records panel in the tree sidebar
- **Known failure modes / reward hacks:**
  - GEDCOM parser that only handles one encoding (UTF-8) and silently corrupts ANSEL names
  - External record search that fires all APIs sequentially instead of in parallel (slow UX)
  - CEMLA scraper that works today but breaks when the site layout changes (needs graceful fallback)
  - Duplicate detection that's too aggressive (merging distinct people) or too lax (creating obvious duplicates)
  - FamilySearch OAuth that stores tokens in plaintext in the database
- **Verifiability class:** `bounded-judgment` (GEDCOM parsing is deterministic, API integration requires manual inspection of result quality, CEMLA scraping needs visual verification)
- **Context policy:** Builder should read the GEDCOM 5.5.1 spec, FamilySearch API docs, and each API's documentation before starting. Builder should prepare a small test GEDCOM file for validation.

## Risk and Verification Notes

### Complexity hotspots
- **GEDCOM parsing**: the format has many vendor-specific extensions and edge cases. Limiting to 5.5.1 and the most common tags (INDI, FAM, NAME, BIRT, DEAT, MARR, CHIL) reduces scope.
- **FamilySearch OAuth 2**: requires redirect flow, token refresh, and secure token storage. This is the most complex auth integration in the sprint.
- **CEMLA scraping**: inherently fragile. Must have a robust fallback to link-out behavior.

### Likely shallow-pass failure modes
- GEDCOM parser that works on a test file but fails on real Ancestry exports (different encoding, different tag ordering)
- External record panel that's added to tree.js but not wired to the sidebar tab system
- CEMLA parser that extracts data from one page layout but misses pagination
- API keys hardcoded instead of coming from environment variables

### Required verification depth
- GEDCOM import must be tested with at least 2 different source platforms' exports (e.g., one from FamilySearch, one from Gramps or Ancestry)
- External record search must be demonstrated with browser evidence showing real API results
- CEMLA must be tested against the live site with a known surname and shown to either return results or gracefully fall back

### What counts as sufficient discriminative power
- GEDCOM: import a file, verify person count matches, verify at least one relationship is correctly created
- External records: search for a known historical figure, verify results from at least 3 sources
- CEMLA: search for a known Italian surname, verify results or fallback behavior
- At least one negative case: upload an invalid file, verify rejection

## Execution Budget

### Builder may explore autonomously
- GEDCOM 5.5.1 tag structure and python-gedcom library options
- Each external API's documentation, authentication, and rate limits
- CEMLA website structure for scraping feasibility
- IIIF viewer library options (OpenSeadragon, Mirador, Leaflet-IIIF)
- Caching strategies for external API results

### Requires escalation
- Any change to the Person, ParentChild, or Partnership models beyond what's needed for import
- Storing FamilySearch OAuth tokens — must be encrypted or use secure session storage
- Any paid API integration
- Adding new Python dependencies beyond standard HTTP/parsing libraries
- CEMLA scraping approach if direct HTML parsing proves infeasible (before switching to headless browser)

### Material scope drift
- Building a two-way sync with FamilySearch
- Adding GEDCOM export
- Building a full IIIF image viewer rather than linking to manifests
- Adding search result saving/bookmarking to person records (defer to a later sprint)
- WikiTree or Internet Archive integration

### Proof obligations before review
- Working GEDCOM import with browser evidence (upload → progress → summary → persons visible in tree)
- External record search with browser evidence (select person → search → results from multiple sources)
- CEMLA search with evidence (either parsed results or graceful fallback)
- Passing test suite including new GEDCOM parser and external records tests
