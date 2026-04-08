# Task Packet - FB-116 Paid Launch Trust Center

Status: Proposed

## Objective

Create a public trust center and internal truth table for privacy, encryption, backups, export, deletion, and cancellation.

## Why / KPI

Privacy is the product wedge. Trust copy must be precise, especially because current encryption is selected field-level encryption, not full end-to-end or zero-knowledge encryption.

## Scope

- In scope:
  - public trust page content
  - privacy/security truth table
  - export/delete/cancel documentation
  - update README/landing copy where claims are unsupported
  - paid beta terms/privacy draft placeholders
- Out of scope:
  - formal legal review
  - SOC 2 or compliance certification
  - client-side encryption redesign

## Likely Files

- `docs/ops/trust-center.md`
- `docs/ops/export-and-delete.md`
- `README.md`
- `app/templates/landing.html`
- `app/templates/base.html`
- `tests/test_pages.py`

## Acceptance Criteria

- [ ] Trust docs distinguish field-level encryption, authenticated media, backups, and transport security.
- [ ] No public copy claims zero-knowledge or end-to-end encryption unless implemented.
- [ ] Export/delete/cancel paths are understandable.
- [ ] Backup and restore guarantees match implementation.
- [ ] Landing/README copy aligns with `FB-113` permission behavior.

## Validation Commands

- `uv run pytest tests/test_pages.py -q`
- `git diff --check`

## Definition of Done

- [ ] Trust copy is launch-safe for paid beta.
