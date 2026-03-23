# family-book — Agent Brief

**Modules:** 101  
**Languages:** python (68), unknown (29), javascript (4)  
**With AI briefings:** 0/101

## Architecture Overview

**Hub modules** (imported by others): `app/models/person.py` (19), `app/config.py` (17), `app/database.py` (13), `app/models/base.py` (12), `app/auth.py` (9), `app/models/relationships.py` (9), `app/models/media.py` (8), `app/services/auth_service.py` (6), `app/models/auth.py` (6), `app/models/moments.py` (6)

**Leaf modules** (import others, not imported): `app/seed.py`, `tests/conftest.py`, `alembic/env.py`, `tests/test_api.py`, `tests/test_auth.py`, `tests/test_media.py`, `tests/test_models.py`, `tests/test_phase1_edge_cases.py`

## Domain Architecture

**domain-0** (53 modules): `app/models/person.py`, `app/config.py`, `app/database.py`, `app/models/base.py`, `app/auth.py`, `app/models/relationships.py`, `app/models/media.py`, `app/services/auth_service.py`
  ... and 45 more

## Architecture Roles

- **Core**: `app/models/person.py`, `app/config.py`, `app/models/base.py`, `app/access_control.py`, `app/schemas.py`
- **Utility**: `app/database.py`, `app/auth.py`, `app/models/relationships.py`, `app/models/media.py`, `app/services/auth_service.py` (+81 more)
- **Test Support**: `tests/conftest.py`, `tests/__init__.py`, `tests/test_api.py`, `tests/test_auth.py`, `tests/test_comments.py` (+5 more)

## Top Modules Requiring Review

| Module | Score | Centrality | Top Factor |
|---|---:|---:|---|
| `app/services/media_service.py` | 0.52 | 0.07 | complexity (red) |
| `app/routes/pages.py` | 0.51 | 0.03 | churn (4 changes) |
| `app/middleware/security.py` | 0.44 | 0.03 | complexity (red) |
| `app/static/js/tree.js` | 0.43 | 0.00 | complexity (red) |
| `app/config.py` | 0.42 | 0.83 | centrality (17 importers) |
| `app/inbound/routes.py` | 0.41 | 0.03 | complexity (red) |
| `app/static/js/main.js` | 0.40 | 0.00 | complexity (red) |
| `app/routes/tree.py` | 0.35 | 0.00 | churn (4 changes) |
| `app/access_control.py` | 0.34 | 0.67 | centrality (5 importers) |
| `app/routes/media.py` | 0.34 | 0.03 | churn (3 changes) |

## Module Briefs

### app/models/person.py [testability: 1.00] [attention: 0.21] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.9 C=0.6 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 6, 137 lines)
**Exports:** `NameDisplayOrder` (class), `Gender` (class), `DatePrecision` (class), `Visibility` (class), `AccountState` (class), `PersonSource` (class), `Person` (class)  
**Constructs:** 7 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/config.py [hotspot] [environment] [testability: 0.65] [attention: 0.42] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.5 C=0.6 E=1.0 S=0.9 T=0.3  
**Language:** python | **Complexity:** yellow (cyclomatic 13, 131 lines)
**Exports:** `Settings` (class), `get_settings` (function)  
**Constructs:** 1 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/database.py [testability: 1.00] [attention: 0.22] [domain-0] [database]

**Radar:** U=0.9 C=0.7 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 4, 48 lines)
**Exports:** `_build_url` (function), `_set_sqlite_pragmas` (function), `get_db` (function), `get_test_engine` (function)  
**Constructs:** 4 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/base.py [testability: 1.00] [attention: 0.10] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=1.0 C=0.8 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 21 lines)
**Exports:** `generate_uuid` (function), `utcnow` (function), `Base` (class), `TimestampMixin` (class)  
**Constructs:** 2 functions, 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/auth.py [testability: 0.70] [attention: 0.33] [domain-0]

**Radar:** U=0.9 C=0.5 E=0.5 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 4, 34 lines)
**Exports:** `get_current_user` (function), `require_auth` (function), `require_admin` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/relationships.py [testability: 1.00] [attention: 0.07] [domain-0]

**Radar:** U=0.8 C=0.8 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 111 lines)
**Exports:** `ParentChildKind` (class), `ParentChildConfidence` (class), `RelationshipSource` (class), `ParentChild` (class), `PartnershipKind` (class), `PartnershipStatus` (class), `Partnership` (class)  
**Constructs:** 7 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/media.py [testability: 1.00] [attention: 0.17] [domain-0]

**Radar:** U=0.9 C=0.8 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 2, 73 lines)
**Exports:** `MediaType` (class), `MediaSource` (class), `Media` (class)  
**Constructs:** 3 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/auth_service.py [hotspot] [testability: 0.85] [attention: 0.23] [domain-0]

**Radar:** U=0.6 C=0.9 E=1.0 S=1.0 T=0.3  
**Language:** python | **Complexity:** yellow (cyclomatic 16, 240 lines)
**Exports:** `_hash_token` (function), `generate_session_token` (function), `generate_invite_token` (function), `generate_magic_link_token` (function), `create_session` (function), `validate_session` (function), `delete_session` (function), `create_invite` (function), `get_valid_invite` (function), `claim_invite` (function)  
**Constructs:** 13 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/auth.py [testability: 1.00] [attention: 0.13] [domain-0]

**Radar:** U=0.9 C=0.9 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 1, 69 lines)
**Exports:** `AuthMethod` (class), `UserSession` (class), `Invite` (class), `MagicLinkToken` (class)  
**Constructs:** 4 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/moments.py [testability: 1.00] [attention: 0.15] [domain-0]

**Radar:** U=0.8 C=0.9 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 3, 136 lines)
**Exports:** `MomentKind` (class), `MilestoneType` (class), `MomentSource` (class), `MomentVisibility` (class), `OccurredPrecision` (class), `Moment` (class), `MomentReaction` (class), `MomentComment` (class)  
**Constructs:** 8 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/access_control.py [hotspot] [testability: 0.40] [attention: 0.34] [domain-0] [unobservable]

**Radar:** U=0.4 C=0.6 E=0.5 S=0.8 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 65, 254 lines)
**Exports:** `can_collaborate` (function), `get_person_access` (function), `get_accessible_person_ids` (function), `can_manage_person` (function), `can_view_media` (function), `can_view_moment` (function), `can_manage_moment` (function), `can_create_moment_for_person` (function), `redact_person_detail` (function), `redact_person_summary` (function)  
**Constructs:** 12 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/schemas.py [hotspot] [testability: 0.70] [attention: 0.28] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.8 C=0.6 E=0.5 S=0.8 T=0.4  
**Language:** python | **Complexity:** green (cyclomatic 3, 263 lines)
**Exports:** `PersonCreate` (class), `PersonUpdate` (class), `PersonSummary` (class), `PersonDetail` (class), `person_to_summary` (function), `person_to_detail` (function), `ParentChildCreate` (class), `ParentChildResponse` (class), `PartnershipCreate` (class), `PartnershipUpdate` (class)  
**Constructs:** 2 functions, 10 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/io_limits.py [hotspot] [filesystem] [testability: 0.35] [attention: 0.33] [domain-0]

**Radar:** U=0.5 C=0.6 E=0.5 S=0.9 T=0.5  
**Language:** python | **Complexity:** yellow (cyclomatic 12, 80 lines)
**Exports:** `SizeLimitExceeded` (class), `read_upload_limited` (function), `stream_upload_to_temp` (function), `read_response_limited` (function)  
**Constructs:** 3 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/audit.py [testability: 0.70] [attention: 0.15] [domain-0]

**Radar:** U=0.9 C=0.6 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 5, 52 lines)
**Exports:** `AuditAction` (class), `AuditLog` (class)  
**Constructs:** 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/__init__.py [testability: 1.00] [attention: 0.00] [domain-0]

**Radar:** U=1.0 C=0.9 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/media.py [hotspot] [testability: 0.70] [attention: 0.34] [domain-0] [endpoint]

**Radar:** U=0.3 C=1.0 E=1.0 S=1.0 T=0.3  
**Language:** python | **Complexity:** red (cyclomatic 37, 257 lines)
**Exports:** `_parse_tagged_person_ids` (function), `_build_tagged_people` (function), `_max_upload_size` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/moments.py [hotspot] [testability: 0.70] [attention: 0.34] [domain-0] [endpoint]

**Radar:** U=0.3 C=1.0 E=1.0 S=1.0 T=0.3  
**Language:** python | **Complexity:** red (cyclomatic 68, 548 lines)
**Exports:** `MomentCreate` (class), `MomentUpdate` (class), `PersonBrief` (class), `MediaBrief` (class), `MomentCard` (class), `CommentCreate` (class), `CommentResponse` (class), `ReactionCreate` (class), `_build_moment_card` (function)  
**Constructs:** 1 functions, 8 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/service.py [hotspot] [filesystem] [testability: 0.35] [attention: 0.32] [domain-0] [observable]

**Radar:** U=0.5 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 13, 122 lines)
**Exports:** `run_backup` (function), `create_download_zip` (function), `get_backup_health` (function), `_cleanup_old_backups` (function)  
**Constructs:** 4 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/i18n.py [hotspot] [filesystem] [testability: 0.35] [attention: 0.32] [domain-0] [observable]

**Radar:** U=0.5 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 14, 88 lines)
**Exports:** `load_translations` (function), `get_translations` (function), `get_relationship_terms` (function), `t` (function), `rel_term` (function), `_resolve_dotted` (function), `_count_keys` (function)  
**Constructs:** 7 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/auth_routes.py [hotspot] [testability: 0.85] [attention: 0.20] [domain-0] [endpoint]

**Radar:** U=0.6 C=1.0 E=1.0 S=1.0 T=0.3  
**Language:** python | **Complexity:** yellow (cyclomatic 17, 216 lines)
**Exports:** `GoogleCredentialRequest` (class), `AdminInviteResponse` (class), `_set_session_cookie` (function)  
**Constructs:** 1 functions, 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/persons.py [hotspot] [testability: 0.55] [attention: 0.30] [domain-0] [endpoint]

**Radar:** U=0.7 C=0.7 E=0.5 S=1.0 T=0.4  
**Language:** python | **Complexity:** yellow (cyclomatic 14, 181 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/relationships.py [hotspot] [testability: 0.85] [attention: 0.20] [domain-0] [endpoint]

**Radar:** U=0.6 C=1.0 E=1.0 S=1.0 T=0.3  
**Language:** python | **Complexity:** yellow (cyclomatic 20, 223 lines)
**Exports:** `_would_create_ancestry_cycle` (function), `_partnership_exists` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/tree.py [hotspot] [testability: 0.55] [attention: 0.35] [domain-0] [endpoint]

**Radar:** U=0.6 C=0.7 E=0.5 S=1.0 T=0.3  
**Language:** python | **Complexity:** yellow (cyclomatic 17, 222 lines)
**Exports:** `TreePreferencesPayload` (class), `MapMarkerPerson` (class), `MapMarker` (class), `MapResponse` (class), `_get_or_create_tree_preferences` (function), `_filtered_tree_people` (function)  
**Constructs:** 2 functions, 4 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/google_auth.py [hotspot] [testability: 0.85] [attention: 0.10] [domain-0]

**Radar:** U=0.7 C=1.0 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** yellow (cyclomatic 11, 52 lines)
**Exports:** `GoogleAuthError` (class), `verify_google_credential` (function), `_optional_str` (function)  
**Constructs:** 2 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/imports.py [testability: 0.70] [attention: 0.14] [domain-0]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 5, 135 lines)
**Exports:** `ImportStatus` (class), `WhatsappImportBatch` (class), `MessengerImportBatch` (class), `AgentApiKey` (class), `ExternalIdentity` (class), `MemorialPlan` (class)  
**Constructs:** 6 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/preferences.py [testability: 0.70] [attention: 0.15] [domain-0]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 2, 37 lines)
**Exports:** `TreePreference` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/health.py [testability: 1.00] [attention: 0.00] [domain-0] [endpoint]

**Radar:** U=1.0 C=1.0 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 3, 20 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/audit_service.py [testability: 0.70] [attention: 0.14] [domain-0]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 23 lines)
**Exports:** `log_audit` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/inbound/routes.py [hotspot] [filesystem] [testability: 0.20] [attention: 0.41] [domain-0] [observable] [endpoint]

**Radar:** U=0.2 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 29, 188 lines)
**Exports:** `EnvelopeAttachment` (class), `EnvelopePayload` (class), `_ext_from_mime` (function), `_is_allowed_attachment_url` (function)  
**Constructs:** 2 functions, 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/middleware/security.py [hotspot] [testability: 0.40] [attention: 0.44] [domain-0] [observable]

**Radar:** U=0.3 C=0.7 E=0.5 S=1.0 T=0.4  
**Language:** python | **Complexity:** red (cyclomatic 21, 188 lines)
**Exports:** `add_security_middleware` (function), `SecurityHeadersMiddleware` (class), `BodySizeLimitMiddleware` (class), `RateLimitMiddleware` (class)  
**Constructs:** 1 functions, 3 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/pages.py [hotspot] [testability: 0.40] [attention: 0.51] [domain-0] [endpoint]

**Radar:** U=0.3 C=0.7 E=0.5 S=1.0 T=0.3  
**Language:** python | **Complexity:** red (cyclomatic 79, 701 lines)
**Exports:** `_get_locale` (function), `_country_flag` (function), `_ctx` (function), `_build_moment_card_simple` (function)  
**Constructs:** 4 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/media_service.py [hotspot] [filesystem] [testability: 0.20] [attention: 0.52] [domain-0]

**Radar:** U=0.2 C=0.7 E=0.5 S=0.9 T=0.3  
**Language:** python | **Complexity:** red (cyclomatic 45, 282 lines)
**Exports:** `_category_for_mime` (function), `_media_type_for_mime` (function), `compute_sha256` (function), `strip_exif` (function), `generate_thumbnail` (function), `get_image_dimensions` (function), `check_duplicate` (function), `save_media_file` (function), `save_media_temp_file` (function)  
**Constructs:** 9 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/matrix/client.py [hotspot] [testability: 0.55] [attention: 0.23] [domain-0] [observable]

**Radar:** U=0.6 C=0.7 E=0.5 S=1.0 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 14, 219 lines)
**Exports:** `MatrixClient` (class), `create_matrix_client` (function)  
**Constructs:** 1 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/matrix/handler.py [hotspot] [filesystem] [testability: 0.35] [attention: 0.31] [domain-0] [observable] [database]

**Radar:** U=0.4 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 18, 237 lines)
**Exports:** `MatrixEventHandler` (class), `_event_timestamp` (function), `_ext_from_mime` (function)  
**Constructs:** 2 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/bootstrap_service.py [hotspot] [testability: 0.55] [attention: 0.24] [domain-0] [observable] [database]

**Radar:** U=0.7 C=0.7 E=0.5 S=1.0 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 11, 59 lines)
**Exports:** `ensure_bootstrap_admin` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/__init__.py [testability: 1.00] [attention: 0.00] [domain-0]

**Radar:** U=1.0 C=1.0 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/routes.py [testability: 0.70] [attention: 0.13] [domain-0] [endpoint]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 40 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/scheduler.py [testability: 0.70] [attention: 0.13] [domain-0] [observable]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 5, 63 lines)
**Exports:** `_next_3am_utc` (function), `_run_and_reschedule` (function), `start_backup_scheduler` (function), `stop_backup_scheduler` (function)  
**Constructs:** 4 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/main.py [filesystem] [testability: 0.80] [attention: 0.14] [domain-0] [observable]

**Radar:** U=0.7 C=1.0 E=1.0 S=0.9 T=0.6  
**Language:** python | **Complexity:** green (cyclomatic 9, 121 lines)
**Exports:** `create_app` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/matrix/startup.py [testability: 0.70] [attention: 0.13] [domain-0] [observable]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 6, 61 lines)
**Exports:** `start_matrix_bot` (function), `stop_matrix_bot` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/__init__.py [testability: 0.70] [attention: 0.24] [domain-0]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 1, 43 lines)
**Exports:** `Base` (function), `Person` (function), `ParentChild` (function), `Partnership` (function), `Media` (function), `Moment` (function), `MomentReaction` (function), `MomentComment` (function), `UserSession` (function), `Invite` (function)  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/governance.py [testability: 0.70] [attention: 0.13] [domain-0]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 81 lines)
**Exports:** `ApprovalKind` (class), `ApprovalThreshold` (class), `ApprovalStatus` (class), `ApprovalRequest` (class), `VoteChoice` (class), `ApprovalVote` (class)  
**Constructs:** 6 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/notifications.py [testability: 0.70] [attention: 0.13] [domain-0]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 100 lines)
**Exports:** `NotificationKind` (class), `Notification` (class), `DeliveryChannel` (class), `DeliveryStatus` (class), `NotificationDelivery` (class), `PushChannel` (class), `PushFrequency` (class), `NotificationPreference` (class)  
**Constructs:** 8 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/pwa/routes.py [filesystem] [testability: 0.50] [attention: 0.21] [domain-0] [observable] [endpoint]

**Radar:** U=0.8 C=0.7 E=0.5 S=0.9 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 6, 91 lines)
**Exports:** `_ext_from_content_type` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/geo.py [testability: 0.70] [attention: 0.14] [domain-0]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 2, 56 lines)
**Exports:** `country_centroid` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/js/main.js [hotspot] [network] [testability: 0.20] [attention: 0.40] [service]

**Radar:** U=0.2 C=0.7 E=0.5 S=0.9 T=0.5  
**Language:** javascript | **Complexity:** red (cyclomatic 23, 133 lines)
**Constructs:** 9 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/js/tree.js [hotspot] [network] [testability: 0.20] [attention: 0.43] [service]

**Radar:** U=0.2 C=0.7 E=0.5 S=0.9 T=0.5  
**Language:** javascript | **Complexity:** red (cyclomatic 49, 444 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/seed.py [hotspot] [filesystem] [testability: 0.35] [domain-0] [observable] [database]

**Radar:** U=0.5 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 14, 67 lines)
**Exports:** `seed` (function), `main` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/js/map.js [hotspot] [network] [testability: 0.35] [attention: 0.30] [service]

**Radar:** U=0.5 C=0.7 E=0.5 S=0.9 T=0.5  
**Language:** javascript | **Complexity:** yellow (cyclomatic 19, 150 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/conftest.py [hotspot] [environment] [domain-0] [database]

**Language:** python | **Complexity:** yellow (cyclomatic 11, 239 lines)
**Exports:** `_set_sqlite_pragmas` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/README [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 1 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/env.py [environment] [testability: 0.50] [domain-0]

**Radar:** U=0.8 C=0.7 E=0.5 S=0.9 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 6, 54 lines)
**Exports:** `run_migrations_offline` (function), `run_migrations_online` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/script.py.mako [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 28 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/versions/2e7d8d8d6d4b_add_google_auth_fields.py [testability: 0.70]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 33 lines)
**Exports:** `upgrade` (function), `downgrade` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/versions/4f3c2e1a9b7d_add_rich_profile_fields_and_tags.py [testability: 0.70]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 7, 41 lines)
**Exports:** `upgrade` (function), `downgrade` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/versions/75d48eb17ca2_initial_schema.py [testability: 0.70]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 5, 399 lines)
**Exports:** `upgrade` (function), `downgrade` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/versions/9b3f4d7c1a2e_add_tree_preferences.py [testability: 0.70]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 33 lines)
**Exports:** `upgrade` (function), `downgrade` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### alembic/versions/c6a8d41f2b5e_add_burial_country_code.py [testability: 0.70]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=1.0  
**Language:** python | **Complexity:** green (cyclomatic 3, 25 lines)
**Exports:** `upgrade` (function), `downgrade` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/inbound/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/matrix/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/middleware/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/pwa/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/__init__.py [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/css/main.css [testability: 0.70] [attention: 0.12]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 684 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/manifest.json [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 42 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/static/sw.js [network] [testability: 0.50] [attention: 0.20] [service]

**Radar:** U=0.8 C=0.7 E=0.5 S=0.9 T=0.7  
**Language:** javascript | **Complexity:** green (cyclomatic 7, 68 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/admin.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 167 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/base.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 52 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/home.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 175 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/invite.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 61 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/landing.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 18 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/login.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 78 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/map.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 114 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/audit_log.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 15 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/comments.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 18 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/media_gallery.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 29 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/moment_card.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 130 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/people_grid.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 24 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/person_sidebar.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 45 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/people.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 34 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/person.html [testability: 0.70] [attention: 0.16]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 147 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/person_edit.html [testability: 0.70] [attention: 0.16]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 244 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/person_new.html [testability: 0.70] [attention: 0.16]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 138 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/settings.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 67 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/tree.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 175 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/en.json [hotspot] [testability: 0.70] [attention: 0.27]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.3  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 128 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/es.json [hotspot] [testability: 0.70] [attention: 0.27]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.3  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 128 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/relationships/en.json [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 45 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/relationships/es.json [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 45 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/relationships/ru.json [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 45 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/ru.json [hotspot] [testability: 0.70] [attention: 0.27]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.3  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 128 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/__init__.py

**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_api.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 536 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_auth.py [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 3, 276 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_comments.py [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 131 lines)
**Exports:** `TestComments` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_media.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 2, 358 lines)
**Exports:** `_make_test_image` (function), `_make_test_png` (function), `TestMediaUpload` (class), `TestMediaDedup` (class), `TestMediaServing` (class), `TestMediaThumbnails` (class), `TestMediaMetadata` (class)  
**Constructs:** 2 functions, 5 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_models.py [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 4, 188 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_moments.py [hotspot] [service]

**Language:** python | **Complexity:** green (cyclomatic 5, 277 lines)
**Exports:** `TestMomentsCRUD` (class), `TestMomentsFeed` (class), `TestMomentsPermissions` (class)  
**Constructs:** 3 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_phase1_edge_cases.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 3, 277 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_reactions.py [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 133 lines)
**Exports:** `TestReactions` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

## Modules Without Briefings

- `app/models/person.py`
- `app/config.py`
- `app/database.py`
- `app/models/base.py`
- `app/auth.py`
- `app/models/relationships.py`
- `app/models/media.py`
- `app/services/auth_service.py`
- `app/models/auth.py`
- `app/models/moments.py`
- `app/access_control.py`
- `app/schemas.py`
- `app/services/io_limits.py`
- `app/models/audit.py`
- `app/routes/__init__.py`
- `app/routes/media.py`
- `app/routes/moments.py`
- `app/backup/service.py`
- `app/i18n.py`
- `app/routes/auth_routes.py`
- `app/routes/persons.py`
- `app/routes/relationships.py`
- `app/routes/tree.py`
- `app/services/google_auth.py`
- `app/models/imports.py`
- `app/models/preferences.py`
- `app/routes/health.py`
- `app/services/audit_service.py`
- `app/inbound/routes.py`
- `app/middleware/security.py`
- `app/routes/pages.py`
- `app/services/media_service.py`
- `app/matrix/client.py`
- `app/matrix/handler.py`
- `app/services/bootstrap_service.py`
- `app/__init__.py`
- `app/backup/routes.py`
- `app/backup/scheduler.py`
- `app/main.py`
- `app/matrix/startup.py`
- `app/models/__init__.py`
- `app/models/governance.py`
- `app/models/notifications.py`
- `app/pwa/routes.py`
- `app/services/geo.py`
- `app/static/js/main.js`
- `app/static/js/tree.js`
- `app/seed.py`
- `app/static/js/map.js`
- `tests/conftest.py`
- `alembic/README`
- `alembic/env.py`
- `alembic/script.py.mako`
- `alembic/versions/2e7d8d8d6d4b_add_google_auth_fields.py`
- `alembic/versions/4f3c2e1a9b7d_add_rich_profile_fields_and_tags.py`
- `alembic/versions/75d48eb17ca2_initial_schema.py`
- `alembic/versions/9b3f4d7c1a2e_add_tree_preferences.py`
- `alembic/versions/c6a8d41f2b5e_add_burial_country_code.py`
- `app/backup/__init__.py`
- `app/inbound/__init__.py`
- `app/matrix/__init__.py`
- `app/middleware/__init__.py`
- `app/pwa/__init__.py`
- `app/services/__init__.py`
- `app/static/css/main.css`
- `app/static/manifest.json`
- `app/static/sw.js`
- `app/templates/admin.html`
- `app/templates/base.html`
- `app/templates/home.html`
- `app/templates/invite.html`
- `app/templates/landing.html`
- `app/templates/login.html`
- `app/templates/map.html`
- `app/templates/partials/audit_log.html`
- `app/templates/partials/comments.html`
- `app/templates/partials/media_gallery.html`
- `app/templates/partials/moment_card.html`
- `app/templates/partials/people_grid.html`
- `app/templates/partials/person_sidebar.html`
- `app/templates/people.html`
- `app/templates/person.html`
- `app/templates/person_edit.html`
- `app/templates/person_new.html`
- `app/templates/settings.html`
- `app/templates/tree.html`
- `locales/en.json`
- `locales/es.json`
- `locales/relationships/en.json`
- `locales/relationships/es.json`
- `locales/relationships/ru.json`
- `locales/ru.json`
- `tests/__init__.py`
- `tests/test_api.py`
- `tests/test_auth.py`
- `tests/test_comments.py`
- `tests/test_media.py`
- `tests/test_models.py`
- `tests/test_moments.py`
- `tests/test_phase1_edge_cases.py`
- `tests/test_reactions.py`

---

*Generated by CodeMap on 2026-03-23 22:28 UTC. Estimated tokens: ~0 (0 words × 1.3). ACE ratio: N/A.*
