# Sprint Plan - S50 Activation and Migration

## Sprint

- Name: `S50 - Activation and Migration`
- Status: Planned
- Primary packet: `FB-120 Onboarding Activation Wizard`
- Core supporting packets:
  - `FB-121 GEDCOM Migration Assistant`
  - `FB-122 Invite Visibility and Contribution Flow`
- Stretch packet:
  - `FB-123 PWA Share Inbox and Media Attachment`

## Sprint Goal

Make the first 15 minutes of a hosted archive feel successful enough that a new paying family steward can reach visible value, trust the migration path, and bring in at least one relative.

## PM Recommendation

Treat `FB-120`, `FB-121`, and `FB-122` as the hard commitment. Treat `FB-123` as stretch unless `FB-120` and `FB-121` land cleanly and early.

Rationale:

- Activation and migration are the direct conversion bottlenecks for the first paid hosted users.
- Invite understanding matters in the same session because "I got someone else in" is a strong activation signal.
- The PWA share inbox is valuable, but it is secondary to first-run onboarding, import trust, and invite handoff.
- `FB-123` can sprawl into media workflow design if it is treated as equal priority too early.

## Why This Sprint

`S49` made Family Book sellable as a hosted product, but not yet easy to adopt:

- a new steward still needs a guided first-run path
- GEDCOM import still feels like a raw tool rather than a safe migration experience
- invitees still need clearer role and contribution framing
- mobile share capture still does not produce a structured intake workflow

Without this sprint, early paid pilots will have billing and hosting but too much activation friction.

## Must-Have Outcomes

- A new hosted archive owner can get to first value in a single session.
- Manual start and GEDCOM start are both supported in the first-run flow.
- Imported archives produce a reviewable migration summary and cleanup checklist.
- Invitees understand what they can see, what they can edit, and what to do first.

## Stretch Outcomes

- Mobile share target creates reviewable inbox items instead of loose media files.
- Activation flow captures meaningful milestone telemetry without storing sensitive content.
- Import follow-up links land users directly in the right cleanup surfaces.

## Acceptance Criteria

1. New hosted archive owners are routed into onboarding until they complete or explicitly skip it.
2. Onboarding is resumable and records milestone completion server-side.
3. Onboarding supports both manual family setup and GEDCOM import entry points.
4. GEDCOM import results are reviewable after the upload, not only during parsing.
5. Import summary clearly surfaces duplicates, unsupported fields, missing key data, and next cleanup steps.
6. Invite claim flow explains role and visibility before the user enters the archive.
7. Invitees land in a role-aware first contribution state after claiming an invite.
8. Activation and invite events are auditable without logging private family content.
9. If `FB-123` lands, the PWA share target creates structured inbox items that can be reviewed, attached, or rejected.

## In Scope

- First-run onboarding state, routes, templates, and resume behavior
- Hosted activation milestone tracking
- GEDCOM post-import review and cleanup workflow
- Invite explanation and role-aware first contribution landing
- PWA share inbox if capacity remains after core activation work
- Tests across onboarding, import, invite, and selected browser flows

## Out of Scope

- Billing checkout redesign
- AI-assisted import cleanup
- Full tutorial or product-tour system
- Native mobile app
- Automatic source matching after GEDCOM import
- Bulk third-party media import connectors

## Implementation Order

1. Execute `FB-120` first because it defines the entry path for every new hosted archive.
2. Execute `FB-121` second because import trust is the highest-friction path for likely early adopters.
3. Execute `FB-122` third so activation ends with a safe, understandable handoff to another relative.
4. Execute `FB-123` only after the core activation/import/invite loop is stable.
5. Keep the unresolved `FB-110` image-build verification visible as an ops follow-up, but do not let it block `S50`.

## Proof Obligations

- A new hosted archive can reach an observable activation milestone without operator intervention.
- A GEDCOM user can understand what imported cleanly and what still needs attention.
- Invitees are not dropped into the archive without role or visibility context.
- Activation analytics do not store private profile, story, or media content.
- Any stretch share-inbox flow produces structured archive value rather than orphan files.

## Risks To Watch

- Onboarding can become too long or tutorial-heavy; keep it focused on first value.
- Import review can become a full data-cleaning subsystem; prioritize summary and safe next actions.
- Invite handoff can be weakened by the newer role/privacy model if prompts are not role-aware.
- `FB-123` can consume disproportionate time if mobile upload and media review UX are not tightly bounded.

## Exit Target

Sprint S50 is complete when a new hosted archive can get from signup to first useful family activity with materially less confusion, and an imported archive no longer feels unsafe or opaque.
