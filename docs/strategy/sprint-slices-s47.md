# Sprint Slices - S47 Hosting and Tenant Architecture

## Slice Order

1. `S47-1 Hosting Decision Inputs`
2. `S47-2 Hosting and Tenant ADR`
3. `S47-3 Tenant Data Boundary`
4. `S47-4 Production Container Runtime Contract`
5. `S47-5 Managed Hosting Baseline` (dependent)
6. `S47-6 Closeout and Commercialization Backlog Update`

## `S47-1 Hosting Decision Inputs`

### Goal

Build the factual inventory needed to make a defensible hosting decision.

### Scope

- review current deployment and release docs
- identify current runtime assumptions around SQLite, media, backups, Fernet, SMTP, passkeys, inbound email, Matrix, and custom domains
- identify which assumptions are safe for single-tenant hosting and unsafe for pooled multi-tenancy
- collect official provider references only where they influence the decision

### Acceptance Checks

- ADR draft has an inventory section before the decision is finalized.
- Decision inputs cover data, secrets, support, backups, restore, delete, export, and cost/ops tradeoffs.
- No provider is selected solely because it is convenient before the data boundary is understood.

## `S47-2 Hosting and Tenant ADR`

### Goal

Choose the first paid-hosting architecture.

### Packets

- `FB-109`

### Scope

- compare managed single-tenant archives, pooled multi-tenant SaaS, staged hybrid, and image-only publishing
- document decision, alternatives, consequences, migration path, and rollback implications
- explain AWS/Railway/Render-style tradeoffs at the level needed for the decision
- link tenant boundary and runtime contract follow-ups

### Acceptance Checks

- ADR exists at `docs/ops/hosting-and-tenant-architecture-adr.md`.
- ADR explicitly chooses managed single-tenant, pooled multi-tenant, or staged hybrid.
- ADR rejects or qualifies "publish an image on AWS" as an insufficient paid-hosting model unless paired with persistent state, backups, secrets, restore, domains, and support operations.
- ADR names what would need to change before pooled multi-tenancy is safe.

## `S47-3 Tenant Data Boundary`

### Goal

Define the boundary around each family archive.

### Packets

- `FB-111`

### Scope

- inventory database, media, variants, thumbnails, backups, exports, sessions, tokens, logs, Matrix bridge data, inbound email attachments, and secrets
- define owner, path/table, retention rule, export behavior, and deletion behavior for each data class
- document current single-archive boundary and future pooled-tenant requirements
- identify tests or fixtures needed for backup/export/media path traversal and archive mix-up

### Acceptance Checks

- Tenant boundary doc exists at `docs/ops/tenant-data-boundary.md`.
- ADR links to the tenant boundary doc.
- Durable data classes have explicit export/delete/retention behavior.
- Future pooled multi-tenant requirements are captured without requiring implementation in this sprint.
- Any testable boundary gaps are either covered or converted into follow-up packets.

## `S47-4 Production Container Runtime Contract`

### Goal

Make the container image deployable as a supported production artifact.

### Packets

- `FB-110`

### Scope

- document production env vars and required secrets
- document required persistent mount paths for SQLite, media, variants, backups, and exports
- document startup, migrations, health/readiness, release tagging, promotion, and rollback
- make production-unsafe behavior visible: dev bypass, demo seed, missing secrets, and local-only assumptions
- add focused config/health tests if behavior needs enforcement

### Acceptance Checks

- Runtime contract exists at `docs/ops/production-container-runtime.md`.
- Required and optional env vars are explicit.
- Persistent paths are explicit and map to current app behavior.
- Health/readiness behavior is clear enough for container orchestration.
- Demo/dev bypass behavior cannot be mistaken for paid production setup.

## `S47-5 Managed Hosting Baseline` (dependent)

### Goal

Document the first operator-supported environment for paid pilot archives.

### Packets

- `FB-112`

### Scope

- choose the baseline only after the ADR settles the hosting model
- document staging, pilot, and production archive setup
- include TLS, trusted hosts, SMTP, passkey origin, secrets, storage, backups, restore verification, logs, support access, and custom domain assumptions
- update production `.env` examples only if the runtime contract identifies clear gaps

### Acceptance Checks

- Managed-hosting baseline exists at `docs/ops/managed-hosting-baseline.md` if this slice is pulled in.
- Operator can provision a staging or paid-pilot archive from documented steps.
- Backup and restore verification are part of the baseline.
- Unsupported hosting shapes are explicitly called out for the current SQLite/media architecture.

## `S47-6 Closeout and Commercialization Backlog Update`

### Goal

Close the sprint with a usable decision and a clean path into privacy/trust and paid-hosting work.

### Scope

- summarize the chosen hosting model and its implications
- update `FB-109` to `FB-112` packet status and evidence
- update the sprint board
- update later commercialization packet scopes if the ADR changes assumptions
- queue follow-ups that should not be smuggled into S47

### Acceptance Checks

- Sprint closeout exists under `docs/strategy/`.
- Board clearly shows S47 status and the next planned sprint.
- Follow-up work for S48/S49 is explicit if the hosting decision changes the roadmap.
- `git diff --check` passes.

## Validation Baseline

- `git diff --check`
- `uv run pytest tests/test_config.py tests/test_health.py -q` if runtime/config code changes
- `uv run pytest tests/test_backup.py tests/test_media.py tests/test_config.py -q` if tenant boundary code or tests change
- `docker build -t family-book:local .` if Dockerfile/runtime scripts change

## Recommended Builder Order

1. `FB-109`
2. `FB-111`
3. `FB-110`
4. `FB-112`
