# Family Book Backlog

Sprint: `S40 - Tree Context Menu (Phase 1: Tree-Native Interactions)`
Status: Ready

## Current Sprint `S40 - Tree Context Menu`

Sprint goal:
- Add a right-click / long-press context menu on tree nodes with the most common actions, and remove the hover-only buttons it replaces.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-081 | Tree Node Context Menu | P0 | todo | `task_packets/FB-081_tree_node_context_menu.md` |
| FB-082 | Remove Node Hover Buttons | P1 | todo | `task_packets/FB-082_remove_node_hover_buttons.md` |

Execution slices:
- `S40-1` Context menu: right-click/long-press, 7 actions, keyboard nav, viewport positioning, i18n
- `S40-2` Remove camera icon and plus button overlays from nodes

## Closed Sprint `S39 - Ancestor Branch View`

Status: Done

## Current Sprint `S39 - Ancestor Branch View`

Sprint goal:
- Add ancestor branch filtering so users can focus on a single lineage within the family tree.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-080 | Ancestor Branch View | P0 | done | `task_packets/FB-080_ancestor_branch_view.md` |

Execution slices:
- `S39-1` Client-side ancestor collection, tree filtering, banner, URL state, sidebar button, i18n

## Closed Sprint `S38 - Tree Sidebar Redesign`

Status: Done

## Current Sprint `S38 - Tree Sidebar Redesign`

Sprint goal:
- Transform the tree sidebar from a form-heavy wall into a reading surface that answers "who is this person?" in under 2 seconds, with editing as a smooth secondary mode.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-077 | Left Panel Cleanup | P1 | done | `task_packets/FB-077_left_panel_cleanup.md` |
| FB-078 | Sidebar Identity and Orientation Redesign | P0 | done | `task_packets/FB-078_sidebar_identity_and_orientation_redesign.md` |
| FB-079 | Sidebar Details Form and Visual Polish | P1 | done | `task_packets/FB-079_sidebar_details_form_and_visual_polish.md` |

Execution slices:
- `S38-1` Left panel: strip to Search + Display Preferences, update toggle labels
- `S38-2` Right sidebar: elevate identity, collapse completeness, unify tabs, remove "What Next"
- `S38-3` Details form: hide empty sections, reduce chrome, increase whitespace

## Closed Sprint `S37 - Auth Visibility and Invite Reliability`

Status: Done

## Current Sprint `S37 - Auth Visibility and Invite Reliability`

Sprint goal:
- Give the admin full visibility into who has logged in and when, persist invite delivery status, surface active sessions, set up Resend email delivery, and fix login/invite error messages so family members can actually get in.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-072 | Login Tracking and Admin Visibility | P0 | done | `task_packets/FB-072_login_tracking_and_admin_visibility.md` |
| FB-073 | Persist Invite Delivery Status | P0 | done | `task_packets/FB-073_persist_invite_delivery_status.md` |
| FB-074 | Admin Session Visibility | P1 | done | `task_packets/FB-074_admin_session_visibility.md` |
| FB-075 | Resend Setup and Invite Email Polish | P1 | done | `task_packets/FB-075_resend_setup_and_invite_email_polish.md` |
| FB-076 | Login and Invite Claim Error UX | P1 | done | `task_packets/FB-076_login_error_ux.md` |

Execution slices:
- `S37-1` last_login_at on Person, login/logout audit entries, admin dashboard login column
- `S37-2` Invite delivery columns, persist Resend result, admin delivery badges, resend button
- `S37-3` Admin session list with device/IP, session revocation
- `S37-4` HTML invite email template, Resend config verification, copy-link fallback
- `S37-5` Login/invite claim error messages with actionable hints, failed attempt logging

## Closed Sprint `S36 - Person Enrichment and Sidebar Polish`

Status: Done

## Current Sprint `S36 - Person Enrichment and Sidebar Polish`

Sprint goal:
- Add place history timeline to person records, wire language autocomplete, introduce auto-save on sidebar fields, tighten sidebar labels, and extend Places autocomplete to the tree sidebar.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-067 | Place History Timeline | P0 | done | `task_packets/FB-067_place_history_timeline.md` |
| FB-068 | Language Input Autocomplete | P1 | done | `task_packets/FB-068_language_autocomplete.md` |
| FB-069 | Auto-Save Person Fields | P1 | done | `task_packets/FB-069_auto_save_person_fields.md` |
| FB-070 | Sidebar Label Tightening and Placeholder Polish | P2 | done | `task_packets/FB-070_sidebar_label_tightening.md` |
| FB-071 | Sidebar Place Autocomplete | P2 | done | `task_packets/FB-071_sidebar_place_autocomplete.md` |

Execution slices:
- `S36-1` PlaceHistoryEntry data model, migration, card editors, wiki section
- `S36-2` Language autocomplete from languages.json on edit page and sidebar
- `S36-3` Debounced auto-save on sidebar person fields with saved indicator
- `S36-4` Label audit and placeholder polish across sidebar Details tab
- `S36-5` Google Places autocomplete on sidebar place fields and place history cards

## Closed Sprint `S35 - Media UX Cleanup`

Sprint: `S35 - Media UX Cleanup`
Status: Done

## Current Sprint `S35 - Media UX Cleanup`

Sprint goal:
- Simplify the upload experience by removing the purpose selector, add delete buttons so users can remove media, and make the avatar circle a one-click headshot upload shortcut.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-064 | Remove Purpose Selector from Upload UI | P1 | done | `task_packets/FB-064_remove_purpose_from_upload_ui.md` |
| FB-065 | Media Delete Buttons | P0 | done | `task_packets/FB-065_media_delete_buttons.md` |
| FB-066 | Click Circle to Upload Headshot | P1 | done | `task_packets/FB-066_click_circle_to_upload_headshot.md` |

Execution slices:
- `S35-1` Remove purpose dropdown from upload forms, default to "memory"
- `S35-2` Add delete button with confirmation to sidebar, wiki gallery, and global gallery
- `S35-3` Make avatar circles clickable upload triggers with camera overlay

## Closed Sprint `S34 - Media Polish and Platform Completeness`

Sprint goal:
- Fix tree headshot rendering so uploaded photos actually display on tree nodes, make the headshot action and gallery discoverable from the tree sidebar, add pre-upload metadata and progress bars, and build the global family gallery page with variant backfill.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-061 | Tree Headshot Rendering and Gallery Access | P0 | done | `task_packets/FB-061_tree_headshot_rendering_and_gallery_access.md` |
| FB-062 | Upload Metadata Panel and Progress Bars | P1 | done | `task_packets/FB-062_upload_metadata_and_progress.md` |
| FB-063 | Global Family Gallery and Variant Backfill | P1 | done | `task_packets/FB-063_global_gallery_and_variant_backfill.md` |

Execution slices:
- `S34-1` Fix tree headshot rendering, add headshot action to sidebar, link gallery from sidebar
- `S34-2` Pre-upload metadata panel with title/description/date/tags, per-file progress bars
- `S34-3` Global /gallery page with filters and pagination, variant backfill script

## Closed Sprint `S33 - Media Management Enhancement`

Sprint goal:
- Make family media a trustworthy, organized archive by adding image variants, video/audio metadata extraction, per-person gallery sections with headshot management, enhanced upload experience, and soft-delete with visibility controls.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-057 | Media Data Model and Variant Pipeline | P0 | done | `task_packets/FB-057_media_data_model_and_variant_pipeline.md` |
| FB-058 | Media Gallery and Headshot Management | P1 | done | `task_packets/FB-058_media_gallery_and_headshot_management.md` |
| FB-059 | Media Upload Experience Enhancement | P1 | done | `task_packets/FB-059_media_upload_experience_enhancement.md` |
| FB-060 | Media Soft Delete and Access Control | P1 | done | `task_packets/FB-060_media_soft_delete_and_access_control.md` |

Execution slices:
- `S33-1` Data model: new columns, variant generation, audio/video metadata extraction
- `S33-2` Gallery: per-person type sections, headshot management, lightbox improvements
- `S33-3` Upload: multi-file, progress indication, metadata entry, person tagging
- `S33-4` Access control: visibility field, soft delete, admin moderation queue

## Closed Sprint `S32 - Person Details Enhancement`

Sprint goal:
- Upgrade person edit form to multi-value contact fields, structured addresses with Places auto-population, inline rich-text bio editing, and ISO 639-1 controlled language vocabulary.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-053 | Person Contact and Identity Data Model Enhancement | P0 | done | `task_packets/FB-053_person_contact_and_identity_data_model_enhancement.md` |
| FB-054 | Multi-Value Contact and Social Edit UX | P1 | done | `task_packets/FB-054_multi_value_contact_and_social_edit_ux.md` |
| FB-055 | Structured Addresses and Places Auto-Population | P1 | done | `task_packets/FB-055_structured_addresses_and_places_auto_population.md` |
| FB-056 | Person Edit Form Polish and Bio Integration | P1 | done | `task_packets/FB-056_person_edit_form_polish_and_bio_integration.md` |

Execution slices:
- `S32-1` Data model: new columns, Pydantic sub-models, migration, API handling
- `S32-2` Frontend: multi-value phone/email/social/name-history card editing
- `S32-3` Addresses: structured subfields and Places auto-population
- `S32-4` Polish: Trix bio editor, structured education/career cards, languages combobox

## Closed Sprint `S31 - Tree Relationship Correction and Repair`

Sprint goal:
- Make mistaken family links repairable directly from the tree by adding canonical relationship update/reverse primitives and exposing edit, reverse, and remove actions on the existing relationship cards.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-051 | Relationship Correction Primitives and API Truth | P0 | done | `task_packets/FB-051_relationship_correction_primitives_and_api_truth.md` |
| FB-052 | Tree Relationship Correction and Editing Flow | P1 | done | `task_packets/FB-052_tree_relationship_correction_and_editing_flow.md` |

Execution slices:
- `S31-1` Canonical parent-child update and reverse primitives
- `S31-2` Tree relationship-card edit, reverse, and remove flow

## Planned Follow-Up Sprints

| Sprint | Title | Packets | Status |
|---|---|---|---|
| S32 | Research UX Overhaul and Test Infrastructure | FB-031, FB-032 | candidate |
| S33 | Platform Completeness | G-11 (fan chart), G-12 (duplicate detection), G-14 (print/export) | candidate |

## Closed Sprint `S30 - Map Truthfulness and Place Intelligence`

Sprint goal:
- Make `/map` and location entry truthful and useful by establishing the Google Maps runtime contract, adding place autocomplete and country normalization on person surfaces, persisting real coordinates for supported map markers, and laying the foundation for kinship-aware family distribution views.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-047 | Google Maps Platform Contract and Railway Runtime Setup | P0 | done | `task_packets/FB-047_google_maps_platform_contract_and_runtime_setup.md` |
| FB-048 | Place Autocomplete and Country Normalization Across Person Surfaces | P1 | done | `task_packets/FB-048_place_autocomplete_and_country_normalization_across_person_surfaces.md` |
| FB-049 | Coordinate Persistence and Truthful Map Marker Placement | P1 | done | `task_packets/FB-049_coordinate_persistence_and_truthful_map_marker_placement.md` |
| FB-050 | Kinship-Aware Map Semantics and Family Distribution Readability | P2 | done | `task_packets/FB-050_kinship_aware_map_semantics_and_family_distribution_readability.md` |

Execution slices:
- `S30-1` Google Maps runtime contract and deploy setup
- `S30-2` Place lookup and normalized country capture in create/edit/tree surfaces
- `S30-3` Persisted coordinates and map marker truthfulness
- `S30-4` Kinship-aware map readability and future relation-layer foundation

## Long Horizon

| Sprint | Title | Packets | Status |
|---|---|---|---|
| Long horizon | AI family memorial | G-21 | candidate |

## Closed Sprint `S29 - Calendar as Primary Surface and Family Calendar Discovery`

Sprint goal:
- Make `/calendar` feel like a consumer family calendar instead of a feed-plumbing page by elevating the month view to the hero surface, moving subscriptions into a clear management layer, improving event meaning and density handling, and making holiday layers discoverable on desktop and mobile.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-043 | Calendar Primary Surface and Layout Hierarchy | P0 | done | `task_packets/FB-043_calendar_primary_surface_and_layout_hierarchy.md` |
| FB-044 | Manage Calendars Drawer and Subscription UX | P1 | done | `task_packets/FB-044_manage_calendars_drawer_and_subscription_ux.md` |
| FB-045 | Calendar Event Density, Discovery, and Detail Intelligence | P1 | done | `task_packets/FB-045_calendar_event_density_discovery_and_detail_intelligence.md` |
| FB-046 | Guided Holiday Layers, Mobile Agenda, and Empty States | P1 | done | `task_packets/FB-046_guided_holiday_layers_mobile_agenda_and_empty_states.md` |

Execution slices:
- `S29-1` Calendar hero layout and page shell
- `S29-2` Manage Calendars grouping, search, and subscribe actions
- `S29-3` Event density, detail intelligence, and upcoming discovery
- `S29-4` Holiday-layer onboarding, mobile agenda, and empty-state recovery

## Closed Sprint `S24 - Tree Photo Headshots and Person Wiki Pages`

Sprint goal:
- Make the tree visually inviting with photo contribution prompts and turn structured person data into readable Wikipedia-style biographical pages.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-029 | Tree Photo Headshots and Add-Photo Prompt | P2 | done | `task_packets/FB-029_tree_photo_headshots_and_add_photo_prompt.md` |
| FB-030 | Person Wiki Pages | P1 | done | `task_packets/FB-030_person_wiki_pages.md` |

Execution slices:
- `S24-1` Tree Photo Headshots and Add-Photo Prompt
- `S24-2` Wiki Page Foundation — Slug, Index, and Read-Only Rendering
- `S24-3` Wiki Page Interactivity — Section Editing and Cross-Links

## Closed Sprint `S23 - Source Citations, Evidence, and Date Intelligence`

Sprint goal:
- Make Family Book credible for serious genealogy research by adding per-person source citations with confidence levels, distinguishing documentary evidence from memory media, and computing age context at life events.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-028 | Source Citations, Evidence, and Date Intelligence | P1 | done | `task_packets/FB-028_source_citations_evidence_and_date_intelligence.md` |

Execution slices:
- `S23-1` Source Citations and Confidence
- `S23-2` Document vs. Evidence Media Classification
- `S23-3` Date Math and Age Display

Long horizon: G-21 (AI family memorial) — prerequisites met (G-19, G-22, G-23 done). Concrete user-facing features and tree trustworthiness come first.

## Closed Sprint `S22 - Genetic Profile, Physical Attributes, and Family Health Intelligence`

Sprint goal:
- Close the remaining person-model depth gaps (physical attributes, genetic profile, structured medical conditions) and build a family health dashboard.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-027 | Genetic Profile, Physical Attributes, and Family Health Intelligence | P1 | done | S22 plan: `.claude/plans/spicy-bouncing-llama.md` |

Execution slices:
- `S22-1` Physical Attributes + Genetic Profile
- `S22-2` Structured Medical Conditions
- `S22-3` Family Health Dashboard

Gap triage: `docs/strategy/genealogy-review-triage.md`

## Closed Sprint `S18 - Completeness Prompts and Sidebar Detail Depth`

Sprint goal:
- Turn missing data into contribution invitations and make the tree sidebar the complete editing surface so members rarely need to detour to the full edit page.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-024 | Completeness Prompts and Sidebar Detail Depth | P1 | done | `task_packets/FB-024_completeness_and_detail_depth.md` |

Execution slices:
- `S18-1` Per-Person Completeness Prompts in Sidebar
- `S18-2` Sidebar Details Tab Field Expansion
- `S18-3` Family-Level Completeness Summary API

## Closed Sprint `S17 - Tree Discovery and Research Foundation`

Sprint goal:
- Make the family tree navigable at scale with in-tree search, fix the person page content hierarchy to surface engaging content, and establish research-notes support for the genealogy-researcher workflow.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-022 | Tree Discovery and Research Foundation | P1 | done | `task_packets/FB-022_tree_discovery_and_research_foundation.md` |

Execution slices:
- `S17-1` Tree Search and Navigate-to-Node
- `S17-2` Person Page Content Hierarchy
- `S17-3` Research Notes Per Person

## Closed Sprint `S16 - Tree Graph Editing and Relationship Modeling`

Sprint goal:
- Make the family tree editable at the graph level so members can create, connect, and correct core family relationships directly from the tree workspace with less sidebar/form friction.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-021 | Tree Graph Editing and Relationship Modeling | P1 | done | `task_packets/FB-021_tree_graph_editing_and_relationship_modeling.md` |

Execution slices:
- `S16-1` Direct Relationship Editing from the Tree
- `S16-2` Graph-Aware Person Creation and Connection
- `S16-3` Relationship Review, Correction, and Confidence

## Closed Sprint `S15 - Rich Family Storytelling and Multi-Item Authoring`

Sprint goal:
- Make the tree workspace capable of richer family-history creation by supporting multi-item story composition, better grouped media/story workflows, and clearer shared family event authoring.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-020 | Rich Family Storytelling and Multi-Item Authoring | P1 | done | `task_packets/FB-020_rich_family_storytelling_and_multi_item_authoring.md` |

Execution slices:
- `S15-1` Rich Story Composition in Tree Context
- `S15-2` Multi-Item Media and Story Grouping
- `S15-3` Cross-Person Family Event Authoring

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

## Closed Sprint `S07 - Observability and Coverage Hardening`

Sprint goal:
- Raise the reliability floor of Family Book by adding direct tests for risky runtime plumbing, improving coverage in central modules, and reducing the remaining high-signal CodeMap warnings.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-010 | Observability and Coverage Hardening | P1 | done | `task_packets/FB-010_observability_and_coverage_hardening.md` |

Execution slices:
- `S07-1` Attack-Surface Test Hardening
- `S07-2` Critical-Module Coverage Expansion
- `S07-3` Observability and Complexity Hardening

## Closed Sprint `S08 - Browser Regression Expansion and Release Confidence`

Sprint goal:
- Increase confidence in staging and production releases by expanding browser-based regression coverage, formalizing staging acceptance criteria, and making release evidence easy to inspect before merges to `main`.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-011 | Browser Regression Expansion and Release Confidence | P1 | done | `task_packets/FB-011_browser_regression_expansion_and_release_confidence.md` |

Execution slices:
- `S08-1` Playwright Coverage Expansion
- `S08-2` Staging Acceptance Contract
- `S08-3` Release Evidence and Promotion Gate

## Closed Sprint `S09 - Accessibility and Interaction Hardening`

Sprint goal:
- Fix the highest-severity UI/UX and accessibility issues from the recent code review so the core Family Book flows are keyboard reachable, overlays behave correctly, dynamic updates communicate state, and core forms become easier to use.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-012 | Accessibility and Interaction Hardening | P1 | done | `task_packets/FB-012_accessibility_and_interaction_hardening.md` |

Execution slices:
- `S09-1` Dialog and Focus Contract
- `S09-2` Keyboard and Semantic Interaction Hardening
- `S09-3` Dynamic Feedback and Form Usability

## Closed Sprint `S10 - Readability and Responsive Polish`

Sprint goal:
- Improve readability, scanability, and narrow-screen usability across the main Family Book surfaces without reopening the critical accessibility work closed in Sprint 09.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-013 | Readability and Responsive Polish | P2 | done | `task_packets/FB-013_readability_and_responsive_polish.md` |

Execution slices:
- `S10-1` Typography and Metadata Legibility
- `S10-2` Mobile and Admin Responsiveness
- `S10-3` Feed Media Stability and Scanability Polish

## Next-Likely Follow-Ups

| ID | Title | Priority | Status | Notes |
|---|---|---:|---|---|
| FB-017 | Post-Integration Structural Cleanup | P2 | candidate | Continue deeper cycle, coupling, and ownership cleanup after Sprint 12 lands the external integrations and targeted hardening |

## Closed Sprint `S14 - Family Content and Relationship Authoring`

Sprint goal:
- Make the tree workspace feel complete by turning metric views into richer content surfaces, keeping more story/media work in-tree, and improving relationship authoring beyond basic link/create detours.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-019 | Family Content and Relationship Authoring | P1 | done | `task_packets/FB-019_family_content_and_relationship_authoring.md` |

Execution slices:
- `S14-1` Rich Metric Workspaces and Content Browsing
- `S14-2` Tree-Native Content Authoring Completion
- `S14-3` Relationship Authoring UX and Cleanup

## Closed Sprint `S13 - Tree Workspace 2.0`

Sprint goal:
- Turn the tree sidebar and adjacent tree interactions into the primary enrichment workspace so members can act on missing stories, media, and relationships without leaving the tree context.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-018 | Tree Workspace Interaction Overhaul | P1 | done | `task_packets/FB-018_tree_workspace_interaction_overhaul.md` |

Execution slices:
- `S13-1` Metric Actions and Sidebar Structure
- `S13-2` Tree-Native Stories, Media, and Inline Editing
- `S13-3` Searchable Relationship Linking and Empty-State Prompts

## Closed Sprint `S11 - Tree as Primary Workspace`

Sprint goal:
- Make the family tree the main workspace for Family Book by improving node identity, in-context editing, relationship creation, and default landing behavior.

Committed packet:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-015 | Tree as Primary Workspace | P1 | done | `task_packets/FB-015_tree_as_primary_workspace.md` |

Execution slices:
- `S11-1` Tree Identity and Richness
- `S11-2` Inline Tree Editing
- `S11-3` Relationship Workflows and Tree-First Landing

## Closed Sprint `S12 - External Integrations and Confidence Hardening`

Sprint goal:
- Deliver the next product-value integrations through Google Maps and Resend while folding the remaining high-signal CodeMap debt into the same sprint as targeted confidence hardening.

Committed packets:

| ID | Title | Priority | Status | Task Packet |
|---|---|---:|---|---|
| FB-016 | External Integrations: Google Maps and Email Delivery | P1 | done | `task_packets/FB-016_external_integrations_google_maps_and_email_delivery.md` |
| FB-014 | Architecture and Maintainability Hardening | P1 | done | `task_packets/FB-014_architecture_and_maintainability_hardening.md` |

Execution slices:
- `S12-1` Google Maps Integration
- `S12-2` Resend Invite Delivery
- `S12-3` Confidence Hardening for Integration Paths
