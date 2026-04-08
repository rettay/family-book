# Trust Center

Family Book is a private family archive, not a zero-knowledge vault. This document states the current privacy and exit guarantees as implemented today.

## Truth Table

| Topic | Current behavior |
|---|---|
| Transport security | Depends on HTTPS at the deployment layer. |
| Database model | Single SQLite database per archive in the current hosted shape. |
| Media storage | Files live under the archive data directory and are served through authenticated routes. |
| Sensitive field protection | Contact, medical, and genetic fields are encrypted at rest in application storage. |
| Access model | Owner/admin can view all active profiles. Stewards can manage visible non-staff profiles. Members and viewers only see visible relatives connected within the configured family-graph distance. |
| Living minors | Contact fields stay staff-only regardless of the general contact policy. |
| Hidden profiles | Hidden profiles are restricted to owner/admin. |
| Backups | Admins can trigger backups, download the latest backup ZIP, and run restore verification. |
| Exitability | Admins can download GEDCOM and full archive exports as ephemeral downloads that are cleaned up after the response completes. |
| Zero-knowledge / E2EE | Not implemented. Do not claim either. |

## Privacy Defaults

- `contact_visibility` defaults to `close_family`.
- `sensitive_visibility` defaults to `staff`.
- Living minors override contact visibility to staff-only.
- Viewers are read-only, including on their own profile.

## Export Model

- GEDCOM export is for interoperability and includes core people and relationship records plus Family Book custom tags.
- Full archive export includes:
  - `people.json`
  - relationship JSON
  - `stories.json`
  - media metadata plus original files where present
  - `exports/family-book.ged`
  - `manifest.json`
- Full archive JSON includes sensitive contact, medical, and genetic fields because the export is admin-only.
- Export artifacts are generated in temporary storage for delivery and are deleted after the download response completes.
- GEDCOM does not represent every Family Book field. The manifest documents omissions and custom fields.

## Deletion and Cancellation

- Profiles are soft-deleted in the application for auditability and recovery.
- Hosted archives should export first, then cancel and request archive deletion according to the hosting policy in force for that environment.
