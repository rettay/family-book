# Sprint Slices - S51 Lovable Engagement

## Slice Order

1. `S51-1 Prompt Campaign Core`
2. `S51-2 Digest and Preferences`
3. `S51-3 Media Discovery and Albums`
4. `S51-4 Family Book Draft Export`
5. `S51-5 Closeout and Follow-Up Capture`

## `S51-1 Prompt Campaign Core`

Goal: create the first recurring contribution loop.

Packets:
- `FB-124`

Scope:
- prompt campaign model
- steward creates and sends prompt to selected relatives
- prompt landing and response flow
- response becomes a story or media inbox submission

Acceptance checks:
- steward can send a prompt campaign
- relative can open a prompt and contribute
- prompt responses respect role and visibility limits

## `S51-2 Digest and Preferences`

Goal: create a weekly reason to return without creating privacy leaks.

Packets:
- `FB-124`

Scope:
- digest assembly
- birthday/anniversary/upcoming items
- unanswered prompt reminders
- digest preference and unsubscribe controls

Acceptance checks:
- digest includes only visible content for the recipient
- digest can be disabled
- unsubscribe and preference changes are auditable

## `S51-3 Media Discovery and Albums`

Goal: make the archive pleasant to browse after new contributions arrive.

Packets:
- `FB-125`

Scope:
- album/collection model
- gallery search
- add/remove media to album
- timeline filters for person/album/decade
- empty-state and add-to-album UX

Acceptance checks:
- albums can be created, edited, and deleted
- search works across core media metadata
- timeline/gallery keep access-control guarantees

## `S51-4 Family Book Draft Export`

Goal: produce a giftable outcome from the archive.

Packets:
- `FB-126`

Scope:
- book project model
- selected people/stories/media
- Markdown draft export
- PDF draft only if low-risk
- provenance/source note inclusion

Acceptance checks:
- Markdown draft export works
- export respects visibility and private media settings
- PDF either works or is explicitly deferred behind a documented fallback

## `S51-5 Closeout and Follow-Up Capture`

Goal: leave the engagement loop shippable and measurable.

Scope:
- audit builder evidence
- record what remains for `S52`
- note any ops follow-up for prompt scheduling/email volume

Acceptance checks:
- board clearly shows S51 status and next sprint candidate
- packets record evidence and any scoped deferrals
- no hidden reliance on manual operator knowledge

## Builder Order

1. `FB-124`
2. `FB-125`
3. `FB-126`

## Suggested Scope Discipline

- Keep digest generation batch/simple for now; no need for generalized automation infrastructure.
- Keep albums lightweight and metadata-driven.
- Keep `FB-126` Markdown-first. PDF is allowed only if it is a thin generation layer over the same content model.
