# Task Packet - FB-040 Multi-Partnership Households and Remarriage Correctness

## Objective

Make the tree render divorces, remarriages, and children across multiple partnerships correctly so each child is attached to the right household without duplicating people or implying the wrong parent pair.

## Why / KPI

- After the family-unit layout foundation lands, the next trust-breaking failure mode is remarriage: a person with multiple partners and children from different relationships can easily produce false household groupings.
- Real family trees include former marriages, current marriages, and half-siblings. If Family Book gets these wrong, serious users will abandon the tree as an authoritative workspace.

Primary KPI:
- improve correctness of household interpretation for people with more than one partnership.

Secondary KPI:
- reduce ambiguity around half-siblings, step-relationships, and former partners on `/tree`.

## Scope

- In scope:
  - explicit rendering of multiple partnerships for one person
  - child-to-household attachment correctness when a parent has children with different partners
  - visual ordering rules for current and former partnerships when dates or status are available
  - branch spacing so half-sibling groups remain legible
  - support for divorced, separated, widowed, and remarried partnership states in tree rendering
- Out of scope:
  - adoption/foster/guardian semantics
  - pets or institutions
  - printable chart variants
  - full historical timeline visualization of every partnership event

## Task Type

- member-facing tree relationship correctness packet

## Dependencies and Ordering Assumptions

- Depends on FB-039. This packet assumes the tree already has explicit family-unit semantics.
- If partnership status or date metadata is insufficient for clear ordering, builder may use stable deterministic ordering now and defer richer chronology to a later packet rather than block correctness.

## Changed Surfaces

- `tree_workspace`

## Target Personas

- Primary personas:
  - `family_admin`
  - `contributing_member`
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
  - one-person multiple-partner rendering
  - correct child attachment to each partnership household
  - visibility of former versus current partnership state
- Should improve:
  - sibling readability across half-sibling and step-sibling groups
  - ordering stability under zoom, focus, and filtering
- Must re-run:
  - adversarial browser cases for remarriage and half-sibling families
  - visual review of desktop and mobile household readability

## Implementation Notes

- Likely files:
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `app/static/css/main.css`
  - `app/routes/tree.py`
  - `tests/ui/playwright_seed.py`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_api.py`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  render multi-partnership households and remarriage cases correctly in the tree
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  household semantics expected by real multigenerational family trees
  partnership status fields already present in Family Book
- Expected evidence:
  a person with two partnerships appears once, each child group is attached to the correct household, and former/current partnership state is readable
- Known failure modes / reward hacks:
  - duplicate person nodes used to fake correctness
  - children attach to the right partner in one branch but sibling ordering becomes unreadable
  - all partnerships look active/current because status is ignored in the tree
  - mobile compresses multi-household groups into overlap
- Verifiability class:
  `bounded-judgment`
- Context policy:
  optimize for household correctness and readability, not maximal chronology detail

## UI Review Requirements

- Structural oracle:
  - CodeMap review over any new multi-partnership placement logic and status-based styling
- Browser oracle:
  - seeded assertions proving:
    - one person can appear in two households without duplication
    - children from each partnership attach to the correct household
    - former/current partnership styling differs when supported by data
    - mobile preserves readable partner and child grouping
- Visual/persona oracle:
  - `family_admin` desktop walkthrough of a divorced-remarried parent with children in both households
  - `contributing_member` desktop walkthrough reading half-siblings correctly
  - `mobile_first_relative` mobile walkthrough confirming the same grouping is still understandable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for multi-partnership states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - a remarried person is not duplicated
  - former and current partnerships are distinguishable
  - children clearly descend from the correct partner pair

## Acceptance Criteria

- [ ] A person with multiple partnerships renders once while still participating in each relevant household.
- [ ] Children from different partnerships attach to the correct household with no false implication that all children share the same parents.
- [ ] Partnership state differences such as divorced, separated, or widowed are visually distinguishable when the data is present.
- [ ] Half-sibling and step-sibling branches remain readable on desktop and mobile without overlap or ambiguous grouping.
- [ ] The packet does not reintroduce false direct ancestry lines while solving multi-partnership cases.

## Risk and Verification Notes

- Complexity hotspots:
  - one node participating in multiple local household structures
  - ordering of current versus former partners
  - crossing reduction when siblings belong to different households
- Likely shallow-pass failure modes:
  - duplicate nodes used as an implementation shortcut
  - statuses exist in DOM but are visually too weak to matter
  - current household reads correctly but former household is pushed into an unreadable detached area
- Required verification depth:
  - multi-household adversarial seed plus persona review
  - negative check that one-parent-many-partner cases do not duplicate person identity
- Sufficient discriminative power means:
  review should fail if a user cannot confidently tell which children belong to which partnership.

## Execution Budget

- Builder may explore:
  - per-partnership union nodes
  - subtle chronology labels or badges if required for clarity
  - branch ordering heuristics that reduce crossings without visual overload
- Builder must escalate if:
  - existing relationship data cannot represent required partnership state truthfully
  - the only viable solution requires a deeper relationship schema change than this packet allows
- Material scope drift:
  - adoption/guardian semantics
  - broad relationship editing redesign
- Proof obligations before review:
  - browser evidence proves a multi-partnership case, not just a single-couple family
  - no duplicate-person shortcut is used

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 multi-household interpretation regressions remain in scope
