# Task Packet - FB-051 Relationship Correction Primitives and API Truth

## Objective

Add truthful relationship-correction primitives so mistaken family links can be updated, reversed, or removed without forcing members to manually delete and recreate parent-child records.

## Why / KPI

- The current tree flow lets members create and remove relationships, but a mistaken parent-child direction still requires a non-obvious delete-and-recreate workaround.
- CFLSR improves when family members can safely correct core genealogy mistakes instead of getting stuck after a wrong relationship entry.

Primary KPI:
- reduce failed or abandoned relationship-correction attempts in the tree workspace.

Secondary KPI:
- preserve trust in family structure by making parent-child direction corrections explicit and atomic.

## Scope

- In scope:
  - add a parent-child update contract in the API
  - add a server-side reverse operation for parent-child relationships
  - preserve cycle detection and duplicate prevention for update/reverse operations
  - broaden relationship response shapes where needed so correction UI can work from canonical data
  - keep partnership update behavior aligned enough that existing relationships can be edited truthfully from UI flows
- Out of scope:
  - redesigning the overall tree layout
  - introducing new relationship entity types
  - bulk relationship editing

## Task Type

- relationship model and correction-primitive packet

## Dependencies and Ordering Assumptions

- Unblocks FB-052, which will surface these correction primitives in the tree workspace.

## Changed Surfaces

- `tree_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
  - `family_admin`
- Safety personas:
  - `mobile_first_relative`

## Required Scenario IDs

- `add_relative_from_tree_context`
- `open_sidebar_and_edit_overview`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/routes/relationships.py`
  - `app/models/relationships.py`
  - `app/schemas.py`
  - `tests/test_api.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_api.py -q`
  - `tests/ui/playwright-flow-checks.sh`

## Evaluation Environment

- Task:
  make relationship correction truthful and atomic in the canonical API
- Verifier:
  API tests plus deterministic browser checks on the tree correction flow
- Reference/oracle:
  correcting a relationship should mutate the same canonical relationship row when safe, and should reject cycle-creating reversals
- Expected evidence:
  route tests, cycle-rejection tests, and tree-flow proof that reverse/edit actions produce the intended canonical relationship state
- Known failure modes / reward hacks:
  - reverse is implemented as a fragile client-side delete-and-create sequence
  - update allows impossible parent-child cycles
  - partnerships remain update-only in code but unreachable from the UI
  - success messages appear while the wrong canonical direction remains stored
- Verifiability class:
  `deterministic`
- Context policy:
  prioritize canonical correctness and failure safety over broad relationship-editing ambition

## UI Review Requirements

- Structural oracle:
  - CodeMap over `tree_workspace`
  - confirm API/schema changes fully support correction semantics rather than partial client hacks
- Browser oracle:
  - tree workflow proves an existing parent-child relation can be reversed and persists correctly
  - negative case proves a reversal that would create an ancestry cycle is rejected
- Visual/persona oracle:
  - covered by FB-052 on the actual tree workspace presentation layer
- Required artifacts:
  - API test evidence
  - browser replay proving reverse/edit/remove outcomes

## Acceptance Criteria

- [ ] The API supports updating existing parent-child relationships without requiring delete-and-recreate from the user’s perspective.
- [ ] The API supports reversing an existing parent-child relationship atomically when it is safe to do so.
- [ ] Reverse/update operations reject ancestry cycles and duplicate impossible states with clear errors.
- [ ] Existing partnership relationships remain editable through a truthful update contract.
- [ ] Browser-visible correction flows can rely on canonical API behavior instead of client-side emulation.

## Risk and Verification Notes

- Complexity hotspots:
  - cycle checking during reverse/update
  - preserving authorization semantics
  - keeping response shapes sufficient for the tree editor
- Likely shallow-pass failure modes:
  - reverse implemented as two separate requests with partial-failure risk
  - cycle check still reading the relationship being reversed and falsely blocking everything
  - UI changes landing before canonical primitives are safe
- Required verification depth:
  - direct route coverage plus at least one UI-visible correction path
- Sufficient discriminative power means:
  review should fail if the user can still end up with the same mistaken direction after “fixing” it.

## Execution Budget

- Builder may explore:
  - route shape, response payload expansion, and internal helper refactors needed for safe reverse/update semantics
- Builder must escalate if:
  - relationship correction requires a broader data-model redesign
- Material scope drift:
  - full relationship history visualization
  - moderation/versioning redesign
- Proof obligations before review:
  - canonical relationship state changes must be directly testable and cycle-safe

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] API and browser evidence attached
- [ ] No P0/P1 relationship-correction regressions remain in scope
- [ ] The canonical relationship model supports direct correction instead of only removal/recreation
