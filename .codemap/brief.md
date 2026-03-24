# family-book — Agent Brief

**Modules:** 114  
**Languages:** python (80), unknown (30), javascript (4)  
**With AI briefings:** 0/114

## Architecture Overview

**Hub modules** (imported by others): `app/models/person.py` (26), `app/config.py` (18), `app/database.py` (13), `app/models/base.py` (12), `app/auth.py` (9), `app/models/relationships.py` (9), `app/models/media.py` (8), `app/models/moments.py` (8), `app/access_control.py` (7), `app/services/field_protection.py` (7)

**Leaf modules** (import others, not imported): `app/seed.py`, `tests/conftest.py`, `alembic/env.py`, `tests/test_access_control.py`, `tests/test_api.py`, `tests/test_auth.py`, `tests/test_media.py`, `tests/test_models.py`, `tests/test_phase1_edge_cases.py`, `tests/test_protection_service.py`

## Domain Architecture

**domain-0** (63 modules): `app/models/person.py`, `app/config.py`, `app/database.py`, `app/models/base.py`, `app/auth.py`, `app/models/relationships.py`, `app/models/media.py`, `app/models/moments.py`
  ... and 55 more

## Architecture Roles

- **Core**: `app/models/person.py`, `app/config.py`, `app/models/base.py`, `app/models/moments.py`, `app/services/field_protection.py` (+1 more)
- **Utility**: `app/database.py`, `app/auth.py`, `app/models/relationships.py`, `app/models/media.py`, `app/access_control.py` (+88 more)
- **Test Support**: `tests/conftest.py`, `tests/__init__.py`, `tests/test_access_control.py`, `tests/test_api.py`, `tests/test_auth.py` (+10 more)

## Top Modules Requiring Review

| Module | Score | Centrality | Top Factor |
|---|---:|---:|---|
| `app/config.py` | 0.51 | 1.00 | centrality (18 importers) |
| `app/routes/pages.py` | 0.51 | 0.00 | churn (7 changes) |
| `app/backup/service.py` | 0.49 | 0.13 | centrality (3 importers) |
| `app/services/media_service.py` | 0.46 | 0.08 | churn (3 changes) |
| `app/middleware/security.py` | 0.44 | 0.03 | complexity (red) |
| `app/static/js/tree.js` | 0.43 | 0.00 | complexity (red) |
| `app/inbound/routes.py` | 0.41 | 0.03 | complexity (red) |
| `app/static/js/main.js` | 0.40 | 0.00 | complexity (red) |
| `app/services/moment_service.py` | 0.39 | 0.17 | churn (3 changes) |
| `app/routes/media.py` | 0.37 | 0.00 | churn (6 changes) |

## Module Briefs

### app/models/person.py [hotspot] [testability: 1.00] [attention: 0.33] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.9 C=0.6 E=1.0 S=1.0 T=0.4  
**Language:** python | **Complexity:** green (cyclomatic 6, 173 lines)
**Exports:** `EncryptedText` (class), `NameDisplayOrder` (class), `Gender` (class), `DatePrecision` (class), `Visibility` (class), `AccountState` (class), `PersonLifecycleState` (class), `PersonSource` (class), `Person` (class)  
**Constructs:** 9 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/config.py [hotspot] [environment] [testability: 0.35] [attention: 0.51] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.6 C=0.4 E=0.5 S=0.7 T=0.4  
**Language:** python | **Complexity:** yellow (cyclomatic 13, 132 lines)
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

### app/models/moments.py [hotspot] [testability: 0.70] [attention: 0.25] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.9 C=0.6 E=0.5 S=0.8 T=0.6  
**Language:** python | **Complexity:** green (cyclomatic 3, 150 lines)
**Exports:** `MomentKind` (class), `MilestoneType` (class), `MomentSource` (class), `MomentVisibility` (class), `OccurredPrecision` (class), `MomentLifecycleState` (class), `Moment` (class), `MomentReaction` (class), `MomentComment` (class)  
**Constructs:** 9 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/access_control.py [hotspot] [testability: 0.70] [attention: 0.30] [domain-0] [observable]

**Radar:** U=0.4 C=0.9 E=1.0 S=1.0 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 73, 277 lines)
**Exports:** `can_collaborate` (function), `get_person_access` (function), `get_accessible_person_ids` (function), `can_manage_person` (function), `can_view_media` (function), `can_view_moment` (function), `can_manage_moment` (function), `can_create_moment_for_person` (function), `redact_person_detail` (function), `redact_person_summary` (function)  
**Constructs:** 12 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/field_protection.py [testability: 0.85] [attention: 0.00] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.7 C=0.9 E=1.0 S=1.0 T=0.8  
**Language:** python | **Complexity:** yellow (cyclomatic 16, 125 lines)
**Exports:** `ProtectionConfigurationError` (class), `ProtectedFieldDecryptionError` (class), `normalize_email_for_lookup` (function), `contact_email_lookup_hash` (function), `is_valid_fernet_key` (function), `get_fernet` (function), `encrypt_string` (function), `decrypt_string` (function), `encrypt_mapping_fields` (function), `decrypt_mapping_fields` (function)  
**Constructs:** 9 functions, 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/auth_service.py [hotspot] [testability: 0.85] [attention: 0.22] [domain-0]

**Radar:** U=0.7 C=0.9 E=1.0 S=1.0 T=0.4  
**Language:** python | **Complexity:** yellow (cyclomatic 15, 243 lines)
**Exports:** `_hash_token` (function), `generate_session_token` (function), `generate_invite_token` (function), `generate_magic_link_token` (function), `create_session` (function), `validate_session` (function), `delete_session` (function), `create_invite` (function), `get_valid_invite` (function), `claim_invite` (function)  
**Constructs:** 13 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/auth.py [testability: 1.00] [attention: 0.13] [domain-0]

**Radar:** U=0.9 C=0.9 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** green (cyclomatic 1, 69 lines)
**Exports:** `AuthMethod` (class), `UserSession` (class), `Invite` (class), `MagicLinkToken` (class)  
**Constructs:** 4 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/schemas.py [hotspot] [testability: 0.70] [attention: 0.28] [CRITICAL] [domain-0] [unobservable]

**Radar:** U=0.8 C=0.6 E=0.5 S=0.8 T=0.4  
**Language:** python | **Complexity:** green (cyclomatic 3, 263 lines)
**Exports:** `PersonCreate` (class), `PersonUpdate` (class), `PersonSummary` (class), `PersonDetail` (class), `person_to_summary` (function), `person_to_detail` (function), `ParentChildCreate` (class), `ParentChildResponse` (class), `PartnershipCreate` (class), `PartnershipUpdate` (class)  
**Constructs:** 2 functions, 10 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/revision_service.py [testability: 1.00] [attention: 0.02] [domain-0] [observable]

**Radar:** U=0.9 C=0.9 E=1.0 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 10, 184 lines)
**Exports:** `_serialize_datetime` (function), `_parse_datetime` (function), `serialize_person_snapshot` (function), `apply_person_snapshot` (function), `serialize_moment_snapshot` (function), `apply_moment_snapshot` (function), `record_revision` (function), `list_revisions` (function), `get_revision` (function)  
**Constructs:** 9 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/service.py [hotspot] [filesystem] [testability: 0.20] [attention: 0.49] [domain-0] [observable]

**Radar:** U=0.3 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 34, 283 lines)
**Exports:** `_backup_dir` (function), `_restore_verification_path` (function), `_load_restore_verification` (function), `_write_restore_verification` (function), `_latest_backup` (function), `_restore_supported` (function), `run_backup` (function), `create_download_zip` (function), `get_backup_health` (function), `restore_backup_archive` (function)  
**Constructs:** 12 functions  

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

### app/models/revisions.py [testability: 0.70] [attention: 0.10] [domain-0]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 1, 30 lines)
**Exports:** `EntityRevision` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/__init__.py [testability: 1.00] [attention: 0.00] [domain-0]

**Radar:** U=1.0 C=0.9 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/auth_routes.py [hotspot] [testability: 0.70] [attention: 0.29] [domain-0] [observable] [endpoint]

**Radar:** U=0.4 C=1.0 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** red (cyclomatic 21, 235 lines)
**Exports:** `GoogleCredentialRequest` (class), `AdminInviteResponse` (class), `_set_session_cookie` (function)  
**Constructs:** 1 functions, 2 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/media.py [hotspot] [testability: 0.70] [attention: 0.37] [domain-0] [observable] [endpoint]

**Radar:** U=0.4 C=1.0 E=1.0 S=1.0 T=0.4  
**Language:** python | **Complexity:** red (cyclomatic 43, 285 lines)
**Exports:** `_parse_tagged_person_ids` (function), `_build_tagged_people` (function), `_max_upload_size` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/moments.py [hotspot] [testability: 0.70] [attention: 0.37] [domain-0] [observable] [endpoint]

**Radar:** U=0.3 C=1.0 E=1.0 S=1.0 T=0.4  
**Language:** python | **Complexity:** red (cyclomatic 87, 811 lines)
**Exports:** `MomentCreate` (class), `MomentUpdate` (class), `PersonBrief` (class), `MediaBrief` (class), `MomentCard` (class), `CommentCreate` (class), `CommentResponse` (class), `ReactionCreate` (class), `ModerateMomentRequest` (class), `_has_moment_content` (function)  
**Constructs:** 6 functions, 9 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/persons.py [hotspot] [testability: 0.70] [attention: 0.29] [domain-0] [observable] [endpoint]

**Radar:** U=0.4 C=1.0 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** red (cyclomatic 29, 333 lines)
**Exports:** `_person_history_entries` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/relationships.py [hotspot] [testability: 0.70] [attention: 0.21] [domain-0] [observable] [endpoint]

**Radar:** U=0.4 C=1.0 E=1.0 S=1.0 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 22, 233 lines)
**Exports:** `_would_create_ancestry_cycle` (function), `_partnership_exists` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/moment_service.py [hotspot] [testability: 0.40] [attention: 0.39] [domain-0]

**Radar:** U=0.4 C=0.7 E=0.5 S=1.0 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 28, 244 lines)
**Exports:** `_moment_order` (function), `_tagged_person_match` (function), `list_visible_moments` (function), `build_moment_cards` (function), `build_moment_card` (function), `build_moments_path` (function)  
**Constructs:** 6 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/i18n.py [hotspot] [filesystem] [testability: 0.35] [attention: 0.32] [domain-0] [observable]

**Radar:** U=0.5 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** yellow (cyclomatic 14, 88 lines)
**Exports:** `load_translations` (function), `get_translations` (function), `get_relationship_terms` (function), `t` (function), `rel_term` (function), `_resolve_dotted` (function), `_count_keys` (function)  
**Constructs:** 7 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/routes/tree.py [hotspot] [testability: 0.85] [attention: 0.23] [domain-0] [observable] [endpoint]

**Radar:** U=0.7 C=1.0 E=1.0 S=1.0 T=0.4  
**Language:** python | **Complexity:** yellow (cyclomatic 17, 239 lines)
**Exports:** `TreePreferencesPayload` (class), `MapMarkerPerson` (class), `MapMarker` (class), `MapResponse` (class), `_get_or_create_tree_preferences` (function), `_filtered_tree_people` (function)  
**Constructs:** 2 functions, 4 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/google_auth.py [hotspot] [testability: 0.85] [attention: 0.10] [domain-0]

**Radar:** U=0.7 C=1.0 E=1.0 S=1.0 T=0.5  
**Language:** python | **Complexity:** yellow (cyclomatic 11, 52 lines)
**Exports:** `GoogleAuthError` (class), `verify_google_credential` (function), `_optional_str` (function)  
**Constructs:** 2 functions, 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/protection_service.py [hotspot] [testability: 0.85] [attention: 0.04] [domain-0] [observable] [database]

**Radar:** U=0.7 C=1.0 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** yellow (cyclomatic 16, 166 lines)
**Exports:** `_protect_person_rows` (function), `_protect_revision_rows` (function), `_assert_readable_protected_data` (function), `ensure_sensitive_person_fields_protected` (function)  
**Constructs:** 4 functions  

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

### app/routes/health.py [testability: 1.00] [attention: 0.00] [domain-0] [observable] [endpoint]

**Radar:** U=1.0 C=1.0 E=1.0 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 3, 25 lines)

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

### app/routes/pages.py [hotspot] [testability: 0.40] [attention: 0.51] [domain-0] [observable] [endpoint]

**Radar:** U=0.3 C=0.7 E=0.5 S=1.0 T=0.4  
**Language:** python | **Complexity:** red (cyclomatic 72, 732 lines)
**Exports:** `_get_locale` (function), `_country_flag` (function), `_ctx` (function), `_moment_people` (function), `_actor_names` (function)  
**Constructs:** 5 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/services/media_service.py [hotspot] [filesystem] [testability: 0.20] [attention: 0.46] [domain-0]

**Radar:** U=0.2 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** red (cyclomatic 49, 296 lines)
**Exports:** `_category_for_mime` (function), `_media_type_for_mime` (function), `compute_sha256` (function), `strip_exif` (function), `generate_thumbnail` (function), `get_image_dimensions` (function), `check_duplicate` (function), `save_media_file` (function), `save_media_temp_file` (function), `delete_media_files` (function)  
**Constructs:** 10 functions  

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

**Radar:** U=0.7 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** python | **Complexity:** yellow (cyclomatic 11, 60 lines)
**Exports:** `ensure_bootstrap_admin` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/__init__.py [testability: 1.00] [attention: 0.00] [domain-0]

**Radar:** U=1.0 C=1.0 E=1.0 S=1.0 T=0.7  
**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/routes.py [testability: 0.70] [attention: 0.14] [domain-0] [observable] [endpoint]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 1, 59 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/backup/scheduler.py [testability: 0.70] [attention: 0.13] [domain-0] [observable]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 5, 63 lines)
**Exports:** `_next_3am_utc` (function), `_run_and_reschedule` (function), `start_backup_scheduler` (function), `stop_backup_scheduler` (function)  
**Constructs:** 4 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/main.py [filesystem] [testability: 0.50] [attention: 0.30] [domain-0] [observable]

**Radar:** U=0.8 C=0.7 E=0.5 S=0.9 T=0.6  
**Language:** python | **Complexity:** green (cyclomatic 9, 123 lines)
**Exports:** `create_app` (function)  
**Constructs:** 1 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/matrix/startup.py [testability: 0.70] [attention: 0.13] [domain-0] [observable]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 6, 61 lines)
**Exports:** `start_matrix_bot` (function), `stop_matrix_bot` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/models/__init__.py [hotspot] [testability: 0.70] [attention: 0.18] [domain-0]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.6  
**Language:** python | **Complexity:** green (cyclomatic 1, 45 lines)
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

### alembic/versions/8c1f9e6b7d11_add_sensitive_field_encryption_support.py [testability: 0.70]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 3, 39 lines)
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

### alembic/versions/f3c4b8e1a9d2_add_revisions_and_recoverable_state.py [testability: 0.70]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** python | **Complexity:** green (cyclomatic 5, 63 lines)
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

### app/templates/admin.html [hotspot] [testability: 0.70] [attention: 0.19]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 191 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/base.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 52 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/home.html [hotspot] [testability: 0.70] [attention: 0.24]

**Radar:** U=0.8 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 341 lines)

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

### app/templates/partials/moment_card.html [hotspot] [testability: 0.70] [attention: 0.22]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 170 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/people_grid.html [testability: 0.70] [attention: 0.12]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 24 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/person_history.html [testability: 0.70] [attention: 0.07]

**Radar:** U=1.0 C=0.7 E=0.5 S=1.0 T=0.8  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 33 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/partials/person_sidebar.html [testability: 0.70] [attention: 0.12]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.7  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 45 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/people.html [testability: 0.70] [attention: 0.23]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 34 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### app/templates/person.html [hotspot] [testability: 0.70] [attention: 0.24]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 311 lines)

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

### locales/en.json [hotspot] [testability: 0.70] [attention: 0.22]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 142 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### locales/es.json [hotspot] [testability: 0.70] [attention: 0.22]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 142 lines)

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

### locales/ru.json [hotspot] [testability: 0.70] [attention: 0.22]

**Radar:** U=0.9 C=0.7 E=0.5 S=1.0 T=0.5  
**Language:** unknown | **Complexity:** green (cyclomatic 1, 142 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/__init__.py

**Language:** python | **Complexity:** green (cyclomatic 1, 0 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_access_control.py [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 1, 99 lines)
**Exports:** `test_can_collaborate_requires_active_account` (function), `test_can_manage_person_blocks_deleted_profile` (function), `test_redact_person_detail_hides_sensitive_fields_without_profile_access` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_api.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 697 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_auth.py [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 3, 300 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_comments.py [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 131 lines)
**Exports:** `TestComments` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_media.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 2, 405 lines)
**Exports:** `_make_test_image` (function), `_make_test_png` (function), `TestMediaUpload` (class), `TestMediaDedup` (class), `TestMediaServing` (class), `TestMediaDeletion` (class), `TestMediaThumbnails` (class), `TestMediaMetadata` (class)  
**Constructs:** 2 functions, 6 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_models.py [hotspot] [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 4, 227 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_moments.py [hotspot] [service]

**Language:** python | **Complexity:** green (cyclomatic 5, 506 lines)
**Exports:** `TestMomentsCRUD` (class), `TestMomentsFeed` (class), `TestMomentsPermissions` (class)  
**Constructs:** 3 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_phase1_edge_cases.py [hotspot] [domain-0] [service]

**Language:** python | **Complexity:** green (cyclomatic 3, 277 lines)

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_protection_service.py [domain-0] [database]

**Language:** python | **Complexity:** green (cyclomatic 5, 96 lines)
**Exports:** `test_invalid_fernet_key_is_rejected` (function), `test_decrypt_string_raises_for_wrong_key` (function), `test_protection_contract_reports_invalid_key` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_reactions.py [service]

**Language:** python | **Complexity:** green (cyclomatic 1, 133 lines)
**Exports:** `TestReactions` (class)  
**Constructs:** 1 classes  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_revision_service.py [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 1, 39 lines)
**Exports:** `test_person_snapshot_encrypts_sensitive_fields` (function), `test_apply_person_snapshot_restores_sensitive_fields` (function)  
**Constructs:** 2 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_schema_models.py [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 1, 54 lines)
**Exports:** `test_person_schema_helpers_preserve_expected_fields` (function), `test_root_person_detail_redacts_name_fields` (function), `test_moment_model_list_properties_round_trip` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

### tests/test_security_guardrails.py [domain-0]

**Language:** python | **Complexity:** green (cyclomatic 5, 85 lines)
**Exports:** `_request` (function), `test_add_security_middleware_registers_expected_stack` (function), `test_rate_limit_resolve_key_prefers_session_cookie` (function)  
**Constructs:** 3 functions  

> *(no AI briefing — run `codemap analyze --ai` to generate)*

## Modules Without Briefings

- `app/models/person.py`
- `app/config.py`
- `app/database.py`
- `app/models/base.py`
- `app/auth.py`
- `app/models/relationships.py`
- `app/models/media.py`
- `app/models/moments.py`
- `app/access_control.py`
- `app/services/field_protection.py`
- `app/services/auth_service.py`
- `app/models/auth.py`
- `app/schemas.py`
- `app/services/revision_service.py`
- `app/backup/service.py`
- `app/services/io_limits.py`
- `app/models/audit.py`
- `app/models/revisions.py`
- `app/routes/__init__.py`
- `app/routes/auth_routes.py`
- `app/routes/media.py`
- `app/routes/moments.py`
- `app/routes/persons.py`
- `app/routes/relationships.py`
- `app/services/moment_service.py`
- `app/i18n.py`
- `app/routes/tree.py`
- `app/services/google_auth.py`
- `app/services/protection_service.py`
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
- `alembic/versions/8c1f9e6b7d11_add_sensitive_field_encryption_support.py`
- `alembic/versions/9b3f4d7c1a2e_add_tree_preferences.py`
- `alembic/versions/c6a8d41f2b5e_add_burial_country_code.py`
- `alembic/versions/f3c4b8e1a9d2_add_revisions_and_recoverable_state.py`
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
- `app/templates/partials/person_history.html`
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
- `tests/test_access_control.py`
- `tests/test_api.py`
- `tests/test_auth.py`
- `tests/test_comments.py`
- `tests/test_media.py`
- `tests/test_models.py`
- `tests/test_moments.py`
- `tests/test_phase1_edge_cases.py`
- `tests/test_protection_service.py`
- `tests/test_reactions.py`
- `tests/test_revision_service.py`
- `tests/test_schema_models.py`
- `tests/test_security_guardrails.py`

---

*Generated by CodeMap on 2026-03-24 00:14 UTC. Estimated tokens: ~0 (0 words × 1.3). ACE ratio: N/A.*
