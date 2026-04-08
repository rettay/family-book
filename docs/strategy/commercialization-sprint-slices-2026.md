# Commercialization Sprint Slices - 2026

Plan date: April 7, 2026

## Slice Order

1. `S47 Hosting and Tenant Architecture`
2. `S48 Privacy and Exit Trust`
3. `S49 Paid Hosted Platform`
4. `S50 Activation and Migration`
5. `S51 Lovable Engagement`
6. `S52 Launch Readiness and Growth`

## `S47-1 Hosting/Tenant ADR`

Goal: decide whether first paid hosting is single-tenant managed archives, pooled multi-tenant SaaS, or a staged hybrid.

Packets: `FB-109`

Acceptance checks:

- ADR includes decision, alternatives, rejected options, and migration implications.
- ADR explicitly covers SQLite, media files, backups, Fernet keys, admin support, tenant deletion/export, and cost/ops tradeoffs.
- ADR does not allow shared app/database/media state without a tenant isolation plan.

## `S47-2 Production Container Contract`

Goal: make the image deployable as a supported product artifact.

Packets: `FB-110`

Acceptance checks:

- Runtime env vars, required secrets, data mount, health check, migrations, startup, and rollback behavior are documented and tested.
- Image can boot with production-safe defaults and no dev bypass.
- Release artifact is versioned and can be promoted between environments.

## `S47-3 Tenant Data Boundary`

Goal: define and test the boundary around each family archive.

Packets: `FB-111`

Acceptance checks:

- Tenant data inventory covers database, media, thumbnails, backups, logs, sessions, secrets, inbound email, Matrix bridge data, exports, and deletion.
- Single-tenant and future pooled-tenant paths are both represented.
- Boundary tests or fixtures prove no cross-archive path traversal or backup/export mix-up.

## `S47-4 Managed Hosting Baseline`

Goal: produce a reproducible first hosted environment.

Packets: `FB-112`

Acceptance checks:

- Operator can provision a staging and paid-pilot archive from documented steps.
- Backup, restore verification, TLS, trusted hosts, SMTP, passkeys, and custom domain assumptions are explicit.
- Known AWS/Railway/Render tradeoffs are recorded without locking the business into one provider prematurely.

## `S48-1 Permission Model`

Goal: fix the current privacy trust blocker.

Packets: `FB-113`

Acceptance checks:

- Current broad non-admin manage rights are replaced or explicitly scoped.
- Graph-distance visibility is implemented if retained in product copy.
- Tests prove distant/non-admin users cannot view contacts or edit profiles outside policy.

## `S48-2 Sensitive Data Defaults`

Goal: make sensitive profile fields safe by default.

Packets: `FB-114`

Acceptance checks:

- Contact, medical, genetic, minor, and private media defaults are explicit.
- Consent and disclosure copy is visible before inviting relatives.
- Export and admin views do not accidentally expose encrypted or private fields.

## `S48-3 Exitability`

Goal: make "you own your data" operationally true.

Packets: `FB-115`

Acceptance checks:

- Archive export includes GEDCOM, media, stories, wiki sections, and manifest.
- Export can run from admin UI and CLI/operator path.
- Tests cover private-field handling and restore/import expectations.

## `S48-4 Trust Center`

Goal: make the privacy/security model understandable to buyers.

Packets: `FB-116`

Acceptance checks:

- Public docs state what is encrypted, what is not, how backups work, and how deletion/export work.
- Unsupported claims are removed from product copy.
- Terms/privacy drafts are sufficient for a paid beta.

## `S49-1 Tenant Provisioning`

Goal: support creating and managing hosted family archives.

Packets: `FB-117`

Acceptance checks:

- Operator can create, suspend, reactivate, and delete an archive.
- Archive state is auditable.
- Provisioning does not require hand-editing a live database.

## `S49-2 Billing`

Goal: map paid plan state to product access.

Packets: `FB-118`

Acceptance checks:

- Stripe checkout/customer/subscription webhooks update plan state.
- Past-due/canceled/suspended states degrade safely without deleting data.
- Self-hosted users are not forced through hosted billing.

## `S49-3 Storage Quotas`

Goal: protect hosting costs and make upgrades understandable.

Packets: `FB-119`

Acceptance checks:

- Storage usage is computed per archive.
- Uploads enforce per-plan limits with graceful copy.
- Admin/operator views expose usage without showing private media contents.

## `S50-1 First-Run Activation`

Goal: get a family steward to first value in one session.

Packets: `FB-120`

Acceptance checks:

- Wizard guides create archive, add self, add close relatives, import GEDCOM or skip, upload first media, and invite one person.
- Progress is resumable.
- Activation events are tracked without collecting sensitive content.

## `S50-2 Migration Assistant`

Goal: make existing genealogy users successful after GEDCOM import.

Packets: `FB-121`

Acceptance checks:

- Preview/import flow exposes duplicates, missing dates, unknown people, unlinked families, and next cleanup steps.
- Import batch details remain reviewable.
- User can undo or quarantine failed import output.

## `S50-3 Invite Contribution Flow`

Goal: help invitees contribute safely.

Packets: `FB-122`

Acceptance checks:

- Invite page explains role and visibility.
- First contribution prompt is contextual: confirm profile, add photo, answer story prompt, or add missing relationship.
- Admin/steward can review high-risk edits if policy requires it.

## `S50-4 PWA Share Inbox`

Goal: turn mobile sharing into archive value.

Packets: `FB-123`

Acceptance checks:

- Share target creates inbox items, not orphan files.
- Inbox items can be attached to people, tagged, captioned, and deleted.
- Upload progress and failure states work on mobile.

## `S51-1 Prompts and Digest`

Goal: create a reason to return.

Packets: `FB-124`

Acceptance checks:

- Steward can send prompt campaigns.
- Weekly digest summarizes new stories, media, birthdays, anniversaries, and unanswered prompts.
- Email content never leaks private archive details to unauthorized recipients.

## `S51-2 Media Discovery`

Goal: make the archive enjoyable to browse.

Packets: `FB-125`

Acceptance checks:

- Media search covers person, date, title, caption, description, and album.
- Albums/collections work across people.
- Timeline and gallery browsing remain fast with realistic media counts.

## `S51-3 Family Book Export`

Goal: produce a giftable outcome.

Packets: `FB-126`

Acceptance checks:

- User can generate a PDF/Markdown family-book draft from selected people, stories, and media.
- Output includes provenance and respects visibility choices.
- Export has a clear path to future print fulfillment.

## `S52-1 Launch Pages`

Goal: prepare acquisition and paid conversion surfaces.

Packets: `FB-127`

Acceptance checks:

- Landing/pricing/waitlist pages communicate hosted vs self-hosted clearly.
- Comparison pages avoid record/DNA overclaims.
- Analytics capture funnel events.

## `S52-2 Beta Operations`

Goal: operate the first paid customers without chaos.

Packets: `FB-128`

Acceptance checks:

- Support playbook covers login, invite, billing, export, restore, and deletion.
- Feedback/interview loop is documented.
- Refund/cancellation process is defined.

## `S52-3 Production Readiness Gate`

Goal: prevent launching a brittle or unsafe paid app.

Packets: `FB-129`

Acceptance checks:

- Release checklist covers tests, migrations, backup restore, access-control probes, rate limits, logging, privacy copy, and rollback.
- Load/performance smoke is run against realistic media/tree sizes.
- Security review focuses on tenant isolation, auth, uploads, export, and admin paths.
