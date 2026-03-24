# Sprint Slices - S06 Theme Customization and Branding Controls

## Slice Sequence

### S06-1 Theme Token Contract and Persistence

Status: `planned`

- Objective:
  establish the bounded theme token model and persist it safely
- Scope:
  default theme, stored settings, token validation, and read path into the app shell
- Deliverable:
  a durable app-level theme contract instead of a CSS-only hardcoded palette
- Verification:
  focused tests proving persistence and default/reset correctness

### S06-2 Admin Theme Controls

Status: `planned`

- Objective:
  provide admin-only UI for editing and resetting the supported theme
- Scope:
  admin form, validation, save/reset flows, and admin authorization
- Deliverable:
  admins can update theme settings without touching code
- Verification:
  focused tests for access control and theme mutation flows

### S06-3 Surface Rollout and Staging Acceptance

Status: `planned`

- Objective:
  apply theme values to shared chrome and key entry surfaces, then use staging for visual acceptance
- Scope:
  shared layout, login, landing, manifest/theme-color, and release-lane verification
- Deliverable:
  the theme is visible in the real product and reviewed in staging before production
- Verification:
  staging walkthrough plus targeted browser/screenshot evidence where helpful

## Slice Rules

- Do not expand into arbitrary CSS customization.
- Do not pull full redesign work into this sprint.
- Keep the token set intentionally small and product-relevant.
- Use staging for manual visual acceptance before any production merge.

## Recommended Builder Order

1. `S06-1`
2. `S06-2`
3. `S06-3`

## PM Note

This sprint is about controlled ownership, not visual experimentation for its own sake. Prefer a small, reliable branding layer that a family admin can understand over a broad theming system that becomes another maintenance burden.
