# UI Review Integration Spec

## Goal

Augment Family Book's existing release process so material member-facing UI changes are reviewed through:

1. structural analysis,
2. deterministic browser oracles,
3. visual and persona-based judgment.

The intent is not to replace pytest, Playwright, or CodeMap. The intent is to close the current blind spot where a feature can be functionally present but visually incomplete, untranslated, hidden, or awkward for a real user persona.

## Persona Translation Mechanism

The system needs an explicit translation layer between product intent and UI review.

The canonical flow is:

1. Product docs define who Family Book serves.
2. `/Users/cheech/code/family-book/foundation/PERSONAS.md` defines canonical launch personas.
3. `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml` expresses those personas as machine-readable test actors.
4. `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml` maps changed surfaces to required personas, scenarios, viewports, and rubric categories.
5. PM resolves persona coverage from that matrix when packetizing the task.
6. CodeMap confirms or refines changed-surface classification and emits required persona/scenario coverage.
7. Folio runs the resolved persona scenarios and captures replay, screenshots, and rubric-backed findings.
8. Auditor checks that the expected persona evidence exists and matches the packet.

This avoids two failure modes:

- a PRD names an audience but the task packet never turns that into executable review work
- a builder or auditor invents personas ad hoc, leading to inconsistent coverage between packets

## Problem Statement

The current system is strong at structural correctness and functional smoke testing, but weaker at presentation-layer completeness.

Recent misses were in this class:

- templates referenced CSS classes without matching stylesheet rules
- locale keys existed but templates still rendered hardcoded English
- controls existed in the DOM but lacked visible or usable presentation
- new UI was functionally reachable but weak for the intended persona

These are not pure backend bugs and not purely subjective design complaints. They sit in the gap between structure and visual reality.

## Review Model

Material member-facing UI work uses three lanes.

### 1. Structural Lane

Primary tool: CodeMap

Purpose:

- detect cross-file wiring gaps
- flag suspicious template/CSS/i18n mismatches
- classify which user-facing surfaces changed
- identify where stronger browser or persona review is required

Artifacts:

- machine-readable report
- concise changed-surface summary
- finding list with severity and file references

### 2. Rendered-Behavior Lane

Primary tools: existing Playwright lane plus Folio deterministic probes

Purpose:

- prove that changed UI renders correctly in a browser
- assert visibility, size, reachability, translation, and layout invariants
- validate the real post-render state rather than template intent

Artifacts:

- pass/fail assertion log
- screenshots for changed surfaces
- replay trace or video for failures and key flows

### 3. Visual/Persona Lane

Primary tool: Folio with a bounded vision-model rubric

Purpose:

- judge whether the changed workflow is understandable and usable for the intended persona
- catch visual or interaction issues that are obvious on inspection but difficult to encode as pure assertions
- provide auditor-reviewable evidence instead of a freeform "looks okay"

Artifacts:

- persona-scoped report
- screenshots and replay
- rubric-backed findings with severity and confidence

## Material UI Change Definition

This spec applies when a task changes any of:

- server-rendered templates
- user-facing JavaScript that changes visible behavior
- CSS or theme tokens
- locale files or translation wiring
- workflow structure on login, tree, wiki, map, research, admin, or person pages
- mobile layout or responsive behavior on member-facing pages

Pure backend work does not require the visual/persona lane unless the packet says otherwise.

## CodeMap Augmentation Spec

CodeMap remains the structural reviewer. It should add a frontend-oriented package or check family with the following responsibilities.

### A. Changed-Surface Classifier

Input:

- git diff or changed-file list

Output:

- impacted routes or templates
- impacted personas
- impacted scenario ids
- whether visual review is mandatory

Heuristics:

- template changes map to route/page surfaces
- CSS changes map to templates that reference the affected selectors
- locale changes map to templates/JS that should consume the keys

### B. CSS Wiring Check

Goal:

- flag newly referenced classes or state classes that have no matching selector or known generation rule

Scope:

- Jinja templates
- server-generated HTML fragments
- user-facing JS that injects HTML
- `app/static/css/main.css` and future stylesheet entry points

Output example:

- `P1`: template adds `.wiki-infobox__social` but no selector exists in the stylesheet set

### C. i18n Usage Check

Goal:

- flag hardcoded user-facing English on changed surfaces when matching locale keys exist or should exist

Scope:

- templates
- user-facing JS strings
- inline HTML snippets built in JS

Output example:

- `P1`: new date mode buttons render `"Freeform"` and `"Calendar"` literals instead of translation hooks

### D. Frontend Completeness Heuristics

Goal:

- flag suspicious partial implementations in changed UI code

Examples:

- new form field added in template but not present in browser test selectors
- new tab/panel classes added without accompanying visible-state selectors
- new locale keys added without any code references
- new interactive control added without accessible name or keyboard path

### E. Audit Artifact

CodeMap should emit a compact artifact that the auditor can read quickly:

- changed surfaces
- required browser scenarios
- required personas
- required scenario ids
- required viewports/locales
- structural findings
- residual uncertainty that must be checked visually

## Folio Augmentation Spec

Folio becomes the visual and exploratory reviewer for changed surfaces.

### A. Deterministic Probe Mode

Folio should support assertion-style probes in addition to free exploration.

Required checks:

- visible and non-zero-size controls
- no horizontal overflow on target viewports
- translated text appears on changed surfaces
- control is not covered or clipped
- important actions are reachable by keyboard and pointer
- expected state transitions occur after interaction

This is where Folio complements, not replaces, the existing Playwright suite.

### B. Persona Run Mode

Folio should run bounded scenarios for named personas:

- family_admin
- contributing_member
- genealogy_researcher
- mobile_first_relative

Each persona run should have:

- goal
- scenario id
- route scope
- allowed time budget
- expected success signals
- viewport and locale
- screenshots and replay

### C. Vision Review Mode

Use a vision model only with an explicit rubric.

Rubric categories:

- visibility and clipping
- hierarchy and readability
- control discoverability
- translation completeness
- mobile fit
- workflow clarity for the named persona

The model should receive:

- screenshot
- DOM or accessibility snapshot
- route and persona context
- scenario id
- changed-surface summary from CodeMap

The model should not be asked for open-ended design criticism without scope.

### D. Baseline Comparison Mode

Optional but useful for stable surfaces:

- compare candidate screenshots against a baseline screenshot set for changed surfaces only
- highlight likely regressions for auditor inspection
- do not block on raw pixel difference alone

### E. Auditor Artifact

Folio should emit:

- scenario id
- persona
- route/surface
- viewport and locale
- findings with severity/confidence
- screenshots
- replay path
- which findings were deterministic vs vision-assisted

## Auditor Contract

For material member-facing UI tasks, audit requires:

1. CodeMap artifact
2. deterministic browser artifact
3. Folio persona/visual artifact

The packet must also show how changed surfaces were resolved into persona/scenario requirements through the canonical registry and surface matrix.

The auditor should fail the task when:

- one of the required lanes is missing
- the structural lane flags probable partial wiring and the browser/visual evidence does not close the risk
- the browser lane proves a visible/usability defect
- the visual lane finds a persona-critical issue supported by screenshots or replay

## Initial Rollout Plan

### Phase 1: Contract

- update `operating_system.md`
- update `auditor.md`
- update task packet template expectations for member-facing UI work

### Phase 2: Cheap Structural Wins

- implement CodeMap changed-surface classifier
- implement CSS wiring check
- implement i18n usage check

### Phase 3: Stronger Browser Oracles

- extend current Playwright checks for visibility, translation, and responsive invariants
- let Folio run deterministic probe bundles on changed surfaces

### Phase 4: Bounded Visual Review

- add Folio persona mode with screenshot/replay
- add rubric-based vision review on critical surfaces only

### Phase 5: Calibration

- measure false positives
- compare Folio findings against human staging review
- tighten heuristics and prompts based on misses

## Success Criteria

The integration is succeeding when:

- UI regressions are found before staging more often than by ad hoc manual review
- auditors can explain why a UI task is safe using durable artifacts instead of intuition
- missing CSS/i18n/wiring defects are caught deterministically
- persona-based findings are specific enough to drive fixes rather than generic taste comments

## Non-Goals

- replacing human judgment on product taste
- requiring full pixel-perfect visual regression across the whole app
- forcing visual review on every backend-only task
- treating a vision model as a source of truth without supporting evidence
