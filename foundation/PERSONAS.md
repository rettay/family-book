# Family Book Personas

Status: Active launch contract for member-facing UI review

## What This Document Is

This document defines the canonical user personas for Family Book launch work.

It exists to translate the product vision into concrete testing actors that PM, CodeMap, Folio, Builder, and Auditor can all reference without inventing ad hoc personas per task.

For material member-facing UI work, task packets must resolve personas from this document through the registry and surface matrix in `/Users/cheech/code/family-book/docs/ops/`.

## Persona Resolution Rule

- Product docs explain who Family Book serves.
- This document defines the canonical personas for launch.
- `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml` expresses those personas in machine-readable test form.
- `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml` maps app surfaces to the personas and scenarios that matter there.
- Task packets must reference the resolved persona ids from that matrix, not invent new personas unless the packet explicitly escalates a gap in the registry.

## Canonical Personas

### 1. Family Admin

The organizer who keeps the family space functioning.

- Role: admin
- Primary goals:
  - invite and manage members
  - keep shared family data coherent
  - fix gaps that block collaboration
  - manage settings without breaking trust
- Typical behaviors:
  - uses the tree as the main workspace
  - performs occasional deeper edits in person and settings screens
  - verifies that another member can see the result
- Main failure risks:
  - permissions look correct in one path but fail in another
  - admin controls are reachable but confusing
  - tree changes do not propagate clearly to shared views

### 2. Contributing Family Member

The normal invited relative who adds memories, stories, photos, and corrections.

- Role: member
- Primary goals:
  - find a person quickly
  - add or improve a piece of family history
  - see contributions reflected without learning a complex tool
- Typical behaviors:
  - browses tree and person pages
  - makes lightweight edits, uploads media, adds stories
  - expects plain language and obvious save flows
- Main failure risks:
  - editing paths feel admin-oriented or too dense
  - empty states do not invite contribution
  - important controls exist but are visually weak or hidden

### 3. Genealogy Researcher

The detail-oriented family member who contributes sourced and uncertain historical data.

- Role: member
- Primary goals:
  - capture partial dates, evidence, and provenance
  - navigate between people, stories, and research context
  - treat Family Book as a working research home base
- Typical behaviors:
  - uses wiki, records, timeline, and research-adjacent surfaces
  - tolerates complexity when it serves clarity
  - expects uncertainty and provenance to be visible
- Main failure risks:
  - research features are buried or mislabeled
  - precision and provenance fields exist but are not surfaced well
  - the app feels like a display layer instead of a workspace

### 4. Mobile-First Relative

The lower-confidence relative who mostly uses a phone and contributes in small bursts.

- Role: member
- Primary goals:
  - open the app, recognize where to tap, and make a small contribution
  - read a person page or story without visual friction
  - avoid getting trapped in dense forms or hidden controls
- Typical behaviors:
  - narrow viewport
  - short sessions
  - low tolerance for clipped text, off-screen actions, or overloaded layouts
- Main failure risks:
  - controls are technically present but hard to discover
  - layout overflow or sticky panels hide primary actions
  - edit flows require too much precision or too many steps

## Persona Usage Rules

- Use these personas for launch-oriented UI review unless a packet explicitly defines a new validated persona and updates this document.
- Do not treat personas as marketing demographics. They are test actors with goals, risks, and expected workflows.
- A packet may require one or more personas depending on the changed surface.
- A surface can have a primary persona and one or more safety-check personas.
- When in doubt, prefer the smallest set of personas that reflects the real blast radius of the changed surface.

## Non-Goals

- This is not a segmentation exercise for growth marketing.
- This is not a claim that every screen must satisfy every persona equally.
- This is not permission to substitute freeform taste comments for evidence-backed persona review.
