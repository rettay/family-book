# Auditor Playbook - Family Book

## Objective

Validate that completed work meets acceptance criteria, that the verifier is trustworthy enough for the risk level, and that the change is safe to ship.

## Audit Inputs Required

Before issuing an audit result, confirm:

1. The packet includes builder evidence.
2. The task is in review.
3. There is no conflict with active decisions or constraints.

## Validation Order

1. Acceptance criteria
2. Functional evidence
3. Verifier quality
4. Adversarial probes
5. Risk review

## Verifier Review

Ask:

- Can the provided checks detect a wrong implementation?
- Are there obvious shortcut paths that would still pass?
- Is the reference/oracle strong enough for the task?
- Does the evidence show member-facing behavior rather than just admin-path behavior?

## Context Window Management Review

- Audit the distilled result, not the raw exploratory transcript.
- Require enough durable evidence to prove that the distillation came from real verification.
- Treat missing handoff artifacts as risk when they hide proof obligations.

## Adversarial Audit

- Do not stop at happy-path confirmation.
- Try one plausible exploit, shortcut, or edge case for each material task.
- For collaboration tasks, probe the second-user view when the feature claims shared visibility.
- For privacy tasks, probe disallowed access explicitly.

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
- No unresolved P0/P1 findings remain in scope
- Distilled findings are supported by durable evidence
