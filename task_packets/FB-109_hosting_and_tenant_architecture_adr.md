# Task Packet - FB-109 Hosting and Tenant Architecture ADR

Status: Proposed

## Objective

Write the architecture decision record for first paid hosting: managed single-tenant archives, pooled multi-tenant SaaS, or staged hybrid.

## Why / KPI

The current app is built around one SQLite database and media directory. Paid hosting cannot be planned responsibly until tenant isolation, backups, secrets, cost, provisioning, and support boundaries are explicit.

## Scope

- In scope:
  - compare single-tenant managed archives, pooled multi-tenant SaaS, and "published image only"
  - decide first paid-hosting architecture
  - document migration path if future pooled multi-tenancy is desired
  - identify impacted components: DB, media, backups, Fernet keys, sessions, SMTP, passkeys, inbound email, Matrix bridges, custom domains, observability
  - include AWS option notes: ECS/Fargate + EFS or EC2/Lightsail-style for current SQLite/media; App Runner only after moving durable state out of local filesystem
- Out of scope:
  - implementing tenant provisioning
  - cloud price optimization
  - Terraform/CDK production implementation

## Likely Files

- `docs/ops/hosting-and-tenant-architecture-adr.md`
- `docs/ops/hosting-environment-options.md`
- `docs/strategy/commercialization-sprint-plan-2026.md`

## Acceptance Criteria

- [ ] ADR has a clear decision, alternatives, consequences, and rollback/migration implications.
- [ ] ADR explicitly states whether first paid hosted archives are single-tenant or pooled.
- [ ] ADR includes tenant isolation boundaries for database, media, backups, secrets, logs, support, export, and deletion.
- [ ] ADR explains why "just publish an image on AWS" is or is not sufficient for paid hosting.
- [ ] ADR includes a future path to pooled multi-tenancy if not chosen now.
- [ ] Docs include references to official provider docs used for assumptions.

## Validation Commands

- `git diff --check`

## Definition of Done

- [ ] ADR reviewed and accepted by the product owner.
- [ ] Follow-up packets updated if the decision changes scope.
