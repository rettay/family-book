# Sprint Plan - S48 Privacy and Exit Trust

## Sprint

- Name: `S48 - Privacy and Exit Trust`
- Status: Planned
- Primary packet: `FB-113 Role and Graph-Distance Privacy Model`
- Core supporting packets:
  - `FB-114 Private Sensitive Fields and Consent Controls`
  - `FB-115 Archive Export and GEDCOM Export`
- Dependent / trust-packaging packet:
  - `FB-116 Paid Launch Trust Center`

## Sprint Goal

Make Family Book's privacy, visibility, and exitability claims true enough to support a paid beta without hand-waving around sensitive living-family data.

## PM Recommendation

Treat `FB-113`, `FB-114`, and `FB-115` as the hard commitment. Treat `FB-116` as required for closeout only after the underlying permission and export behavior is implemented.

Rationale:

- The biggest remaining commercialization risk is a mismatch between the product's privacy story and the actual permission model.
- Public trust docs are only useful if they describe real enforcement, not future intent.
- Export and deletion credibility are part of the product wedge, not post-launch polish.

## Why This Sprint

`S47` established the hosting shape, but the product still has trust blockers:

- non-admin permissions are too broad for a privacy-first archive
- sensitive fields need explicit conservative defaults
- exitability is not yet operationally true
- public trust copy can still drift from implementation

Without this sprint, hosted paid pilots would rely on a privacy promise that is not yet defensible.

## Must-Have Outcomes

- Non-admin members cannot broadly edit every visible active person.
- Contact, medical, genetic, minor, and private-media visibility rules are explicit and enforced.
- Archive export and GEDCOM export exist through admin and operator paths.
- Product copy, README language, and trust docs no longer imply unsupported privacy guarantees.

## Stretch Outcomes

- Steward role or similar mid-tier moderation role is implemented cleanly if it proves necessary.
- Invite copy is improved enough that a new invitee can understand what they can see before joining.
- Export docs include a practical restore/import expectation note, not only file-format details.

## Acceptance Criteria

1. Active non-admin members cannot edit every visible active person.
2. Contact fields are visible only according to explicit policy.
3. Medical/genetic fields are hidden unless policy permits.
4. Minor-related defaults are conservative for profile visibility and media visibility.
5. Graph-distance privacy is either implemented and tested or removed from any product copy that promises it.
6. Admin can download a GEDCOM export and a full archive export.
7. Export behavior for sensitive fields is explicit and tested.
8. Public trust docs distinguish field-level encryption, authenticated media access, backups, transport security, export, and deletion.
9. No public copy claims end-to-end encryption or zero-knowledge storage unless implemented.
10. Invite/admin flows still work after the permission changes.

## In Scope

- Access-control model redesign and enforcement
- Sensitive field defaults and auditability
- Export services and admin/operator export paths
- Trust-center and README/landing/privacy copy alignment
- Tests across API, HTML, media, and export flows

## Out of Scope

- Tenant provisioning
- Billing and Stripe
- Legal review or final terms drafting
- Client-side encryption redesign
- HIPAA/compliance positioning
- Native mobile work

## Implementation Order

1. Execute `FB-113` first because the permission model sets the boundary for every other trust claim.
2. Execute `FB-114` next to make sensitive-field defaults and UI disclosure match the new permission model.
3. Execute `FB-115` after the permission model is stable so export behavior can explicitly define what admins can leave with.
4. Execute `FB-116` last so the public trust copy matches implemented behavior rather than roadmap intent.
5. Keep the unresolved `FB-110` image-build verification as a tracked follow-up, but do not let it block `S48` execution.

## Proof Obligations

- A non-admin user must be unable to use existing UI/API paths to edit or view data outside the new policy.
- Sensitive fields must be redacted consistently in both API and HTML paths.
- Export must preserve ownership portability without silently leaking hidden/private data to unauthorized users.
- Trust docs must match the actual permission and storage model from `S47` and `S48`.
- Any retained graph-distance promise must be proven in tests, not only described in docs.

## Risks To Watch

- Permission changes can easily break legitimate family contribution flows if the role model is too restrictive.
- Export can accidentally become an admin-only dump that ignores private-field nuance or undocumented omissions.
- Trust docs can drift again if they are written before implementation settles.
- Mid-sprint role-model expansion can sprawl into moderation tooling; keep the first version simple.

## Exit Target

Sprint S48 is complete when Family Book's privacy promise, sensitive-data behavior, and exit story are strong enough to support a paid beta without misleading users.
