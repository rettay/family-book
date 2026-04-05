# Task Packet - FB-094 Sidebar Popup, Resize, and Dock

## Objective

Allow the tree sidebar to be detached as a floating panel, resized by dragging, and re-docked to its default right-side position — giving users the flexibility to keep a person's information visible while freely navigating the tree canvas.

## Why / KPI

- The fixed sidebar forces a trade-off: open sidebar = less tree canvas visible. Power users (genealogy_researcher, family_admin) want to read a bio or check relationships while panning to a distant node.
- A floating, resizable panel removes this trade-off. The tree canvas fills the full viewport when the sidebar is undocked.
- Matches the UX North Star directive: progressive disclosure, tree as workspace.

## Scope

**In scope:**
- A "Pop out" button added to the sidebar header — clicking detaches the sidebar as a floating panel (position: fixed, visible on top of the tree canvas)
- Floating panel is draggable by its header bar (pointer events, no external library required — vanilla JS pointer event drag)
- Floating panel is resizable from its bottom-right corner handle
- A "Dock" button on the floating panel header re-attaches the sidebar to the right-side slot and restores the canvas to split-panel layout
- Panel position (x, y) and size (width, height) are stored in `localStorage` (`treeSidebarFloating`, `treeSidebarX`, `treeSidebarY`, `treeSidebarW`, `treeSidebarH`) and restored on next page load
- Sidebar state (docked vs. floating) also persisted in `localStorage` (`treeSidebarDocked`)
- When floating, the tree canvas expands to full viewport width (the right-side slot collapses)
- Minimum panel size: 280 × 400px. Maximum: 90vw × 90vh.
- Panel stays within viewport bounds during drag (clamp on pointerup)
- On mobile (viewport < 768px): pop-out is hidden; sidebar remains anchored as a bottom sheet (existing mobile behaviour unchanged)
- One sidebar only — no multiple instances

**Out of scope:**
- Multiple simultaneous panels showing different people
- Snap-to-grid or snap-to-edges
- Panel collapse/minimize (the existing hide/collapse affordance is separate)
- Persisting panel content across reloads (content is always re-loaded from the server when the sidebar is opened for a person)

## Task Type

- Member-facing UI — tree sidebar interaction enhancement

## Dependencies

- None. This is a pure front-end change to existing sidebar markup and JS.

## Target Personas

- `genealogy_researcher` — wants to read a long bio or research notes while navigating the tree
- `family_admin` — wants to manage a person's details while keeping the full tree visible for context

## Changed Surfaces

- `GET /tree` — sidebar layout changes (pop-out/dock controls, floating behaviour)

## Likely Files

- `app/templates/tree.html` — add pop-out button to sidebar header, add dock button, restructure sidebar slot for collapse-on-float
- `app/static/js/tree.js` — add `popOutSidebar()`, `dockSidebar()`, pointer-event drag handler, resize handle handler, localStorage persistence, startup restoration
- `app/static/css/main.css` — floating panel styles (box-shadow, z-index), resize handle, dock/pop-out button styles, canvas full-width override when floating

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual checks:
# Click pop-out → sidebar detaches, canvas expands
# Drag sidebar header → panel moves
# Drag resize handle → panel resizes (respects min/max)
# Click dock → panel re-attaches, canvas returns to split layout
# Reload page → panel restores to previous position/state

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] "Pop out" button is visible in the sidebar header on desktop (≥768px).
- [ ] Clicking pop out detaches the sidebar as a floating panel; the tree canvas expands to full width.
- [ ] The floating panel is draggable by its header; drag moves the panel.
- [ ] The floating panel has a resize handle at the bottom-right corner; drag resizes it.
- [ ] Panel respects minimum (280×400px) and maximum (90vw×90vh) size constraints.
- [ ] "Dock" button on the floating panel re-attaches the sidebar; canvas returns to split layout.
- [ ] Panel position, size, and docked/floating state survive a page reload (localStorage).
- [ ] Panel stays within viewport bounds (no dragging off-screen).
- [ ] On mobile (< 768px): pop-out button is hidden; behaviour is unchanged from today.
- [ ] No regressions in sidebar content, tab switching, or HTMX interactions while floating.
- [ ] `uv run pytest tests/` passes.

## Structural Oracle

- `[data-sidebar-popout-btn]` present in sidebar header
- `[data-sidebar-dock-btn]` present (visible when floating, hidden when docked)
- `#tree-sidebar` has `.tree-sidebar--floating` class when detached
- `#tree-sidebar` has `style` with `left`, `top`, `width`, `height` when floating
- `#tree-page` does not have the split-panel layout class when sidebar is floating

## Risk and Verification Notes

- **Pointer event drag:** Use `pointermove` + `pointerdown`/`pointerup` on the header. Call `setPointerCapture` to continue tracking if pointer leaves the element. Do not use mousedown/mousemove (breaks on touch).
- **Resize handle:** A 16×16px absolutely-positioned div at the bottom-right corner of the panel. Use a separate `pointerdown` handler on the handle that resizes rather than moves.
- **HTMX interactions while floating:** The sidebar content is loaded via HTMX (`hx-get` calls). These must still work when the sidebar is floating — ensure the HTMX target (`#tree-sidebar-content` or equivalent) is still present in the DOM in both states.
- **Tree canvas expansion:** When floating, set the tree container to `width: 100%` by removing the layout class that creates the sidebar slot. Use a CSS class toggle, not inline styles, so the transition is smooth.
- **Z-index:** Floating panel must sit above the tree SVG and context menu. Use `z-index: 500` for the panel; context menu stays at higher `z-index: 600` so it still appears above the panel.
- **Viewport clamp on restore:** On page load, if stored position puts the panel partially off-screen (e.g. after window resize), clamp it back into viewport before showing.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Pop out | Click button | `.tree-sidebar--floating` class | Sidebar detaches, canvas expands | Nothing happens |
| Drag | Drag header | Panel position changes | Panel moves with pointer | Panel does not move |
| Resize | Drag handle | Panel dimensions change | Panel resizes | Handle unresponsive |
| Dock | Click dock button | Class removed, slot restored | Canvas returns to split | Canvas stays full-width |
| Persist | Reload after pop out | Panel position/state restored | Panel restores as floating at same position | Reverts to docked |
| HTMX in float | Click a tree node while floating | Sidebar content loads | Person data appears in floating panel | Blank panel |
| Mobile | 390px viewport | Pop-out button hidden | Bottom sheet behaviour unchanged | Button visible, broken layout |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] Manually verified on desktop: pop out, drag, resize, dock, reload persistence
- [ ] Manually verified on 390px mobile: no pop-out affordance, existing behaviour unchanged
