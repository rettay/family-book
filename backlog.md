# Family Book Backlog

Sprint: `S02 - Tree and Discovery Foundation`
Status: Closed

## Current Sprint `S02 - Tree and Discovery Foundation`

Sprint goal:
- Make the shared family record easier to explore through persisted tree preferences, server-backed filters, and a first authenticated map view.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-005 | Tree Preferences, Filters, and Map Foundation | P2 | done | `task_packets/FB-005_tree_preferences_filters_and_map_foundation.md` |

Closeout:
- Sprint 02 is complete.
- Implementation and audit both landed on `codex/shared-collaboration-reset`.
- Verified builder baseline at closeout: `56 passed` on `tests/test_api.py` and `tests/test_models.py`.
- Repo-local CodeMap config now exists at `.codemap/config.yaml` to keep governance scans focused on product code.

## Recently Completed

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-001 | Product Contract and Operating System Bootstrap | P0 | done | `task_packets/FB-001_product_contract_and_operating_system_bootstrap.md` |
| FB-002 | Account, Invite, and Admin Foundation | P0 | done | `task_packets/FB-002_account_invite_and_admin_foundation.md` |
| FB-003 | Flat Family Access and Shared Visibility Reset | P0 | done | `task_packets/FB-003_flat_family_access_and_shared_visibility_reset.md` |
| FB-004 | Rich Person Record and Tagged Family Content Foundation | P1 | done | `task_packets/FB-004_rich_person_record_and_tagged_family_content_foundation.md` |
| FB-005 | Tree Preferences, Filters, and Map Foundation | P2 | done | `task_packets/FB-005_tree_preferences_filters_and_map_foundation.md` |

## Next Sprint

- `S03 - Timeline and Family Moments Expansion`
- Recommended opening packet: `FB-006 Timeline and Family Moments Expansion`
- Follow-on candidates after `FB-006`:
  - `FB-007 Version History, Revert, and Moderation Controls`
  - `FB-009 Encryption and Backup Hardening Pass`

## Next-Likely Follow-Ups

| ID | Title | Priority | Status | Notes |
|---|---|---:|---|---|
| FB-006 | Timeline and Family Moments Expansion | P1 | todo | Enrich stories, notes, external references, and tagged multi-person events |
| FB-007 | Version History, Revert, and Moderation Controls | P1 | todo | Needed once collaborative editing becomes broad |
| FB-008 | Theme Customization and Branding Controls | P2 | todo | Admin-configurable color system and surface branding |
| FB-009 | Encryption and Backup Hardening Pass | P1 | todo | Clarify runtime guarantees and protect sensitive content |
