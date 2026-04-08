# Managed Hosting Baseline

## Goal

Define the first operator-supported hosting baseline for paid pilot archives.

## Baseline Decision

Use managed single-tenant archives.

For each archive:

- one app deployment
- one persistent archive volume
- one canonical archive domain or subdomain
- one archive-specific secret bundle
- one operator runbook for backup, restore, and delete

## Environments

### Staging

Purpose:

- validate image/runtime changes before paid archive rollout

Characteristics:

- separate volume from production archives
- may use demo data
- `FAMILY_BOOK_ENV=staging`

### Paid Pilot Archive

Purpose:

- first real customer deployment

Characteristics:

- no demo data
- `FAMILY_BOOK_ENV=production`
- dedicated persistent storage
- dedicated secret set
- backup and restore verification enabled before go-live

## Required Baseline Controls

### Storage

- mount persistent volume to `DATA_DIR`
- keep SQLite path inside `DATA_DIR`
- do not share the volume between archives

### TLS And Hostnames

- terminate HTTPS at the edge or platform ingress
- set `BASE_URL` to the canonical `https://` archive URL
- set `TRUSTED_HOSTS` to the archive hostname and any required proxy hostname

### Secrets

- unique `SECRET_KEY` per archive deployment
- unique `FERNET_KEY` per archive deployment
- separate SMTP credentials where practical
- rotate webhook and Matrix credentials when archives are deleted or ownership changes

### Email And Passkeys

- configure SMTP before enabling invite and magic-link expectations for customers
- set passkey origin consistently with `BASE_URL`
- if custom domains are used, passkey/WebAuthn relying-party values must match that domain decision

### Backups And Restore

- verify `/api/admin/backup/status` before launch
- run backup restore verification before go-live
- document the retention rule and where backup artifacts live

### Logs And Support Access

- use provider logs for deploy/runtime debugging
- prefer health, backup status, and configuration checks before reading customer content
- scope support access to the single archive deployment

## Provider Baseline Recommendations

### Primary near-term baseline

Railway-style or Render-style single archive deployment with a dedicated persistent volume or disk.

Why:

- matches current app shape
- low operator overhead
- easy to reason about one archive per deployment

### AWS operator path

ECS/Fargate plus EFS, or EC2/Lightsail-style single archive host.

Why:

- acceptable fit for the current persistent-filesystem model
- clearer long-term operator control if the business outgrows simpler platforms

## Unsupported Baseline For First Paid Pilots

- pooled multi-tenant archive hosting
- stateless runtime with ephemeral local disk as the only database/media storage
- custom domains without matching `BASE_URL`, `TRUSTED_HOSTS`, and passkey origin review

## Provisioning Checklist

1. Generate archive-specific `SECRET_KEY` and `FERNET_KEY`.
2. Create persistent volume and set `DATA_DIR`.
3. Set `DATABASE_URL` inside `DATA_DIR`.
4. Set `BASE_URL`, `TRUSTED_HOSTS`, and `FAMILY_BOOK_ENV=production`.
5. Configure SMTP if invites and magic links are customer-facing.
6. Deploy image and confirm `/health`.
7. Confirm admin bootstrap/login.
8. Confirm backup status and run restore verification.
9. Record archive inventory and support contact path.
