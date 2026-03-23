# Sprint Plan - S02 Tree and Discovery Foundation

## Sprint

- Name: `S02 - Tree and Discovery Foundation`
- Status: Planned
- Primary packet: `FB-005 Tree Preferences, Filters, and Map Foundation`

## Sprint Goal

Make the shared family record easier to explore by adding launch-grade tree personalization, supported tree filters, and a first authenticated map view for living and burial locations.

## Why This Sprint

Sprint 01 built the collaboration spine. The next highest-value gap is not permissions or another data-model rewrite. It is usability: members need practical ways to inspect, filter, and navigate the shared family record they can now collaboratively build.

## Must-Have Outcomes

- Users can persist their own tree display preferences without mutating another user's defaults.
- Users can filter the tree by launch-supported attributes:
  living/deceased, branch, residence country, birth country.
- The app exposes an authenticated map view foundation for:
  residence locations and burial locations.
- Tree and map outputs respect the authenticated family boundary.

## Acceptance Criteria

1. A logged-in member can change tree display settings and see them persist across refresh/session restart.
2. A second logged-in member retains their own independent display settings.
3. Tree filters affect actual API or rendered outputs, not just local UI state.
4. The map view loads only for authenticated users and returns only authorized person/location data.
5. Burial locations appear on the map when present in the underlying person record.
6. Focused tests or browser evidence prove one-user preference persistence and filtered tree correctness.

## In Scope

- Per-user tree preference persistence
- Tree filter backend and UI wiring
- Authenticated map data route
- Initial map page/template
- Use of existing persisted fields only
- Focused API and UI verification

## Out of Scope

- Version history or moderation controls
- Field-level privacy segmentation changes
- Timeline/news/social ingestion
- Theme customization work
- External geocoding or polished GIS features
- Broad mobile redesign

## Implementation Order

1. Add a per-user preference model and persistence route.
2. Wire tree API and tree page to consume saved preferences.
3. Add server-backed filters for the supported person attributes.
4. Add authenticated map data output using existing location fields.
5. Add a simple map page that proves the route and visibility model work.
6. Add focused tests and browser evidence.

## Proof Obligations

- Preferences are stored per account, not globally.
- Filtered tree results are deterministic and based on persisted fields.
- Map endpoints are authenticated and do not leak hidden or unauthorized records.
- Tree and map behavior remain aligned with the flat-family collaboration contract from Sprint 01.

## Risks To Watch

- Preference persistence implemented only in browser storage instead of server state
- Cosmetic filters that do not change actual tree data
- Map output blocked by missing or inconsistent location data
- Scope creep into version history, privacy redesign, or visual polish work

## Exit Target

Sprint 02 is complete when Family Book moves from “shared but hard to navigate” to “shared and practically explorable” for everyday family members.
