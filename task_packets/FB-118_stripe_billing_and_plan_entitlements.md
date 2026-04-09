# Task Packet - FB-118 Stripe Billing and Plan Entitlements

Status: Done

## Objective

Implement paid hosted billing state and plan entitlements.

## Why / KPI

The product needs to accept payments, handle trials/cancellations/past-due states, and keep self-hosted deployments unaffected.

## Scope

- In scope:
  - Stripe checkout for hosted plans
  - webhook handling for customer/subscription/payment state
  - plan entitlement model
  - hosted-only gating for suspended/canceled/past-due archives
  - admin/operator billing status display
  - test mode setup docs
- Out of scope:
  - tax automation
  - enterprise invoicing
  - marketplace/app-store billing
  - forcing self-hosted users through Stripe

## Likely Files

- `app/models/hosted_archive.py`
- `app/routes/hosted_platform.py`
- `app/services/billing_service.py`
- `app/config.py`
- `app/templates/settings.html`
- `app/templates/operator.html`
- `.env.example`
- `tests/test_billing.py`
- `docs/ops/billing-runbook.md`

## Acceptance Criteria

- [x] Hosted user can start checkout for available plans.
- [x] Stripe webhooks update subscription state idempotently.
- [x] Past-due/canceled/suspended states degrade safely without deleting data.
- [x] Hosted mode fails closed when the archive record is missing.
- [x] Self-hosted mode has no Stripe dependency.
- [x] Billing secrets are not logged.

## Validation Commands

- `uv run pytest tests/test_billing.py tests/test_config.py tests/test_auth.py -q`
- `git diff --check`

## Evidence

- `app/services/billing_service.py`
- `app/routes/hosted_platform.py`
- `app/config.py`
- `app/templates/settings.html`
- `tests/test_billing.py`
- `docs/ops/billing-runbook.md`

## Definition of Done

- [x] Paid hosted billing can support a founding-customer launch.
