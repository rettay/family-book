# Sprint Plan - S51 Lovable Engagement

## Sprint Summary

- Name: `S51 - Lovable Engagement`
- Goal: create recurring reasons for families to return after onboarding by adding prompt-driven contribution loops, enjoyable media browsing, and a giftable export foundation.
- Primary packet: `FB-124 Family Prompt Campaigns and Digest`
- Supporting packets:
  - `FB-125 Media Search, Albums, and Timeline Delight`
  - `FB-126 Family Book Export Foundation`

## PM Recommendation

Treat `FB-124` and `FB-125` as the hard commitment.

Treat `FB-126` as committed but tightly scoped:
- ship Markdown export as the required artifact
- ship PDF only if the rendering path stays low-risk
- do not let print-like layout work consume the sprint

Reasoning:
- S50 improved activation. S51 needs to improve return behavior.
- Prompt campaigns and digest are the clearest recurring engagement loop.
- Media search and albums make the archive feel rewarding instead of merely functional.
- Export matters for paid conversion, but it is the easiest packet to let sprawl.

## Scope

- In scope:
  - steward-authored prompt campaigns to selected relatives
  - role-safe prompt response flow that produces stories or media inbox contributions
  - weekly digest with visible stories, media, anniversaries, birthdays, and unanswered prompts
  - digest preference and unsubscribe controls
  - albums/collections across people
  - gallery and timeline search/filter improvements tied to media metadata
  - Markdown family-book draft export
  - PDF draft only if the implementation is a thin wrapper around the Markdown/export data model
- Out of scope:
  - SMS/push campaigns
  - AI-generated outbound messaging
  - face clustering, OCR, or transcription search
  - print fulfillment and advanced book layout tooling
  - pooled notification infrastructure

## Success Criteria

1. A steward can send a prompt and receive a real story or media response from a relative.
2. A recipient only sees digest content they are authorized to view.
3. Media can be found again by person, date, title, caption, description, source, and album.
4. A family steward can generate a shareable family-book draft without leaking hidden/private content.
5. The sprint produces at least one loop that plausibly increases weekly return usage.

## Delivery Strategy

1. Build `FB-124` first.
   This creates the core return loop and forces permission-safe recipient/content modeling early.
2. Build `FB-125` second.
   This turns contributed media into something enjoyable and discoverable.
3. Build `FB-126` third.
   Reuse the same visibility and content-selection logic from prompts/media instead of creating a separate export interpretation layer.

## Risks

- Digest visibility can become a privacy bug if it composes content before filtering per-recipient.
- Prompt response UX can drift into a second onboarding flow if it becomes too heavy.
- Album/search work can become a database/indexing project if it is not bounded to current storage.
- PDF work can consume the sprint if layout ambitions are not constrained.

## Mitigations

- Make visibility filtering a shared service used by digest assembly and export assembly.
- Keep prompt response lightweight: answer prompt, attach memory, submit.
- Start albums as lightweight metadata/grouping, not a full DAM system.
- Make Markdown the release artifact for `FB-126`; treat PDF as optional if generation remains deterministic.

## Validation Expectations

- `FB-124`
  - `uv run pytest tests/test_prompts.py tests/test_email_delivery.py tests/test_access_control.py -q`
- `FB-125`
  - `uv run pytest tests/test_media.py tests/test_multimedia.py -q`
  - `make test-ui-playwright`
- `FB-126`
  - `uv run pytest tests/test_book_export.py tests/test_access_control.py -q`
- Sprint hygiene
  - `git diff --check`

## Exit Criteria

- Steward can send prompt campaigns and receive usable responses.
- Weekly digest is privacy-safe and preference-aware.
- Gallery/timeline media discovery feels materially better than S50.
- Family Book can produce a giftable draft export, with Markdown guaranteed and PDF optional if stable.
