# Task Packet - FB-037 Tree Selected-Person Context and Focus Framing

## Objective

Help members interpret what they are looking at by adding clear selected-person relationship summaries, explicit root/focus framing, and action-oriented gap prompts in the tree sidebar.

## Why / KPI

- Even with a correct graph layout, users still need quick confirmation of "who is this person relative to the family and to my current view?"
- The current tree provides data and controls, but it does not yet give a fast narrative summary that helps a member verify correctness before editing.

Primary KPI:
- increase first-pass comprehension of a selected person's family position and likely next action.

Secondary KPI:
- reduce sidebar scanning time before a member understands whether the selected person is a parent, child, or partner in the current context.

## Scope

- In scope:
  - compact selected-person relationship summary at the top of the tree sidebar
  - explicit labeling for current focus person versus designated root person where relevant
  - actions to re-center or return to the focus/root context without losing orientation
  - overview-level gap prompts that convert missing dates/media/stories/relationships into invitations to contribute
  - stronger summary copy that helps a user sanity-check the family structure before editing
- Out of scope:
  - full wiki/profile redesign
  - broad research-workspace redesign
  - map or timeline information architecture changes
  - schema changes for new relationship metadata

## Task Type

- member-facing comprehension / orientation packet

## Dependencies and Ordering Assumptions

- Best sequenced after FB-035 because a clear summary is more trustworthy once family-unit layout semantics are fixed.
- Can proceed independently of FB-038 if needed, but benefits from any later control regrouping.

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
  - selected-person interpretability
  - root/focus clarity
  - gap prompts in the overview
- Should improve:
  - confidence that the selected person is the intended target before editing
  - branch/family orientation for large trees
- Must re-run:
  - browser assertions for summary text, focus/root labeling, and prompt interactions
  - visual/persona review of selected-person comprehension

## Implementation Notes

- Likely files:
  - `app/templates/partials/person_sidebar.html`
  - `app/templates/tree.html`
  - `app/static/js/tree.js`
  - `app/routes/tree.py`
  - `app/routes/persons.py`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_pages.py`
  - `tests/test_api.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  improve in-tree orientation and selected-person comprehension
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  selected-person overview behavior in the current tree
- Expected evidence:
  a member can open a person and quickly answer:
  - who is this person?
  - how do they connect here?
  - what is missing that I can add next?
- Known failure modes / reward hacks:
  - adding verbose copy that still takes too long to parse
  - root and focus labels exist but remain visually interchangeable
  - gap prompts read like passive metadata rather than invitations
  - desktop summaries overflow or collapse poorly on mobile
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prioritize quick human understanding over exhaustive metadata display

## UI Review Requirements

- Structural oracle:
  - CodeMap review over sidebar summary composition, root/focus state wiring, and prompt conditions
- Browser oracle:
  - deterministic checks that:
    - selecting a person shows a readable relationship summary
    - root and focus labels are present only when appropriate
    - re-center or return-to-focus actions work
    - at least one missing-data prompt opens the relevant editing surface
- Visual/persona oracle:
  - `contributing_member` desktop review for fast comprehension
  - `family_admin` desktop review for root/focus verification
  - `mobile_first_relative` mobile review for summary scanability and reachable next-step prompts
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for selected-person overview states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - the selected person's role in the family is summarized near the top of the sidebar
  - root and focus are visually distinct concepts
  - missing information appears as an invitation to contribute rather than a dead blank

## Acceptance Criteria

- [ ] Selecting a person surfaces a concise relationship summary that helps a member understand their family position without opening the full profile page.
- [ ] The tree distinguishes designated root from current focus/centering state when both concepts are present.
- [ ] The UI offers an explicit way to re-center or reorient to the current focus/root context after navigating elsewhere in the tree.
- [ ] Missing stories, photos, dates, or relationships appear as action-oriented prompts in the overview rather than passive blanks where appropriate.
- [ ] The new summary and prompts remain scannable and usable on desktop and mobile in `en` and `es`.

## Risk and Verification Notes

- Complexity hotspots:
  - deriving human-readable relationship summaries without misleading overclaim
  - root versus focus semantics
  - keeping summary density low enough for mobile
- Likely shallow-pass failure modes:
  - summary text repeats raw counts without improving comprehension
  - gap prompts exist but route users into confusing surfaces
  - root/focus labels are technically present but visually weak
- Required verification depth:
  - human-readability review plus deterministic functional checks
  - negative-case check for root/focus labels not appearing incorrectly
- Sufficient discriminative power means:
  the packet should fail if a user still has to infer orientation entirely from raw graph geometry.

## Execution Budget

- Builder may explore:
  - compact summary chips, sentences, or hybrid treatments
  - light path/focus highlighting if needed for orientation
  - the smallest prompt set that improves contribution motivation
- Builder must escalate if:
  - summary requirements imply a more complex relationship-engine feature than this packet can safely hold
- Material scope drift:
  - full person profile rewrite
  - generalized activity-feed or research redesign
- Proof obligations before review:
  - selected-person comprehension demonstrably improves in browser and visual evidence
  - root/focus semantics are explicit and accurate

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No new root/focus confusion or misleading summary copy remains in scope
