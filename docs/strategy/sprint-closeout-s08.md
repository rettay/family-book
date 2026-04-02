# Sprint Closeout - S08 Browser Regression Expansion and Release Confidence

## Sprint

- Name: `S08 - Browser Regression Expansion and Release Confidence`
- Status: Closed
- Result: `pass`

## Goal

Increase confidence in Family Book staging and production releases by expanding browser-based regression coverage, making staging acceptance criteria explicit, and tightening the evidence required before promotion to `main`.

## Outcome

Sprint 08 turned the existing browser smoke script into a stronger release-confidence lane. The Playwright flow now covers login, protected-route redirect behavior, quick and rich moment creation, browser-based person creation, admin release-readiness surfaces, member visibility, person timelines, tree filters, and map filters. The sprint also documented a reusable staging acceptance checklist and an explicit release-promotion gate so staging review, CI artifacts, and production promotion follow the same contract.

During implementation and audit, the sprint also fixed a real route-order regression on `/people/new` and hardened the browser harness so it can run on a clean CI runner and preserve trace/video artifacts on failure.

## Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S08-1 | Playwright Coverage Expansion | done |
| S08-2 | Staging Acceptance Contract | done |
| S08-3 | Release Evidence and Promotion Gate | done |

## Verification

- `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - result: `7 passed`
- `make test-ui-playwright`
  - result: success
- `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Audit Result

- Builder implementation completed on `codex/s08-release-confidence`
- Auditor identified CI portability and failure-artifact issues in the first review
- Builder corrected both issues by adding a repo-local Playwright wrapper and finalizing browser artifacts before copy on cleanup
- Final audit result: acceptable to close

## Product / Engineering Readout

- Release evidence is now materially stronger than the prior “smoke test plus judgment” model
- The staging acceptance path is explicit and reusable rather than improvised each sprint
- Browser automation now covers meaningful member and admin flows, not just route availability
- CI can upload screenshots and Playwright artifacts that line up with the documented promotion gate

## Residual Debt

- Browser coverage is still intentionally bounded rather than a full visual regression or cross-browser matrix
- CodeMap still flags structural warnings around dependency cycles, hidden coupling, observability, and a few attack-surface modules
- The release lane is stronger, but the next leverage point is codebase maintainability rather than another large feature addition

## Recommended Next Sprint

- `S09 - Accessibility and Interaction Hardening`
- Rationale: with release confidence materially improved, the next highest-value work is now direct UI operability. The latest code review found concrete overlay, keyboard, HTMX-feedback, and form-usability failures in the main Family Book flows, and those issues should be fixed before lower-priority structural cleanup.
