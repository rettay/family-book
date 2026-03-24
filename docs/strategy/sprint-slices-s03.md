# Sprint Slices - S03 Timeline and Family Moments Expansion

## Slice Sequence

### S03-1 Timeline Query and Ordering Hardening

Status: `done`

- Objective:
  make timeline retrieval correct and consistent across feed contexts
- Scope:
  tagged-person queries, ordering rules, pagination expectations
- Deliverable:
  tagged people reliably see relevant moments in person-specific timeline results
- Verification:
  focused tests for tagged-person timeline correctness and feed ordering

### S03-2 Rich Moments Authoring and Tagged Events

Status: `done`

- Objective:
  make family moments expressive enough for real shared history
- Scope:
  richer story/note authoring, multi-person tagging, persisted event detail
- Deliverable:
  members can create and retrieve richer moments with multiple tagged people
- Verification:
  focused tests for create/read behavior and tagged event persistence

### S03-3 Home and Person Timeline Integration

Status: `done`

- Objective:
  make the richer timeline visible where members actually browse the app
- Scope:
  home feed rendering, person-page timeline rendering, moment-card consistency
- Deliverable:
  shared memories appear coherently in both the home feed and person views
- Verification:
  focused tests plus browser evidence for visible timeline entries in both surfaces

## Slice Rules

- Do not pull version history into S03-1.
- Do not pull moderation workflow into S03-2.
- Do not pull external ingestion or AI enrichment into S03-3.
- Each slice should leave the app in a green, testable state before the next slice starts.

## Recommended Builder Order

1. `S03-1`
2. `S03-2`
3. `S03-3`

## PM Note

The sprint is about narrative product value. Keep it centered on trustworthy timeline behavior and visible family-history payoff, not infrastructure sprawl.

## Closeout Note

- Sprint 03 shipped all three slices.
- Audit follow-up tightened moment visibility validation and repaired the richer home composer flow so uploads target the selected person and failed submissions clean up uploaded media.
- Playwright flow evidence is now part of the repo-level UI evaluation layer via `make test-ui-playwright`.
