# Sprint Plan - S04 Version History, Revert, and Moderation Controls

## Sprint

- Name: `S04 - Version History, Revert, and Moderation Controls`
- Status: Planned
- Primary packet: `FB-007 Version History, Revert, and Moderation Controls`

## Sprint Goal

Make broad family collaboration trustworthy by adding inspectable edit history, reversible recovery for core shared records, and narrow admin moderation controls for problematic content.

## Why This Sprint

Family Book now has working shared editing, discovery, and timeline authoring. That means mistakes are no longer hypothetical. Without revision history and recovery, the app still depends on trust in careful behavior rather than trust in the software itself.

## Must-Have Outcomes

- Core collaborative entities have real revision history, not just coarse audit logs.
- Destructive or mistaken changes in launch scope can be recovered through supported app behavior.
- Admins can moderate problematic shared content without manual database work.
- History, revert, and moderation behavior align with the flat-family collaboration model.

## Acceptance Criteria

1. Supported person and moment edits generate persisted revision history with actor and timestamp context.
2. An authorized user can inspect recent history for supported entities in a supported UI or API path.
3. An admin can revert a supported person change and a supported moment change through the app.
4. Supported destructive mistakes become recoverable without direct database intervention.
5. Moderated content in launch scope is suppressed consistently from supported member-facing surfaces.
6. Focused tests and browser evidence prove history and recovery behavior across at least two authenticated users.

## In Scope

- revision history for supported collaborative entities
- history inspection surfaces or APIs
- revert/restore for people and moments
- recoverable delete semantics where required for launch scope
- light admin moderation controls for supported shared content
- focused tests and Playwright/browser evidence

## Out of Scope

- role redesign or fine-grained access segmentation
- encryption and backup hardening
- approval queues or editorial workflow
- generalized revert across every entity in the repo
- theme or brand customization

## Implementation Order

1. Execute Slice 1: revision capture and history retrieval foundation.
2. Execute Slice 2: revert and recoverable-delete flows for supported entities.
3. Execute Slice 3: admin moderation controls on supported shared-content surfaces.
4. Validate the combined sprint outcomes with focused tests plus browser evidence.

## Execution Slices

### Slice 1 - Revision Capture and History Retrieval

- Goal:
  create a truthful persisted history layer for core collaborative edits
- Scope:
  revision model, storage, retrieval APIs, and minimal history surfaces
- Must prove:
  history survives create/update cycles and is not just derived from template state
- Suggested acceptance checks:
  person and moment edits produce retrievable history entries
  history includes actor and temporal context

### Slice 2 - Revert and Recoverable Delete

- Goal:
  turn mistakes into recoverable app behavior instead of irreversible mutations
- Scope:
  revert paths for supported entities, soft-delete or restore semantics where needed
- Must prove:
  an admin can restore a supported prior state without direct database edits
- Suggested acceptance checks:
  reverting a person change restores visible profile data
  reverting or restoring a moment changes home/person timeline state correctly

### Slice 3 - Moderation Controls for Shared Content

- Goal:
  give admins a narrow, launch-grade way to suppress and restore problematic shared content
- Scope:
  moderation state, admin controls, and consistent member-surface enforcement
- Must prove:
  moderated content is consistently removed from supported member-facing surfaces and can be restored
- Suggested acceptance checks:
  moderated moments disappear from home/person feeds
  restored content reappears without data loss

## Proof Obligations

- History must be persisted and recoverable, not merely displayed.
- Revert behavior must change the live runtime state of the app.
- Moderation semantics must be enforced by supported APIs, not only templates.
- Sprint scope must stay away from encryption, permissions redesign, and workflow approvals.

## Risks To Watch

- “Version history” collapsing into audit-log cosmetics
- Revert paths that restore one record but leave related surfaces inconsistent
- Moderation flags that hide cards in one surface but leak content elsewhere
- Soft-delete behavior breaking timeline ordering, tree integrity, or tagged references

## Exit Target

Sprint 04 is complete when Family Book supports core collaborative editing with a credible safety net: members can inspect what changed, admins can recover from mistakes, and problematic shared content can be suppressed and restored without database surgery.
