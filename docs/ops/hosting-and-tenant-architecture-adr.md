# Hosting And Tenant Architecture ADR

Status: Accepted for first paid-hosting pilot

Date: 2026-04-08

## Decision

Family Book will launch paid hosting as managed single-tenant family archives.

Each paying archive gets:

- one isolated application runtime
- one SQLite database file
- one media and variants directory tree
- one backup scope
- one Fernet key
- one admin owner group
- one operator support boundary

Pooled multi-tenant SaaS is explicitly deferred until the data model, storage model, provisioning model, and support model are redesigned for tenant identity from first principles.

## Context

The current application is not a stateless multi-tenant web app. It assumes one archive-shaped data root:

- SQLite database path derived from `DATABASE_URL`
- `DATA_DIR` for media, variants, and backups
- restore and download archives built from one database plus one media tree
- one `FERNET_KEY` used for protected person fields
- one SMTP identity and one passkey/WebAuthn relying-party origin per deployment
- one optional Matrix bot identity and room binding per deployment

That shape is commercially workable for early paid hosting if each customer archive is isolated at the runtime and storage layer. It is not safe to pool customers into one runtime and filesystem without redesigning tenant identity, support access, export/delete behavior, and backup boundaries.

## Why This Decision

### Strengths of managed single-tenant archives

- Fits the current architecture instead of fighting it.
- Keeps database, media, backups, and secrets naturally isolated.
- Makes support, restore, export, and deletion easier to reason about.
- Produces a simpler trust story for living-family data.
- Lets the business start paid pilots without first building a SaaS control plane.

### Why pooled multi-tenancy is rejected for now

- Current backup/export flows operate on one archive at a time, not tenant-scoped rows.
- Current storage paths do not include a tenant identifier.
- Current runtime secrets are process-wide, not tenant-scoped.
- Support tooling and logs are deployment-scoped, not tenant-aware.
- A pooled architecture would require tenant-aware authorization, rate limiting, billing entitlements, job isolation, and operational tooling.

### Why "publish an image on AWS" is not enough

Publishing a container image is only the packaging step. Paid hosting also needs:

- persistent storage for SQLite, media, variants, backups, and exports
- secret management
- TLS and trusted-host configuration
- backup scheduling and restore verification
- SMTP and passkey origin configuration
- logs and support access conventions
- archive delete and export procedures

Without those pieces, an image is not an operating model.

## Options Considered

### Option A: Managed single-tenant archives

Decision: accepted

Shape:

- one deployment per family archive
- one mounted persistent volume per archive
- one SQLite database inside that archive volume
- one set of archive-specific secrets

Operational impact:

- higher per-archive infrastructure cost than pooled SaaS
- lower isolation complexity
- easier first restore and support workflows

### Option B: Pooled multi-tenant SaaS

Decision: rejected for first paid pilot

Would require:

- tenant identity in every durable data path
- tenant-aware backup and export isolation
- tenant-aware admin/support tooling
- tenant-aware billing and provisioning
- media/object storage partitioning
- database migration away from one-file SQLite assumptions

### Option C: Publish a self-host image only

Decision: rejected as the primary paid-hosting path

This remains valid for self-hosting, but it does not solve hosted operations, support, data recovery, or customer trust for a paid managed offer.

### Option D: Staged hybrid

Decision: implicit long-term path, not the first paid architecture

The staged path is:

1. launch managed single-tenant archives
2. standardize runtime and storage boundaries
3. learn operational cost and support patterns
4. revisit pooled services only after product-market fit and tenant-model redesign

## Tenant Isolation Boundary

The first paid hosted boundary is deployment-level isolation, not row-level isolation.

Archive boundary covers:

- database file
- media originals
- media variants and thumbnails
- backups
- export zip files
- restore-verification metadata
- process-wide secrets
- SMTP sender identity for that archive deployment
- passkey/WebAuthn relying-party origin for that archive domain
- Matrix bot credentials and room bindings for that archive deployment
- inbound email webhook secret and attachment downloads
- deployment logs and support access

See [tenant-data-boundary.md](/Users/cheech/code/family-book/docs/ops/tenant-data-boundary.md).

## Hosting Implications

Supported first-pilot shapes:

- Railway-style single service plus dedicated persistent volume
- Render-style web service plus persistent disk
- AWS ECS/Fargate plus EFS, or EC2/Lightsail-style single archive host

Unsupported first-pilot shape:

- pooled multi-tenant app runtime sharing one filesystem and database across multiple families

Conditional shape:

- App Runner or similar stateless container platforms only after durable state moves off local filesystem assumptions; this is an inference from the current Family Book storage contract, not a separate product decision.

See [hosting-environment-options.md](/Users/cheech/code/family-book/docs/ops/hosting-environment-options.md).

## Consequences

### Positive

- Fastest credible path to paid hosting
- Stronger customer trust story
- Lower accidental cross-family data leakage risk
- Restore and deletion are simpler to audit

### Negative

- Higher per-family hosting cost
- More deployments to operate
- Slower path to commodity SaaS margins

## Rollback And Migration Implications

If this decision fails commercially, the archive remains exportable and self-hostable.

If pooled SaaS is revisited later, migration work must include:

- tenant identifier strategy across all durable records
- database/storage migration design
- per-tenant backup, export, delete, and restore semantics
- per-tenant secret strategy or envelope-encryption strategy
- support and observability model that avoids reading customer content casually
- billing and provisioning controls

## References

- [AWS SaaS Tenant Isolation Strategies](https://docs.aws.amazon.com/whitepapers/latest/saas-tenant-isolation-strategies/saas-tenant-isolation-strategies.html)
- [Amazon ECS EFS volumes](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/efs-volumes.html)
- [Railway volumes guide](https://docs.railway.com/guides/volumes)
- [Render persistent disks](https://render.com/docs/disks)
