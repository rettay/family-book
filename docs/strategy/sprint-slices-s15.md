# Sprint Slices - S15 Rich Family Storytelling and Multi-Item Authoring

## Slice Order

1. `S15-1 Rich Story Composition in Tree Context`
2. `S15-2 Multi-Item Media and Story Grouping`
3. `S15-3 Cross-Person Family Event Authoring`

## `S15-1 Rich Story Composition in Tree Context`

### Goal

Make the tree sidebar capable of richer story composition so members can capture a fuller memory without leaving the tree workspace.

### Scope

- improved in-tree story composition UX
- support for multiple attachments in one story flow
- better save feedback and immediate post-create review in the tree sidebar

### Acceptance Checks

- a member can create a richer story from the tree without leaving `/tree`
- multiple attachments can be associated with the same story flow
- the sidebar remains clear and keyboard reachable during and after story creation

## `S15-2 Multi-Item Media and Story Grouping`

### Goal

Make a small group of story-linked media items feel like one family-memory unit instead of a flat sequence of uploads.

### Scope

- grouped post-create presentation for story-linked media
- better browsing and review of story-related attachments in the sidebar
- stronger empty and populated states for media-backed stories

### Acceptance Checks

- story-linked media is presented as a coherent grouped memory
- users can review attached media and surrounding narrative from the same tree workspace
- grouped media handling does not regress upload or browse flows already proven in Sprint 14

## `S15-3 Cross-Person Family Event Authoring`

### Goal

Make shared family events first-class in the tree workspace instead of leaving them as ambiguous tagged-person stories.

### Scope

- clearer event authoring intent in the tree sidebar
- improved multi-person tagging and event participant feedback
- clearer distinction between personal stories and shared events

### Acceptance Checks

- a member can author a shared family event from the tree and tag multiple people
- the resulting sidebar state makes the event participants obvious
- the workflow remains understandable without falling back to older forms or feed routes

## Validation Baseline

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Recommended Builder Order

1. `S15-1`
2. `S15-2`
3. `S15-3`

This order matters because the richer story form and review flow define the authoring shell for the rest of the sprint. Grouped media should feel coherent inside that shell before shared-event authoring expands the same workflow across multiple people.
