# Task Packet - FB-054 Multi-Value Contact and Social Edit UX

## Objective

Build card-based add/remove editing for phone numbers, email addresses, and social media accounts in the person edit form, replacing single-field inputs with the multi-value arrays from FB-053.

## Why / KPI

- Family members currently can only store one phone and one email per person. Social media is six fixed fields with no room for new platforms.
- CFLSR improves when contributors can add multiple contact methods and social accounts and have them display correctly to other members.

Primary KPI:
- enable multi-value phone, email, and social editing in the person edit form.

Secondary KPI:
- introduce a reusable card-based multi-value editing pattern that future fields can adopt.

## Scope

- In scope:
  - phone number cards: number input, type dropdown (mobile/home/work/other), optional label, primary radio
  - email address cards: address input, type dropdown (personal/work/other), primary radio
  - social account cards: platform dropdown (instagram, facebook, twitter, linkedin, tiktok, youtube, threads, bluesky, other), handle/URL input, visibility toggle
  - add/remove controls for each card type with keyboard accessibility
  - primary-flag radio behavior (selecting one unsets others) via JS
  - form serialization: collect card data into JSON arrays for the existing PUT endpoint
  - name history cards: surname, reason dropdown, year, notes with add/remove
  - obituary URL field in memorial section (text input with URL validation)
  - deprecation of old single-field phone/email/social inputs (hide them, read from new arrays)
  - i18n for new labels across en, es, ru
- Out of scope:
  - address changes (FB-055)
  - bio Trix editor integration (FB-056)
  - languages combobox (FB-056)
  - education/career/organizations structured editing (FB-056)
  - phone number format validation beyond basic HTML pattern (no libphonenumber dependency)

## Task Type

- member-facing form UX enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-053 (data model must exist before form can bind to it).
- FB-056 depends on this establishing the card-based editing pattern.

## Changed Surfaces

- `person_edit`

## Target Personas

- Primary: `contributing_member`, `family_admin`
- Safety: `mobile_first_relative`, `genealogy_researcher`

## Required Scenario IDs

- `add_multiple_phone_numbers`
- `add_multiple_email_addresses`
- `manage_social_accounts`
- `record_name_history`
- `update_core_identity_fields`
- `save_without_losing_context`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`, `ru`

## Likely Files

- `app/templates/person_edit.html`
- `app/static/css/main.css`
- `locales/en.json`, `locales/es.json`, `locales/ru.json`
- `tests/test_pages.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  replace single-field contact/social inputs with card-based multi-value editing
- Verifier:
  structural review, deterministic page-load assertions, manual browser check
- Reference/oracle:
  existing contact-address card pattern in person_edit.html as the baseline UX
- Expected evidence:
  page-load tests pass, i18n keys present, form serializes correctly to API
- Known failure modes / reward hacks:
  - cards render but serialization loses data on save
  - add/remove works on desktop but breaks on mobile
  - primary radio does not unset siblings
  - i18n keys added to en but missing from es/ru
- Verifiability class:
  `bounded-judgment`
- Context policy:
  follow the existing address-card pattern exactly; do not introduce new JS libraries or component frameworks

## UI Review Requirements

- Structural oracle:
  - confirm card markup follows the existing `.person-edit-address-card` pattern
  - confirm ARIA labels on add/remove buttons
- Browser oracle:
  - page loads without JS errors
  - add/remove/primary interactions work
  - form submits successfully with multi-value data
- Visual/persona oracle:
  - `contributing_member` can add 2 phones and 1 email without confusion
  - `mobile_first_relative` can reach add/remove on narrow viewport
- Required artifacts:
  - test output
  - i18n key coverage confirmation

## Acceptance Criteria

- [ ] Phone number cards support add/remove with type, label, number, and primary radio.
- [ ] Email address cards support add/remove with type, address, and primary radio.
- [ ] Social account cards support add/remove with platform dropdown, handle/URL, and visibility toggle.
- [ ] Name history cards support add/remove with surname, reason, year, and notes.
- [ ] Obituary URL field appears in memorial section.
- [ ] All card controls are keyboard accessible (tab, enter, delete).
- [ ] Form serialization sends new arrays to PUT endpoint and data round-trips correctly.
- [ ] Old single-field inputs are replaced by new card-based UI.
- [ ] i18n keys exist for all new labels in en, es, and ru.
- [ ] Mobile layout does not clip or hide add/remove controls.

## Risk and Verification Notes

- Complexity hotspots:
  - form serialization must collect dynamically-created card fields into JSON arrays
  - primary-radio mutual exclusion must work across dynamically-added cards
- Likely shallow-pass failure modes:
  - cards render but data is lost on save
  - only desktop tested
- Required verification depth:
  - page-load + API round-trip + i18n assertions
- Sufficient discriminative power means:
  tests should fail if card data does not persist through save, or if i18n keys are missing.

## Execution Budget

- Builder may explore:
  - factoring card-rendering JS into a shared helper for reuse across phone/email/social
- Builder must escalate if:
  - the existing form serialization pattern cannot handle nested card arrays
- Material scope drift:
  - address schema changes, bio editor, languages
- Proof obligations before review:
  - data round-trips from card UI → API → reload → card UI

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions on person edit form
