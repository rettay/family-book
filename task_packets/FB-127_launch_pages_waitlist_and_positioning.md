# Task Packet - FB-127 Launch Pages, Waitlist, and Positioning

Status: Proposed

## Objective

Create acquisition pages for the hosted and self-hosted offers with precise positioning.

## Why / KPI

To reach 500 paying users, the product needs pages that convert the right audience and avoid impossible Ancestry/MyHeritage comparisons.

## Scope

- In scope:
  - landing page refresh for private family archive positioning
  - pricing page for hosted Family, hosted Steward, and self-host Support
  - waitlist or checkout CTA depending on billing readiness
  - comparison pages: Ancestry private archive alternative, webtrees for non-technical families, Storyworth multi-person alternative
  - analytics for visit, signup, checkout, activation
- Out of scope:
  - paid ad campaign execution
  - SEO content calendar beyond launch pages
  - broad brand redesign

## Likely Files

- `app/templates/landing.html`
- `app/templates/pricing.html`
- `app/routes/pages.py`
- `app/static/css/main.css`
- `tests/test_pages.py`
- `docs/marketing/positioning.md`

## Acceptance Criteria

- [ ] Landing page states what Family Book is and is not.
- [ ] Pricing page distinguishes hosted and self-hosted offers.
- [ ] Claims about privacy, encryption, export, and subscriptions match implementation.
- [ ] Waitlist/checkout event is captured.
- [ ] Comparison pages avoid record/DNA overclaims.

## Validation Commands

- `uv run pytest tests/test_pages.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [ ] Public acquisition funnel can support a paid beta launch.
