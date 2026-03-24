# Family Book Collaboration and Privacy Contract

## Purpose

Define the launch rules for who can see what, who can change what, and how sensitive data is handled.

## Roles

### Admin

Can:

- invite people by email
- link accounts to person records
- edit or disable accounts
- configure app-level settings
- inspect audit history
- moderate or remove problematic content

### Family member

Can:

- view shared family content
- create and edit people, stories, notes, relationships, and media
- update shared records collaboratively
- use tree, timeline, person, and map surfaces

## Launch Access Model

Family Book launch uses **flat shared access** within the authenticated family boundary.

That means:

- active family members can view all shared people
- active family members can view all shared media
- active family members can create and edit shared content
- the boundary is membership in the family space, not graph distance

## Sensitive Data Policy

The current launch assumption is:

- contact information is shared to active family members
- medical history is shared to active family members

This is intentionally simple and matches the collaborative family-wiki direction. Because it increases sensitivity, the system must also provide:

- strong invite/account controls
- audit history for major mutations
- soft-delete or recoverable-change behavior where practical
- encryption in transit and at rest

## Privacy Boundary

The privacy boundary is:

- authenticated,
- invited,
- active family membership.

The product should not rely on hidden relationship-distance rules to decide visibility for launch.

## Editing and Integrity Rules

- Shared content is editable by family members.
- Important mutations should be auditable.
- Destructive actions should be reversible where practical.
- Later moderation/version-history work is expected once broad collaboration is live.

## Non-Member Access

- No anonymous access
- No public media URLs
- No guest viewing in launch scope

## Product Implications

The following current patterns do not fit the launch contract and should be treated as migration targets:

- graph-distance gating for viewing people
- graph-distance gating for media visibility
- admin-only creation flows for normal family content
- product copy that implies collaboration while runtime behavior hides shared data
