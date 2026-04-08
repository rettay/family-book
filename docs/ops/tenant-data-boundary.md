# Tenant Data Boundary

## Decision Context

For the first paid-hosting pilot, one tenant equals one deployed family archive.

The boundary is deployment-level isolation, not row-level isolation.

## Archive Root

For a managed single-tenant archive, the archive root is `DATA_DIR`.

Current expected layout:

```text
DATA_DIR/
  family.db
  media/
  media/thumbnails/
  media/variants/
  backups/
  backups/family-*.db.gz
  backups/family-book-backup.zip
  backups/restore-verification.json
```

`DATABASE_URL=sqlite:///data/family.db` resolves inside `DATA_DIR` through the current settings contract.

## Durable Data Inventory

| Data class | Current owner | Current location | Retention rule | Export behavior | Delete behavior |
|---|---|---|---|---|---|
| Primary database | archive runtime | SQLite file from `DATABASE_URL` | indefinite until deleted | included via backup/export archive | remove as part of archive delete |
| Media originals | archive runtime | `DATA_DIR/media/*` | indefinite until deleted | included in backup/export archive | remove as part of archive delete |
| Media thumbnails | archive runtime | `DATA_DIR/media/thumbnails/*` | derived from originals | not separately required; can be regenerated | remove with archive delete |
| Media variants | archive runtime | `DATA_DIR/media/variants/*` | derived from originals | not separately required; can be regenerated | remove with archive delete |
| Compressed DB backups | backup service | `DATA_DIR/backups/family-*.db.gz` | `BACKUP_RETENTION_DAYS` | latest backup included in export zip | remove with archive delete |
| Export zip | backup service | `DATA_DIR/backups/family-book-backup.zip` | operator-controlled temporary artifact | direct download artifact | remove after use or archive delete |
| Restore verification metadata | backup service | `DATA_DIR/backups/restore-verification.json` | latest verification only | not customer-facing by default | remove with archive delete |
| Session rows | app database | database tables | app-managed | included in database export | invalidated by archive delete |
| Magic links and auth audit | app database | database tables | app-managed | included in database export | removed with archive delete |
| Protected person-field ciphertext | app database | database tables | same as person records | included encrypted in DB export | removed with archive delete |
| Fernet key | deployment secrets | secret manager or env vars | until rotated | not exported with customer data | revoke/destroy on archive delete after retention policy |
| SMTP credentials | deployment secrets | secret manager or env vars | until rotated | not exported | revoke/destroy on archive delete |
| Passkey RP origin config | deployment config | env vars | until domain changes | not exported | remove with archive delete |
| Inbound email webhook secret | deployment secrets | env vars | until rotated | not exported | revoke/destroy on archive delete |
| Inbound email attachments | archive runtime | saved into `DATA_DIR/media/*` | same as media | exported as media | removed with archive delete |
| Matrix bot credentials | deployment secrets | env vars | until rotated | not exported | revoke/destroy on archive delete |
| Matrix room mappings and events | app database plus Matrix service | DB rows and external service | app-managed | DB portion exported; external service data is not a formal archive export yet | remove local references, then rotate bot credentials |
| Deployment logs | hosting platform | provider logs | provider retention policy | not part of customer export | expire per provider policy |

## Boundary Rules

### Database

- one archive deployment must not point at another archive's SQLite path
- in production, SQLite path must live inside `DATA_DIR`
- pooled database rows are unsupported in the current architecture

### Media And Variants

- media paths are archive-local under `DATA_DIR/media`
- variants stay under `DATA_DIR/media/variants`
- archive export must include only that archive's media tree

### Backups And Exports

- backup files stay under `DATA_DIR/backups`
- restore verification metadata is archive-local
- restore must reject unsafe archive paths
- do not combine multiple family archives into one backup directory

### Secrets

- `SECRET_KEY`, `FERNET_KEY`, SMTP credentials, webhook secrets, and Matrix credentials are deployment-scoped
- do not share a secret bundle across unrelated paid archives unless there is an explicit rotation and blast-radius policy

### Support Access

- operator access should be deployment-scoped
- support workflows should use health, backup, and provisioning state before inspecting customer content
- production logs should avoid raw secrets and raw auth tokens

## Current Enforcement

- runtime contract blocks production SQLite paths outside `DATA_DIR`
- backup restore rejects unsafe zip paths
- media storage uses archive-local paths under `DATA_DIR/media`

## Future Pooled-Tenant Requirements

If Family Book later moves to pooled multi-tenancy, the following become mandatory:

- tenant identifier across every durable table and storage object
- tenant-scoped object storage prefixes or buckets
- tenant-scoped backup and export jobs
- tenant-aware support tooling and audit trails
- tenant-aware rate limits and billing entitlements
- database migration plan away from single-file SQLite assumptions
