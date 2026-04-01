# Task Packet - FB-086 Comprehensive Demo Seed Data

## Objective

Build a rich synthetic seed dataset of ~100 people that stress-tests the system with international names, complex relationships, diverse life stages, and edge cases — providing a realistic testing corpus for staging.

## Why / KPI

- The current Playwright seed has ~20 people with simple Anglo names. It doesn't exercise internationalization, complex family structures, or edge cases.
- Staging needs realistic data to catch rendering bugs, encoding issues, and layout problems before production.
- CFLSR depends on the app handling real-world family diversity — not just ASCII names and nuclear families.

## Scope

- In scope:
  - **~100 synthetic people** across 4-5 extended family branches, spanning 4-5 generations
  - **International name diversity**:
    - Chinese names (李明, 王小红) — tests CJK character rendering
    - Japanese names (田中太郎, 佐藤花子) — tests CJK + different naming conventions
    - Russian/Cyrillic names (Дмитрий Иванович Петров) — tests Cyrillic + patronymics
    - Eastern European with diacritics (Łukasz Wójcik, Jiří Dvořák)
    - German umlauts (Müller, Schröder)
    - French/Spanish cedillas and accents (François, José María García López)
    - Arabic names (أحمد محمد) — tests RTL-capable fields
    - Very long names (>40 characters) — tests layout overflow
    - Very short names (1-2 characters) — tests minimum width
  - **Complex relationships**:
    - Blended families (step-parents, half-siblings)
    - Adoptive relationships
    - Multiple marriages/partnerships
    - Single parents
    - Co-parents without partnership
    - Guardian relationships
    - 4+ children in one family (tests tree layout density)
  - **Diverse life stages**:
    - Living persons (ages 0-100)
    - Deceased persons (with death dates and burial info)
    - Persons with unknown birth dates ("about 1920")
    - Persons with only approximate dates
  - **Data richness on select persons**:
    - Bio text (some long, some short)
    - Place history entries
    - Education and career entries
    - Multiple languages
    - Medical conditions (on a few)
    - Photos (reuse existing demo photos, assigned to varied persons)
  - **Seed script**: extend `tests/ui/playwright_seed.py` or create a separate `app/seed_comprehensive.py` that can be run via `uv run python -m app.seed_comprehensive`
  - **Idempotent**: safe to re-run (clears and re-creates)
  - **Controlled by env var**: only runs when `LOAD_DEMO_DATA=comprehensive` or similar
- Out of scope:
  - Real family data
  - Performance benchmarking (separate concern)
  - Automated test assertions against the seed data

## Task Type

- developer tooling / test infrastructure

## Likely Files

- `app/seed_comprehensive.py` (new — the comprehensive seed script)
- `docker/start.sh` (add support for LOAD_DEMO_DATA=comprehensive)

## Acceptance Criteria

- [ ] Seed creates ~100 persons across 4-5 generations.
- [ ] Names include Chinese, Japanese, Russian, Eastern European, German, French/Spanish, Arabic, and very long/short names.
- [ ] Relationships include biological, adoptive, step, guardian, co-parent, and multiple partnerships.
- [ ] Ages range from infant to 100+, with both living and deceased persons.
- [ ] Select persons have rich data (bio, place history, education, career, languages, photos).
- [ ] Approximate/unknown dates are represented ("about 1920", "before 1900").
- [ ] Script is idempotent (safe to re-run).
- [ ] Controlled by env var (doesn't run in production).
- [ ] Tree renders all 100+ persons without layout breakage.
- [ ] International names render correctly in tree nodes, sidebar, wiki pages.

## Risk and Verification Notes

- Unicode edge cases: ensure SQLite handles all character sets (it does, but verify emoji and RTL).
- Tree layout: 100+ persons will test the D3 force layout at scale. Watch for overlapping nodes.
- Very long names: verify they don't overflow node labels or sidebar headers.
- The seed should create realistic family structures, not 100 unconnected persons.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Seed runs without errors
- [ ] Tree renders the full dataset
- [ ] International names display correctly across all surfaces
