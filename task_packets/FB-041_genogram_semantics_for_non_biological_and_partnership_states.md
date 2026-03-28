# Task Packet - FB-041 Genogram Semantics for Non-Biological and Partnership States

## Objective

Add clear visual semantics and editing support for non-biological parent-child relationships and partnership states so adoptions, foster/guardian ties, step-relationships, and divorce or separation can be interpreted correctly on the tree.

## Why / KPI

- The current tree is close to a basic genealogy viewer but not yet a trustworthy family diagram. Real families need more than one edge style.
- When biological, adoptive, foster, guardian, step, and former-partner relationships look the same, users either avoid entering truthful data or misread the tree after it is entered.

Primary KPI:
- increase correct interpretation of relationship type on `/tree`.

Secondary KPI:
- make Family Book more usable for families with adoption, guardianship, and non-linear household histories.

## Scope

- In scope:
  - visual semantics for biological vs adoptive vs foster/guardian parent-child ties
  - visual semantics for current vs former partnership state
  - tree legend or inline semantic cues that explain those styles without requiring prior genealogy knowledge
  - relationship authoring or editing affordances in tree context for the supported relationship kinds
  - step-relationship interpretation support where it can be inferred from household structure and relationship kind
- Out of scope:
  - pets or institutions as separate node types
  - legal-document workflows or provenance-specific adoption evidence capture
  - broad person-edit page redesign outside what is needed to support the new kinds

## Task Type

- member-facing tree semantics and relationship-authoring packet

## Dependencies and Ordering Assumptions

- Depends on FB-039 because the visual semantics need a trustworthy family-unit foundation.
- Best sequenced after FB-040 if that packet introduces partnership-state rendering primitives; however, this packet may absorb the minimal state styling if FB-040 ships narrower than expected.
- If current relationship APIs cannot express a required kind truthfully, builder must escalate rather than infer unsupported meaning.

## Changed Surfaces

- `tree_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
  - `family_admin`
- Safety personas:
  - `mobile_first_relative`

## Required Scenario IDs

- `find_person_in_tree`
- `open_sidebar_and_edit_overview`
- `add_relative_from_tree_context`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - non-biological relationship distinguishability
  - partnership-state semantics
  - discoverable legend or cues
  - tree-context authoring for the supported relationship kinds
- Should improve:
  - step-family readability
  - relationship confidence or explanatory helper copy if already supported by the model
- Must re-run:
  - adversarial browser flows creating or editing at least one non-biological relationship
  - locale review so the legend and labels are translated

## Implementation Notes

- Likely files:
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/routes/relationships.py`
  - `app/routes/tree.py`
  - `app/static/css/main.css`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/ui/playwright_seed.py`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_api.py`
  - `tests/test_phase3.py`
- Validation commands:
  - `uv run pytest tests/test_api.py tests/test_phase3.py tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make non-biological and former/current relationship types visible and editable in the tree
- Verifier:
  structural review, deterministic browser checks, locale parity, and visual/persona review
- Reference/oracle:
  light genogram conventions adapted to Family Book
  Family Book relationship kinds and partnership status fields
- Expected evidence:
  a viewer can tell the difference between biological and non-biological ties, and can tell whether a partnership is current or former
- Known failure modes / reward hacks:
  - edge styles technically differ but are too subtle to interpret
  - legend exists but is hidden, untranslated, or detached from the tree state
  - authoring UI exposes kinds but the renderer ignores them
  - mobile legend or controls are clipped or unreachable
- Verifiability class:
  `bounded-judgment`
- Context policy:
  use just enough genealogy convention to improve truthfulness without turning the tree into an expert-only tool

## UI Review Requirements

- Structural oracle:
  - CodeMap review over relationship rendering, legend wiring, and authoring controls
- Browser oracle:
  - seeded assertions proving:
    - biological and adoptive or guardian ties render differently
    - current and former partnership states render differently
    - legend or explanatory cues are visible and translated
    - tree-context editing can create or update the supported kinds
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough reading a simple adoption or guardian case
  - `family_admin` desktop walkthrough updating a partnership state and seeing the tree reflect it
  - `mobile_first_relative` mobile walkthrough confirming legend and relationship cues remain usable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for relationship-style states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - edge meanings are understandable without guessing
  - legend is present but not overwhelming
  - edit affordances do not require leaving the tree for a common relationship correction

## Acceptance Criteria

- [ ] The tree visually distinguishes biological parent-child ties from at least one non-biological tie type supported by the model.
- [ ] The tree visually distinguishes active/current partnerships from former partnership states when the data is present.
- [ ] The relationship legend or equivalent explanatory cues are visible, translated, and usable on desktop and mobile.
- [ ] Tree-context relationship editing can set and persist the supported non-biological or partnership-state kinds without requiring a page-detour workaround.
- [ ] The new semantics improve truthfulness without making the tree materially harder for non-expert family members to read.

## Risk and Verification Notes

- Complexity hotspots:
  - balancing genealogy accuracy with mainstream readability
  - relationship-authoring UX density in the sidebar
  - locale completeness across new user-facing terms
- Likely shallow-pass failure modes:
  - semantics exist only in color and fail accessibility or subtlety checks
  - legend is added but not connected to live rendered states
  - relationship kind can be authored only by admins or only in one code path
- Required verification depth:
  - wrong-variant checks for missing translation and ignored relationship kinds
  - browser evidence must cover both reading and authoring
- Sufficient discriminative power means:
  review should fail if a viewer still cannot reliably distinguish biological from non-biological ties or current from former partnerships.

## Execution Budget

- Builder may explore:
  - line styles, markers, badges, and low-friction legend patterns
  - progressive disclosure for advanced relationship options
- Builder must escalate if:
  - required relationship kinds are missing from the underlying model or API
  - proposed semantics would conflict with the launch UX contract by overwhelming casual users
- Material scope drift:
  - full research/provenance redesign for relationship evidence
  - broad person-edit page overhaul
- Proof obligations before review:
  - renderer and authoring paths are both exercised
  - locale parity includes `ru` as well as the required UI review locales

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 truthfulness regressions remain in the affected relationship rendering and editing paths
