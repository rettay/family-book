# Billing Runbook

Purpose: operate the hosted single-archive billing flow without leaking family content or introducing a hard Stripe dependency into self-hosted installs.

## Scope

- Hosted deployments only.
- One hosted archive record per deployment.
- Stripe is optional and only enabled when the hosted env vars are configured.

## Required Env Vars

- `HOSTED_ARCHIVE_ENABLED=true`
- `HOSTED_ARCHIVE_BILLING_PROVIDER=stripe`
- `HOSTED_ARCHIVE_KEY`
- `HOSTED_ARCHIVE_NAME`
- `HOSTED_ARCHIVE_OWNER_EMAIL`
- `HOSTED_ARCHIVE_PLAN`
- `OPERATOR_TOKENS`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_FOUNDING`
- `STRIPE_PRICE_FAMILY`
- `STRIPE_PRICE_FAMILY_PLUS`

## Operational Surfaces

- Admin billing state:
  - `GET /api/billing/hosted-archive`
  - `POST /api/billing/checkout`
  - `POST /api/billing/portal`
- Stripe webhook:
  - `POST /api/billing/stripe/webhook`
- Operator safe-summary view:
  - `GET /api/operator/archive`
  - `GET /operator?token=...`

## Hosted Archive Lifecycle

- `active`: normal access.
- `suspended`: member access blocked; admins can still reach billing/settings/export paths.
- `deletion_requested`: member access blocked; operators/admins can coordinate export and deletion.
- `deleted`: archive should be considered retired; runtime teardown remains an operator action outside the app.

## Billing Status Expectations

- `unconfigured`: hosted archive exists but no active subscription is attached yet.
- `trialing` / `active`: normal hosted operation.
- `past_due` / `unpaid` / `canceled` / `suspended`: member access is degraded and write operations such as upload are blocked.

## Stripe Webhook Handling

- Signature validation uses `STRIPE_WEBHOOK_SECRET`.
- Event receipts are stored in `billing_event_receipts`.
- Duplicate Stripe events are ignored idempotently by `external_event_id`.
- Subscription events update the hosted archive record without exposing private family data in logs.

## Support Rules

- Use the operator summary rather than browsing people/media content.
- Prefer counts, lifecycle state, billing state, backup freshness, and storage totals for first-line diagnosis.
- Do not ask families for screenshots of private profile data when the operator summary already answers the question.

## Common Cases

### Start checkout for a hosted archive

1. Confirm the archive has a record in `hosted_archives`.
2. Confirm the target Stripe price id exists for the chosen plan.
3. Use the admin settings/admin dashboard hosted billing action or `POST /api/billing/checkout`.

### Billing portal access

1. Confirm `stripe_customer_id` is present on the hosted archive record.
2. Use `POST /api/billing/portal`.

### Billing webhook not updating state

1. Check `billing_event_receipts` for the Stripe event id.
2. Confirm the webhook signature secret matches the Stripe endpoint.
3. Confirm archive matching data exists:
   - `metadata.archive_key`, or
   - `stripe_customer_id`, or
   - `stripe_subscription_id`.

### Storage quota complaints

1. Check admin/operator usage summary.
2. Confirm plan quota and current usage.
3. If needed, move the archive to a larger plan and restart checkout.

## Validation

- `uv run pytest tests/test_billing.py tests/test_config.py -q`
- `uv run pytest tests/test_operator.py tests/test_storage_usage.py tests/test_media.py -q`
- `git diff --check`
