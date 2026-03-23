# Task Packet - FB-003 Flat Family Access and Shared Visibility Reset

## Objective

Replace the current graph-distance visibility behavior with the launch model of flat shared access for active family members across people, tree data, and media.

## Why / KPI

- CFLSR is directly blocked when one family member's contributions are invisible to another.
- The current access-control behavior implements the wrong product.
- Shared tree and shared media visibility are the core collaborative loop.

## Scope

- In scope:
  - person visibility rules
  - tree visibility rules
  - media visibility rules
  - related tests and documentation updates
- Out of scope:
  - account/invite model
  - rich content-model expansion
  - map and tree customization features

## Constraints

- Keep the family boundary authenticated.
- Do not accidentally make content public.
- Do not preserve graph-distance hiding for launch behavior.

## Implementation Notes

- Likely files:
  - `app/access_control.py`
  - `app/routes/persons.py`
  - `app/routes/tree.py`
  - `app/routes/media.py`
  - `app/routes/pages.py`
  - `tests/test_api.py`
  - `tests/test_media.py`
  - any page or template code reflecting hidden-member assumptions
- Validation commands:
  - `uv run pytest tests/test_api.py tests/test_media.py -q`
  - targeted multi-user collaboration checks

## Evaluation Environment

- Task: visibility and sharing model reset
- Verifier: automated tests plus multi-user wrong-variant checks
- Reference/oracle: `foundation/COLLABORATION_AND_PRIVACY.md`
- Expected evidence: member-created or member-viewed content is visible to another active member; non-members still blocked
- Known failure modes / reward hacks:
  - tree becomes shared but media remains hidden
  - admin sees everything but members still see redacted shells
  - public/static leaks are introduced while fixing member visibility
- Verifiability class: `deterministic`

## Acceptance Criteria

- [ ] Active family members can view shared person records without graph-distance gating.
- [ ] Active family members can view shared tree data for the family space.
- [ ] Active family members can view shared media attached to visible people.
- [ ] Anonymous or unauthenticated requests still cannot access protected content.
- [ ] Automated tests prove both the allowed member-sharing path and the denied unauthenticated path.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation commands reproducible and passing
- [ ] No remaining tests assert the old graph-distance product model for launch behavior

## Risk and Verification Notes

- Complexity hotspots:
  - central access-control helpers
  - tests currently encode the old model
- Shallow-pass risk:
  - implementation updates one surface but leaves another on the old rules
- Required verification depth:
  - people, tree, and media must all be checked
