# Person Edit UI Audit Evidence - Details Workspace Refinement

Surface under review: `person_edit`

Scope under audit:
- person editor details-section refinement on `/people/:id/edit`
- supporting backend truthfulness for multi-nickname, typed-address, phone, and memorial-state handling

Resolved from canonical sources:
- Persona registry: `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml`
- UI surface matrix: `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml`

Resolved personas:
- `family_admin`
- `contributing_member`
- `mobile_first_relative`
- `genealogy_researcher`

Resolved scenarios:
- `update_core_identity_fields`
- `capture_normalized_place_with_autocomplete`
- `add_social_or_contact_info`
- `save_without_losing_context`

Resolved viewports/locales:
- `desktop`, `mobile`
- `en`, `es`

## Structural Lane

Artifacts:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/person-edit-ui-codemap.json`

Changed files on `person_edit`:
- `/Users/cheech/code/family-book/app/templates/person_edit.html`
- `/Users/cheech/code/family-book/app/routes/persons.py`
- `/Users/cheech/code/family-book/app/models/person.py`
- `/Users/cheech/code/family-book/app/schemas.py`
- `/Users/cheech/code/family-book/app/services/revision_service.py`
- `/Users/cheech/code/family-book/app/access_control.py`
- `/Users/cheech/code/family-book/alembic/versions/a1b2c3d4e5f6_add_person_editor_identity_contact_fields.py`

Result:
- the editor is now backed by real model/API support for `alternate_nicknames`, `contact_phone`, `contact_addresses`, and `remains_disposition`
- create and update flows normalize typed contact addresses through the same place-resolution path used by the main location fields
- memorial-state normalization now fails closed:
  - living people do not retain burial/final-resting data
  - cremated records do not retain cemetery/plot-only fields that the UI hides

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands reviewed:
- `uv run pytest tests/test_api.py tests/test_pages.py tests/test_models.py tests/test_i18n.py -q`
- focused browser proof on `/people/:id/edit` covering:
  - hidden country edits clearing stale coordinates
  - nickname chip entry
  - typed address repeater state
  - memorial disclosure and cremation-driven burial-field hiding

Result:
- `pytest`: `93 passed`
- focused browser proof: `passed`

High-signal person-edit checks covered by the current evidence:
- the edit surface still exposes coordinate-backed normalized place fields
- changing the hidden normalized country input clears stale lat/lng values instead of preserving mismatched coordinates
- multiple nicknames work as chips rather than a single overloaded text field
- typed multiple addresses can be added with address type and label metadata
- the memorial section starts hidden for living people, becomes visible when the person is marked deceased, and burial-site-only inputs hide when disposition is `cremated`

Note on the broad Playwright flow:
- the current `tests/ui/playwright-flow-checks.sh` run still ends red because of pre-existing unrelated `tree_workspace` failures later in the script
- the person-edit checks in that flow passed before those unrelated tree failures
- the focused post-patch browser proof above was run to verify the edited country-clearing oracle after the country field became hidden

## Visual / Persona Lane

Artifacts:
- Desktop editor state: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/person-edit-admin.png`
- Spanish localized editor: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/person-edit-es.png`
- Mobile editor layout: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/person-edit-mobile.png`

Review notes:
- `family_admin` / `update_core_identity_fields` / desktop / `en`
  - `person-edit-admin.png` shows the calmer section hierarchy, nickname chips, address repeater affordance, and memorial disclosure separated from everyday identity/contact inputs
- `contributing_member` / `add_social_or_contact_info` / desktop / `es`
  - `person-edit-es.png` shows localized section titles and labels on the changed details workspace
- `mobile_first_relative` / `add_social_or_contact_info` / mobile / `en`
  - `person-edit-mobile.png` shows the stacked mobile layout with reachable nickname, address, and memorial controls without horizontal clipping

## Reviewer Notes

- This bundle is specific to `person_edit`; existing `tree_workspace`, `calendar_workspace`, and `map_view` evidence remains separate in `/Users/cheech/code/family-book/output/audit`.
- The key truthfulness regressions found in audit were closed in code and in tests:
  - new-person creation now persists normalized contact-address coordinates from the normalized payload
  - living/cremated memorial-state transitions no longer leave hidden cemetery/plot data behind
