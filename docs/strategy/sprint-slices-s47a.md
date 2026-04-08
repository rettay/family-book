# Sprint Slices - S47a Product Stabilization Before Commercialization

## Slice Order

1. `S47a-1 Timeline Filter Repair`
2. `S47a-2 Research Beta and Source Status`
3. `S47a-3 Tree Sidebar Popout Behavior`
4. `S47a-4 Research Link and Result Quality` (stretch)
5. `S47a-5 Overlay/Panel Interaction Contract` (stretch)

## `S47a-1 Timeline Filter Repair`

### Goal

Make timeline filters reliable and remove bogus `could not load content` errors.

### Scope

- fix event-type value mapping
- fix `All Events` serialization
- verify year filters with event filters
- make empty state distinct from request failure
- add regression tests for `1880` to `2002`

### Acceptance Checks

- `All Events` + `1880` to `2002` returns matching events or a truthful empty state.
- `Births`, `Deaths`, and `Marriages` work with the same year range.
- UI values map to backend-supported values.
- No valid filter response displays `could not load content`.

## `S47a-2 Research Beta and Source Status`

### Goal

Stop the Research page from overpromising while keeping it available for founder use.

### Scope

- beta/low-confidence label
- per-source configured/not configured/error/no results status
- clearer distinction between real search results and guided lookup links
- copy for optional API-key sources

### Acceptance Checks

- Research page shows a beta/low-confidence notice.
- Unconfigured API-key sources are shown as not configured.
- Source failures are visible per source.
- Guided links are not displayed as equivalent to real search hits.

## `S47a-3 Tree Sidebar Popout Behavior`

### Goal

Make popped-out tree sidebar controls predictable.

### Scope

- inspect current docked/floating/collapsed/closed state model
- fix caret behavior in popped-out mode
- ensure `x` remains the only close control
- decide whether popped-out mode supports minimize/collapse or only dock/close
- preserve current sidebar resize/drag behavior

### Acceptance Checks

- In popped-out mode, clicking the caret does not simply close/disappear the panel.
- Close remains available through `x`.
- Dock/collapse/minimize semantics are visually and functionally distinct.
- Behavior is covered by a focused regression test or Playwright smoke.

## `S47a-4 Research Link and Result Quality`

### Goal

Fix or demote the Antenati result flow and establish a basic relevance baseline.

### Scope

- validate current Antenati endpoint and query URL
- remove stale/certificate-error links
- test `cutroni`, `maglio`, and `maglio family`
- verify Chronicling America and NARA behavior in the production-like environment
- improve ranking so synthetic guided links do not dominate real results

### Acceptance Checks

- Antenati no longer sends users through the reported broken certificate/redirect flow as a "result."
- `cutroni` and `maglio` searches show honest per-source status.
- Known free sources either return results or a clear no-results/error state.
- Result links preserve enough context to be useful.

## `S47a-5 Overlay/Panel Interaction Contract`

### Goal

Document a small interaction contract for future panels, drawers, popovers, and dialogs.

### Scope

- define canonical panel states
- define canonical controls
- define keyboard behavior
- define mobile fallback behavior
- evaluate whether native `<dialog>`, Floating UI, Shoelace, or custom JS should be used per component type

### Acceptance Checks

- Contract doc exists under `docs/ops/` or `docs/strategy/`.
- Contract explicitly says no dependency is approved unless a future packet adopts it.
- Tree sidebar fix aligns with the contract.
- Future packets can reference the contract instead of inventing panel behavior.

## Validation Baseline

- `uv run pytest tests/test_timeline.py tests/test_pages.py -q`
- `uv run pytest tests/test_external_records.py tests/test_research.py -q`
- `uv run pytest tests/test_access_control.py tests/test_media.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Recommended Builder Order

1. `FB-132`
2. `FB-133`
3. `FB-131`
4. `FB-134` (stretch)
5. `FB-130` (stretch)
