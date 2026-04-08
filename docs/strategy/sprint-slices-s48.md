# Sprint Slices - S48 Privacy and Exit Trust

## Slice Order

1. `S48-1 Permission Model Decision And Enforcement`
2. `S48-2 Sensitive Data Defaults And Disclosure`
3. `S48-3 Archive Export And Exitability`
4. `S48-4 Trust Copy And Launch Claims`
5. `S48-5 Closeout And Follow-Up Capture`

## `S48-1 Permission Model Decision And Enforcement`

### Goal

Replace the broad current non-admin permission model with one that is commercially defensible.

### Packets

- `FB-113`

### Scope

- decide the role model: owner/admin/steward/member/viewer or a simpler equivalent
- decide whether graph-distance privacy remains part of the product promise
- enforce the new view/edit/manage rules across person, tree, wiki, relationships, and media surfaces
- preserve invite/admin bootstrap flows

### Acceptance Checks

- Non-admin active members cannot edit every visible active person.
- Contact visibility is policy-driven rather than implicitly broad.
- Any retained graph-distance promise is backed by tests.
- Existing admin and invite flows still work.

## `S48-2 Sensitive Data Defaults And Disclosure`

### Goal

Make sensitive fields and private-media handling safe by default.

### Packets

- `FB-114`

### Scope

- define defaults for contact, medical, genetic, minor, and private-media fields
- expose UI explanations and badges where visibility is restricted
- add audit events for sensitive-visibility changes
- update invite copy so new users know what is visible

### Acceptance Checks

- Sensitive defaults are documented and visible in UI copy.
- Medical/genetic/contact data cannot be accidentally exposed to all members.
- Minor-related defaults are conservative.
- API and HTML paths both redact restricted fields correctly.

## `S48-3 Archive Export And Exitability`

### Goal

Make "you own your data" operationally true.

### Packets

- `FB-115`

### Scope

- add GEDCOM export
- add full archive export with media, stories, wiki sections, and manifest
- support admin UI export and operator/CLI export
- define sensitive-field behavior in export output

### Acceptance Checks

- Admin can download GEDCOM export.
- Admin can download full archive export.
- Export manifest is explicit about omissions and custom fields.
- Unauthorized users cannot access export output or hidden/private data.

## `S48-4 Trust Copy And Launch Claims`

### Goal

Make the privacy/security story understandable and accurate to the implementation.

### Packets

- `FB-116`

### Scope

- create trust-center docs
- align README and landing copy
- explain encryption, backups, export, delete, and cancellation accurately
- remove unsupported claims

### Acceptance Checks

- Trust docs distinguish field-level encryption from end-to-end encryption.
- Backup and restore claims match implementation.
- Export/delete/cancel paths are understandable to a paying customer.
- Landing and README copy align with the actual permission model.

## `S48-5 Closeout And Follow-Up Capture`

### Goal

Close the sprint with a defensible trust posture and a clear path into hosted billing/provisioning work.

### Scope

- update packet evidence and sprint board
- record the final permission/trust model
- queue any post-sprint follow-ups such as expanded stewardship moderation or more complete export coverage
- keep the `FB-110` image-build verification blocker visible as a cross-sprint ops follow-up

### Acceptance Checks

- Sprint closeout exists under `docs/strategy/`.
- Board clearly shows S48 status and the next planned sprint.
- Trust-related follow-ups are captured separately from paid-platform work.
- `git diff --check` passes.

## Validation Baseline

- `uv run pytest tests/test_access_control.py tests/test_api.py tests/test_media.py tests/test_pages.py -q`
- `uv run pytest tests/test_export.py tests/test_gedcom_parser.py tests/test_access_control.py -q`
- `git diff --check`

## Recommended Builder Order

1. `FB-113`
2. `FB-114`
3. `FB-115`
4. `FB-116`
