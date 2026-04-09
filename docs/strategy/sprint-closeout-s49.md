# Sprint Closeout - S49 Paid Hosted Platform

Status: Closed

Audit result: PASS

## Scope Completed

- `FB-117`: hosted archive provisioning and operator console.
- `FB-118`: Stripe billing state and plan entitlements.
- `FB-119`: storage usage metering and quota enforcement.

## Outcome

- Family Book now has a single-archive hosted platform record with lifecycle, plan, billing, export, and deletion metadata.
- Operator access can provision the archive record, inspect a safe support summary, and transition lifecycle state with audit logging.
- Hosted mode now fails closed if the archive record is missing, so paid-host access cannot silently degrade into unrestricted normal mode.
- Hosted billing is optional and self-host-safe: Stripe checkout and webhook processing only activate when hosted billing env vars are configured.
- Stripe webhook receipts are idempotent, and billing state now maps onto hosted archive status rather than living only in external Stripe dashboards.
- Hosted storage usage is now measured across database, media originals, media variants, backups, and exports.
- Hosted uploads are blocked gracefully when quota is exceeded.
- Suspended or billing-blocked hosted archives now degrade member access while preserving admin settings/export/billing recovery paths.

## Structural Evidence

- `uv run pytest tests/test_operator.py tests/test_billing.py tests/test_storage_usage.py tests/test_media.py tests/test_pages.py tests/test_config.py -q`
- `uv run pytest tests/test_operator.py tests/test_auth.py tests/test_billing.py tests/test_config.py tests/test_media.py tests/test_storage_usage.py tests/test_pages.py -q`
- `uv run python -m py_compile app/config.py app/auth.py app/main.py app/routes/hosted_platform.py app/routes/media.py app/routes/pages.py app/services/billing_service.py app/services/hosted_archive_service.py app/services/storage_usage_service.py app/models/hosted_archive.py`
- `git diff --check`

## Documentation Deliverables

- `docs/ops/billing-runbook.md`
- `.env.example`
- `app/templates/operator.html`

## Notes

- This sprint still assumes one hosted archive per deployment, matching the S47 ADR.
- Stripe is implemented via direct HTTPS calls so self-hosted installs do not gain a hard runtime dependency on the Stripe SDK.
- The export-retention finding raised during closeout review belongs to the earlier privacy/export sprint, not S49, and does not change the hosted-platform audit result.
- The two untracked `docs/bizanalysis/*` analyst input files remain untouched and are not part of S49 deliverables.
