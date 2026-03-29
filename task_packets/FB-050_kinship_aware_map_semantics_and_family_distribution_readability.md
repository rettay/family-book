# Task Packet - FB-050 Kinship-Aware Map Semantics and Family Distribution Readability

## Objective

Improve `/map` readability so family members can understand who markers represent and prepare the surface for future “where is my family” kinship-distance views without inventing relationship semantics the product does not actually compute.

## Why / KPI

- Once the map is based on better coordinates, the next trust issue is semantic readability: users need to know whether they are seeing residence, burial, immediate family, or broader kin without reading raw labels one by one.
- CFLSR improves when the map helps members orient themselves in the family network rather than just plotting anonymous points.

Primary KPI:
- improve comprehension of family distribution on `/map`.

Secondary KPI:
- establish a truthful foundation for future relation-distance map features.

## Scope

- In scope:
  - redesign marker semantics, legend, and interaction cues so residence vs burial and supported kinship classes are readable at a glance
  - add truthful relationship-distance semantics where the product can actually compute them from the family graph
  - improve map-side filtering or focus states so users can interpret who is “my family nearby” vs the broader family set
  - explicitly bound future-facing kinship layers so the UI does not promise unsupported cousin-depth logic if not yet implemented
  - preserve mobile readability and legend discoverability
- Out of scope:
  - full social-network map visualization
  - arbitrary manual kinship tagging
  - exhaustive cousin-level relation storytelling if the graph logic is not ready

## Task Type

- member-facing map readability and semantic-foundation packet

## Dependencies and Ordering Assumptions

- Depends on FB-049 so the map has truthful coordinate-backed data to read.
- May narrow launch scope if only immediate-family / graph-distance classes are safely verifiable in this sprint.

## Changed Surfaces

- `map_view`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `genealogy_researcher`
  - `mobile_first_relative`

## Required Scenario IDs

- `view_people_or_burials_on_map`
- `interpret_family_distribution_on_map`
- `understand_empty_state_and_filters`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/templates/map.html`
  - `app/static/js/map.js`
  - `app/routes/tree.py`
  - relationship/path utilities if reused
  - `app/static/css/main.css`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/test_api.py`
  - `tests/test_pages.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_api.py tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make map markers and filters semantically understandable enough for family-distribution use
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  marker meaning should come from actual location and relationship data, not decorative guesswork
- Expected evidence:
  legend/marker screenshots, filter/focus walkthroughs, and checks showing the semantics align with real graph data
- Known failure modes / reward hacks:
  - icons become prettier but not more truthful
  - “immediate family” or cousin labels appear without real graph-distance logic
  - desktop legend works while mobile hides critical semantic cues
  - marker semantics rely on color alone and become ambiguous
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prioritize truthful, limited kinship semantics over ambitious but weakly grounded cousin-map storytelling

## UI Review Requirements

- Structural oracle:
  - CodeMap over `map_view`
  - confirm marker semantics and legend states are wired to actual route data and filters
- Browser oracle:
  - seeded assertions proving:
    - users can distinguish supported marker kinds
    - map semantics remain understandable on mobile
    - any kinship class shown is computed truthfully from the graph
    - empty/filter states explain what is and is not being shown
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough understanding where close family members are
  - `genealogy_researcher` walkthrough interpreting the legend and semantic distinctions correctly
  - `mobile_first_relative` mobile walkthrough keeping marker meaning discoverable without dense chrome
- Required artifacts:
  - CodeMap JSON output
  - desktop/mobile screenshots of the map legend and marker states
  - replay notes covering one focused kinship/filter interpretation flow
- Expected visual states:
  - marker semantics are legible without reading raw data labels line by line
  - the UI does not imply relation-depth support beyond what the graph can truly calculate

## Acceptance Criteria

- [ ] `/map` communicates marker meaning clearly for the supported location and kinship semantics in scope.
- [ ] Any kinship-distance language shown on the map is computed from actual relationship data rather than decorative heuristics.
- [ ] Desktop and mobile both keep the legend/filter/story understandable without relying on hidden controls.
- [ ] Empty or filtered states explain why a marker set is small, broad, or absent.
- [ ] The implementation leaves a truthful extension path for future “where is my family” relation-distance views.

## Risk and Verification Notes

- Complexity hotspots:
  - avoiding overclaim on kinship semantics
  - balancing marker readability with dense-family maps
  - preserving mobile clarity
- Likely shallow-pass failure modes:
  - iconography changes without semantic value
  - relation-distance language exceeds the verified graph logic
  - legend is technically present but clipped or ignorable on mobile
- Required verification depth:
  - deterministic graph-aligned marker assertions plus visual evidence on both breakpoints
- Sufficient discriminative power means:
  review should fail if a user still cannot tell why a marker is on the map or what family meaning it represents.

## Execution Budget

- Builder may explore:
  - focused legends, marker badges, simple relation-class toggles, and selected-person map focus states
- Builder must escalate if:
  - desired cousin-depth semantics require broader graph-distance APIs than the current launch contract can support safely
- Material scope drift:
  - full social-graph geovisualization
  - speculative relation-distance UI beyond verifiable graph logic
- Proof obligations before review:
  - semantic marker meaning and any kinship classes shown are both demonstrated and graph-truthful

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 semantic-truth regressions remain on `/map`
- [ ] The map becomes readable enough to support future family-distribution features without faking graph meaning
