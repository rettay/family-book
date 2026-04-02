# Sprint Closeout - S12 External Integrations and Confidence Hardening

## Outcome

- Status: `closed`
- Exit result: `pass`

Sprint 12 landed the first real external integrations in Family Book without breaking the existing fallback and release-confidence contract. The map can now use Google Maps in configured environments while retaining the private SVG fallback, and admin invite flows can now deliver through Resend while preserving manual-link fallback when delivery is unavailable or fails.

## Delivered

- Google Maps integration with truthful provider/fallback behavior
- Resend-backed invite delivery with admin-facing delivery feedback
- focused hardening for the central integration paths touched by Sprint 12
- audit follow-up fixing:
  - configured Google Maps keyboard accessibility
  - retryability after Google Maps loader failure
  - escaped outbound invite email HTML

## Verification Baseline

- `uv run python -m compileall app tests`
  - result: success
- `uv run pytest tests/test_email_delivery.py tests/test_auth.py tests/test_pages.py tests/test_config.py tests/test_access_control.py tests/test_schema_models.py -q`
  - result: `52 passed`
- `make test-ui-playwright`
  - result: success
- `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`

## Residual Non-Blocking Debt

- CodeMap warning-only structural debt remains around:
  - the settings/theme-service dependency cycle
  - observability gaps in central modules
  - bus factor and hidden coupling noise
- the full repo-wide pytest suite was not rerun as part of the final Sprint 12 audit, only the focused sprint verification set

## PM Read

Sprint 12 is acceptable to close. The integrations are now real, configured environments behave meaningfully better, unconfigured environments still degrade safely, and the promotion gate remained intact through audit and follow-up.
