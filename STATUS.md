# Family Book Status

## Overall State

Family Book is in **product-contract reset**.

The codebase is substantial and partially tested, but the current shipped behavior is not aligned with the desired product model of a collaborative family wiki with flat member access.

## North Star

- **Primary KPI:** Collaborative Family Loop Success Rate (CFLSR)
- **Definition:** percentage of invited active family members who can:
  1. sign in,
  2. see shared family content,
  3. make a change,
  4. have another member see that change correctly.

## Current Baseline

- Test baseline from current repo inspection:
  - `uv run pytest -q`
  - Result: `143 passed, 2 failed, 1 xfailed`
- The two failing tests are naming/branding drift, not core runtime collapse.
- The larger issue is product mismatch:
  - current access-control behavior is graph-distance-driven and restrictive,
  - the desired product is collaborative and flat-access for family members.

## Current Risks

- Product contract drift between older specs and desired launch behavior
- Access/privacy rules coded for a different product model
- Multi-user collaboration not proven end to end
- Media and richer family-history content under-modeled relative to the desired product
- Sensitive-data handling needs explicit policy, not implicit behavior

## Current Priority Order

1. Canonicalize the product contract and execution system
2. Repair account/invite/onboarding foundation
3. Replace graph-distance access with the flat family access model
4. Expand the person/content model for collaborative family history
5. Add user-facing tree customization, filtering, and map support

## Active Sprint

See `/Users/cheech/code/family-book/backlog.md` and `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`.
