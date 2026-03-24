# Builder Playbook - Family Book

## Objective

Implement task packets with minimal scope drift and provide reproducible evidence strong enough for the risk level of the change.

## Pre-Execution Checks

Before coding:

1. Confirm the packet is executable.
2. Confirm the task has a verifier, reference/oracle, and expected evidence.
3. Confirm the required runtime or environment is available.
4. Reload the canonical product docs when the task touches product behavior.

## Required Context

Read:

- `operating_system.md`
- `foundation/PRODUCT_VISION.md`
- `foundation/V1_PRODUCT_REQUIREMENTS.md`
- `foundation/COLLABORATION_AND_PRIVACY.md`
- `docs/CODEBASE_BRIEFING.md`
- the active task packet

## Task Model

Before implementation, restate:

- The state transition being introduced or modified
- The invariants that must remain true
- The main failure modes or reward hacks
- The proof obligations needed before review

## Execution Strategy

- Read the packet and relevant code first.
- Implement in thin slices.
- Prefer explicit procedures over intuition.
- Use bounded search and backtracking when the path is unclear.
- Record materially failed branches when they affect confidence or follow-up work.

## Context Window Management

- Keep the main task thread focused on the current decision and verified state.
- Offload noisy research, codebase spelunking, and speculative exploration into external artifacts when needed.
- Merge back only distilled findings, concrete commands, produced artifacts, and residual risks.
- Persist useful distilled findings to durable files instead of relying on transcript recall.

## Environment-First Work

- For auth/invite tasks: validate with at least two users or two simulated sessions.
- For access/privacy tasks: prove both allowed and denied behavior.
- For media tasks: verify upload, storage, visibility, and render behavior.
- For UI/tree tasks: use browser or rendered evidence when possible, not just API checks.
- For docs/product-contract tasks: use drift-sensitive cross-file checks.

## Risk-Weighted Verification Duties

- Identify complexity hotspots.
- Add tests that distinguish correct behavior from plausible wrong behavior.
- Use negative-case probes or deliberate wrong-variant thinking where feasible.
- Treat "works for admin" as insufficient evidence when the feature is for normal members.

## Verification Duties

- Run targeted checks first, then broader checks.
- Record exact commands and outcomes.
- Map evidence directly to acceptance criteria.
- Include positive evidence and at least one negative or edge-case check for material changes.

## Output Format

- Implementation summary
- Files changed
- Validation commands and results
- Acceptance-criteria evidence map
- Follow-up risks/limitations
- Verifier-strength notes
