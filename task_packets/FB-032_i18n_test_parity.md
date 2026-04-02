# FB-032: i18n Test Parity

## Objective

Add an automated test that validates all 3 locale files (en, es, ru) have matching key sets, catching missing or extra keys before they ship.

## Why / KPI

**CFLSR impact:** Medium. When locale keys are added to one file but forgotten in another, users of that locale see raw key strings instead of translated text. This has been a manual verification step every sprint — an automated test prevents regression and saves auditor time.

**Gap reference:** Auditor finding S24-F03 (P3, pre-existing). No `tests/test_i18n.py` exists despite being referenced as a verification step in sprint plans since S20.

## In Scope

- New `tests/test_i18n.py` with:
  - `test_all_locales_have_same_keys` — load all 3 JSON locale files, flatten nested keys into dot-separated paths, assert all 3 sets are identical
  - `test_locale_files_are_valid_json` — confirm each locale file parses without error
  - `test_no_empty_translations` — verify no key has an empty string value
- The test should support nested locale structure (e.g., `person.first_name`, `wiki.edit_section`)

## Out of Scope

- Translation quality validation
- Adding new locale keys
- RTL or plural form support
- Translation management tooling

## Dependencies

- Existing locale files at `locales/en.json`, `locales/es.json`, `locales/ru.json`

## Acceptance Criteria

- [ ] `tests/test_i18n.py` exists and passes
- [ ] Test catches a simulated missing key (add a test-only key to one locale, verify assertion fails)
- [ ] Test works with the current nested JSON structure
- [ ] `uv run pytest tests/test_i18n.py -q` passes

## Likely Files

| File | Change |
|------|--------|
| `tests/test_i18n.py` | New test file |

## Complexity

Low. Single test file, no backend changes, no migration, no template changes.

## Definition of Done

- `tests/test_i18n.py` exists with 3+ tests
- All locale files pass parity check
- Full test suite passes

## Evaluation Environment

- **Task:** Validate locale key parity across 3 files
- **Verifier:** pytest assertion comparing flattened key sets
- **Reference/oracle:** Set comparison — if sets differ, the diff shows exactly which keys are missing/extra
- **Expected evidence:** `uv run pytest tests/test_i18n.py -v` shows 3+ passing tests
- **Known failure modes:** Test only checks key existence, not translation quality
- **Verifiability class:** High — binary pass/fail on set equality

## Execution Budget

- Builder may implement autonomously — no exploration needed
- No escalation expected
- Material scope drift: adding translation quality checks or new locales
