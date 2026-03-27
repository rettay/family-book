# Auditor Playbook - Family Book

## Objective

Validate that completed work meets acceptance criteria, that the verifier is trustworthy enough for the risk level, and that the change is safe to ship.

## Audit Inputs Required

Before issuing an audit result, confirm:

1. The packet includes builder evidence.
2. The task is in review.
3. There is no conflict with active decisions or constraints.
4. For material member-facing UI work, the packet names changed surfaces, target personas, and required UI artifacts.
5. For material member-facing UI work, target personas and scenarios resolve from the canonical persona registry and UI surface matrix rather than ad hoc prose.

## Validation Order

1. Acceptance criteria
2. Structural evidence
3. Rendered-behavior evidence
4. Visual/persona evidence
5. Verifier quality
6. Adversarial probes
7. Risk review

## UI Audit Stack

For material member-facing UI work, audit all three lanes:

1. Structural lane
- Review CodeMap or equivalent structural findings for changed-surface classification, CSS/i18n wiring, and partial implementation risk.

2. Rendered-behavior lane
- Review deterministic browser checks proving the changed UI is visible, translated, reachable, and usable on the relevant breakpoints and roles.

3. Visual/persona lane
- Review Folio or equivalent screenshot/replay findings for workflow clarity and persona-specific usability on the changed surfaces.
- Confirm the reviewed personas and scenarios match the packet's resolved persona ids and scenario ids.

Missing lane evidence is a verifier-quality defect, not a documentation nit.
Missing canonical persona resolution is also a verifier-quality defect.

## Verifier Review

Ask:

- Can the provided checks detect a wrong implementation?
- Are there obvious shortcut paths that would still pass?
- Is the reference/oracle strong enough for the task?
- Does the evidence show member-facing behavior rather than just admin-path behavior?
- For UI work, can the verifier catch a DOM-present but visually broken implementation?
- For UI work, can the verifier catch untranslated copy, missing styling, clipped controls, or persona-critical confusion?
- For UI work, were the right personas and scenarios selected from the canonical registry and surface matrix?

## Context Window Management Review

- Audit the distilled result, not the raw exploratory transcript.
- Require enough durable evidence to prove that the distillation came from real verification.
- Treat missing handoff artifacts as risk when they hide proof obligations.

## Adversarial Audit

- Do not stop at happy-path confirmation.
- Try one plausible exploit, shortcut, or edge case for each material task.
- For collaboration tasks, probe the second-user view when the feature claims shared visibility.
- For privacy tasks, probe disallowed access explicitly.
- For UI tasks, probe one realistic presentation failure path such as:
  - new control exists but is not visible,
  - new copy bypasses i18n,
  - mobile layout makes the primary action hard to reach,
  - the intended persona can technically complete the flow but only through confusing or hidden steps.

## Risk-Weighted Verification Review

- Coverage is not confidence.
- Complexity plus weak discriminative power is risk.
- Stronger logic needs stronger checks.
- Treat high complexity plus low discrimination as a finding, even with a green suite.

## Audit Statuses

- `PASS`
- `PASS WITH FOLLOW-UPS`
- `NEEDS WORK`

## PASS Gate

Only pass when all are true:

- All acceptance criteria pass
- Evidence is reproducible
- Verifier quality is strong enough for the risk level
- For material member-facing UI work:
  - structural, rendered-behavior, and visual/persona artifacts all exist,
  - target personas and scenarios were resolved from the canonical persona registry and UI surface matrix,
  - the three lanes do not materially disagree about ship safety,
  - no probable presentation-completeness gap remains unexplained.
- No unresolved P0/P1 findings remain in scope
- Distilled findings are supported by durable evidence
