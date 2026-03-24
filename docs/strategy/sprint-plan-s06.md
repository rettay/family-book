# Sprint Plan - S06 Theme Customization and Branding Controls

## Sprint

- Name: `S06 - Theme Customization and Branding Controls`
- Status: Closed
- Primary packet: `FB-008 Theme Customization and Branding Controls`

## Sprint Goal

Make Family Book feel owner-operated rather than hardcoded by giving admins a supported way to control the core visual palette and minimal branding surfaces, with staging as the manual approval lane before production.

## Why This Sprint

The product now has collaboration, discovery, recovery, protection, and a functioning release path. The next value gap is presentation and ownership. A family should not need to edit source files just to make the app feel like theirs.

## Must-Have Outcomes

- Theme settings are persisted instead of embedded in CSS only.
- Admins can change supported theme tokens through a supported interface.
- Core shared surfaces visibly adopt the configured theme.
- Staging becomes the normal manual acceptance lane for visual changes.

## Acceptance Criteria

1. Family Book persists a bounded app-theme contract for core colors and minimal brand text.
2. Admin can change supported theme values from the app UI without editing files or redeploying.
3. Updated theme values apply across `base`, `login`, `landing`, and core shared app chrome on subsequent loads.
4. Browser/PWA theme-color metadata reflects the active theme.
5. Admin can reset to the default Family Book theme.
6. Theme acceptance is verified in staging before production release.

## In Scope

- persisted app theme settings
- bounded color-token model
- minimal branding fields like app display name and tagline
- admin edit/reset UI
- theme application to shared shell and key entry pages
- staging/manual acceptance guidance for visual review

## Out of Scope

- custom font uploads
- logo/media upload management
- per-user appearance settings
- arbitrary CSS injection
- broad redesign of every content surface

## Implementation Order

1. Execute Slice 1: theme token model and persistence.
2. Execute Slice 2: admin theme controls and validation.
3. Execute Slice 3: surface rollout, manifest alignment, and staging/manual acceptance.
4. Validate with focused tests and staging review before production merge.

## Execution Slices

### Slice 1 - Theme Token Contract and Persistence

- Goal:
  define the bounded theme token set and persist it safely
- Scope:
  app-level theme settings model, defaults, validation, and load path
- Must prove:
  theme values persist across reloads and restarts

### Slice 2 - Admin Theme Controls

- Goal:
  let admins update and reset supported theme settings without code changes
- Scope:
  admin UI, validation, reset flow, and admin-only enforcement
- Must prove:
  admin changes take effect and non-admins cannot mutate theme settings

### Slice 3 - Surface Rollout and Manual Acceptance

- Goal:
  apply the active theme to the shared shell and key entry surfaces, then verify it in staging
- Scope:
  `base.html`, auth/landing pages, manifest/theme-color metadata, and manual staging acceptance
- Must prove:
  the configured theme is visible in real rendered pages and is acceptable before `main`

## Proof Obligations

- The theme contract must be bounded and validated.
- Theme settings must actually drive rendered output, not just exist in storage.
- The visual acceptance path must use staging, not production-first trial and error.
- Sprint scope must remain on useful, durable theming rather than visual churn.

## Risks To Watch

- too many inline/hardcoded colors to cleanly parameterize in one sprint
- theme settings that break readability or contrast
- partial rollout where shell pages change but auth/landing/PWA metadata do not
- over-expanding from “theme controls” into a full redesign sprint

## Exit Target

Sprint 06 is complete when a family admin can change the app’s core palette and minimal branding through a supported UI, verify it in staging, and promote it to production through the normal branch/release flow.
