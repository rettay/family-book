# Task Packet - FB-112 Managed Hosting Environment Baseline

Status: Proposed

## Objective

Document and, where practical, script a first managed-hosting baseline for paid pilot archives.

## Why / KPI

The business needs a repeatable way to host real customers before deciding on a full SaaS control plane. The baseline should be boring, isolated, and restorable.

## Scope

- In scope:
  - choose the first operator-supported hosting baseline after `FB-109`
  - document staging, pilot, and production archive environments
  - TLS, trusted hosts, SMTP, passkeys, secrets, persistent storage, backups, restore verification, log access, and custom domain assumptions
  - optional AWS path with ECS/Fargate+EFS or EC2/Lightsail-style single archive
  - Railway/Render continuation path if retained
- Out of scope:
  - full IaC automation for every provider
  - pooled multi-tenant control plane
  - high availability beyond what is required for first paid pilot

## Likely Files

- `docs/ops/managed-hosting-baseline.md`
- `docs/ops/staging-env-vars.md`
- `.env.production.example`
- `.env.hosted-archive.example`

## Acceptance Criteria

- [ ] Operator can provision a paid pilot archive from documented steps.
- [ ] Baseline includes backup and restore verification before launch.
- [ ] Baseline includes domain/TLS/passkey origin requirements.
- [ ] Baseline states where logs live and how support should access them.
- [ ] Baseline calls out unsupported hosting shapes for the current SQLite/media architecture.

## Validation Commands

- `git diff --check`

## Definition of Done

- [ ] Hosting baseline is accepted as enough for first paid pilots or explicitly rejected with replacement path.
