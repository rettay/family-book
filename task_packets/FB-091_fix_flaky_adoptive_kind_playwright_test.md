# Task Packet - FB-091 Fix Flaky "Adoptive Kind" Playwright Test

## Objective

Diagnose and fix the intermittent failure in the Playwright assertion `"tree renders adoptive and single-parent guardian households distinctly"` so it passes reliably on every run.

## Why / KPI

- A flaky test that sometimes passes and sometimes fails gives false confidence. When it fails on a staging run it blocks the promotion checklist and wastes investigation time.
- Reliable tests are a prerequisite for the staging pipeline (S41) working as intended.

## Scope

**In scope:**
- Identify the root cause of intermittent failure in the `"tree renders adoptive and single-parent guardian households distinctly"` assertion in `tests/ui/playwright-flow-checks.sh` (line ~175)
- Fix the root cause — do not suppress the assertion or add excessive wait times as a workaround
- If the cause is a rendering timing issue, add a targeted `waitFor` on the specific element (not a global `setTimeout` increase)
- If the cause is seed data being absent or incorrect, fix the seed (`tests/ui/playwright_seed.py`)
- If the cause is a CSS class name mismatch (e.g., `parent-child-line--adoptive` not always applied), fix the tree rendering logic
- Re-run the test 3 times in a row locally to confirm consistent passes before closing

**Out of scope:**
- Rewriting or expanding other Playwright tests
- Changing the test assertions to be less strict
- Adding skip markers or xfail decorations

## Task Type

- Test reliability fix

## Dependencies

- None (this is an independent cleanup; can be executed in parallel with FB-088)

## Likely Files

- `tests/ui/playwright-flow-checks.sh` (the assertion, possibly a targeted `waitFor` fix)
- `tests/ui/playwright_seed.py` (if Rosa/Ben/Mia/Lee/June seed data is missing or wrong)
- `app/static/js/tree.js` (if `parent-child-line--adoptive` or `parent-child-line--guardian` CSS class is applied inconsistently)
- `app/static/css/main.css` (if the CSS class exists but is not defined, causing a selector match failure)

## Relevant Context

The test checks for:
1. `parent-child-line--adoptive` edges from Rosa and Ben to Mia
2. `parent-child-line--guardian` edge from Lee to June
3. Y-position: adoptive child Mia renders below adoptive parents Rosa and Ben
4. Y-position: single-parent guardian child June renders below guardian Lee

Seed data for these persons is in `playwright_seed.py` (lines ~410-411): `ParentChild(parent_id=ROSA_ID, child_id=MIA_ID, kind="adoptive")`.

Common causes for intermittent failure in this type of test:
- Tree SVG hasn't finished layout when the assertion runs (async D3 layout)
- CSS class applied only on some render paths (e.g., after a zoom/pan vs. initial render)
- Seed race condition: DB not fully committed before page load
- `getTranslate` throws if the node hasn't been rendered yet (returns `null` transform)

## Local Validation Commands

```bash
# Run Playwright flow checks (requires app running and seed loaded)
cd tests/ui
bash playwright-flow-checks.sh 2>&1 | grep -A 5 "adoptive"

# Run 3 times to verify consistency
for i in 1 2 3; do bash playwright-flow-checks.sh 2>&1 | grep "adoptive"; done

# Run pytest to confirm no regressions
uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] The `"tree renders adoptive and single-parent guardian households distinctly"` assertion passes on 3 consecutive runs without modification to the assertion logic.
- [ ] Root cause is identified and documented in a code comment at the fix site.
- [ ] No other previously-passing Playwright assertions are broken by the fix.
- [ ] Fix does not use `page.waitForTimeout(N)` with N > 1000ms as a workaround (targeted `waitFor` on a specific locator is acceptable).
- [ ] `uv run pytest tests/` still passes.

## Risk and Verification Notes

- **Timing vs. logic:** First determine whether this is a timing failure (tree layout not ready) or a logic failure (CSS class sometimes missing). Add a `console.log` in `tree.js` for the class application and check the Playwright trace if needed.
- **Do not loosen the assertion:** The test checks that `parent-child-line--adoptive` and `parent-child-line--guardian` classes are present. These classes are the visual contract for showing relationship kind on the tree. If the classes are missing due to a rendering bug, fix the rendering bug — do not remove the assertion.
- **Seed data integrity:** Confirm `ROSA_ID`, `BEN_ID`, `MIA_ID`, `LEE_ID`, `JUNE_ID` are the same UUIDs used in the seed and in the test assertions. A mismatch would cause a consistent failure, not intermittent — rule this out first.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Consistent pass | 3 consecutive runs | Exit code 0 for adoptive assertion | All 3 pass | Still intermittent |
| No regression | All other assertions | `playwright-flow-checks.sh` output | All other assertions still pass | Other test broken |
| Root cause documented | Code review | Comment at fix site | Explanation of what changed and why | No comment |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] 3 consecutive passes confirmed
- [ ] Root cause documented at fix site
- [ ] `uv run pytest tests/` passes
