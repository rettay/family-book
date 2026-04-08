# Task Packet - FB-124 Family Prompt Campaigns and Digest

Status: Proposed

## Objective

Add prompt campaigns and a weekly family digest to create recurring engagement.

## Why / KPI

Ancestry retains users through hints; Storyworth retains through prompts. Family Book needs a privacy-first engagement loop.

## Scope

- In scope:
  - prompt campaign model
  - steward can send prompts to selected relatives
  - prompt responses create stories or media inbox items
  - weekly digest email with new stories/media, upcoming birthdays/anniversaries, and unanswered prompts
  - unsubscribe/digest preference controls
- Out of scope:
  - SMS campaigns
  - AI-generated outbound content
  - global social feed

## Likely Files

- `app/models/prompts.py`
- `app/routes/prompts.py`
- `app/services/email_delivery.py`
- `app/services/calendar_service.py`
- `app/templates/prompts.html`
- `app/templates/email/digest.html`
- `tests/test_prompts.py`
- `tests/test_email_delivery.py`

## Acceptance Criteria

- [ ] Steward can create/send a prompt campaign.
- [ ] Relative can respond and create a story or media contribution.
- [ ] Weekly digest includes only content visible to the recipient.
- [ ] Digest preferences can disable emails.
- [ ] Tests cover visibility filtering and unsubscribe behavior.

## Validation Commands

- `uv run pytest tests/test_prompts.py tests/test_email_delivery.py tests/test_access_control.py -q`
- `git diff --check`

## Definition of Done

- [ ] Families have a recurring reason to return.
