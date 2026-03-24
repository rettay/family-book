# Family Book Operating System

## Purpose

Provide an explicit execution protocol for moving Family Book from an inconsistent prototype into a reliable collaborative family wiki through scoped task packets with clear PM -> Builder -> Auditor handoffs.

The operating objective is to maximize **Collaborative Family Loop Success Rate (CFLSR)** while preserving data trust, privacy, and product truthfulness.

## North Star

- **Primary KPI:** Collaborative Family Loop Success Rate (CFLSR)
- **Definition:** percentage of invited active family members who can complete the core shared loop without manual intervention:
  1. sign in,
  2. view shared tree/content,
  3. make a content change,
  4. have another member see that change correctly.

## Source of Truth

- Operating system: `/Users/cheech/code/family-book/operating_system.md`
- PM playbook: `/Users/cheech/code/family-book/pm.md`
- Builder playbook: `/Users/cheech/code/family-book/builder.md`
- Auditor playbook: `/Users/cheech/code/family-book/auditor.md`
- Product vision: `/Users/cheech/code/family-book/foundation/PRODUCT_VISION.md`
- V1 requirements: `/Users/cheech/code/family-book/foundation/V1_PRODUCT_REQUIREMENTS.md`
- Collaboration and privacy contract: `/Users/cheech/code/family-book/foundation/COLLABORATION_AND_PRIVACY.md`
- Codebase briefing: `/Users/cheech/code/family-book/docs/CODEBASE_BRIEFING.md`
- Backlog queue: `/Users/cheech/code/family-book/backlog.md`
- Task packets: `/Users/cheech/code/family-book/task_packets/`
- Kanban board: `/Users/cheech/code/family-book/docs/strategy/kanban-2026q1.md`
- Sprint board: `/Users/cheech/code/family-book/docs/strategy/sprint-board-2026q1.md`
- Status tracker: `/Users/cheech/code/family-book/STATUS.md`
- Decisions log: `/Users/cheech/code/family-book/DECISIONS.md`

## Product Contract Rule

For launch-oriented implementation work, the foundation docs listed above override speculative or future-state ideas elsewhere in the repo. Older broad docs such as `SPEC.md` remain useful context, but they are not the launch contract when they conflict with the foundation docs.

## System Model

Family Book execution is modeled as a finite-state workflow over task packets.

### State Variables

- `backlog_status(task) ∈ {todo, in_progress, in_review, done}`
- `kanban_state(task) ∈ {Ready, In Progress, In Review, Done}`
- `packet_ready(task) ∈ BOOLEAN`
- `acceptance_defined(task) ∈ BOOLEAN`
- `environment_defined(task) ∈ BOOLEAN`
- `evidence_attached(task) ∈ BOOLEAN`
- `audit_result(task) ∈ {pending, pass, pass_with_follow_ups, needs_work}`
- `escalated(task) ∈ BOOLEAN`

### Allowed Transitions

- `Select(task)`: PM chooses the highest-priority unblocked task.
- `Packetize(task)`: PM creates or updates a task packet with objective, scope, verifier, and acceptance criteria.
- `StartBuild(task)`: Builder begins execution on a ready packet.
- `SubmitForAudit(task)`: Builder attaches evidence and moves the task into review.
- `AuditPass(task)`: Auditor validates all gates and closes the task.
- `AuditFail(task)`: Auditor returns the task to active work with explicit findings.
- `Close(task)`: PM updates system-level records when product behavior or assumptions changed.
- `Escalate(task)`: PM or user decision is required because policy, proof obligations, or dependencies are unclear.

### Invariants

- No task may enter build unless `packet_ready(task) = TRUE`.
- No task may enter build unless `acceptance_defined(task) = TRUE`.
- No task may enter build unless `environment_defined(task) = TRUE`.
- No task may enter review unless `evidence_attached(task) = TRUE`.
- `audit_result(task) = pass` implies all acceptance criteria are satisfied.
- `backlog_status(task) = done` implies `kanban_state(task) = Done`.
- The shipped product contract must remain truthful to actual runtime behavior.
- Shared family collaboration must not be silently broken by access-control drift.

## Roles

- PM: prioritize work, define packets, and keep the product contract coherent
- Builder: implement scoped changes, preserve invariants, and provide reproducible evidence
- Auditor: validate acceptance criteria, verifier quality, risk, and ship safety

## Execution Strategy

- Prefer explicit procedures over freeform judgment for recurring work.
- Use bounded search and backtracking for ambiguous work.
- Keep state visible and transitions reversible where possible.
- Compile repeatable workflows into scripts, checks, fixtures, and runbooks.
- Escalate when proof obligations, privacy policy, or data-model direction are unclear.

## Context Window Management

- Treat context as a constrained operational resource.
- Keep the main execution thread small, current, and decision-relevant.
- Offload noisy research, experiments, and speculative branch exploration into external artifacts when needed.
- Merge back only verified conclusions, concrete commands, produced artifacts, and residual risks.
- Persist distilled findings to files instead of relying on transcript memory.

## Evaluation Environments

Every recurring task class must define:

- Task
- Verifier
- Reference/oracle
- Evidence format
- Failure modes / reward hacks
- Verifiability class: `deterministic`, `bounded-judgment`, or `judgment-heavy`
- Context policy

Examples:

- Auth/invite/account tasks: API tests plus end-to-end multi-user validation
- Access/privacy tasks: negative-case checks proving unauthorized access is rejected and authorized family sharing still works
- Media tasks: upload, dedup, visibility, and cross-user render validation
- Tree/UI tasks: browser or UI-harness evidence against real rendered behavior
- Docs/product-contract tasks: drift-sensitive text checks plus cross-doc consistency review

## Workflow

1. Select
- PM selects the highest-priority unblocked item from `backlog.md`.
- PM verifies dependencies, verifier design, and packet readiness.

2. Packetize
- Packet exists in `task_packets/` with objective, scope, evaluation environment, acceptance criteria, validation plan, and definition of done.
- Backlog status is `todo`.

3. Build
- Builder moves task `Ready -> In Progress` and backlog to `in_progress`.
- Builder implements in thin slices and records evidence.
- Builder moves task `In Progress -> In Review` and backlog to `in_review` when complete.

4. Audit
- Auditor validates acceptance criteria, verifier quality, and risk with explicit evidence.
- If fail: task returns to `in_progress` with explicit findings.
- If pass: task moves to `done`.

5. Close
- PM updates `STATUS.md` and `DECISIONS.md` when product behavior, contracts, or assumptions changed.
- PM reorders backlog for the next cycle.

## Adversarial Quality Gates

- Happy-path validation is insufficient.
- Verifiers must reject hardcoded, shortcut, or admin-only solutions when the feature is supposed to be collaborative.
- Audits must probe at least one realistic failure path for material changes.
- Weak verifier quality is itself a blocker.

## Risk-Weighted Verification

- Coverage shows what ran; it does not prove meaningful checking.
- Complexity plus low discriminative power is a release risk.
- Verification strength must scale with branching, statefulness, and blast radius.
- When mutation tooling is impractical, use equivalent wrong-variant or negative-case probes.

## Trust and Escalation

- Trust is earned through repeated verified performance.
- Privacy and medical-data tasks require stronger review when product rules are ambiguous.
- Escalate when:
  - requirements conflict with the launch contract,
  - access/privacy behavior is unclear,
  - data-model choices affect multiple downstream packets,
  - verification quality is too weak for the blast radius,
  - an older spec conflicts with the new canonical docs.

## Definition of Done

A task is done only when all are true:

- Acceptance criteria are explicitly satisfied.
- Validation commands are reproducible and passing.
- Evidence is strong enough for the risk level of the changed path.
- No unresolved P0/P1 issues remain in task scope.
- Backlog status is `done`.
- CFLSR is preserved or improved.

## Reporting Cadence

- During active execution: brief progress updates at phase transitions and material blocker discovery
- At completion: concise summary of files changed, validation evidence, residual risks, and verifier-strength notes
- When exploration is offloaded: return only distilled findings and durable artifacts to the mainline
