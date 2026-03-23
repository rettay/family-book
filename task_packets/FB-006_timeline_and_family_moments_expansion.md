# Task Packet - FB-006 Timeline and Family Moments Expansion

## Objective

Turn Family Book's moments feature into a real family-history timeline by improving story authoring, tagged multi-person events, and timeline visibility across the home feed and person pages.

## Why / KPI

- Sprint 01 made the app collaborative.
- Sprint 02 made the shared record explorable.
- The next value layer is narrative depth: members need a useful way to capture stories, notes, milestones, and shared family memories over time.

Primary KPI:
- increase the percentage of active members who can add a meaningful timeline entry and have another member discover it in the expected surfaces.

## Scope

- In scope:
  - timeline query and ordering hardening
  - richer moments authoring for stories, notes, and tagged people
  - multi-person tagged events showing up in both home and person contexts
  - timeline rendering improvements on existing home/person surfaces
  - focused API and UI verification for timeline behavior
- Out of scope:
  - version history or moderation workflow
  - external news or social-media ingestion
  - AI summarization or auto-tagging
  - theme redesign work

## Constraints

- Timeline behavior must remain inside the authenticated family boundary.
- Tagged-person timeline results must be correct before adding visual polish.
- Existing moments/media data should be extended carefully rather than replaced.

## Implementation Notes

- Likely files:
  - `app/routes/moments.py`
  - `app/routes/pages.py`
  - `app/models/moments.py`
  - `app/templates/home.html`
  - `app/templates/person.html`
  - `app/templates/partials/moment_card.html`
  - `tests/test_moments.py`
  - `tests/test_api.py`
- Validation commands:
  - focused pytest for moments and API flows
  - optional browser evidence for home/person timeline surfaces

## Evaluation Environment

- Task: richer timeline and family-moments behavior
- Verifier: API tests plus rendered UI evidence
- Reference/oracle: `foundation/V1_PRODUCT_REQUIREMENTS.md`
- Expected evidence: members can create, discover, and view tagged timeline content in the right surfaces
- Known failure modes / reward hacks:
  - tagged people saved but not queryable in person timelines
  - new authoring fields exist in UI but are not persisted
  - home feed and person feed disagree on visibility or ordering
- Verifiability class: `bounded-judgment`

## Acceptance Criteria

- [ ] Members can create timeline entries that support richer story and note content.
- [ ] Tagged multi-person moments appear in the right person timelines, not only for the posting owner.
- [ ] The home feed and person timeline surfaces show consistent, correctly ordered results.
- [ ] Focused tests prove timeline/tagged-person correctness and visibility for at least two users.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] Timeline query correctness verified for tagged people
