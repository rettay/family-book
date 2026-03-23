# Sprint Slices - S02 Tree and Discovery Foundation

## Slice Sequence

### S02-1 Tree Preference Persistence

Status: `done`

- Objective:
  persist per-user tree display preferences on the server
- Scope:
  preference model, persistence route, tree page load/save wiring
- Deliverable:
  one user can save tree display settings and retrieve them later
- Verification:
  focused tests proving one user's preferences do not overwrite another user's

### S02-2 Tree Filters

Status: `done`

- Objective:
  make the tree meaningfully explorable through supported filters
- Scope:
  living/deceased, branch, residence country, birth country
- Deliverable:
  filters change real tree outputs and remain aligned with persisted person fields
- Verification:
  focused tests for filtered tree results and UI/backend parameter alignment

### S02-3 Authenticated Map Foundation

Status: `done`

- Objective:
  provide the first private map view for shared family location data
- Scope:
  authenticated map data route, basic map page, residence and burial location output
- Deliverable:
  logged-in members can open a map view and inspect supported location markers
- Verification:
  auth-gated map route checks plus browser evidence for visible markers

## Slice Rules

- Do not pull version history into S02-1.
- Do not pull moderation or privacy redesign into S02-2.
- Do not pull external geocoding or visual polish into S02-3.
- Each slice should leave the app in a green, testable state before the next slice starts.

## Recommended Builder Order

1. `S02-1`
2. `S02-2`
3. `S02-3`

## PM Note

The slices are intentionally narrow. The goal of Sprint 02 is user-facing exploration value, not another deep platform rewrite.

## Closeout Note

- Sprint 02 shipped all three slices.
- Audit follow-up added truthful burial-location mapping and corrected the tree-name privacy toggle.
- CodeMap setup was added for this repo so later governance scans are scoped to product code instead of docs/data noise.
