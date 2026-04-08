# Commercialization Sprint Plan - Hosted and Sellable Family Book

Plan date: April 7, 2026

Purpose: turn the current self-hostable family archive into an application that can be hosted, paid for, operated, supported, and trusted by real customers.

Primary business target: 500 paying users by December 31, 2026.

## Product North Star

Family Book should become a private family archive for family stewards: a place to preserve a family tree, living-family details, photos, documents, and stories without handing that data to a record/DNA marketplace.

Do not compete directly with Ancestry or MyHeritage on record collections or DNA networks. Compete on privacy, ownership, low-friction family contribution, and emotional output.

## Hosting Strategy Recommendation

Short-term recommendation: launch paid hosting as managed single-tenant archives, not pooled multi-tenant SaaS.

Rationale:

- The current app assumes one SQLite database and one media directory under `DATA_DIR`.
- Tenant isolation is commercially important because family data includes living people, contact data, minors, medical/genetic fields, and private media.
- Single-tenant managed archives let us sell sooner while preserving strong isolation: one runtime, database file, media directory, backup scope, Fernet key, and admin owner per family archive.
- Pooled multi-tenancy can be a later redesign once product-market fit is validated.

Near-term hosting shape:

- Build and publish a production container image.
- Provision one isolated archive per paying family.
- For AWS, prefer ECS/Fargate plus EFS or EC2/Lightsail-style instances for the current SQLite+media architecture. App Runner can be evaluated only if database/media state moves to managed services such as Postgres and object storage.
- Continue Railway/Render-style single-instance hosting as an operator path while the SaaS hosting model is designed.

Decision gate:

- If we keep SQLite+filesystem for the first paid version, choose single-tenant managed hosting.
- If we choose pooled multi-tenant SaaS, first redesign tenant identity, database isolation, media key partitioning, backup/restore, billing entitlements, admin support, and deletion/export guarantees.

## Sprint Sequence

| Sprint | Name | Goal | Packets |
|---|---|---|---|
| S47 | Hosting and Tenant Architecture | Decide and implement the minimum production hosting contract without accidentally creating weak multi-tenancy. | `FB-109` to `FB-112` |
| S48 | Privacy and Exit Trust | Make privacy claims true, visible, and enforceable before charging customers. | `FB-113` to `FB-116` |
| S49 | Paid Hosted Platform | Add archive provisioning, billing, storage quotas, and operator support. | `FB-117` to `FB-119` |
| S50 | Activation and Migration | Let a new paying user reach first value quickly through onboarding, import, invites, and media capture. | `FB-120` to `FB-123` |
| S51 | Lovable Engagement | Add recurring prompts, better media discovery, and a giftable/exportable family-book output. | `FB-124` to `FB-126` |
| S52 | Launch Readiness and Growth | Add external launch surfaces, beta operations, and production readiness gates. | `FB-127` to `FB-129` |

## S47 - Hosting and Tenant Architecture

Sprint goal: make a tenant/hosting decision and ship the platform contract needed for a safe paid-hosting pilot.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 109 | FB-109 | Hosting and Tenant Architecture ADR | P0 |
| 110 | FB-110 | Production Container Runtime Contract | P0 |
| 111 | FB-111 | Tenant Data Boundary and Storage Model | P0 |
| 112 | FB-112 | Managed Hosting Environment Baseline | P1 |

Exit criteria:

- Architecture Decision Record chooses single-tenant managed archives, pooled multi-tenancy, or a staged hybrid, with explicit tradeoffs.
- The production image/runtime contract is documented and testable.
- Tenant data boundary is explicit for database, media, backups, secrets, logs, email domains, and restore/delete/export operations.
- A first managed-hosting environment can be provisioned reproducibly from docs or scripts.

## S48 - Privacy and Exit Trust

Sprint goal: remove trust blockers before asking users to pay.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 113 | FB-113 | Role and Graph-Distance Privacy Model | P0 |
| 114 | FB-114 | Private Sensitive Fields and Consent Controls | P0 |
| 115 | FB-115 | Archive Export and GEDCOM Export | P0 |
| 116 | FB-116 | Paid Launch Trust Center | P1 |

Exit criteria:

- README/marketing privacy claims match enforced behavior.
- Active non-admin members cannot broadly edit every visible person.
- Contacts, medical/genetic data, minors, private media, and deceased/living differences have understandable defaults.
- A paying customer can export the archive and leave.
- Public trust docs avoid unsupported "zero-knowledge" or "end-to-end encrypted" claims.

## S49 - Paid Hosted Platform

Sprint goal: support paid hosted archives without manual database surgery.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 117 | FB-117 | Tenant Provisioning and Operator Console | P0 |
| 118 | FB-118 | Stripe Billing and Plan Entitlements | P0 |
| 119 | FB-119 | Storage Quota Metering and Upgrade Controls | P1 |

Exit criteria:

- A new archive can be provisioned, suspended, reactivated, and deleted with an audit trail.
- Billing state maps to plan entitlements without leaking between archives.
- Storage usage can be measured and enforced before hosting costs become unbounded.
- Operator support can identify archive state without reading private family content.

## S50 - Activation and Migration

Sprint goal: make the first 15 minutes compelling enough for paid conversion.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 120 | FB-120 | Onboarding Activation Wizard | P0 |
| 121 | FB-121 | GEDCOM Migration Assistant | P0 |
| 122 | FB-122 | Invite Visibility and Contribution Flow | P1 |
| 123 | FB-123 | PWA Share Inbox and Media Attachment | P1 |

Exit criteria:

- New user can create an archive, add or import people, upload media, and invite a relative in under 15 minutes.
- GEDCOM import has a guided migration checklist and post-import cleanup tasks.
- Invitees can understand what they can see and contribute before entering the archive.
- PWA share target creates a real media inbox item that can be attached to a person.

## S51 - Lovable Engagement

Sprint goal: create recurring value beyond the initial tree import.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 124 | FB-124 | Family Prompt Campaigns and Digest | P0 |
| 125 | FB-125 | Media Search, Albums, and Timeline Delight | P1 |
| 126 | FB-126 | Family Book Export Foundation | P1 |

Exit criteria:

- Family stewards can send story/photo prompts and see responses.
- Weekly family digest gives relatives a reason to return.
- Media can be searched and grouped into albums or collections.
- Users can produce a shareable/exportable family-book draft.

## S52 - Launch Readiness and Growth

Sprint goal: run a paid beta and prepare public acquisition.

Committed packets:

| Order | ID | Title | Priority |
|---|---|---|---:|
| 127 | FB-127 | Launch Pages, Waitlist, and Positioning | P0 |
| 128 | FB-128 | Beta Operations, Support, and Metrics | P0 |
| 129 | FB-129 | Production Readiness Security and Performance Gate | P0 |

Exit criteria:

- Public pages describe the hosted and self-hosted offers without overclaiming.
- Beta cohort support, incident handling, refunds/cancellations, and feedback loops are documented.
- Production readiness gate covers privacy, backups, export, load, abuse, logging, and security headers.
- Launch can proceed without relying on undocumented operator knowledge.

## Explicit Non-Goals Before 500 Paying Users

- Building a proprietary record database.
- Building or brokering DNA matching.
- Full pooled multi-tenant redesign unless the S47 ADR explicitly chooses it.
- Native mobile app before PWA capture and digest loops prove demand.
- Family-office enterprise sales as the primary 2026 user-count path.
- Strong claims of end-to-end encryption or zero-knowledge storage unless client-side key architecture is implemented.

## Links and References

- Local market report: `docs/bizanalysis/family-book-market-comparison-roadmap-2026-04-07.md`
- Current release flow: `docs/ops/railway-release-flow.md`
- Current protection contract: `docs/ops/protection-and-backup-contract.md`
- AWS SaaS tenant isolation strategy reference: https://docs.aws.amazon.com/whitepapers/latest/saas-tenant-isolation-strategies/saas-tenant-isolation-strategies.html
- AWS ECS + EFS volume reference for stateful container storage: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/efs-volumes.html
