# Task Packet - FB-008 Theme Customization and Branding Controls

## Objective

Give Family Book a supported admin-controlled visual identity layer so the app can be branded for a real family deployment without editing CSS by hand or redeploying for simple color changes.

## Why / KPI

- The app is now functionally credible enough that visual ownership matters.
- A private family app should feel like the family’s space, not a fixed default demo palette.
- The current UI uses a strong warm palette, but it is hardcoded across CSS, templates, manifest metadata, and auth pages.

Primary KPI:
- improve **Family Visual Ownership Rate (FVOR)** by making production/staging theming changes admin-driven instead of code-driven.

Secondary KPI:
- reduce the gap between “demo styling” and “deployable family product branding.”

## Scope

- In scope:
  - persisted app-level theme settings
  - admin UI for editing supported theme tokens
  - reset-to-default behavior
  - theme application across core shared surfaces
  - browser/PWA theme-color alignment
  - focused tests and staging/manual acceptance guidance
- Out of scope:
  - per-user themes
  - custom font uploads
  - arbitrary CSS injection
  - full logo/media asset management
  - complete redesign of every screen

## Task Type

- Product polish and admin-control packet

## Dependencies and Ordering Assumptions

- Depends on `FB-002` because admin controls already exist.
- Depends on `FB-005` and `FB-006` because the shared shell, tree, map, and timeline surfaces now exist and need consistent visual application.
- Should happen before broader visual-regression expansion so the visual baseline is not locked to a hardcoded palette.

## Constraints

- Theme settings must be safe and bounded. No raw CSS fields.
- Prefer CSS custom properties driven by stored settings over inline color duplication.
- Core surfaces must remain legible and usable after theme changes.
- The first implementation should favor a small, durable token set over dozens of loosely defined knobs.

## Recommended Launch Scope Within This Packet

- Must support persisted admin-configurable values for:
  - app background
  - surface/card background
  - primary action color
  - accent/highlight color
  - text color
  - muted text color
  - border color
  - browser/PWA theme color
- Should support minimal branding fields:
  - brand display name
  - short tagline or subtitle for landing/auth surfaces
- Must expose:
  - admin edit form
  - preview/apply path
  - reset to default theme

## Implementation Notes

- Likely files:
  - `app/models/` for persisted theme/app settings
  - `app/routes/pages.py`
  - `app/routes/admin` or existing admin route surfaces
  - `app/templates/base.html`
  - `app/templates/admin.html`
  - `app/templates/landing.html`
  - `app/templates/login.html`
  - `app/static/css/main.css`
  - `app/static/manifest.json`
  - tests covering persistence and rendered theme token application
- Validation commands:
  - focused pytest for settings persistence and admin access
  - browser/manual validation on Railway staging
  - existing compile check

## Evaluation Environment

- Task:
  add deployable admin-managed theming and minimal branding controls
- Verifier:
  focused tests, manual staging review, and browser-flow evidence where useful
- Reference/oracle:
  `foundation/V1_PRODUCT_REQUIREMENTS.md`
  `foundation/PRODUCT_VISION.md`
  `docs/ops/railway-release-flow.md`
- Expected evidence:
  admin changes a supported theme token, saves it, reloads the app, and sees the new values applied across the shared shell and key entry pages without code changes
- Known failure modes / reward hacks:
  - settings exist but are not actually applied to rendered CSS
  - theme changes only affect one page while login/landing/manifest remain stale
  - unrestricted custom CSS introduces unsafe or broken styling paths
  - preview works only in memory and does not persist
- Verifiability class:
  `bounded-judgment`
- Context policy:
  keep the token set small, durable, and product-relevant

## Acceptance Criteria

- [ ] Family Book has a persisted app-theme model or equivalent settings contract for a bounded token set.
- [ ] Admin can update supported theme colors through a supported UI without code edits.
- [ ] Updated theme values are applied on subsequent loads across the core shell, login, and landing surfaces.
- [ ] Browser/PWA theme metadata reflects the active theme instead of a hardcoded default.
- [ ] A reset path restores the default Family Book theme.
- [ ] Staging can be used as the manual review lane for theme acceptance before production release.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] Theme controls are admin-only
- [ ] Theme values are validated and bounded
- [ ] No raw CSS injection path is introduced

## Risk and Verification Notes

- Complexity hotspots:
  - reducing hardcoded color duplication without destabilizing existing pages
  - keeping the admin UI simple while still being useful
  - ensuring theme metadata and rendered CSS stay aligned
- Likely shallow-pass failure modes:
  - only CSS variables change while inline styles remain wrong
  - PWA/browser theme color remains stale
  - theme settings do not survive restart or deploy
  - staging review path exists on paper but is not used in the acceptance loop
- Required verification depth:
  - inspect persisted settings
  - verify rendered output on multiple key pages
  - verify staging manual acceptance path
- Sufficient discriminative power means:
  the verifier must fail if theming is cosmetic-only, non-persistent, or confined to a single surface

## Execution Budget

- Builder may explore:
  - whether app-level settings belong in a dedicated model or existing settings surface
  - whether theme values should be injected into the base template or served as a generated variable block
  - the smallest useful branding fields beyond colors
- Builder must escalate if:
  - safe theming requires a much larger UI refactor than fits this sprint
  - the current UI has too many hardcoded styles to support bounded admin theming cleanly in one sprint
- Material scope drift:
  - custom logo uploads
  - full visual redesign
  - per-user themes
  - arbitrary CSS/HTML branding injection
- Proof obligations before review:
  - admin-set values persist
  - key pages consume them
  - staging remains the manual acceptance lane before production merge
