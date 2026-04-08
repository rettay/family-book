# Sprint Plan - S47 Hosting and Tenant Architecture

## Sprint

- Name: `S47 - Hosting and Tenant Architecture`
- Status: Planned
- Primary packet: `FB-109 Hosting and Tenant Architecture ADR`
- Core supporting packets:
  - `FB-111 Tenant Data Boundary and Storage Model`
  - `FB-110 Production Container Runtime Contract`
- Stretch / dependent packet:
  - `FB-112 Managed Hosting Environment Baseline`

## Sprint Goal

Decide the first paid-hosting shape and make the production runtime and tenant data boundary explicit enough to safely host the first paid pilot archives.

## PM Recommendation

Default to managed single-tenant family archives unless `FB-109` finds a clear reason not to.

Rationale:

- The current product shape is naturally one archive: one SQLite database, one media tree, one backup scope, and one set of secrets.
- Living-family data has high trust and privacy sensitivity, so tenant isolation must be structurally simple for the first paid version.
- Pooled multi-tenant SaaS can be a later redesign after the product proves demand and the tenant model is intentionally rebuilt.
- "Publish an image on AWS" is not enough by itself because the paid product also needs persistent storage, backups, restore verification, secrets, domains, email, logs, and an operator support model.

## Why This Sprint

The commercialization roadmap cannot move to billing, provisioning, or growth until the hosting model is chosen. Without this sprint, later work risks optimizing around the wrong architecture or accidentally creating weak multi-tenancy around sensitive family data.

## Must-Have Outcomes

- ADR chooses the first hosted architecture: managed single-tenant, pooled multi-tenant, or staged hybrid.
- Tenant data inventory covers database, media, variants, backups, exports, logs, sessions, tokens, secrets, inbound email, Matrix bridge data, and deletion/export behavior.
- Production container/runtime contract documents required environment variables, secrets, data mounts, health checks, startup/migration behavior, and rollback expectations.
- Follow-up scope for `S48` to `S49` is updated if the ADR changes the commercialization path.

## Stretch Outcomes

- A first managed-hosting baseline is documented for staging and one paid pilot archive.
- Provider tradeoffs are captured for current Railway/Render-style operation and AWS options such as ECS/Fargate plus EFS or EC2/Lightsail-style single-archive hosting.
- `.env` examples are updated only if the runtime contract discovers clear production gaps.

## Acceptance Criteria

1. ADR exists at `docs/ops/hosting-and-tenant-architecture-adr.md` with decision, alternatives, consequences, rollback/migration implications, and provider references.
2. ADR explicitly explains why a raw published container image is not sufficient for paid hosting without an operating model.
3. ADR includes a future path to pooled multi-tenancy if it is not chosen now.
4. Tenant boundary doc exists at `docs/ops/tenant-data-boundary.md` and is linked from the ADR.
5. Every durable data class has an owner, path/table, retention rule, and export/delete behavior.
6. Runtime contract exists at `docs/ops/production-container-runtime.md` and documents required env vars, secrets, volumes, health checks, startup, migration, release tagging, and rollback.
7. Production docs make dev bypass, demo seed, and missing production secrets fail-closed or clearly unsupported.
8. Managed-hosting baseline exists at `docs/ops/managed-hosting-baseline.md` if `FB-112` is pulled into the sprint.
9. Sprint closeout explicitly states which hosting option was chosen and which later commercialization packets need updates.

## In Scope

- Hosting architecture ADR
- Tenant boundary and storage model
- Production container runtime contract
- Current deployment and ops docs review
- Minimal tests or config checks needed to make runtime assumptions enforceable
- Managed hosting baseline if the ADR is settled early enough

## Out of Scope

- Stripe billing
- Tenant provisioning control plane
- Pooled multi-tenant implementation
- Full Terraform/CDK implementation
- Postgres migration
- Object-storage migration
- High-availability architecture beyond first paid pilot needs
- New public launch/marketing pages

## Implementation Order

1. Execute `FB-109` first to settle the hosting decision.
2. Execute `FB-111` immediately after or in parallel with `FB-109` because the data inventory is an input to the ADR.
3. Execute `FB-110` after the ADR has chosen the production runtime shape.
4. Pull in `FB-112` only after the ADR and runtime contract make the baseline concrete.
5. Update the commercialization plan only if the ADR changes the sprint sequence or packet scopes.

## Proof Obligations

- The chosen hosting model must have an explicit tenant-isolation story for database, media, backups, secrets, logs, email, export, deletion, and support access.
- The runtime contract must be concrete enough for a new operator to identify required env vars and persistent paths without reading application code.
- If any implementation changes are made, they must include focused tests or a documented reason they are docs-only.
- Provider assumptions must cite official docs where they materially affect the decision.
- The sprint must not mark pooled multi-tenancy as "future possible" unless the missing implementation boundaries are named.

## Risks To Watch

- Choosing provider details before tenant/data boundaries are clear.
- Treating single-tenant hosting as "no tenant work" when backups, logs, secrets, and support access still need boundaries.
- Overbuilding AWS-specific infrastructure before the first paid pilot requires it.
- Under-documenting rollback and restore, which are core trust requirements for a paid family archive.
- Letting environment examples drift from actual config behavior.

## Exit Target

Sprint S47 is complete when the hosting decision, tenant boundary, and production runtime contract are accepted as the basis for paid pilot hosting, with managed-hosting baseline work either completed or explicitly queued.
