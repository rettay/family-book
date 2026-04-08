# Export and Delete

## Admin Export Paths

- `GET /api/admin/exports/gedcom`
  - Returns a GEDCOM file for people, partnerships, parent-child links, dates, places, and notes that map cleanly.
  - Generated as a temporary download artifact and deleted after the response completes.
- `GET /api/admin/exports/archive`
  - Returns a ZIP archive with manifest, JSON data, media metadata, original media files where present, and an embedded GEDCOM export.
  - Generated as a temporary download artifact and deleted after the response completes.
- `GET /api/admin/backup/download`
  - Returns the latest operational backup ZIP.

## What Each Export Is For

- GEDCOM:
  - best for moving into other genealogy tools
  - lossy for Family Book-only fields
- Full archive ZIP:
  - best for ownership, support, and long-term retention
  - preserves Family Book privacy settings, stories, and sensitive JSON fields
- Backup ZIP:
  - best for operational restore of the same archive
  - not the preferred portability format for another product

## Sensitive Data

- GEDCOM omits or flattens most sensitive contact, medical, and genetic data.
- Full archive ZIP includes those fields because only admins can generate it.
- Media visibility is still enforced in the application; unauthorized users cannot generate archive output.

## Delete Model

- Person deletion is soft-delete today.
- Archive cancellation for a hosted offering should follow this order:
  1. export GEDCOM or full archive
  2. confirm cancellation
  3. delete hosted archive data according to the environment policy
