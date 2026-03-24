# Family Book Backlog

Sprint: `S06 - Theme Customization and Branding Controls`
Status: Closed

## Closed Sprint `S04 - Version History, Revert, and Moderation Controls`

Sprint goal:
- Make broad family collaboration trustworthy through edit history, revert, recoverability, and light admin moderation.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-007 | Version History, Revert, and Moderation Controls | P1 | done | `task_packets/FB-007_version_history_revert_and_moderation_controls.md` |

Execution slices:
- `S04-1` Revision Capture and History Retrieval
- `S04-2` Revert and Recoverable Delete
- `S04-3` Moderation Controls for Shared Content

## Recently Completed

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-001 | Product Contract and Operating System Bootstrap | P0 | done | `task_packets/FB-001_product_contract_and_operating_system_bootstrap.md` |
| FB-002 | Account, Invite, and Admin Foundation | P0 | done | `task_packets/FB-002_account_invite_and_admin_foundation.md` |
| FB-003 | Flat Family Access and Shared Visibility Reset | P0 | done | `task_packets/FB-003_flat_family_access_and_shared_visibility_reset.md` |
| FB-004 | Rich Person Record and Tagged Family Content Foundation | P1 | done | `task_packets/FB-004_rich_person_record_and_tagged_family_content_foundation.md` |
| FB-005 | Tree Preferences, Filters, and Map Foundation | P2 | done | `task_packets/FB-005_tree_preferences_filters_and_map_foundation.md` |
| FB-006 | Timeline and Family Moments Expansion | P1 | done | `task_packets/FB-006_timeline_and_family_moments_expansion.md` |
| FB-007 | Version History, Revert, and Moderation Controls | P1 | done | `task_packets/FB-007_version_history_revert_and_moderation_controls.md` |

## Closed Sprint `S05 - Encryption and Backup Hardening Pass`

Sprint goal:
- Make Family Book credible for sensitive family data by establishing a truthful protection contract, proving backup and restore behavior, and tightening launch-default runtime hardening.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-009 | Encryption and Backup Hardening Pass | P1 | done | `task_packets/FB-009_encryption_and_backup_hardening_pass.md` |

Execution slices:
- `S05-1` Data Protection Contract
- `S05-2` Backup and Restore Truthfulness
- `S05-3` Operational Hardening

## Closed Sprint `S06 - Theme Customization and Branding Controls`

Sprint goal:
- Make Family Book feel owner-operated through admin-managed theme tokens, minimal branding controls, and staging-based visual acceptance.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-008 | Theme Customization and Branding Controls | P2 | done | `task_packets/FB-008_theme_customization_and_branding_controls.md` |

Execution slices:
- `S06-1` Theme Token Contract and Persistence
- `S06-2` Admin Theme Controls
- `S06-3` Surface Rollout and Staging Acceptance

## Next Sprint

- Recommended next sprint: `S07 - Observability and Coverage Hardening`
- Primary packet: `TBD`
- Follow-on candidate after Sprint 06:
  - backup/observability cleanup from remaining CodeMap warnings
  - attack-surface tests for `app/middleware/security.py` and `app/services/io_limits.py`
  - critical-module coverage for `app/config.py`, `app/models/moments.py`, and `app/schemas.py`

## Next-Likely Follow-Ups

| ID | Title | Priority | Status | Notes |
|---|---|---:|---|---|
| FB-010 | Observability and Coverage Hardening | P1 | todo | CodeMap warning cleanup, attack-surface tests, and core runtime observability |
