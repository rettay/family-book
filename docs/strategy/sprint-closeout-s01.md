# Sprint Closeout - S01 Shared Collaboration Reset

## Outcome

Sprint 01 is closed with a passing audit result.

The sprint accomplished the intended reset from a restrictive, graph-distance-oriented family tree runtime toward a collaborative family wiki baseline with:

- invite and account lifecycle support
- Google-based sign-in and session handling
- flat shared visibility for active family members
- richer person records for medical and burial data
- tagged media and tagged moments
- focused builder and auditor verification

## Evidence

- implementation branch: `codex/shared-collaboration-reset`
- closeout commits:
  - `eeb33bf` - implement sprint 01 collaboration reset
  - `7f3f2b2` - fix audited sprint 01 defects
- focused closeout verification:
  - `uv run pytest tests/test_models.py tests/test_api.py tests/test_auth.py tests/test_media.py tests/test_moments.py tests/test_phase1_edge_cases.py -q`
  - result: `117 passed, 1 xfailed`

## What Changed

- `FB-002` completed:
  account invites, account lifecycle controls, onboarding/auth spine
- `FB-003` completed:
  flat shared access reset across people, tree, media, and moments
- `FB-004` completed:
  richer person fields and persisted tagged-content support

## Not In Sprint 01

- tree display personalization
- tree filtering UX beyond current backend support
- map view
- version history and revert workflows
- stronger field-level sensitive-data policy

## Recommended Sprint 02

- Name: `S02 - Tree and Discovery Foundation`
- Primary packet: `FB-005 Tree Preferences, Filters, and Map Foundation`
- Secondary follow-on candidate: `FB-006 Timeline and Family Moments Expansion`

## PM Note

Sprint 01 should be treated as the collaboration spine. Sprint 02 should now focus on making the shared data easier to navigate and inspect rather than adding another major permissions rewrite.
