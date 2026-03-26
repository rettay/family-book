# FB-029: Tree Photo Headshots and Add-Photo Prompt

## Objective

Improve the tree node photo experience by enhancing the circular headshot rendering and adding a visual prompt on photo-less nodes that invokes the photo upload flow when clicked.

## Why / KPI

**CFLSR impact:** High. The tree is the primary workspace. Photo-less nodes show initials on colored circles — functional but impersonal. Adding a subtle "add photo" affordance on empty nodes turns passive viewing into active contribution ("I have a photo of grandma, let me add it"). Better photo rendering makes the tree feel like a real family artifact rather than a technical diagram.

**Gap reference:** User feedback (2026-03-26). Enhances existing photo support (photo_url on Person, circular SVG clip in tree.js).

## In Scope

### Add-photo prompt on empty nodes
- When a tree node has no `photo_url`, overlay a subtle camera/plus icon on the initials circle
- Clicking the icon invokes the existing photo upload flow for that person
- The prompt should be visually subtle (low opacity, appears on hover) — not distracting at rest
- After upload completes, the node re-renders with the new photo

### Photo rendering improvements
- Evaluate whether the current center-crop (`preserveAspectRatio='xMidYMid slice'`) is sufficient or whether face-detection smart cropping would meaningfully improve results
- If face detection is warranted: use PIL-based face detection during thumbnail generation to compute a face-centered crop region, store crop metadata on Media
- Ensure thumbnail resolution (currently 400x400) is sufficient for the 60px circular display — consider a smaller, sharper tree-specific thumbnail
- Handle portrait vs. landscape photos gracefully in the circular viewport

## Out of Scope

- Changing tree node shape (stays circular)
- Bulk photo upload or AI-assisted photo matching
- Photo editing/cropping UI in the browser
- Face recognition (identifying who is in a photo)

## Acceptance Criteria

- [ ] Tree nodes without photos show a camera/plus icon overlay
- [ ] Clicking the icon opens the photo upload flow for that person
- [ ] After successful upload, the node re-renders with the new photo
- [ ] Existing photo rendering continues to work (no regression)
- [ ] The add-photo prompt is visually subtle and not distracting
- [ ] Mobile: the prompt is touch-accessible
- [ ] Tests pass with no regression

## Likely Files

| File | Change |
|------|--------|
| `app/static/js/tree.js` | Render camera icon on photo-less nodes, click handler for upload |
| `app/static/css/main.css` | Styling for camera overlay icon |
| `app/services/media_service.py` | Potentially: face-detection crop during thumbnail generation |
| `app/models/media.py` | Potentially: crop metadata field |

## Complexity

Medium. The add-photo prompt is straightforward (SVG overlay + click handler). Face-detection cropping is the stretch goal — evaluate before committing.

## Definition of Done

- Photo-less tree nodes show add-photo affordance
- Clicking it uploads a photo for that person
- All existing tests pass
