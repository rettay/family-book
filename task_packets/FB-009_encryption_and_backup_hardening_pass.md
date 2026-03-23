# Task Packet - FB-009 Encryption and Backup Hardening Pass

## Objective

Make Family Book trustworthy for sensitive family data by adding a truthful encryption contract for the highest-risk fields, verifying backup and restore behavior end to end, and tightening deployment defaults so the runtime does not quietly undermine privacy or durability.

## Why / KPI

- Sprint 04 added recoverability and moderation.
- The next gap is protection: Family Book now stores collaborative family history, contact data, medical notes, and burial/location details that should not rely on vague "host encryption" assumptions.
- Operators also need a backup story that is provably restorable, not merely "files exist in `/data`".

Primary KPI:
- improve **Sensitive Data Protection Confidence (SDPC)** by reducing the gap between documented protection guarantees and actual runtime behavior.

Secondary KPI:
- reduce restore-failure risk for normal self-hosted deployments.

## Scope

- In scope:
  - explicit encryption policy for launch-critical sensitive data
  - field-level encryption for the highest-risk stored fields
  - backup creation, retention, restore procedure, and health truthfulness
  - deployment/runtime hardening needed to support those guarantees
  - focused tests and browser/admin evidence for protection and restore behavior
- Out of scope:
  - a full cryptographic redesign across every table and blob
  - per-user key management
  - end-to-end encrypted collaboration or client-side crypto
  - broad role redesign or permissions segmentation
  - theme customization and branding work

## Task Type

- Security, durability, and operational-truthfulness packet

## Dependencies and Ordering Assumptions

- Depends on `FB-002` through `FB-007` because authentication, collaboration, revision history, and moderation are now the active product model.
- Should execute before `FB-008` because a visually nicer app is lower priority than truthful protection and restore guarantees.
- May incorporate or refine the existing hardening work already present in deploy/runtime/security paths.

## Constraints

- Do not claim broad encryption guarantees that the code does not actually implement.
- Prefer strong, explicit protection on fewer fields over shallow "everything is encrypted" messaging.
- Restore procedures must be runnable and testable by an operator without ad hoc database surgery.
- Runtime hardening must remain compatible with self-hosted deployment, not only a single cloud platform.

## Recommended Launch Scope Within This Packet

- Must protect at rest with field-level encryption for:
  - medical history fields
  - direct contact fields such as email, phone, WhatsApp, Signal, Telegram, and similar private identifiers
- Must validate and document:
  - backup location
  - backup retention
  - restore steps
  - health/freshness reporting
- Should harden:
  - docs exposure defaults
  - trusted hosts
  - cache behavior for authenticated responses
  - request/body limits for high-risk upload paths
  - inbound webhook attachment constraints

## Implementation Notes

- Likely files:
  - `app/config.py`
  - `app/models/person.py`
  - `app/schemas.py`
  - `app/routes/persons.py`
  - `app/routes/auth_routes.py`
  - `app/routes/health.py`
  - `app/backup/routes.py`
  - `app/backup/service.py`
  - `app/services/`
    - new encryption/protection service if needed
    - backup/restore helpers
  - `app/middleware/security.py`
  - `app/main.py`
  - deployment docs and container startup paths
  - focused tests for encryption, backup, restore, and hardening behavior
  - Playwright or admin-flow evidence where it helps prove the operator path
- Validation commands:
  - focused pytest for protected-field persistence and restore behavior
  - `uv run python -m compileall app`
  - CodeMap or equivalent governance check after changes

## Evaluation Environment

- Task:
  protect sensitive stored data honestly and make backup/restore behavior operationally truthful
- Verifier:
  focused API/unit tests, operator-path checks, and governance/security review
- Reference/oracle:
  `foundation/V1_PRODUCT_REQUIREMENTS.md`
  `foundation/COLLABORATION_AND_PRIVACY.md`
  `security_best_practices_report.md`
- Expected evidence:
  protected fields are not stored in plaintext in the normal persistence path, backup creation and restore are both runnable, and deploy defaults no longer expose docs or cache authenticated private responses by accident
- Known failure modes / reward hacks:
  - "encryption" means only disk-level assumptions or Fernet helper code that is never used on real fields
  - backups exist but restore path is undocumented or untested
  - health reports "ok" while backup freshness or protection state is misleading
  - hardening applies only to one route while adjacent routes still leak the same class of risk
- Verifiability class:
  `bounded-judgment`
- Context policy:
  keep scope on the highest-risk fields and operator workflows; do not drift into general crypto architecture or broad access-model redesign

## Acceptance Criteria

- [ ] Family Book has a documented protection contract that distinguishes in-transit protection, deployment/disk expectations, and field-level encryption.
- [ ] Supported sensitive person fields are encrypted through the normal persistence path and decrypted only through supported application reads.
- [ ] Focused tests prove protected fields are not stored as plaintext values in the underlying persistence representation.
- [ ] Backup creation and restore are both executable, documented, and validated against a usable restored app state.
- [ ] Health/admin backup surfaces report truthful freshness and protection state for the supported deployment model.
- [ ] Launch-default runtime hardening is verified for docs exposure, trusted hosts, authenticated cache behavior, and bounded upload/download paths.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] At least one negative-case path proves restore or protection state fails closed instead of silently claiming success
- [ ] Protection claims in docs/config match the code that actually runs
- [ ] No new false-security language is introduced into README, status docs, or operator surfaces

## Risk and Verification Notes

- Complexity hotspots:
  - retrofitting encrypted fields without breaking existing forms, tests, and migrations
  - making restore behavior truthful when current deployments may already have mixed path assumptions
  - avoiding a split brain between "security hardening" docs and actual runtime defaults
- Likely shallow-pass failure modes:
  - helper functions for encryption exist but sensitive columns still persist plaintext
  - restore restores files but not a working application state
  - backup health says "fresh" while restore cannot succeed
  - middleware hardening applies only to a subset of paths and leaves equivalent bypasses
- Required verification depth:
  - inspect stored values or serialized snapshots for protected fields
  - run a restore-path verification on a bounded fixture or temp data dir
  - verify at least one default deployment path behaves safely without extra operator tweaks
- Sufficient discriminative power means:
  the verifier must fail if encryption is cosmetic, if restore is aspirational, or if hardening language overstates what the runtime actually guarantees

## Execution Budget

- Builder may explore:
  - whether protected fields should be encrypted at the model layer, service layer, or schema translation layer
  - whether restore verification should be API-driven, direct service-driven, or both
  - the smallest operator-facing status surface that truthfully communicates protection and backup state
- Builder must escalate if:
  - field-level encryption requires a broader schema redesign than this sprint can safely absorb
  - restore truthfulness requires changing the deployment/storage contract beyond sprint scope
  - the current flat collaboration model conflicts with the intended protection rules for medical/contact data
- Material scope drift:
  - full-database encryption claims
  - client-side or per-user key management
  - broad trust-and-safety or access-model redesign
- Proof obligations before review:
  - protected fields are actually transformed before persistence
  - restore changes live app state in a usable way
  - hardening is enforced by runtime behavior, not only documentation
