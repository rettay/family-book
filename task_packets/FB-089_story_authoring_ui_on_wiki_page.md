# Task Packet - FB-089 Story Authoring UI on Wiki Page

## Objective

Add a "Stories" section to the wiki person page where any family member can read all attributed stories and write new ones — using the Trix rich-text editor and HTMX inline editing, consistent with the bio section.

## Why / KPI

- The stories API (FB-088) has no front-end surface until this packet ships. This is the primary contribution surface for the stories feature.
- Reading stories is the most frequent interaction — the section must render clearly and invite contribution without requiring admin access.
- CFLSR improves when contributing members can complete a meaningful loop in one page visit: read existing stories, add their own, and see it appear immediately.

## Scope

**In scope:**
- New "Stories" section in `app/templates/wiki_person.html` — positioned after the media gallery section, before the Research Notes section
- Story list: each story displays title, rich-text body, author name, relative timestamp (e.g., "3 days ago"), and Edit/Delete controls
- "Add Story" button visible to all authenticated members — opens inline Trix editor form (HTMX)
- HTMX inline edit flow:
  - Click "Edit" → story card swaps to edit form (GET `/api/wiki/{slug}/stories/{id}` prefills form)
  - Save button → POST/PUT → HTMX replaces the story card in place
  - Cancel → HTMX restores original card without page reload
- Delete button: visible to author and admin only (rendered conditionally server-side); confirms with a simple inline confirm step before DELETE
- New Trix editor instance per story (add and edit forms); title is a plain `<input>`, body uses Trix
- Author name rendered from `story.author_name` returned by the API
- Empty state: if no stories, show `t('stories.story_empty')` with an "Add Story" button
- New partials:
  - `app/templates/partials/wiki_story_card.html` — single story card (used for list and for HTMX swap target)
  - `app/templates/partials/wiki_story_form.html` — add/edit form with Trix + title input + Save/Cancel
- Pass `stories` list and `story_count` from wiki route to template context
- i18n: use all 13 keys from FB-088

**Out of scope:**
- Audio playback (audio_media_id placeholder in model; no player UI)
- Story pagination (all stories loaded at once; paginate in a future sprint if needed)
- Story ordering or pinning controls
- Story revision history
- Markdown rendering (body is HTML from Trix, rendered with `| safe` filter)

## Task Type

- Member-facing UI — wiki person page enhancement

## Dependencies

- FB-088 must be complete (API endpoints and i18n keys must exist before this packet executes)

## Target Personas

- `contributing_member` — primary author and reader; must be able to add and edit stories without admin access
- `genealogy_researcher` — contributes sourced, long-form stories; needs Trix editor to work well for dense text
- `mobile_first_relative` — reads stories on mobile; cards must be readable on narrow viewport
- `family_admin` — can delete any story; delete control must be visible and unambiguous

## Changed Surfaces

- `GET /wiki/{slug}` — new Stories section rendered on the person wiki page

## Required Viewports

- Desktop (1280px): full section visible with add/edit controls readable
- Mobile (390px): story cards readable, Trix editor usable, title input accessible

## Likely Files

- `app/templates/wiki_person.html` (add Stories section)
- `app/templates/partials/wiki_story_card.html` (new)
- `app/templates/partials/wiki_story_form.html` (new)
- `app/routes/wiki.py` (pass `stories` and `story_count` to wiki_person context)
- `app/static/css/main.css` (story card styles, add-story button)
- `locales/en.json` and 4 other locales (all keys already added in FB-088)

## Local Validation Commands

```bash
# Start the dev server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run pytest
uv run pytest tests/test_wiki.py -v
uv run pytest tests/ -k "story" -v

# Verify i18n parity (no new keys introduced beyond FB-088)
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] Wiki person page renders a "Stories" section after the media gallery.
- [ ] If no stories exist, empty state text and an "Add Story" button are shown.
- [ ] If stories exist, each is shown as a card with: title (bold), body (rich text rendered), author name, and a relative or formatted date.
- [ ] "Add Story" button is visible to any authenticated member and opens an inline form with a title input and Trix editor.
- [ ] Submitting the add form creates the story and replaces the form with the new story card without a full page reload (HTMX swap).
- [ ] Each story card has an "Edit" button. Clicking it swaps the card to an edit form (prefilled). Saving updates the card in place. Cancelling restores the original card.
- [ ] Delete button is visible only to the story's author and to admins. Clicking triggers a confirm step; confirming sends DELETE and removes the card.
- [ ] Non-author non-admin member does NOT see the delete button on stories they did not write.
- [ ] Trix editor initializes correctly for both add and edit forms. Previously saved rich text is correctly prefilled in the edit form.
- [ ] Story cards are readable on 390px mobile viewport (no horizontal overflow, controls accessible).
- [ ] No full page reload is required for add, edit, or delete operations.
- [ ] `uv run pytest tests/test_wiki.py` passes with tests covering story list rendering and at least the create flow.

## Structural Oracle

- `#wiki-stories-section` exists in DOM when page loads
- `[data-story-id]` cards count matches API story count
- Empty state `[data-wiki-stories-empty]` visible only when count is 0
- Add form contains `input[name="title"]` and `trix-editor`
- Edit/Delete buttons have `data-story-author-id` or similar for conditional rendering

## Risk and Verification Notes

- **Trix in HTMX swaps:** Trix editors do not auto-initialize inside dynamically injected HTML. Use a `htmx:afterSwap` or `htmx:afterSettle` event listener to call `Trix.start()` or re-initialize the editor element after swaps.
- **`| safe` filter:** body content is rendered with Jinja2 `| safe`. This is correct because body is sanitized server-side in FB-088. Do not sanitize again in the template.
- **Author name rendering:** `author_name` should come from the API response, not from a separate DB query in the template. Confirm the list endpoint returns this field.
- **HTMX swap target scoping:** Each story card must have a unique `id` (e.g., `id="story-{{ story.id }}"`) so HTMX `hx-target` can replace the correct card.
- **Delete confirm step:** Do not use native `window.confirm()`. Use an inline HTMX confirmation pattern (e.g., a two-button confirm row that swaps in on first click).
- **Shallow-pass failure mode:** If the builder renders the stories section as static HTML without wiring HTMX, the section will appear but add/edit/delete will do full page reloads. Verify that all mutations are swap-only.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Section renders | Visit `/wiki/{slug}` | DOM `#wiki-stories-section` | Section visible | Section absent or conditional on admin |
| Empty state | Visit page with 0 stories | `[data-wiki-stories-empty]` visible | Empty state text shown | Always hidden |
| Add story | Fill form + submit | New card appears, no reload | Story card rendered in DOM | Full page reload |
| Edit by non-author | Click Edit as a different member | Edit form opens | Form shown | 403 or button hidden |
| Delete shown to author | Log in as author | Delete button visible | Button present | Button absent |
| Delete hidden from non-author non-admin | Log in as third member | Delete button absent | Button not rendered | Button shown incorrectly |
| Trix in edit form | Open edit form | Trix editor populated | Prior content appears | Blank editor |
| Mobile layout | 390px viewport | Cards legible, no overflow | No clipping | Controls off-screen |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] i18n parity maintained
- [ ] HTMX add/edit/delete flows tested manually on dev server
- [ ] Mobile layout verified at 390px
- [ ] Trix re-initialization confirmed in HTMX-injected forms
