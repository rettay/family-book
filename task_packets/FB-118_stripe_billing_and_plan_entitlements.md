# Task Packet - FB-118 Stripe Billing and Plan Entitlements

Status: Proposed

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

- `app/models/billing.py`
- `app/routes/billing.py`
- `app/services/billing_service.py`
- `app/config.py`
- `app/templates/settings.html`
- `app/templates/operator.html`
- `.env.example`
- `tests/test_billing.py`
- `docs/ops/billing-runbook.md`

## Acceptance Criteria

- [ ] Hosted user can start checkout for available plans.
- [ ] Stripe webhooks update subscription state idempotently.
- [ ] Past-due/canceled/suspended states degrade safely without deleting data.
- [ ] Self-hosted mode has no Stripe dependency.
- [ ] Billing secrets are not logged.

## Validation Commands

- `uv run pytest tests/test_billing.py tests/test_config.py tests/test_security_guardrails.py -q`
- `git diff --check`

## Definition of Done

- [ ] Paid hosted billing can support a founding-customer launch.
