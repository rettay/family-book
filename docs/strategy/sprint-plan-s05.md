# Sprint Plan - S05 Encryption and Backup Hardening Pass

## Sprint

- Name: `S05 - Encryption and Backup Hardening Pass`
- Status: Closed
- Primary packet: `FB-009 Encryption and Backup Hardening Pass`

## Sprint Goal

Make Family Book credible for sensitive family data by adding a truthful protection contract for the highest-risk fields, proving backup and restore behavior, and tightening launch-default runtime hardening.

## Why This Sprint

Family Book now supports shared collaboration, recovery, and moderation. That increases the value of the stored data and the cost of operator mistakes. The next bottleneck is not feature breadth. It is whether the app can honestly claim to protect sensitive fields and survive routine self-hosted failures.

## Must-Have Outcomes

- Sensitive-data protection is explicitly defined instead of implied.
- The highest-risk fields have real application-level protection at rest.
- Backup creation and restore are both part of the supported runtime contract.
- Launch-default hardening removes the most obvious privacy and durability footguns from deployment.

## Acceptance Criteria

1. Family Book documents a truthful protection contract covering in-transit security, deployment/disk assumptions, and field-level encryption scope.
2. Supported sensitive fields persist in encrypted form rather than plaintext through the normal application path.
3. A focused test proves those fields are not stored as readable plaintext values in the underlying persistence layer.
4. Backup creation and restore are both supported, documented, and verified against a usable restored state.
5. Health/admin surfaces report truthful backup freshness and protection state.
6. Launch-default hardening is verified for docs exposure, trusted-host behavior, authenticated cache behavior, and bounded upload/download paths.

## In Scope

- documented protection contract
- field-level encryption for medical and direct-contact fields
- backup/restore truthfulness and bounded restore verification
- backup-health/operator-status truthfulness
- deployment/runtime hardening needed to support those guarantees
- focused tests and governance review

## Out of Scope

- full-database or client-side encryption
- role redesign or privacy segmentation rewrite
- theme customization and branding
- broad cloud-platform abstraction work
- generalized disaster-recovery orchestration

## Implementation Order

1. Execute Slice 1: data protection contract and field-level protection path.
2. Execute Slice 2: backup and restore truthfulness.
3. Execute Slice 3: operational hardening and protection-state surfacing.
4. Validate the combined sprint outcomes with focused tests and governance/security review.

## Execution Slices

### Slice 1 - Data Protection Contract

- Goal:
  define exactly what protection Family Book does and does not provide, then implement application-level encryption for the highest-risk fields
- Scope:
  protected field set, encryption/decryption path, schema/service integration, and truthful operator documentation
- Must prove:
  protected fields no longer persist as readable plaintext through the normal app path
- Suggested acceptance checks:
  medical and direct-contact fields round-trip correctly for supported app reads
  stored values are not plaintext when inspected directly

### Slice 2 - Backup and Restore Truthfulness

- Goal:
  turn backup from "files exist" into a supported restore contract
- Scope:
  backup path, restore procedure, retention assumptions, and bounded restore verification
- Must prove:
  a produced backup can restore a usable app state in the supported environment
- Suggested acceptance checks:
  a bounded restore test or operator-path verification succeeds
  backup health surfaces reflect actual backup freshness and availability

### Slice 3 - Operational Hardening

- Goal:
  ensure launch-default runtime behavior does not quietly violate the protection contract
- Scope:
  docs exposure, trusted hosts, cache behavior, upload/download bounds, webhook constraints, and truthful status surfaces
- Must prove:
  unsafe defaults are removed from the normal deployment path
- Suggested acceptance checks:
  docs are disabled by default
  authenticated responses are not service-worker cached by default
  high-risk body/download paths are bounded and fail closed

## Proof Obligations

- Encryption claims must be backed by actual persistence behavior, not helper code that sits unused.
- Restore claims must be backed by a runnable verification path, not prose alone.
- Hardening must be enforced by default runtime behavior, not only optional docs advice.
- Sprint scope must stay narrow enough to deliver real protection on the highest-risk fields.

## Risks To Watch

- overclaiming encryption guarantees
- retrofits that break existing CRUD flows or revisions
- restore paths that work in theory but not in the actual temp/data-dir model used by the app
- hardening that fixes one endpoint while leaving the same issue elsewhere

## Exit Target

Sprint 05 is complete when Family Book can truthfully say what sensitive data it protects, can prove the highest-risk fields are protected in storage, and can demonstrate that backup and restore work as part of a normal self-hosted operating model.

## Closeout

- Status: Closed
- Outcome:
  Sprint 05 delivered field-level protection for medical and direct-contact data, explicit fail-closed key handling, plaintext revision-history backfill, restore-verification truthfulness, and tighter runtime hardening with updated focused tests.
- Verification baseline:
  - `uv run pytest tests/test_protection_service.py tests/test_revision_service.py tests/test_security_guardrails.py tests/test_schema_models.py tests/test_phase3.py tests/test_auth.py -q` → `54 passed`
  - `uv run python -m compileall app tests` → success
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json` → `16 PASS`, `0 FAIL`, `9 WARN`
