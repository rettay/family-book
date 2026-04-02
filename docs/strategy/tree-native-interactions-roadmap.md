# Tree-Native Interactions Roadmap

Status: Active initiative
Phase 1: Sprint 40 (FB-081, FB-082)
Phases 2-4: Horizon (post-UAT pipeline)

## Vision

Transform the family tree from a sidebar-driven visualization into a direct-manipulation canvas where the most common actions happen right where the user is looking. The sidebar becomes a deep-dive panel, not the default for every interaction.

## Design Principles

1. Most frequent actions should be closest to the node
2. Progressive complexity: simple on canvas, complex in sidebar
3. Nothing breaks: every canvas shortcut has a sidebar equivalent
4. Mobile-aware: long-press replaces right-click

---

## Phase 1: Context Menu + Cleanup (Sprint 40) — PLANNED

**Packets:** FB-081, FB-082

- Right-click / long-press context menu on tree nodes
- 7 actions: View branch, Add parent/child/partner, Upload photo, Edit details, View profile
- Remove hover-only camera/plus buttons (replaced by context menu)
- Single-click behavior unchanged (still opens sidebar)

**Risk:** Low. Additive — doesn't change existing interactions.

---

## Phase 2: Inline Node Editing Card — HORIZON

**Concept:** Single-click a node → a floating card appears near the node showing name, dates, photo. Fields are inline-editable with auto-save. Double-click or "More details" opens the full sidebar.

**What changes:**
- Single-click no longer opens the sidebar automatically
- A compact "quick edit card" appears floating near the clicked node
- Card shows: name (editable text), birth date (editable), death date (editable), photo (clickable to upload)
- Auto-save on blur (reuses FB-069 debounce infrastructure)
- "More details →" link opens the full sidebar
- Escape closes the card

**Key design decisions needed:**
- Card size and position (fixed size? responsive to content?)
- What happens when you click a second node while a card is open? (Close first, or allow multiple?)
- How does this interact with graph mode?
- Mobile: card needs to work at 340px width

**Risk:** High. Changes the fundamental click behavior. Existing users expect sidebar on click.

**Prerequisite:** UAT pipeline so we can test the UX shift safely with a staging environment.

---

## Phase 3: Canvas Relationship Creation — HORIZON

**Concept:** Drag from one node to another to create a relationship. A popover appears asking for relationship type and kind.

**What changes:**
- Drag gesture from node → shows a visual line following the cursor → drop on target node
- Popover at drop point: "Connect {source} and {target} as..." with relationship type selector
- Replaces the current graph mode workflow (pick on tree → click target)
- Graph mode still works as a fallback for keyboard users

**Key design decisions needed:**
- Drag vs. click-click (current graph mode)? Support both?
- What visual feedback during drag? (Ghost line, highlight valid targets)
- Mobile: drag is natural on touch, but conflicts with pan/scroll

**Risk:** Medium. Drag interactions are tricky to get right on both desktop and mobile.

---

## Phase 4: Remove Left Panel, Float All Controls — HORIZON

**Concept:** The left panel disappears. All controls move to floating UI:
- Search → Cmd+K / Ctrl+K floating search bar
- Display preferences → gear icon popover
- Branch view → context menu (already done in Phase 1)

**What changes:**
- Tree takes full viewport width
- Search accessible via keyboard shortcut or a floating search icon
- Preferences in a minimal popover triggered by a toolbar button
- No persistent side panels at all

**Key design decisions needed:**
- Where does the search bar float? (Top center? Bottom?)
- How do users discover keyboard shortcuts?
- What about the tree-controls toolbar (zoom, fit, center)? Keep or redesign?

**Risk:** Low for the change itself. Higher for discoverability — users need to learn the new locations.

---

## What Does NOT Move to the Canvas

These stay in the sidebar (accessed via "Edit details" in context menu or double-click):
- Biographical editing (education, career, organizations, medical)
- Place history timeline
- Media gallery browsing
- Relationship metadata (confidence, source, notes)
- Research records and external source searches
- Name history, contact information
- Language management

---

## Architecture Notes

- `renderNode()` needs an "expanded/editing" state per node (Phase 2)
- Context menu system (Phase 1) should be reusable for other surfaces
- Auto-save infrastructure (FB-069) extends naturally to inline cards
- tree.js is ~4800 lines — Phases 2-3 will add significant complexity
- Consider splitting tree.js into modules if it grows past 6000 lines

## Prerequisite for Phases 2-4

UAT/staging pipeline must be in place before changing fundamental click behavior. Real users are on production — we can't experiment with their daily workflow without a safety net.
