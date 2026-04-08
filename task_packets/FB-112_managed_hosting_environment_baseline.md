# Task Packet - FB-112 Managed Hosting Environment Baseline

Status: Done

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

- [x] Operator can provision a paid pilot archive from documented steps.
- [x] Baseline includes backup and restore verification before launch.
- [x] Baseline includes domain/TLS/passkey origin requirements.
- [x] Baseline states where logs live and how support should access them.
- [x] Baseline calls out unsupported hosting shapes for the current SQLite/media architecture.

## Validation Commands

- `git diff --check`

## Definition of Done

- [x] Hosting baseline is accepted as enough for first paid pilots or explicitly rejected with replacement path.

## Builder Evidence

- Deliverable: `docs/ops/managed-hosting-baseline.md`.
- Supporting env examples: `.env.production.example`, `.env.hosted-archive.example`, `.env.staging.example`.
- Staging reference updated to current SMTP flow: `docs/ops/staging-env-vars.md`.
- Baseline explicitly supports managed single-tenant pilot archives and rejects pooled shared-data hosting for first paid pilots.
