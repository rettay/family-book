# Task Packet - FB-095 Photo Editing — Crop, Rotate, Resize

## Objective

Add basic photo editing (crop, rotate, resize) to the media upload flow and to existing photos in the gallery, using Cropper.js, so family members can make scanned or phone photos presentable before they enter the family record.

## Why / KPI

- Older relatives frequently upload sideways scans or portrait photos with large white borders. Today admins must edit photos externally and re-upload. This is a manual step that breaks the contribution loop.
- If a `mobile_first_relative` can upload a photo and fix it in the same session, the contribution is complete in one visit — directly improving CFLSR.
- Cropper.js is MIT-licensed, widely used, and requires no backend changes for the editor itself.

## Scope

**In scope:**
- **Upload flow edit step:** After a user selects an image file (before submitting the upload form), an optional "Edit photo" step is available. Clicking "Edit before upload" opens a Cropper.js modal.
  - Operations: free-form crop, rotate 90° CW/CCW, flip horizontal, flip vertical
  - Confirm → `canvas.toBlob()` produces a new Blob that replaces the original `File` in the upload form
  - Skip → original file is uploaded unchanged
- **Edit existing photo:** An "Edit photo" button on the media detail view and on the gallery item context (admin or media owner only)
  - Opens Cropper.js modal with the existing image loaded
  - Confirm → the edited image is POSTed to a new endpoint `POST /api/media/{media_id}/edit-image` that replaces the stored file and regenerates thumb/medium variants
  - The media record's `updated_at` is bumped; no new Media row is created
- Cropper.js loaded from a static file (`app/static/js/vendor/cropper.min.js` and `cropper.min.css`) — not from CDN (works offline / on private family deployment)
- Supported input types: image/jpeg, image/png, image/webp, image/gif (GIF output is JPEG after edit)
- Output format: JPEG at 92% quality for all edited images
- The edit modal shows: image canvas (Cropper.js), rotate left button, rotate right button, flip H button, flip V button, aspect ratio free toggle, Confirm button, Cancel button

**Out of scope:**
- Colour correction, brightness, contrast adjustments
- Drawing/annotation tools
- Editing non-image media (audio, video, PDF)
- Revision history for edited photos
- Undo/redo beyond Cropper.js built-in reset

## Task Type

- Member-facing UI — media upload + gallery enhancement

## Dependencies

- Existing media upload flow (upload modal, `/api/media` POST endpoint)
- Existing media detail/gallery views
- `thumb` and `medium` variant generation service must be callable from the new edit endpoint

## Target Personas

- `mobile_first_relative` — uploads a sideways phone photo or a poorly-cropped scan
- `family_admin` — fixes presentation-quality of legacy media already in the system
- `genealogy_researcher` — crops a group photo to isolate the relevant person

## Changed Surfaces

- Media upload modal (upload flow — optional edit step)
- Gallery item actions (new "Edit photo" button)
- Media detail view (new "Edit photo" button)
- New backend endpoint: `POST /api/media/{media_id}/edit-image`

## Likely Files

- `app/static/js/vendor/cropper.min.js` + `cropper.min.css` (new — download and commit)
- `app/templates/partials/media_upload_modal.html` (or equivalent) — add "Edit before upload" affordance, add `#photo-edit-modal` container
- `app/templates/gallery.html` and media detail partial — add "Edit photo" button
- `app/static/js/tree.js` or a new `app/static/js/photo_edit.js` — Cropper.js initialisation, canvas→Blob logic, existing-photo edit flow
- `app/routes/media.py` — new `POST /api/media/{media_id}/edit-image` endpoint
- `app/services/media_service.py` or variant generation service — expose `regenerate_variants(media_id)` helper if not already callable
- `app/static/css/main.css` — photo edit modal styles, button layout

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual: upload a photo → click "Edit before upload" → crop/rotate → confirm → upload
# Result: uploaded image is the cropped/rotated version, not the original
# Manual: open gallery → click "Edit photo" on an existing image → rotate → confirm
# Result: image in gallery updated; thumb/medium variants regenerated

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] Cropper.js is served from a local static file (no CDN call).
- [ ] During upload: "Edit before upload" button appears after file selection for image files.
- [ ] Clicking it opens the edit modal with the selected image loaded in Cropper.
- [ ] Rotate left, rotate right, flip horizontal, flip vertical controls work.
- [ ] Confirming the edit replaces the file-to-upload with the edited Blob; upload proceeds normally.
- [ ] Skipping edit uploads the original file unchanged.
- [ ] For existing photos: "Edit photo" button visible to media owner and admins on the gallery item and media detail view.
- [ ] Opening edit for an existing photo loads the current image in Cropper.
- [ ] Confirming sends `POST /api/media/{media_id}/edit-image` with the edited image bytes.
- [ ] The endpoint replaces the stored file, regenerates thumb and medium variants, and returns the updated media record.
- [ ] The gallery/detail view reflects the updated image after the edit (HTMX refresh or page reload).
- [ ] Non-image media types do not show the "Edit photo" button.
- [ ] `uv run pytest tests/` passes.

## Structural Oracle

- `#photo-edit-modal` present in DOM (hidden by default)
- `#photo-edit-modal canvas` present after Cropper init
- `[data-photo-edit-btn]` on gallery items for image media
- `POST /api/media/{media_id}/edit-image` returns 200 with updated media record

## Risk and Verification Notes

- **Cropper.js initialisation:** Cropper requires the `<img>` element to be visible (not `display:none`) when `new Cropper(imgEl, options)` is called. Open the modal first, then init Cropper inside an `onshown` callback or `setTimeout(0)`.
- **canvas.toBlob() for upload:** Replace the `input[type=file]` value by constructing a `DataTransfer`, appending the Blob as a `File`, and assigning `input.files = dt.files`. This is the standard workaround for un-settable `files` property. Test on Safari — `DataTransfer` constructor requires recent Safari.
- **Variant regeneration:** The existing variant generation for uploads (thumb/medium) must be callable post-save. Confirm the service function is importable in the new endpoint. If it is inline in the upload handler, extract it first.
- **File size:** After editing, the JPEG output may be larger than the input (e.g. a heavily compressed WebP becomes a 92%-quality JPEG). This is acceptable — do not impose a size limit in this sprint.
- **Edit button visibility:** Use the same `media.uploaded_by == current_user.id or current_user.is_admin` guard as the delete button.
- **Undo in Cropper:** Cropper.js has a built-in reset button — include it in the modal controls so users can start over without reopening.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Edit during upload | Upload image → edit → confirm | Uploaded file matches crop | Cropped image in gallery | Original uploaded instead |
| Skip edit | Upload image → skip | Uploaded file is original | Original image in gallery | Cropped version uploaded |
| Edit existing | Gallery → Edit photo → rotate → confirm | Updated image in gallery | Image updated, variants regenerated | Image unchanged |
| Non-image no button | PDF in gallery | No edit button | Button absent | Button shown on PDF |
| Access control | Non-owner non-admin | Edit button absent | Button not shown | Button shown |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Cropper.js committed as static asset (no CDN)
- [ ] `uv run pytest tests/` passes
- [ ] Manually verified: upload edit flow; existing photo edit flow; variant regeneration confirmed in dev DB
