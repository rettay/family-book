# Protection And Backup Contract

## Field-Level Protection Scope

Family Book applies application-level field encryption to the highest-risk person fields:

- `medical_history`
- `contact_whatsapp`
- `contact_telegram`
- `contact_signal`
- `contact_email`

This protection applies to the normal persistence path and to person revision snapshots stored by the app.

## What This Does Not Mean

- This is not client-side end-to-end encryption.
- This is not full-database encryption.
- Operators must still protect backups, database files, media files, and host access.

## Runtime Assumptions

- HTTPS should terminate at the deployment edge.
- SQLite data, media, and backups should live under the configured `DATA_DIR`.
- `FERNET_KEY` must be configured and kept private.

## Backup Contract

- Backups are created from the live SQLite database using SQLite's backup API.
- Backups are written under `DATA_DIR/backups`.
- The downloadable archive contains the latest compressed database backup plus media files.
- Restore verification restores that archive into a temporary data directory and verifies the restored database is readable.

## Operator Verification Paths

- Trigger backup: `POST /api/admin/backup`
- Download latest backup archive: `GET /api/admin/backup/download`
- Inspect backup/protection status: `GET /api/admin/backup/status`
- Verify restore path: `POST /api/admin/backup/verify`
